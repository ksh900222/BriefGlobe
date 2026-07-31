#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
 fetch_markets_kis.py · 한국투자증권(KIS) OpenAPI 시세 수집 (시장 도메인)
------------------------------------------------------------
 야후 대신/병행으로 주식(한국·미국)·(추후 한국 국고채) 시세를 KIS 에서 받는다.
  - 인증: 앱키/앱시크릿 → 접근토큰(24h) 발급·캐시(.kis_token.json)
          (토큰 재발급 빈도 제한이 있어 캐시 필수)
  - 국내주식: 일봉(inquire-daily-itemchartprice) + 현재가(inquire-price)
  - 해외주식: 일봉(dailyprice) + 현재가(price) — 현재가엔 시간외(연장) 반영 가능
  - 한국 국고채 수익률: domestic_bond (2단계에서 추가 — 대표 만기 종목코드 지정)

 키는 로컬 '.kis_secret' 또는 환경변수에서 읽는다(절대 커밋/배포 금지 — .gitignore 처리).
   .kis_secret (2줄):
     KIS_APPKEY=발급받은앱키
     KIS_APPSECRET=발급받은앱시크릿
   (모의투자면 KIS_ENV=vts 추가)

 테스트(키 넣은 뒤):
   python3 fetch_markets_kis.py --token         # 토큰 발급 확인
   python3 fetch_markets_kis.py --kr 005930      # 삼성전자 일봉+현재가
   python3 fetch_markets_kis.py --us NAS AAPL    # 애플(나스닥)
   python3 fetch_markets_kis.py --selftest       # 대표 종목 몇 개 점검

 ⚠️ tr_id·엔드포인트는 KIS 공식 문서 기준이나, 실계정 테스트로 최종 확인 권장.
    (실전/모의는 일부 tr_id 가 다름 — 국내주식 시세계 tr_id 는 동일, 주문계는 다름)
============================================================
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
SECRET_FILE = HERE / ".kis_secret"
TOKEN_CACHE = HERE / ".kis_token.json"


# ------------------------------------------------------------
# 설정(키) 로드 — 로컬 파일 + 환경변수
# ------------------------------------------------------------
def _load_secret():
    cfg = {}
    if SECRET_FILE.exists():
        for line in SECRET_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                cfg[k.strip()] = v.strip()
    for k in ("KIS_APPKEY", "KIS_APPSECRET", "KIS_ENV"):   # 환경변수 우선
        if os.environ.get(k):
            cfg[k] = os.environ[k]
    return cfg


CFG = _load_secret()
APPKEY = CFG.get("KIS_APPKEY", "")
APPSECRET = CFG.get("KIS_APPSECRET", "")
IS_VTS = CFG.get("KIS_ENV", "").lower() in ("vts", "mock", "모의")
BASE = ("https://openapivts.koreainvestment.com:29443" if IS_VTS
        else "https://openapi.koreainvestment.com:9443")


# ------------------------------------------------------------
# HTTP
# ------------------------------------------------------------
class _RateLimit(Exception):
    """KIS 유량제한(EGW00201, '초당 거래건수 초과') — 잠시 후 재시도 가능."""


def _http(url, method="GET", headers=None, body=None, timeout=15):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")
        if "EGW00201" in detail:              # 유량제한 → 재시도 가능하게 별도 예외
            raise _RateLimit(detail)
        raise RuntimeError(f"HTTP {e.code} {url.split('?')[0]}: {detail[:300]}")


# ------------------------------------------------------------
# 토큰 (24h, 캐시)
# ------------------------------------------------------------
def get_token(force=False):
    if not (APPKEY and APPSECRET):
        raise SystemExit("⚠ 키 없음 — '.kis_secret' 에 KIS_APPKEY / KIS_APPSECRET 를 넣으세요 "
                         "(.kis_secret.example 참고).")
    env = "vts" if IS_VTS else "real"
    if not force and TOKEN_CACHE.exists():
        try:
            c = json.loads(TOKEN_CACHE.read_text())
            if c.get("env") == env and c.get("expire", 0) - time.time() > 600:
                return c["access_token"]
        except Exception:
            pass
    res = _http(BASE + "/oauth2/tokenP", "POST",
                {"content-type": "application/json"},
                {"grant_type": "client_credentials", "appkey": APPKEY, "appsecret": APPSECRET})
    tok = res["access_token"]
    exp = time.time() + int(res.get("expires_in", 86400))
    TOKEN_CACHE.write_text(json.dumps({"access_token": tok, "expire": exp, "env": env}))
    return tok


