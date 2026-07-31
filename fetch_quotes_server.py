#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
 fetch_quotes_server.py · Mac 로컬 실시간 시세 서버 (하이브리드 A의 Mac 쪽)
------------------------------------------------------------
 Mac은 KIS 유량제한을 안 받으므로(로컬 IP) 25종목을 병렬로 ~1-2초에 받아 캐시.
 백그라운드 스레드가 장중 REFRESH_SEC 마다 갱신 → HTTP 요청엔 캐시를 즉시 반환.
 cloudflared quick tunnel로 노출해 프런트가 폴링(실패 시 CF /api/quotes 폴백).

  · 조회(quotations) 전용 — 주문/거래 없음(read-only)
  · CORS 허용(world-info.pages.dev 및 로컬)
  · 127.0.0.1 바인딩 — 외부 노출은 cloudflared 터널만 담당

 실행:  python3 fetch_quotes_server.py            # 포트 8787
        curl http://127.0.0.1:8787/quotes         # 확인
============================================================
"""
import json
import sys
import threading
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import fetch_markets_kis as kis

PORT = 8787
REFRESH_SEC = 3          # 장중·조회 중일 때 갱신 주기(Mac→KIS)
IDLE_GRACE = 30          # 마지막 조회로부터 이 시간 내에만 빠르게 갱신(아무도 안 보면 KIS 호출 안 함)
ALLOW_ORIGIN = "*"       # 프런트(world-info.pages.dev)에서 fetch 허용

# 대상 25종목 (KIS 국내 UN통합 + 미국 last)
KR = ["005930", "000660", "034020", "011070", "003550", "373220",
      "035420", "035720", "000720", "034730", "096770"]
KR_ID = {c: c + ".KS" for c in KR}
US = [("AAPL", "AAPL"), ("MSFT", "MSFT"), ("GOOGL", "GOOGL"), ("AMZN", "AMZN"),
      ("NVDA", "NVDA"), ("META", "META"), ("TSLA", "TSLA"), ("PLTR", "PLTR"),
      ("LCID", "LCID"), ("PSNY", "PSNY"), ("SMR", "SMR"), ("OKLO", "OKLO"),
      ("BRK-A", "BRK/A"), ("BRK-B", "BRK/B"),
      ("SPCX", "SPCX"), ("XE", "XE")]            # (seriesId, KIS심볼) — SPCX·XE 나스닥 상장

# 암호화폐 — 24시간 실시간(무료·키 불필요). KIS와 무관해 한도 영향 없음.
CRYPTO_USD = {"BTC-USD": "BTCUSDT", "ETH-USD": "ETHUSDT", "SOL-USD": "SOLUSDT",
              "XRP-USD": "XRPUSDT", "BNB-USD": "BNBUSDT", "DOGE-USD": "DOGEUSDT"}   # Binance
CRYPTO_KRW = {"UPBIT-KRW-BTC": "KRW-BTC", "UPBIT-KRW-ETH": "KRW-ETH", "UPBIT-KRW-SOL": "KRW-SOL",
              "UPBIT-KRW-XRP": "KRW-XRP", "UPBIT-KRW-DOGE": "KRW-DOGE"}             # Upbit

# 지수 — KIS. 국내(업종 U): 코스피·코스닥. 해외(N): S&P·나스닥종합·나스닥100·필반·다우.
#   닛케이·항셍·DAX는 KIS 해외지수 코드가 없어 제외(시간당 야후 유지).
IDX_KR = {"^KS11": "0001", "^KQ11": "1001"}
IDX_OV = {"^GSPC": "SPX", "^IXIC": "COMP", "^NDX": "NDX", "^SOX": "SOX", "^DJI": ".DJI"}

# 환율(달러) — KIS FX@<통화>(div X). 값이 우리 시리즈와 직접 일치.
#   INR 제외: KIS FX@INR 는 인도루피 아닌 인도네시아 루피아(IDR). (INR=X 는 시간당 야후 유지)
FX_USD = {"KRW=X": "FX@KRW", "JPY=X": "FX@JPY", "EURUSD=X": "FX@EUR", "GBPUSD=X": "FX@GBP",
          "CHF=X": "FX@CHF", "CNY=X": "FX@CNY", "TWD=X": "FX@TWD", "CZK=X": "FX@CZK", "VND=X": "FX@VND"}

_cache = {"updated": None, "quotes": {}, "_fresh": 0}
_lock = threading.Lock()
_last_access = 0.0        # 마지막 /quotes 조회 시각(단조시계) — 보는 사람 있을 때만 빠르게 갱신


def _kst_now():
    return datetime.now(timezone.utc) + timedelta(hours=9)


def stock_market_open():
    """주식 조회 시간대 — KST 근사(한국 NXT 08~20 월~금, 미국 저녁~새벽). 크립토는 무관(24h)."""
    n = _kst_now()
    d, h = n.weekday(), n.hour + n.minute / 60   # weekday(): 월0..일6
    kr = d <= 4 and 8 <= h < 20
    us_eve = d <= 4 and h >= 18
    us_morn = 1 <= d <= 5 and h < 7
    return kr or us_eve or us_morn


def _get_json(url, timeout=8):
    req = urllib.request.Request(url, headers={"User-Agent": "world-info/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def fetch_crypto():
    """암호화폐(달러=Binance, 원=Upbit) 실시간. {id:{price,chg(24h%)}}. 24시간."""
    out = {}
    try:
        arr = _get_json("https://api.binance.com/api/v3/ticker/24hr?symbols="
                        + urllib.parse.quote(json.dumps(list(CRYPTO_USD.values()), separators=(",", ":"))))
        inv = {v: k for k, v in CRYPTO_USD.items()}
        for d in arr:
            sid = inv.get(d.get("symbol"))
            if sid:
                out[sid] = {"price": float(d["lastPrice"]), "chg": float(d["priceChangePercent"])}
    except Exception as e:
        sys.stderr.write(f"[crypto] binance 실패: {e}\n")
    try:
        arr = _get_json("https://api.upbit.com/v1/ticker?markets=" + ",".join(CRYPTO_KRW.values()))
        inv = {v: k for k, v in CRYPTO_KRW.items()}
        for d in arr:
            sid = inv.get(d.get("market"))
            if sid:
                out[sid] = {"price": float(d["trade_price"]), "chg": float(d["signed_change_rate"]) * 100}
    except Exception as e:
        sys.stderr.write(f"[crypto] upbit 실패: {e}\n")
    return out


def _one_kr(code, token):
    p = kis.kr_stock_price(code, token)
    return KR_ID[code], {"price": p["price"], "chg": p["change_pct"]}


def _one_us(sid, symb, token):
    excd = kis.US_EXCD[sid]
    p = kis.us_stock_price(excd, symb, token)
    return sid, {"price": p["price"], "chg": p["change_pct"]}


def _one_kr_idx(sid, code, token):
    r = kis._get("/uapi/domestic-stock/v1/quotations/inquire-index-price", "FHPUP02100000",
                 {"FID_COND_MRKT_DIV_CODE": "U", "FID_INPUT_ISCD": code}, token)
    o = r.get("output", {}) or {}
    return sid, {"price": float(o.get("bstp_nmix_prpr") or 0), "chg": float(o.get("bstp_nmix_prdy_ctrt") or 0)}


def _one_ov_idx(sid, code, token):
    r = kis._get("/uapi/overseas-price/v1/quotations/inquire-time-indexchartprice", "FHKST03030200",
                 {"FID_COND_MRKT_DIV_CODE": "N", "FID_INPUT_ISCD": code,
                  "FID_HOUR_CLS_CODE": "0", "FID_PW_DATA_INCU_YN": "N"}, token)
    o = r.get("output1", {}) or {}
    return sid, {"price": float(o.get("ovrs_nmix_prpr") or 0), "chg": float(o.get("prdy_ctrt") or 0)}


def _one_fx(sid, code, token):
    r = kis._get("/uapi/overseas-price/v1/quotations/inquire-time-indexchartprice", "FHKST03030200",
                 {"FID_COND_MRKT_DIV_CODE": "X", "FID_INPUT_ISCD": code,
                  "FID_HOUR_CLS_CODE": "0", "FID_PW_DATA_INCU_YN": "N"}, token)
    o = r.get("output1", {}) or {}
    return sid, {"price": float(o.get("ovrs_nmix_prpr") or 0), "chg": float(o.get("prdy_ctrt") or 0)}


def _add_krw_crosses(out):
    """환율(원) 크로스 — 라이브 USD쌍에서 계산. chg는 성분 근사(1차)."""
    def g(sid):
        v = out.get(sid)
        return (v["price"], v["chg"]) if v and v.get("price") else (None, 0.0)
    krw, kc = g("KRW=X")
    if not krw:
        return
    jpy, jc = g("JPY=X"); eur, ec = g("EURUSD=X"); gbp, gc = g("GBPUSD=X")
    cny, cc = g("CNY=X"); chf, fc = g("CHF=X"); twd, tc = g("TWD=X"); vnd, vc = g("VND=X")
    rows = []
    if jpy: rows.append(("KRWX-JPY=X", krw / jpy * 100, kc - jc))       # 엔(100)/원
    if eur: rows.append(("KRWX-EURUSD=X", krw * eur, kc + ec))          # 유로/원
    if gbp: rows.append(("KRWX-GBPUSD=X", krw * gbp, kc + gc))          # 파운드/원
    if cny: rows.append(("KRWX-CNY=X", krw / cny, kc - cc))             # 위안/원
    if chf: rows.append(("KRWX-CHF=X", krw / chf, kc - fc))             # 스위스프랑/원
    if twd: rows.append(("KRWX-TWD=X", krw / twd, kc - tc))             # 대만달러/원
    if vnd: rows.append(("KRWX-VND=X", krw / vnd * 100, kc - vc))       # 동(100)/원
    for sid, px, ch in rows:
        out[sid] = {"price": round(px, 4), "chg": round(ch, 2)}


def _fetch_stocks():
    token = kis.get_token()
    out = {}
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = [ex.submit(_one_kr, c, token) for c in KR] + \
               [ex.submit(_one_us, sid, symb, token) for sid, symb in US] + \
               [ex.submit(_one_kr_idx, sid, cd, token) for sid, cd in IDX_KR.items()] + \
               [ex.submit(_one_ov_idx, sid, cd, token) for sid, cd in IDX_OV.items()] + \
               [ex.submit(_one_fx, sid, cd, token) for sid, cd in FX_USD.items()]
        for f in futs:
            try:
                sid, q = f.result()
                if q["price"]:
                    out[sid] = q
            except Exception:
                pass
    _add_krw_crosses(out)   # 환율(원) 크로스 계산(라이브 USD쌍 기반)
    return out


def refresh_once():
    """주식(장중에만) + 크립토(24시간) 조회 → 캐시에 병합. 성공분만 갱신."""
    out = {}
    if stock_market_open():
        try:
            out.update(_fetch_stocks())
        except Exception as e:
            sys.stderr.write(f"[stocks] {e}\n")
    out.update(fetch_crypto())              # 24시간 실시간
    if out:
        with _lock:
            merged = dict(_cache["quotes"]); merged.update(out)   # 실패분은 직전값 유지
            _cache["quotes"] = merged
            _cache["updated"] = _kst_now().isoformat()
            _cache["_fresh"] = len(out)
    return len(out)


def refresher():
    while True:
        try:
            viewing = (time.monotonic() - _last_access) < IDLE_GRACE
            if viewing:
                n = refresh_once()               # 주식(장중)+크립토(24h)
                sys.stderr.write(f"[quotes] {n}개 갱신 {_kst_now().strftime('%H:%M:%S')}\n")
                time.sleep(REFRESH_SEC)          # 조회 중 → 3초마다
            else:
                time.sleep(3)                    # 무조회 → 호출 안 함, 3초마다 상태만 확인
        except Exception as e:
            sys.stderr.write(f"[quotes] refresher 오류: {e}\n")
            time.sleep(10)


class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", ALLOW_ORIGIN)
        self.send_header("Cache-Control", "no-store")

    def do_GET(self):
        if self.path.startswith("/health"):
            self.send_response(200); self._cors()
            self.send_header("Content-Type", "text/plain"); self.end_headers()
            self.wfile.write(b"ok"); return
        if self.path.startswith("/quotes"):
            global _last_access
            _last_access = time.monotonic()      # 조회 있음 → refresher가 빠르게 갱신 재개
            with _lock:
                body = json.dumps(_cache, ensure_ascii=False).encode("utf-8")
            self.send_response(200); self._cors()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers(); self.wfile.write(body); return
        self.send_response(404); self._cors(); self.end_headers()

    def log_message(self, *a):
        pass   # 접근 로그 억제


def main():
    global _last_access
    _last_access = time.monotonic()      # 시작 직후 워밍업 창(첫 IDLE_GRACE 동안 활성)
    try:
        refresh_once()                    # 콜드 캐시 방지 — 시작 시 동기 1회 채움
        sys.stderr.write(f"[quotes] 초기 워밍업 {_cache['_fresh']}/25\n")
    except Exception as e:
        sys.stderr.write(f"[quotes] 초기 갱신 실패: {e}\n")
    threading.Thread(target=refresher, daemon=True).start()
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    sys.stderr.write(f"[quotes] 서버 시작 http://127.0.0.1:{PORT}/quotes\n")
    srv.serve_forever()


if __name__ == "__main__":
    main()
