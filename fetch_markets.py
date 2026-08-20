#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
 fetch_markets.py · 시장 데이터 수집 → market-data.js
------------------------------------------------------------
 Yahoo Finance 비공식 chart API에서 지수·기술·환율·금리·원자재의
 최근 1년 일봉(종가)을 수집. 원화 크로스 환율은 달러 페어에서 계산.
 표준 라이브러리만 사용. 키·토큰 불필요.

 사용:  python3 fetch_markets.py
 (auto_update.sh 가 자동 실행. 데이터는 일봉 = 하루 1개 확정값)
============================================================
"""
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "market-data.js"
API = "https://query1.finance.yahoo.com/v8/finance/chart/{sym}?range=3y&interval=1d"

# (야후 심볼, 표시명, 그룹, 단위)
SERIES = [
    # ---- 지수 ----
    ("^GSPC",   "S&P 500",           "지수", ""),
    ("^IXIC",   "나스닥 종합",        "지수", ""),
    ("^DJI",    "다우존스",           "지수", ""),
    ("^KS11",   "코스피",             "지수", ""),
    ("^KQ11",   "코스닥",             "지수", ""),
    ("^N225",   "닛케이 225",         "지수", ""),
    ("^HSI",    "항셍 (홍콩)",        "지수", ""),
    ("^GDAXI",  "독일 DAX",           "지수", ""),
    # ---- 기술 ----
    ("^SOX",    "필라델피아 반도체",   "기술", ""),
    ("^NDX",    "나스닥 100 (빅테크)", "기술", ""),
    # ---- 주식 - 미국 (매그니피센트 7, M7) ----
    ("AAPL",    "애플 (Apple)",           "주식 - 미국", "$"),
    ("MSFT",    "마이크로소프트 (Microsoft)", "주식 - 미국", "$"),
    ("GOOGL",   "알파벳·구글 (Alphabet)",  "주식 - 미국", "$"),
    ("AMZN",    "아마존 (Amazon)",         "주식 - 미국", "$"),
    ("NVDA",    "엔비디아 (Nvidia)",       "주식 - 미국", "$"),
    ("META",    "메타 (Meta)",             "주식 - 미국", "$"),
    ("TSLA",    "테슬라 (Tesla)",          "주식 - 미국", "$"),
    ("SPCX",    "스페이스X (SpaceX)",      "주식 - 미국", "$"),   # 2026.6 상장(Space Exploration Technologies)
    ("PLTR",    "팔란티어 (Palantir)",     "주식 - 미국", "$"),
    ("SMR",     "뉴스케일파워 (NuScale)",   "주식 - 미국", "$"),   # SMR 소형모듈원자로, NYSE
    ("LCID",    "루시드 그룹 (Lucid)",      "주식 - 미국", "$"),   # 전기차, NASDAQ
    ("PSNY",    "폴스타 (Polestar)",        "주식 - 미국", "$"),   # 전기차, NASDAQ
    ("BRK-A",   "버크셔 해서웨이 A (Berkshire A)", "주식 - 미국", "$"),  # NYSE (야후 하이픈 BRK-A)
    ("BRK-B",   "버크셔 해서웨이 B (Berkshire B)", "주식 - 미국", "$"),  # NYSE (야후 하이픈 BRK-B)
    ("XE",      "엑스에너지 (X-Energy)",     "주식 - 미국", "$"),   # SMR 원자력, 2026 상장(NASDAQ GS)
    ("OKLO",    "오클로 (Oklo)",             "주식 - 미국", "$"),   # SMR·차세대 원자력(Aurora 고속로), NYSE, 2024 AltC SPAC
    ("PFE",     "화이자 (Pfizer)",           "주식 - 미국", "$"),   # 제약, NYSE
    ("MRNA",    "모더나 (Moderna)",          "주식 - 미국", "$"),   # mRNA 백신·항암, NASDAQ
    ("BNTX",    "바이오엔테크 (BioNTech)",    "주식 - 미국", "$"),   # mRNA, 나스닥 ADR(독일 본사)
    # ---- 주식 - 한국 (원화 KRW · 야후 .KS) ----
    ("005930.KS", "삼성전자 (Samsung Elec)",       "주식 - 한국", "₩"),
    ("000660.KS", "SK하이닉스 (SK hynix)",         "주식 - 한국", "₩"),
    ("034020.KS", "두산에너빌리티 (Doosan Enerbility)", "주식 - 한국", "₩"),
    ("011070.KS", "LG이노텍 (LG Innotek)",         "주식 - 한국", "₩"),
    ("003550.KS", "LG (LG Corp.)",                 "주식 - 한국", "₩"),
    ("373220.KS", "LG에너지솔루션 (LG Energy Solution)", "주식 - 한국", "₩"),
    ("035420.KS", "NAVER (네이버)",                "주식 - 한국", "₩"),
    ("035720.KS", "카카오 (Kakao)",                "주식 - 한국", "₩"),
    ("000720.KS", "현대건설 (Hyundai E&C)",         "주식 - 한국", "₩"),
    ("034730.KS", "SK (SK Inc.)",                  "주식 - 한국", "₩"),
    ("096770.KS", "SK이노베이션 (SK Innovation)",   "주식 - 한국", "₩"),
    # ---- 환율(달러 기준) : USD 1달러당 각국 통화 ----
    ("KRW=X",   "달러/원",            "환율(달러)", "₩"),
    ("JPY=X",   "달러/엔",            "환율(달러)", "¥"),
    ("EURUSD=X","유로/달러",          "환율(달러)", "$"),
    ("GBPUSD=X","파운드/달러",        "환율(달러)", "$"),
    ("CHF=X",   "달러/스위스프랑",     "환율(달러)", "Fr"),
    ("CNY=X",   "달러/위안",          "환율(달러)", "元"),
    ("TWD=X",   "달러/대만달러",      "환율(달러)", "NT$"),
    ("INR=X",   "달러/인도루피",      "환율(달러)", "₹"),
    ("CZK=X",   "달러/체코코루나",     "환율(달러)", "Kč"),
    ("VND=X",   "달러/베트남동",      "환율(달러)", "₫"),
    # ---- 미국 채권 (국채 수익률 곡선; 정책금리는 FRED 키 등록 시 별도) ----
    ("^IRX",    "미국 3개월물",       "미국 채권", "%"),
    ("2YY=F",   "미국 2년물",         "미국 채권", "%"),
    ("^FVX",    "미국 5년물",         "미국 채권", "%"),
    ("^TNX",    "미국 10년물",        "미국 채권", "%"),
    ("^TYX",    "미국 30년물",        "미국 채권", "%"),
    # ---- 한국·일본 채권 (ETF 가격 프록시 — 수익률과 반대로 움직임에 유의)
    #      실제 국고채 수익률은 한국은행 ECOS API 키 등록 시 교체 가능
    ("114260.KS", "국고채 3년 ETF (KODEX)",  "채권(한·일)", "₩"),
    ("148070.KS", "국고채 10년 ETF (KOSEF)", "채권(한·일)", "₩"),
    ("2561.T",    "일본국채 ETF (iShares)",  "채권(한·일)", "¥"),
    # ---- 원자재 · 에너지 ----
    ("CL=F",    "WTI 원유",           "원자재·에너지", "$"),
    ("BZ=F",    "브렌트유",           "원자재·에너지", "$"),
    ("NG=F",    "천연가스",           "원자재·에너지", "$"),
    ("SRUUF",   "우라늄 (실물신탁)",   "원자재·에너지", "$"),
    # ---- 원자재 · 금속 ----
    ("GC=F",    "금",                 "원자재·금속", "$"),
    ("SI=F",    "은",                 "원자재·금속", "$"),
    ("HG=F",    "구리",               "원자재·금속", "$"),
    ("PL=F",    "백금",               "원자재·금속", "$"),
    ("PA=F",    "팔라듐",             "원자재·금속", "$"),
    ("TIO=F",   "철광석 (62% Fe)",    "원자재·금속", "$"),
    # ---- 원자재 · 식품 ----
    ("ZC=F",    "옥수수",             "원자재·식품", "$"),
    ("ZW=F",    "밀",                 "원자재·식품", "$"),
    ("ZS=F",    "대두",               "원자재·식품", "$"),
    ("SB=F",    "설탕",               "원자재·식품", "$"),
    ("KC=F",    "커피",               "원자재·식품", "$"),
    ("CC=F",    "코코아",             "원자재·식품", "$"),
    # ---- 원자재 · 의류 ----
    ("CT=F",    "면화",               "원자재·의류", "$"),
    # ---- 암호화폐 (달러, 야후) ----
    ("BTC-USD", "비트코인",           "암호화폐(달러)", "$"),
    ("ETH-USD", "이더리움",           "암호화폐(달러)", "$"),
    ("SOL-USD", "솔라나",             "암호화폐(달러)", "$"),
    ("XRP-USD", "리플",               "암호화폐(달러)", "$"),
    ("BNB-USD", "바이낸스코인",       "암호화폐(달러)", "$"),
    ("DOGE-USD","도지코인",           "암호화폐(달러)", "$"),
]

# 암호화폐 원화: 업비트 공개 API (무키, 실제 한국 거래소 시세 = 김치프리미엄 반영)
UPBIT_SERIES = [
    ("KRW-BTC",  "비트코인 (업비트)"),
    ("KRW-ETH",  "이더리움 (업비트)"),
    ("KRW-SOL",  "솔라나 (업비트)"),
    ("KRW-XRP",  "리플 (업비트)"),
    ("KRW-DOGE", "도지코인 (업비트)"),
]

# 미국 정책·단기자금 금리(DFF·SOFR·역레포)는 '거시·경기' 탭(fetch_macro.py)으로 일원화 →
#   시장페이지 중복 제거. 여기선 비움(한국 금리는 ECOS, 미국 국채 실시간은 야후 SERIES 유지).
FRED_SERIES = []

# 원화 크로스: (이름, 분자심볼, 분모심볼, 배수)
#   달러/원 ÷ 달러/X = X/원.  예) 엔/원 = KRW=X ÷ JPY=X (×100 → 100엔당 원)
KRW_CROSSES = [
    ("엔(100)/원",      "KRW=X", "JPY=X", 100),
    ("유로/원",         None,    "EURUSD=X", 1),   # KRW × EURUSD (달러표시 통화는 곱)
    ("파운드/원",       None,    "GBPUSD=X", 1),
    ("위안/원",         "KRW=X", "CNY=X", 1),
    ("스위스프랑/원",   "KRW=X", "CHF=X", 1),
    ("대만달러/원",     "KRW=X", "TWD=X", 1),
    ("동(100)/원",      "KRW=X", "VND=X", 100),
]


def _ts_to_points(ts, closes):
    dedup = {}
    for t, c in zip(ts or [], closes or []):
        if c is None:
            continue
        d = datetime.fromtimestamp(t, tz=timezone.utc).strftime("%Y-%m-%d")
        dedup[d] = round(float(c), 6)
    return dict(sorted(dedup.items()))


def fetch_one(sym, rng="3y"):
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/"
           f"{urllib.parse.quote(sym)}?range={rng}&interval=1d")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.loads(r.read().decode("utf-8"))
    res = data["chart"]["result"][0]
    return _ts_to_points(res.get("timestamp"),
                         res["indicators"]["quote"][0].get("close"))


def fetch_spark(symbols, rng="3y"):
    """야후 spark 배치: 여러 심볼을 1회 호출로. 반환 {sym: {date: close}}.
       rng: 시드는 '3y', 이미 누적된 심볼의 증분 갱신은 '1mo'(갭 방지 여유)."""
    q = urllib.parse.quote(",".join(symbols), safe=",=")
    url = (f"https://query1.finance.yahoo.com/v7/finance/spark"
           f"?symbols={q}&range={rng}&interval=1d")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=25) as r:
        data = json.loads(r.read().decode("utf-8"))
    results = (data.get("spark", {}).get("result")
               or data.get("result") or [])
    out = {}
    for item in results:
        try:
            resp = item["response"][0]
            out[item["symbol"]] = _ts_to_points(
                resp.get("timestamp"),
                resp["indicators"]["quote"][0].get("close"))
        except (KeyError, IndexError):
            continue
    return out


def _fred_api_key():
    """공식 FRED API 키: ~/.fred_api_key 파일에서 읽음 (웹루트 밖 = LAN에 노출 안 됨)."""
    p = Path.home() / ".fred_api_key"
    if p.exists():
        k = p.read_text(encoding="utf-8").strip()
        if k:
            return k
    return None


def fetch_fred_official(series_id, api_key, start):
    """공식 FRED API (안정적, 무료 키 필요)."""
    url = ("https://api.stlouisfed.org/fred/series/observations"
           f"?series_id={series_id}&api_key={api_key}&file_type=json"
           f"&observation_start={start}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.loads(r.read().decode("utf-8"))
    pts = {}
    for ob in data.get("observations", []):
        v = ob.get("value", ".")
        if v in (".", ""):
            continue
        try:
            pts[ob["date"]] = round(float(v), 4)
        except ValueError:
            continue
    return dict(sorted(pts.items()))


def fetch_fred(series_id):
    """FRED: 키 있으면 공식 API, 없으면 무키 CSV(불안정) 시도. 최근 1년치."""
    from datetime import timedelta
    start = (datetime.now(timezone.utc) - timedelta(days=370)).strftime("%Y-%m-%d")
    key = _fred_api_key()
    if key:
        return fetch_fred_official(series_id, key, start)
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    text = ""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            text = r.read().decode("utf-8", "replace")
    except Exception:
        # urllib가 막히면 curl 폴백 (맥 기본 탑재)
        import subprocess
        r = subprocess.run(["curl", "-s", "--max-time", "20", "-A", "Mozilla/5.0", url],
                           capture_output=True, text=True)
        text = r.stdout
    pts = {}
    for line in text.splitlines()[1:]:          # 헤더 제외
        parts = line.split(",")
        if len(parts) != 2 or parts[1] in (".", ""):
            continue
        try:
            if parts[0] >= start:                # 최근 1년치만
                pts[parts[0]] = round(float(parts[1]), 4)
        except ValueError:
            continue
    return dict(sorted(pts.items()))


def fetch_upbit(market, seeded=False, inc=10):
    """업비트 일봉. 반환 {date: 종가(원)}.
       seeded=True(이미 누적)면 최근 inc일만(증분, 갭 여유 포함), 아니면 ~1년 시드."""
    base = "https://api.upbit.com/v1/candles/days"
    pts = {}
    to = ""
    for count in ((max(10, inc),) if seeded else (200, 170)):
        url = f"{base}?market={market}&count={count}" + (f"&to={to}" if to else "")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0",
                                                   "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=15) as r:
            data = json.loads(r.read().decode("utf-8"))
        if not data:
            break
        for c in data:
            d = c["candle_date_time_utc"][:10]
            pts[d] = round(float(c["trade_price"]), 2)
        to = data[-1]["candle_date_time_utc"] + "Z"   # 다음 페이지 기준점
        time.sleep(0.25)
    return dict(sorted(pts.items()))


# ---- #8 가격 이력 누적: 기존 market-data.js 를 읽어 새 데이터와 합집합 병합 ----
#   · 다운로드는 3년(range=3y)으로 시드하고, 이후엔 기존 이력과 합쳐 절대 줄지 않게 한다.
#   · KIS 로 매 시각 최근값이 append 되는 주식(주식-미국/한국)은 충분히 시드되면
#     Yahoo 재다운로드를 생략한다(요청 절감) — 최신값은 fetch_markets_kis.py --enrich 가 채움.
# (구) 그룹 기준 판정 — 지금은 _kis_can_serve() 로 심볼 단위 판정한다.
#   지수·환율도 KIS 일봉이 있어 그룹만으로는 구분이 안 되기 때문.
KIS_SEED_MIN = 600     # 이 이상 쌓이면 시드 완료로 보고 Yahoo 재다운 스킵(≈2.5년 영업일)


def _kis_can_serve(sym):
    """KIS 가 이 심볼의 **일봉 이력**을 줄 수 있나.

    주식(한국 전 종목·미국 US_EXCD 등재분) + 지수(국내/해외) + 환율.
    이 목록에 들면 Yahoo 를 더 받지 않고 KIS append 만으로 이어간다
    (Yahoo 3년 시드는 이미 확보돼 있으므로 재다운로드가 낭비다).
    두 목록이 어긋나면 조용히 시세가 멈추므로 coverage_check 가 드리프트를 감시한다.
    """
    if sym.endswith(".KS"):
        return True
    try:
        from fetch_markets_kis import FX_USD, IDX_KR, IDX_OV, US_EXCD
    except ImportError:
        return False
    return sym in US_EXCD or sym in IDX_KR or sym in IDX_OV or sym in FX_USD


# KIS 로 이어가는 시리즈가 이 일수 이상 뒤처지면 KIS 쪽이 고장난 것 → 그 회차만 Yahoo 로 메운다.
#   '더 이상 Yahoo 를 받지 않는다'는 원칙의 예외는 이것 하나다. 이 안전망이 없으면
#   KIS 가 조용히 멈출 때 차트가 영구 정지한다(실제로 두 번 겪었다: MRNA 3주·지수 3주).
KIS_STALE_FALLBACK_DAYS = 5


def load_existing_history():
    """기존 market-data.js → {id: {date: close}}. 없거나 파싱 실패면 {}."""
    p = HERE / "market-data.js"
    if not p.exists():
        return {}
    try:
        t = p.read_text(encoding="utf-8")
        i0 = t.index("[", t.index("MARKET_DATA"))
        i1 = t.rindex("]")
        arr = json.loads(t[i0:i1 + 1])
        return {e["id"]: dict(zip(e.get("dates", []), e.get("closes", [])))
                for e in arr if e.get("dates") and e.get("closes")}
    except Exception as ex:
        print(f"  · 기존 이력 로드 실패({ex}) — 신규 시드로 진행")
        return {}


def merge_hist(old, new):
    """{date:close} 두 개 합집합(new 우선) → (dates[], closes[]) 날짜 오름차순."""
    m = dict(old or {})
    m.update(new or {})
    ks = sorted(m.keys())
    return ks, [m[k] for k in ks]


def main():
    raw = {}          # sym -> {date: close}
    out = []
    ok = fail = 0
    existing = load_existing_history()   # #8 누적 기반
    def seeded_kis(sym, group):
        # ⚠️ 'KIS 가 이어받는다'는 전제는 **KIS 가 실제로 그 심볼을 조회할 수 있을 때만** 성립한다.
        #   예전엔 이력 길이만 보고 Yahoo 를 건너뛰어서, US_EXCD 에 없는 종목(PFE·MRNA·BNTX)이
        #   Yahoo 도 KIS 도 안 받는 사각지대에 빠져 시드 시점(2026-07-29)에 영구 정지했다.
        #   그 사이 모더나는 +161% 급등했는데 화면엔 3주 전 값이 떠 있었다.
        base = existing.get(sym, {})
        if len(base) < KIS_SEED_MIN or not _kis_can_serve(sym):
            return False
        # 안전망: KIS 가 며칠째 못 채우고 있으면 이번 회차는 Yahoo 로 갭을 메운다.
        y, m, d = map(int, max(base).split("-"))
        behind = (datetime.now(timezone.utc).date() - datetime(y, m, d).date()).days
        if behind > KIS_STALE_FALLBACK_DAYS:
            print(f"  ⚠ {sym}: KIS 이력이 {behind}일 뒤처짐 → 이번 회차만 Yahoo 로 보강")
            return False
        return True

    # ---- FRED 정책·단기 금리 (공식 API 키 있을 때만 — 무키는 차단이 잦아 생략) ----
    fred_list = FRED_SERIES if _fred_api_key() else []
    if not fred_list:
        print("  · FRED 건너뜀 (~/.fred_api_key 없음 — 키 등록 시 기준금리·SOFR·역레포 추가)")
    for fid, name in fred_list:
        try:
            pts = fetch_fred(fid)
            if len(pts) < 10:
                raise RuntimeError(f"포인트 부족({len(pts)})")
            out.append({"id": "FRED-" + fid, "name": name, "group": "정책금리(미국)", "unit": "%",
                        "dates": list(pts.keys()), "closes": list(pts.values())})
            ok += 1
            last_d = list(pts)[-1]
            print(f"  ✓ [FRED] {name}: {len(pts)}일 (최근 {last_d} = {pts[last_d]}%)")
        except Exception as e:
            fail += 1
            print(f"  ⚠ [FRED] {name}({fid}) 실패: {e}")
        time.sleep(0.4)
    # ---- 야후: spark 배치로 16심볼씩 한 번에 (46회→3회, 빠르고 요청 수↓) ----
    CHUNK = 16
    fetched = {}
    # #8: 이미 시드된 KIS 주식은 Yahoo 재다운로드에서 제외(요청 절감·누적 유지)
    all_syms = [s[0] for s in SERIES if not seeded_kis(s[0], s[2])]
    n_skip = len(SERIES) - len(all_syms)
    if n_skip:
        print(f"  · KIS 누적 주식 {n_skip}종목 Yahoo 재다운 스킵(기존 이력 유지 + KIS append)")
    # 비주식(Yahoo)도 3년치가 쌓였으면 증분만, 신규/부족분만 3년 시드 — 페이로드 대폭 절감.
    seeded_syms = [s for s in all_syms if len(existing.get(s, {})) >= KIS_SEED_MIN]
    fresh_syms = [s for s in all_syms if s not in set(seeded_syms)]
    # 증분 range 는 '마지막 데이터가 며칠 지났나'로 동적 결정 — 평소 5d(가벼움),
    #   파이프라인이 오래 멈춰 뒤처지면 자동으로 넓게 받아 갭(구멍)을 메운다.
    # ⚠️ '얼마나 뒤처졌나'는 **가장 오래된** 심볼로 재야 한다(min).
    #   예전엔 max 를 써서, KIS 로 매일 갱신되는 심볼 하나(114260.KS)가 배치 전체를
    #   '최신'으로 보이게 만들었다 → gap=-1 → 항상 5d → 나머지 51심볼이 3주간 정지.
    last_dates = [max(existing[s]) for s in seeded_syms if existing.get(s)]
    gap = 999
    if last_dates:
        y, m, d = map(int, min(last_dates).split("-"))
        gap = (datetime.now(timezone.utc).date() - datetime(y, m, d).date()).days
    inc_range = "5d" if gap <= 4 else ("1mo" if gap <= 25 else "3mo")
    print(f"  · Yahoo: 증분({inc_range}, 마지막+{gap}일) {len(seeded_syms)}심볼 · 시드(3y) {len(fresh_syms)}심볼")

    def _run_batches(syms, rng):
        for i in range(0, len(syms), CHUNK):
            chunk = syms[i:i + CHUNK]
            try:
                fetched.update(fetch_spark(chunk, rng))
            except Exception as e:
                print(f"  ⚠ 배치 실패({e}) → 개별 수집 폴백")
                for sym in chunk:                  # 폴백: 심볼별 chart API
                    try:
                        fetched[sym] = fetch_one(sym, rng)
                    except Exception:
                        pass
                    time.sleep(0.5)
            time.sleep(0.6)

    _run_batches(seeded_syms, inc_range)
    _run_batches(fresh_syms, "3y")

    for sym, name, group, unit in SERIES:
        if seeded_kis(sym, group):
            # 다운로드 없이 기존 이력 그대로 사용(최신값은 KIS enrich 가 append)
            base = existing.get(sym, {})
            ds, cs = sorted(base), [base[d] for d in sorted(base)]
            raw[sym] = base
            out.append({"id": sym, "name": name, "group": group, "unit": unit,
                        "dates": ds, "closes": cs, "src": "누적(KIS)"})
            ok += 1
            continue
        pts = fetched.get(sym) or {}
        base = existing.get(sym, {})
        # ⚠️ '10점 미만 = 수집 실패' 는 3년 시드에만 맞는 기준이다.
        #   증분(5d)은 정상이어도 4~6점뿐이라 이 조건에 걸려 **매번 통째로 폐기**됐다.
        #   이미 이력이 있으면 1점만 늘어도 유효한 증분이다.
        min_pts = 1 if len(base) >= 10 else 10
        if len(pts) < min_pts:
            # 신규 수집 실패해도 기존 이력이 있으면 그것으로 유지(누락 방지)
            if len(base) >= 10:
                ds, cs = sorted(base), [base[d] for d in sorted(base)]
                raw[sym] = base
                out.append({"id": sym, "name": name, "group": group, "unit": unit,
                            "dates": ds, "closes": cs, "src": "누적(유지)"})
                ok += 1
            else:
                fail += 1
                print(f"  ⚠ {name}({sym}) 실패: 포인트 부족({len(pts)})")
            continue
        # #8 누적: 기존 이력 + 신규(3y) 합집합 → 절대 줄지 않음
        ds, cs = merge_hist(existing.get(sym, {}), pts)
        raw[sym] = dict(zip(ds, cs))
        out.append({"id": sym, "name": name, "group": group, "unit": unit,
                    "dates": ds, "closes": cs})
        ok += 1

    # ---- 원화 크로스 계산 (달러 페어에서 유도) ----
    krw = raw.get("KRW=X", {})
    for name, num_sym, den_sym, mul in KRW_CROSSES:
        try:
            if num_sym is None:
                # 달러표시 통화(EURUSD 등): X/원 = (달러/원) × (X/달러)
                den = raw.get(den_sym, {})
                common = sorted(set(krw) & set(den))
                vals = {d: round(krw[d] * den[d] * mul, 4) for d in common}
            else:
                den = raw.get(den_sym, {})
                common = sorted(set(krw) & set(den))
                vals = {d: round(krw[d] / den[d] * mul, 4) for d in common}
            if len(vals) < 10:
                raise RuntimeError("교집합 부족")
            out.append({"id": "KRWX-" + den_sym, "name": name, "group": "환율(원)",
                        "unit": "₩", "dates": list(vals.keys()),
                        "closes": list(vals.values())})
            last_d = list(vals)[-1]
            print(f"  ✓ [계산] {name}: 최근 {last_d} = {vals[last_d]}₩")
        except Exception as e:
            print(f"  ⚠ [계산] {name} 실패: {e}")

    # ---- 암호화폐 원화 (업비트 실제 시세) ----
    #   업비트 시드는 ~370일이라 KIS_SEED_MIN(600) 대신 전용 임계값(180)으로 증분 판정.
    for market, name in UPBIT_SERIES:
        try:
            prev = existing.get("UPBIT-" + market, {})
            up_seeded = len(prev) >= 180
            # 뒤처진 일수 + 여유(7일)만큼만 받기 — 평소 ~8일, 오래 멈추면 그만큼 넓게
            up_gap = 0
            if prev:
                yy, mm, dd = map(int, max(prev).split("-"))
                up_gap = (datetime.now(timezone.utc).date() - datetime(yy, mm, dd).date()).days
            pts = fetch_upbit(market, seeded=up_seeded, inc=up_gap + 7)
            if len(pts) < 10 and len(prev) < 10:
                raise RuntimeError(f"포인트 부족({len(pts)})")
            ds, cs = merge_hist(prev, pts)   # 기존 + 증분(60일) 합집합
            out.append({"id": "UPBIT-" + market, "name": name, "group": "암호화폐(원)",
                        "unit": "₩", "dates": ds, "closes": cs})
            ok += 1
            print(f"  ✓ [업비트] {name}: {len(ds)}일 누적 ({'증분' if up_seeded else '시드'} {len(pts)}건, 최근 {ds[-1]} = {cs[-1]:,.0f}원)")
        except Exception as e:
            fail += 1
            print(f"  ⚠ [업비트] {name}({market}) 실패: {e}")
        time.sleep(0.3)

    if not out:
        print("✖ 수집 실패 — 기존 market-data.js 유지")
        return

    # #8 최종 누적 패스 — 계산·외부(FRED·원화크로스·업비트) 포함 전 시리즈를
    #    기존 이력과 합쳐 절대 줄지 않게(주식은 위에서 이미 병합됨 → no-op).
    for e in out:
        cur = dict(zip(e["dates"], e["closes"]))
        ds, cs = merge_hist(existing.get(e["id"], {}), cur)
        e["dates"], e["closes"] = ds, cs

    # (주식 - 미국 그룹은 M7 + 스페이스X(SPCX) 모두 상장 종목이라 실시간 수집으로 충분.
    #  xAI 는 스페이스X에 병합되어 별도 표기하지 않는다.)

    # ---- Grok 분석용 압축 다이제스트 (작업 C 입력) ----
    digest = []
    for s in out:
        c = s["closes"]
        n = len(c)
        def chg(k):   # k일 전 대비 %
            return round((c[-1] - c[-1 - k]) / c[-1 - k] * 100, 2) if n > k else None
        digest.append({
            "name": s["name"], "group": s["group"], "unit": s["unit"],
            "last": c[-1], "last_date": s["dates"][-1],
            "d1_pct": chg(1), "d7_pct": chg(5), "d30_pct": chg(21), "y1_pct": chg(min(n - 1, 251)),
        })
    (HERE / "market-digest.json").write_text(
        json.dumps(digest, ensure_ascii=False, indent=1), encoding="utf-8")

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    OUTPUT.write_text(
        f"/* 자동 생성 · {stamp} · 출처: Yahoo Finance 일봉 3년 시드+누적 (원화 크로스는 계산값, KIS 주식은 KIS append)\n"
        f"   직접 수정 금지. fetch_markets.py 가 덮어씁니다. */\n"
        f"const MARKET_UPDATED = \"{stamp}\";\n"
        f"const MARKET_DATA = {json.dumps(out, ensure_ascii=False)};\n",
        encoding="utf-8",
    )
    print(f"✔ market-data.js 생성: {len(out)}개 시리즈 (수집 {ok}, 실패 {fail})")


if __name__ == "__main__":
    main()