def _headers(tr_id, token):
    return {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {token}",
        "appkey": APPKEY, "appsecret": APPSECRET,
        "tr_id": tr_id, "custtype": "P",
    }


def _get(path, tr_id, params, token, tries=4):
    """유량제한(초당 거래건수)에 걸리면 잠시 후 재시도. 기본 텀 0.25s(슬라이딩 윈도우 여유)."""
    q = urllib.parse.urlencode(params)
    for i in range(tries):
        time.sleep(0.25 if i == 0 else 1.0)   # 첫 호출 텀 + 재시도 시 더 길게
        try:
            return _http(BASE + path + "?" + q, "GET", _headers(tr_id, token))
        except _RateLimit:
            if i == tries - 1:
                raise
    return {}


# ------------------------------------------------------------
# 국내주식
# ------------------------------------------------------------
def kr_stock_daily(code, token, days=100):
    """국내주식 일봉 {date: close}. code=6자리(예 '005930'). 호출당 최대 ~100영업일."""
    end = datetime.now().strftime("%Y%m%d")
    start = (datetime.now() - timedelta(days=days * 2)).strftime("%Y%m%d")
    res = _get("/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice",
               "FHKST03010100",
               {"FID_COND_MRKT_DIV_CODE": "J", "FID_INPUT_ISCD": code,
                "FID_INPUT_DATE_1": start, "FID_INPUT_DATE_2": end,
                "FID_PERIOD_DIV_CODE": "D", "FID_ORG_ADJ_PRC": "0"}, token)
    pts = {}
    for r in res.get("output2", []) or []:
        d, c = r.get("stck_bsop_date"), r.get("stck_clpr")
        if d and c and c not in ("", "0"):
            pts[f"{d[:4]}-{d[4:6]}-{d[6:8]}"] = float(c)
    return dict(sorted(pts.items()))


def kr_stock_price(code, token):
    """국내주식 현재가. {price, change_pct}.
    시장구분 UN(통합=KRX+NXT) → 정규시간엔 정규가, 장외엔 NXT 프리/애프터가를 자동 반영
    (넥스트레이드 프리 08:00~08:50 · 애프터 15:30~20:00). 미국 해외 last 와 동일 성격."""
    res = _get("/uapi/domestic-stock/v1/quotations/inquire-price", "FHKST01010100",
               {"FID_COND_MRKT_DIV_CODE": "UN", "FID_INPUT_ISCD": code}, token)
    o = res.get("output", {}) or {}
    return {"price": float(o.get("stck_prpr") or 0), "change_pct": float(o.get("prdy_ctrt") or 0)}


# ------------------------------------------------------------
# 해외주식 (미국)  EXCD: NAS(나스닥) NYS(뉴욕) AMS(아멕스)
# ------------------------------------------------------------
def us_stock_daily(excd, symb, token):
    """해외주식 일봉 {date: close}. 호출당 최대 ~100영업일."""
    res = _get("/uapi/overseas-price/v1/quotations/dailyprice", "HHDFS76240000",
               {"AUTH": "", "EXCD": excd, "SYMB": symb, "GUBN": "0", "BYMD": "", "MODP": "1"}, token)
    pts = {}
    for r in res.get("output2", []) or []:
        d, c = r.get("xymd"), r.get("clos")
        if d and c and c not in ("", "0"):
            pts[f"{d[:4]}-{d[4:6]}-{d[6:8]}"] = float(c)
    return dict(sorted(pts.items()))


def us_stock_price(excd, symb, token):
    """해외주식 현재가. {price, change_pct}. (시간외=프리/애프터는 실시간시세 이용신청 시 반영)"""
    res = _get("/uapi/overseas-price/v1/quotations/price", "HHDFS00000300",
               {"AUTH": "", "EXCD": excd, "SYMB": symb}, token)
    o = res.get("output", {}) or {}
    return {"price": float(o.get("last") or 0), "change_pct": float(o.get("rate") or 0)}


# ------------------------------------------------------------
# market-data.js 오버레이 (하이브리드) — 주식만 KIS로, 실패 시 야후값 유지(폴백)
# ------------------------------------------------------------
import re

US_EXCD = {   # 미국 티커 → KIS 거래소코드(NAS 나스닥·NYS 뉴욕). 없으면 KIS 스킵 → 야후 폴백.
    "AAPL": "NAS", "MSFT": "NAS", "GOOGL": "NAS", "AMZN": "NAS", "NVDA": "NAS",
    "META": "NAS", "TSLA": "NAS", "PLTR": "NAS", "LCID": "NAS", "PSNY": "NAS",
    "SMR": "NYS", "OKLO": "NYS", "BRK-A": "NYS", "BRK-B": "NYS",
    "SPCX": "NAS", "XE": "NAS",   # 스페이스X·엑스에너지 — 나스닥 상장(2026)
    # SPCX(스페이스X 비상장)·XE(엑스에너지) 등은 미매핑 → 야후 유지
}


