#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
 fetch_rates_ecos.py · 한국은행 ECOS 시장금리(일별) 수집 (시장 도메인)
------------------------------------------------------------
 한국의 대표 금리 지표를 ECOS OpenAPI 에서 받아 market-data.js 에 append 한다.
 (KIS 는 개별 채권 표준코드가 반기마다 교체돼 지표금리엔 부적합 → 공식 통계인 ECOS 사용)

  지표(그룹 "금리(한국)", 단위 %):
    한국은행 기준금리        722Y001 / 0101000
    콜금리(1일, 전체거래)     817Y002 / 010101000
    CD(91일)                817Y002 / 010502000
    국고채 3년               817Y002 / 010200000
    국고채 5년               817Y002 / 010200001
    국고채 10년              817Y002 / 010210000

 인증키는 로컬 '.ecos_secret' 또는 환경변수 ECOS_APIKEY 에서 읽는다
   (절대 커밋/배포 금지 — .gitignore 처리).  read-only 조회 전용.

 테스트:
   python3 fetch_rates_ecos.py --test          # 전 지표 최근값 출력
   python3 fetch_rates_ecos.py --append         # market-data.js 에 반영
   python3 fetch_rates_ecos.py --append --dry    # 미리보기(파일 미변경)
============================================================
"""
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
SECRET_FILE = HERE / ".ecos_secret"
MARKET_JS = HERE / "market-data.js"
BASE = "https://ecos.bok.or.kr/api"
GROUP = "금리(한국)"
WINDOW_DAYS = 375           # 약 1년치 (기존 시리즈 창과 맞춤)

# 지표 정의 — 카드 표시 순서(정책→단기→장기)
INDICATORS = [
    {"id": "ECOS-BASE",   "name": "한국은행 기준금리",  "stat": "722Y001", "item": "0101000",   "cycle": "D"},
    {"id": "ECOS-CALL",   "name": "콜금리 (익일물)",    "stat": "817Y002", "item": "010101000", "cycle": "D"},
    {"id": "ECOS-CD91",   "name": "CD 91일",          "stat": "817Y002", "item": "010502000", "cycle": "D"},
    {"id": "ECOS-KTB3Y",  "name": "국고채 3년",        "stat": "817Y002", "item": "010200000", "cycle": "D"},
    {"id": "ECOS-KTB5Y",  "name": "국고채 5년",        "stat": "817Y002", "item": "010200001", "cycle": "D"},
    {"id": "ECOS-KTB10Y", "name": "국고채 10년",       "stat": "817Y002", "item": "010210000", "cycle": "D"},
]


def _load_key():
    key = os.environ.get("ECOS_APIKEY", "")
    if not key and SECRET_FILE.exists():
        for line in SECRET_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("ECOS_APIKEY") and "=" in line:
                key = line.split("=", 1)[1].strip()
    if not key:
        raise RuntimeError(".ecos_secret 또는 환경변수 ECOS_APIKEY 가 필요합니다.")
    return key


KEY = None  # lazy


def _http(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "world-info/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def fetch_series(ind, start_yyyymmdd, end_yyyymmdd):
    """한 지표의 일별 시계열 → (dates[YYYY-MM-DD], closes[float])."""
    global KEY
    if KEY is None:
        KEY = _load_key()
    url = (f"{BASE}/StatisticSearch/{KEY}/json/kr/1/1000/"
           f"{ind['stat']}/{ind['cycle']}/{start_yyyymmdd}/{end_yyyymmdd}/{ind['item']}")
    j = _http(url)
    if "StatisticSearch" not in j:
        msg = (j.get("RESULT") or {}).get("MESSAGE", str(j)[:200])
        raise RuntimeError(f"ECOS 응답 이상({ind['id']}): {msg}")
    rows = j["StatisticSearch"].get("row", []) or []
    pairs = []
    for r in rows:
        t, v = r.get("TIME", ""), r.get("DATA_VALUE", "")
        if len(t) != 8 or v in (None, "", "-"):
            continue
        try:
            val = float(v)
        except ValueError:
            continue
        pairs.append((f"{t[:4]}-{t[4:6]}-{t[6:]}", val))
    pairs.sort(key=lambda p: p[0])          # 날짜 오름차순 보장
    return [p[0] for p in pairs], [p[1] for p in pairs]


def build_all():
    end = datetime.now()
    start = end - timedelta(days=WINDOW_DAYS)
    s8, e8 = start.strftime("%Y%m%d"), end.strftime("%Y%m%d")
    out, fail = [], []
    for ind in INDICATORS:
        try:
            dates, closes = fetch_series(ind, s8, e8)
            if not dates:
                fail.append((ind["id"], "빈 시계열"))
                continue
            out.append({"id": ind["id"], "name": ind["name"], "group": GROUP,
                        "unit": "%", "dates": dates, "closes": closes})
        except Exception as e:
            fail.append((ind["id"], str(e)[:80]))
    return out, fail


def append_to_market_data(dry=False):
    series, fail = build_all()
    if not series:
        print("[ECOS] 수집 실패 — market-data.js 미변경.", file=sys.stderr)
        for i, e in fail:
            print(f"    ✗ {i}: {e}", file=sys.stderr)
        return 1
    txt = MARKET_JS.read_text(encoding="utf-8")
    i0 = txt.index("[", txt.index("MARKET_DATA"))
    i1 = txt.rindex("]")
    arr = json.loads(txt[i0:i1 + 1])
    arr = [s for s in arr if not str(s.get("id", "")).startswith("ECOS-")]  # 기존 ECOS 제거(멱등)
    arr.extend(series)
    for s in series:
        print(f"    ✓ {s['id']:<12} {s['name']:<14} {s['closes'][-1]}% "
              f"({s['dates'][-1]}, {len(s['dates'])}일)")
    for i, e in fail:
        print(f"    ✗ {i}: {e}", file=sys.stderr)
    if dry:
        print("[ECOS] --dry: 파일 미변경.")
        return 0
    new_txt = txt[:i0] + json.dumps(arr, ensure_ascii=False) + txt[i1 + 1:]
    MARKET_JS.write_text(new_txt, encoding="utf-8")
    print(f"[ECOS] market-data.js 반영: {len(series)}개 금리 시리즈"
          + (f" (실패 {len(fail)})" if fail else ""))
    return 0


if __name__ == "__main__":
    argv = sys.argv[1:]
    if "--test" in argv:
        s, f = build_all()
        for x in s:
            print(f"  {x['id']:<12} {x['name']:<14} 최근 {x['closes'][-1]}% "
                  f"({x['dates'][-1]}, {len(x['dates'])}일, 처음 {x['dates'][0]})")
        for i, e in f:
            print(f"  ✗ {i}: {e}")
    elif "--append" in argv:
        sys.exit(append_to_market_data(dry=("--dry" in argv)))
    else:
        print(__doc__)
