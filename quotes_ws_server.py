#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
 quotes_ws_server.py · Mac 실시간 시세 서버 (WebSocket 푸시 + REST)
------------------------------------------------------------
 fetch_quotes_server.py 를 대체 — 여기에 KIS WebSocket(주식 실시간체결) + 브라우저 WS 푸시 추가.
  · 주식(국내 H0STCNT0 / 해외 HDFSCNT0): KIS WS 로 틱마다 실시간 갱신
  · 지수·환율·크립토: 3초 폴러(REST, fetch_quotes_server 로직 재사용)
  · 브라우저: /ws 로 스냅샷+델타 푸시(초 이하). REST /quotes 도 유지(CF 폴백·초기로드)
 포트: 8787(HTTP /quotes,/health, http.server 스레드) + 8788(WS /ws, asyncio)
 조회 전용(read-only). cloudflared named tunnel: /ws→8788, 그 외→8787.
============================================================
"""
import asyncio
import json
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import fetch_quotes_server as base   # 맵·폴러 함수 재사용(KR/US/IDX/FX/CRYPTO, _fetch_stocks, fetch_crypto)
import fetch_markets_kis as kis

HTTP_PORT = 8787
WS_PORT = 8788
POLL_SEC = 3
KIS_WS = "ws://ops.koreainvestment.com:21000"

CACHE = {}                      # id -> {price, chg}
CHANGED = set()                 # 마지막 flush 이후 바뀐 id
_last_access = 0.0
_lock = threading.Lock()

# KIS WS 구독 대상 (BRK 는 심볼에 '/' 있어 WS 제외 → 폴러가 담당)
WS_US = [(sid, base.kis.US_EXCD[sid], symb) for sid, symb in base.US if "/" not in symb]
WS_KR = list(base.KR)           # 6자리 코드


def _update(cid, price, chg):
    if not price:
        return
    with _lock:
        cur = CACHE.get(cid)
        if cur and abs(cur["price"] - price) < 1e-9 and abs(cur.get("chg", 0) - chg) < 1e-9:
            return
        CACHE[cid] = {"price": price, "chg": chg}
        CHANGED.add(cid)


# ---------------- 폴러(REST 3초): 지수·환율·크립토 + 주식 백스톱 ----------------
def _poll_blocking():
    out = {}
    if base.stock_market_open():
        try:
            out.update(base._fetch_stocks())      # 주식+지수+환율(+크로스)
        except Exception:
            pass
    out.update(base.fetch_crypto())               # 크립토 24h
    return out


async def poller():
    loop = asyncio.get_event_loop()
    ex = ThreadPoolExecutor(max_workers=2)
    while True:
        try:
            if CLIENTS or (time.monotonic() - _last_access < 30):   # WS 접속자 또는 최근 REST 조회
                out = await loop.run_in_executor(ex, _poll_blocking)
                for cid, q in out.items():
                    _update(cid, q["price"], q["chg"])
        except Exception as e:
            print("[poll]", str(e)[:80], flush=True)
        await asyncio.sleep(POLL_SEC)


# ---------------- KIS WebSocket(주식 실시간체결) ----------------
def _approval_key():
    body = json.dumps({"grant_type": "client_credentials",
                       "appkey": base.kis.APPKEY, "secretkey": base.kis.APPSECRET}).encode()
    req = urllib.request.Request("https://openapi.koreainvestment.com:9443/oauth2/Approval",
                                 data=body, headers={"content-type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=10).read())["approval_key"]


def _sub_msg(ak, tr_id, tr_key):
    return json.dumps({"header": {"approval_key": ak, "custtype": "P", "tr_type": "1", "content-type": "utf-8"},
                       "body": {"input": {"tr_id": tr_id, "tr_key": tr_key}}})


def _parse_tick(raw):
    """KIS WS 데이터('0|TRID|CNT|f^f^...') → (id, price, chg) 리스트."""
    out = []
    try:
        parts = raw.split("|")
        if len(parts) < 4:
            return out
        tr_id, data = parts[1], parts[3]
        f = data.split("^")
        if tr_id == "H0STCNT0":            # 국내: 0=코드,2=현재가,5=등락율
            code = f[0]
            out.append((code + ".KS", float(f[2]), float(f[5])))
        elif tr_id == "HDFSCNT0":          # 해외: 1=심볼,11=현재가,14=등락율
            symb = f[1]
            out.append((symb, float(f[11]), float(f[14])))
    except Exception:
        pass
    return out


async def kis_ws():
    import websockets
    while True:
        try:
            ak = _approval_key()
            async with websockets.connect(KIS_WS, ping_interval=None, max_size=None) as ws:
                for sid, excd, symb in WS_US:
                    await ws.send(_sub_msg(ak, "HDFSCNT0", "D" + excd + symb)); await asyncio.sleep(0.03)
                for code in WS_KR:
                    await ws.send(_sub_msg(ak, "H0STCNT0", code)); await asyncio.sleep(0.03)
                print(f"[kisws] 구독 {len(WS_US)}미국+{len(WS_KR)}국내", flush=True)
                async for m in ws:
                    if m[0] in "01":                       # 실시간 데이터
                        for cid, px, ch in _parse_tick(m):
                            _update(cid, px, ch)
                    elif "PINGPONG" in m:                  # 핑퐁 응답(연결유지)
                        await ws.send(m)
        except Exception as e:
            print("[kisws] 재연결:", str(e)[:80], flush=True)
            await asyncio.sleep(5)


# ---------------- 크립토 WebSocket(24시간 실시간) ----------------
async def crypto_ws():
    import websockets

    async def binance():
        streams = "/".join(v.lower() + "@ticker" for v in base.CRYPTO_USD.values())
        url = "wss://stream.binance.com:9443/stream?streams=" + streams
        inv = {v: k for k, v in base.CRYPTO_USD.items()}          # BTCUSDT -> BTC-USD
        while True:
            try:
                async with websockets.connect(url, ping_interval=None, max_size=None) as ws:
                    async for m in ws:
                        d = json.loads(m).get("data", {})
                        sid = inv.get(d.get("s"))
                        if sid:
                            _update(sid, float(d["c"]), float(d["P"]))
            except Exception as e:
                print("[binance ws]", str(e)[:60], flush=True); await asyncio.sleep(5)

    async def upbit():
        inv = {v: k for k, v in base.CRYPTO_KRW.items()}          # KRW-BTC -> UPBIT-KRW-BTC
        sub = json.dumps([{"ticket": "wi"}, {"type": "ticker", "codes": list(base.CRYPTO_KRW.values())}])
        while True:
            try:
                async with websockets.connect("wss://api.upbit.com/websocket/v1", ping_interval=None, max_size=None) as ws:
                    await ws.send(sub)
                    async for m in ws:
                        d = json.loads(m if isinstance(m, str) else m.decode())
                        sid = inv.get(d.get("code"))
                        if sid:
                            _update(sid, float(d["trade_price"]), float(d["signed_change_rate"]) * 100)
            except Exception as e:
                print("[upbit ws]", str(e)[:60], flush=True); await asyncio.sleep(5)

    await asyncio.gather(binance(), upbit())


# ---------------- 브라우저 WS 서버(스냅샷 + 델타 푸시) ----------------
CLIENTS = set()


async def ws_handler(conn):
    CLIENTS.add(conn)
    try:
        with _lock:
            snap = {"type": "snapshot", "quotes": dict(CACHE)}
        await conn.send(json.dumps(snap))
        async for _ in conn:            # 클라이언트→서버 메시지는 무시(핑 용도)
            pass
    except Exception:
        pass
    finally:
        CLIENTS.discard(conn)


async def broadcaster():
    import websockets
    async with websockets.serve(ws_handler, "127.0.0.1", WS_PORT, ping_interval=20):
        print(f"[ws] 브라우저 WS :{WS_PORT}/ws", flush=True)
        while True:
            await asyncio.sleep(0.1)          # 100ms flush → 초당 최대 10회 푸시
            if not CLIENTS:
                continue
            with _lock:
                if not CHANGED:
                    continue
                delta = {cid: CACHE[cid] for cid in CHANGED if cid in CACHE}
                CHANGED.clear()
            if delta:
                msg = json.dumps({"type": "delta", "quotes": delta})
                for c in list(CLIENTS):
                    try:
                        await c.send(msg)
                    except Exception:
                        CLIENTS.discard(c)


# ---------------- 실시간 군용기(ADS-B) 중계 ----------------
# 왜 Mac 을 경유하나: 커뮤니티 ADS-B 관측망이 데이터센터 IP 를 막는다.
#   airplanes.live  → 전 IP 403(공개 API 폐쇄, contact 요구)
#   adsb.lol /v2/mil → 200 이지만 항상 total 0(피드 고갈)
#   adsb.fi         → 가정용 IP 정상 / Cloudflare Workers 이그레스는 403
# 그래서 살아있는 adsb.fi 를 집 IP 에서 받아 중계한다. CF /api/mil-aircraft 는 폴백으로 유지.
MIL_SOURCES = [
    ("adsb.fi", "https://opendata.adsb.fi/api/v2/mil"),
    ("adsb.lol", "https://api.adsb.lol/v2/mil"),
]
MIL_TTL = 8.0                   # 프론트 갱신주기(8초)와 동일 — 원천 호출을 늘리지 않는다
MIL_FILL = ["t", "desc", "r", "ownOp", "flight", "category", "gs", "track",
            "true_heading", "alt_baro", "lat", "lon", "squawk"]
_mil_cache = {"at": 0.0, "body": None}
_mil_lock = threading.Lock()


def _fetch_mil_one(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; world-info-map/1.0; +https://briefglobe.com)",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=8) as r:
        data = json.loads(r.read().decode("utf-8", "replace"))
    return data.get("ac") or []


def _build_mil():
    """관측망별로 받아 hex 기준 병합. 한 곳이 죽어도 나머지로 계속(부분 결과 허용)."""
    by_hex, sources, diag = {}, {}, {}
    for name, url in MIL_SOURCES:
        try:
            lst = _fetch_mil_one(url)
            diag[name] = f"ok {len(lst)}"
        except Exception as e:
            lst, diag[name] = [], f"err {type(e).__name__}: {str(e)[:60]}"
        sources[name] = len(lst)
        for a in lst:
            hx = a.get("hex") if isinstance(a, dict) else None
            if not hx:
                continue
            cur = by_hex.get(hx)
            if cur is None:
                by_hex[hx] = dict(a, _srcs=[name])
            else:
                cur["_srcs"].append(name)
                for f in MIL_FILL:      # 빈 필드만 다른 관측망 값으로 보충
                    if cur.get(f) in (None, "") and a.get(f) not in (None, ""):
                        cur[f] = a[f]
    ac = list(by_hex.values())
    return {"ac": ac, "total": len(ac), "sources": sources, "diag": diag,
            "via": "mac", "now": int(time.time() * 1000)}


def _mil_body():
    with _mil_lock:                       # TTL 캐시 — 동시 요청이 원천을 두드리지 않게
        if _mil_cache["body"] and (time.monotonic() - _mil_cache["at"]) < MIL_TTL:
            return _mil_cache["body"]
        body = json.dumps(_build_mil()).encode()
        _mil_cache.update(at=time.monotonic(), body=body)
        return body


# ---------------- HTTP 서버(/quotes REST, http.server 스레드) ----------------
class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")

    def do_GET(self):
        global _last_access
        if self.path.startswith("/health"):
            self.send_response(200); self._cors(); self.send_header("Content-Type", "text/plain")
            self.end_headers(); self.wfile.write(b"ok"); return
        if self.path.startswith("/quotes"):
            _last_access = time.monotonic()
            with _lock:
                body = json.dumps({"updated": time.time(), "quotes": dict(CACHE)}).encode()
            self.send_response(200); self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers(); self.wfile.write(body); return
        if self.path.startswith("/mil-aircraft"):
            try:
                body = _mil_body()
            except Exception as e:      # 여기서 죽어도 시세 서버는 계속 살아있어야 한다
                body = json.dumps({"ac": [], "total": 0, "via": "mac",
                                   "error": str(e)[:120]}).encode()
            self.send_response(200); self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers(); self.wfile.write(body); return
        self.send_response(404); self._cors(); self.end_headers()

    def log_message(self, *a):
        pass


def http_thread():
    ThreadingHTTPServer(("127.0.0.1", HTTP_PORT), Handler).serve_forever()


async def main():
    global _last_access
    _last_access = time.monotonic()
    try:                                   # 초기 워밍업
        out = await asyncio.get_event_loop().run_in_executor(None, _poll_blocking)
        for cid, q in out.items():
            _update(cid, q["price"], q["chg"])
        print(f"[warmup] {len(CACHE)}종", flush=True)
    except Exception as e:
        print("[warmup]", e, flush=True)
    await asyncio.gather(poller(), kis_ws(), crypto_ws(), broadcaster())


if __name__ == "__main__":
    threading.Thread(target=http_thread, daemon=True).start()
    print(f"[quotes-ws] HTTP :{HTTP_PORT}  WS :{WS_PORT}", flush=True)
    asyncio.run(main())