def _kis_ref(series_id):
    """market-data 심볼 → ('kr', 6자리) 또는 ('us', 거래소코드). 주식 아니면 None(스킵)."""
    if series_id.endswith(".KS"):
        return ("kr", series_id[:-3])
    if series_id in US_EXCD:
        return ("us", US_EXCD[series_id])
    return None


# 지수·환율(KIS) — 시간당 enrich 에서도 kisNow 부여(장외에도 ● 표시). Mac 라이브 서버와 동일 코드.
IDX_KR = {"^KS11": "0001", "^KQ11": "1001"}
IDX_OV = {"^GSPC": "SPX", "^IXIC": "COMP", "^NDX": "NDX", "^SOX": "SOX", "^DJI": ".DJI"}
FX_USD = {"KRW=X": "FX@KRW", "JPY=X": "FX@JPY", "EURUSD=X": "FX@EUR", "GBPUSD=X": "FX@GBP",
          "CHF=X": "FX@CHF", "CNY=X": "FX@CNY", "TWD=X": "FX@TWD", "CZK=X": "FX@CZK", "VND=X": "FX@VND"}


def kr_index(code, token):
    r = _get("/uapi/domestic-stock/v1/quotations/inquire-index-price", "FHPUP02100000",
             {"FID_COND_MRKT_DIV_CODE": "U", "FID_INPUT_ISCD": code}, token)
    o = r.get("output", {}) or {}
    return float(o.get("bstp_nmix_prpr") or 0), float(o.get("bstp_nmix_prdy_ctrt") or 0)


def _ov_chart(code, div, token):
    r = _get("/uapi/overseas-price/v1/quotations/inquire-time-indexchartprice", "FHKST03030200",
             {"FID_COND_MRKT_DIV_CODE": div, "FID_INPUT_ISCD": code,
              "FID_HOUR_CLS_CODE": "0", "FID_PW_DATA_INCU_YN": "N"}, token)
    o = r.get("output1", {}) or {}
    return float(o.get("ovrs_nmix_prpr") or 0), float(o.get("prdy_ctrt") or 0)


def enrich_indices_fx(arr, token, ok, fail):
    """지수·환율·원화크로스에 kisNow/kisChg 부여."""
    byid = {s["id"]: s for s in arr}
    fxv = {}

    def setq(sid, price, chg):
        s = byid.get(sid)
        if s and price:
            s["kisNow"] = round(price, 4); s["kisChg"] = round(chg, 2); s["src"] = "kis"
            ok.append(sid)

    for sid, code in IDX_KR.items():
        try: setq(sid, *kr_index(code, token))
        except Exception as e: fail.append((sid, str(e)[:50]))
    for sid, code in IDX_OV.items():
        try: setq(sid, *_ov_chart(code, "N", token))
        except Exception as e: fail.append((sid, str(e)[:50]))
    for sid, code in FX_USD.items():
        try:
            p, c = _ov_chart(code, "X", token); fxv[sid] = (p, c); setq(sid, p, c)
        except Exception as e: fail.append((sid, str(e)[:50]))
    # 원화 크로스 (라이브 USD쌍에서 계산)
    krw = fxv.get("KRW=X")
    if krw and krw[0]:
        k, kc = krw
        for sid, num, mul in [("KRWX-JPY=X", "JPY=X", 100), ("KRWX-CNY=X", "CNY=X", 1),
                              ("KRWX-CHF=X", "CHF=X", 1), ("KRWX-TWD=X", "TWD=X", 1),
                              ("KRWX-VND=X", "VND=X", 100)]:
            v = fxv.get(num)
            if v and v[0]: setq(sid, k / v[0] * mul, kc - v[1])
        for sid, num in [("KRWX-EURUSD=X", "EURUSD=X"), ("KRWX-GBPUSD=X", "GBPUSD=X")]:
            v = fxv.get(num)
            if v and v[0]: setq(sid, k * v[0], kc + v[1])


