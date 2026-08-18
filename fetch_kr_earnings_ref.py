#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
 fetch_kr_earnings_ref.py · 한국 종목 분기 실적 '공시 원본' 대조표
------------------------------------------------------------
 market_guard.py 의 ⑤ 대조검증이 쓰는 정답지를 만든다.
 AI 가 조사한 실적값을 상식(마진 범위)으로 판정하면 정상 데이터까지 지운다 —
 실제로 SK하이닉스 2026Q2 영업이익률은 76%(공시)다. 그래서 원문과 직접 맞춘다.

 출처: 네이버 금융 종목 분기재무 API(전자공시 DART 기반 집계).
   https://m.stock.naver.com/api/stock/{code}/finance/quarter
 단위: 억원 → 조원 환산. 단일 분기값(누적 아님).

 산출: kr-earnings-ref.json
   {"updated": ISO8601,
    "data": {"005930.KS": {"202606": {"매출액":173.86,"영업이익":85.05,"당기순이익":...}}}}

 실패해도 파이프라인을 죽이지 않는다 — 기존 캐시를 남기고 종료(부분 결과 허용).
============================================================
"""
import json
import re
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
MARKET_DATA = HERE / "market-data.js"
OUT = HERE / "kr-earnings-ref.json"

API = "https://m.stock.naver.com/api/stock/{code}/finance/quarter"
UA = "Mozilla/5.0 (compatible; world-info-map/1.0; +https://briefglobe.com)"
WANT = ("매출액", "영업이익", "당기순이익")
TIMEOUT = 20


def kr_tickers():
    """market-data.js '주식 - 한국' 그룹 전체(하드코딩 금지 — 종목 추가 시 자동 포함)."""
    s = MARKET_DATA.read_text(encoding="utf-8")
    return re.findall(r'\{"id": "(\d{6}\.KS)", "name": "[^"]+", "group": "주식 - 한국"', s)


def fetch_one(code):
    req = urllib.request.Request(API.format(code=code),
                                 headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        doc = json.load(r)
    out = {}
    for row in (doc.get("financeInfo") or {}).get("rowList") or []:
        title = row.get("title")
        if title not in WANT:
            continue
        for col, cell in (row.get("columns") or {}).items():
            if not re.fullmatch(r"\d{6}", col or ""):
                continue                      # '연간' 등 분기 아닌 열 제외
            raw = (cell or {}).get("value")
            try:
                val = float(str(raw).replace(",", "")) / 10000.0   # 억원 → 조원
            except (TypeError, ValueError):
                continue
            out.setdefault(col, {})[title] = round(val, 4)
    return out


def main():
    try:
        tickers = kr_tickers()
    except OSError as e:
        print(f"  ⚠ market-data.js 읽기 실패({e}) — 대조표 갱신 건너뜀")
        return 0
    data, errors = {}, []
    for tk in tickers:
        code = tk.split(".")[0]
        try:
            q = fetch_one(code)
            if q:
                data[tk] = q
            else:
                errors.append(f"{tk}: 빈 응답")
        except (urllib.error.URLError, ValueError, TimeoutError) as e:
            errors.append(f"{tk}: {type(e).__name__}")
        time.sleep(0.3)                      # 예의상 간격

    if not data:                             # 전부 실패 = 기존 캐시 보존(덮어쓰지 않음)
        print(f"  ⚠ 공시 대조표 수집 실패({'; '.join(errors[:3])}) — 기존 캐시 유지")
        return 0

    OUT.write_text(json.dumps({
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "네이버 금융 분기재무(DART 기반) · market_guard 대조검증 전용",
        "errors": errors,
        "data": data,
    }, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    quarters = sum(len(v) for v in data.values())
    print(f"✔ 공시 대조표: {len(data)}종목 · {quarters}분기 → {OUT.name}"
          + (f" (실패 {len(errors)})" if errors else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