def enrich_market_data(dry=False):
    """market-data.js(야후가 생성)에서 주식 시리즈를 KIS 값으로 보강.
       - 일봉: 야후 1년 + KIS 최근(정확) 병합(KIS 날짜는 KIS값 우선)
       - 현재가: kisNow/kisChg 필드 추가(장중 실시간)
       실패한 종목은 야후값 그대로(폴백). 나머지 그룹(환율·원자재·코인·지수)은 손대지 않음."""
    token = get_token()
    path = HERE / "market-data.js"
    txt = path.read_text(encoding="utf-8")
    i0 = txt.index("[", txt.index("MARKET_DATA"))
    i1 = txt.rindex("]")
    arr = json.loads(txt[i0:i1 + 1])

    ok, fail, skip = [], [], 0
    for s in arr:
        ref = _kis_ref(s.get("id", ""))
        if not ref:
            skip += 1
            continue
        kind, arg = ref
        try:
            if kind == "kr":
                daily = kr_stock_daily(arg, token)
                px = kr_stock_price(arg, token)
            else:
                symb = s["id"].replace("-", "/") if s["id"].startswith("BRK") else s["id"]  # 버크셔는 BRK/A 형식일 수 있음
                daily = us_stock_daily(arg, symb, token)
                px = us_stock_price(arg, symb, token)
            if not daily:
                raise RuntimeError("일봉 빈값")
            # 병합: 야후(1년) 위에 KIS 최근 덮기
            merged = dict(zip(s.get("dates", []), s.get("closes", [])))
            merged.update(daily)
            merged = dict(sorted(merged.items()))
            s["dates"] = list(merged.keys())
            s["closes"] = list(merged.values())
            if px.get("price"):
                s["kisNow"] = round(px["price"], 4)
                s["kisChg"] = round(px.get("change_pct", 0), 2)
            s["src"] = "kis"
            ok.append(s["id"])
        except Exception as e:
            fail.append((s["id"], str(e)[:60]))

    enrich_indices_fx(arr, token, ok, fail)     # 지수·환율·원화크로스 kisNow 부여

    print(f"KIS 보강: 성공 {len(ok)} · 실패(야후유지) {len(fail)} · 스킵(비주식) {skip}")
    if fail:
        for t, e in fail:
            print(f"   ⚠ {t}: {e}")
    if dry:
        print("(dry-run — 저장 안 함)")
        return 0
    new_txt = txt[:i0] + json.dumps(arr, ensure_ascii=False) + txt[i1 + 1:]
    path.write_text(new_txt, encoding="utf-8")
    print(f"✓ market-data.js 저장(주식 {len(ok)}종목 KIS 반영)")
    return 0


# ------------------------------------------------------------
# CLI (테스트)
# ------------------------------------------------------------
def _main(argv):
    if "--token" in argv:
        t = get_token()
        print("✓ 토큰 발급 OK:", t[:24] + "…", "| env:", "모의" if IS_VTS else "실전")
        return 0
    tok = get_token()
    if "--kr" in argv:
        code = argv[argv.index("--kr") + 1]
        daily = kr_stock_daily(code, tok)
        px = kr_stock_price(code, tok)
        last = list(daily.items())[-3:] if daily else []
        print(f"[국내 {code}] 현재가 {px['price']:.0f}원 ({px['change_pct']:+.2f}%) | 일봉 {len(daily)}일, 최근: {last}")
        return 0
    if "--us" in argv:
        i = argv.index("--us"); excd, symb = argv[i + 1], argv[i + 2]
        daily = us_stock_daily(excd, symb, tok)
        px = us_stock_price(excd, symb, tok)
        last = list(daily.items())[-3:] if daily else []
        print(f"[해외 {excd}:{symb}] 현재가 {px['price']:.2f} ({px['change_pct']:+.2f}%) | 일봉 {len(daily)}일, 최근: {last}")
        return 0
    if "--enrich" in argv:
        return enrich_market_data(dry="--dry" in argv)
    if "--selftest" in argv:
        print("== KIS 셀프테스트 ==")
        for code in ("005930", "000660"):
            try:
                d = kr_stock_daily(code, tok); p = kr_stock_price(code, tok)
                print(f"  국내 {code}: 일봉 {len(d)}일, 현재가 {p['price']:.0f}원 {p['change_pct']:+.2f}%")
            except Exception as e:
                print(f"  ✗ 국내 {code}: {e}")
        for excd, symb in (("NAS", "AAPL"), ("NAS", "NVDA")):
            try:
                d = us_stock_daily(excd, symb, tok); p = us_stock_price(excd, symb, tok)
                print(f"  해외 {excd}:{symb}: 일봉 {len(d)}일, 현재가 {p['price']:.2f} {p['change_pct']:+.2f}%")
            except Exception as e:
                print(f"  ✗ 해외 {excd}:{symb}: {e}")
        return 0
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
