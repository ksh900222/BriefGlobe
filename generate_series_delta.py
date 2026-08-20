#!/usr/bin/env python3
"""
econ-calendar.json의 실제값(actual)과 컨센서스(forecast)를 바탕으로
series-delta.json을 생성하고 earnings·macro 섹션을 채운다.

프로세스:
1. econ-calendar.json 읽기
2. Earnings 섹션: 실적 종목별로 period, revenue, eps, netIncome, opMargin, fcf, source 정리
3. Macro 섹션: 거시지표별로 releases에 period, cons, act, momCons, momAct, source 추가
4. series-delta.json 생성
"""

import json
from datetime import datetime
from collections import defaultdict

# 지수 실적 발표 컨센서스 매핑
earnings_consensus = {
    "MSFT": {"eps": 4.74, "revenue": 90.0},
    "META": {"eps": 6.18, "revenue": 60.8},
    "AMZN": {"eps": 5.75, "revenue": 200.61},
    "AAPL": {"eps": 2.02, "revenue": 109.42},
    "PLTR": {"eps": 0.41, "revenue": 1.935},
    "BNTX": {"revenue": 0.1056},
    "PFE": {"eps": 0.77, "revenue": 15.03},
    "SMR": {"eps": -0.13},
    "LCID": {"eps": -3.46, "revenue": 0.282},
    "ROKU": {"revenue": 1.11},
    "OKLO": {"eps": -0.28, "revenue": 0.00121},
    "BRK-B": {"eps": 5.17, "revenue": 92.5},
    "035420.KS": {"revenueKRW": 3.3888, "opIncomeKRW": 0.5203, "netIncomeKRW": 0.7043},
    "017670.KS": {"revenueKRW": 4.3591, "opIncomeKRW": 0.566, "netIncomeKRW": 0.466},
}

# 거시지표 매핑 (지표 ID -> 캘린더 제목 패턴)
macro_mapping = {
    "US_PPI": {"country": "미국", "patterns": ["PPI"]},
    "US_CPI": {"country": "미국", "patterns": ["CPI"]},
    "US_RETAIL": {"country": "미국", "patterns": ["소매판매", "Retail Sales"]},
    "CN_INDUSTRIAL": {"country": "중국", "patterns": ["산업생산", "Industrial Production"]},
    "CN_RETAIL": {"country": "중국", "patterns": ["소매판매", "Retail Sales"]},
}

def load_econ_calendar():
    """econ-calendar.json 로드"""
    try:
        with open("econ-calendar.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def extract_metric(value_str):
    """
    "YoY 4.7% · MoM 0.0%" 같은 문자열에서 수치 추출
    """
    import re

    if not value_str:
        return None, None

    yoy = None
    mom = None

    parts = value_str.split("·")
    for part in parts:
        part = part.strip()
        if part.startswith("YoY"):
            # "YoY 4.7%" 또는 "YoY +4.7%"에서 첫 번째 숫자 추출
            match = re.search(r"[+-]?[\d.]+", part)
            if match:
                try:
                    yoy = float(match.group(0))
                except:
                    pass
        elif part.startswith("MoM"):
            # "MoM +0.3%" 또는 "MoM -0.1%" 에서 첫 번째 숫자 추출
            match = re.search(r"[+-]?[\d.]+", part)
            if match:
                try:
                    mom = float(match.group(0))
                except:
                    pass

    return yoy, mom

def build_earnings_delta(calendar):
    """earnings-series에 추가할 delta 객체 생성"""
    earnings_delta = {}

    earnings_events = [e for e in calendar if e.get("kind") == "실적" and e.get("ticker")]

    for event in earnings_events:
        ticker = event.get("ticker")
        title = event.get("title")
        date = event.get("date")
        actual = event.get("actual")
        forecast = event.get("forecast")
        source = event.get("source")

        if not ticker or not actual:
            continue

        # 분기 추출 (제목에서)
        period = extract_period_from_title(title, date)
        if not period:
            continue

        # 메트릭별 값 추출
        if ticker not in earnings_delta:
            earnings_delta[ticker] = {
                "quarters": []
            }

        # 해당 분기 엔트리 찾기 또는 생성
        quarter_entry = None
        for q in earnings_delta[ticker]["quarters"]:
            if q["period"] == period:
                quarter_entry = q
                break

        if not quarter_entry:
            quarter_entry = {"period": period, "source": source}
            earnings_delta[ticker]["quarters"].append(quarter_entry)

        # actual 값에서 메트릭 추출 (간단한 파싱)
        if isinstance(actual, str):
            if ticker.endswith(".KS"):
                # 한국 종목: "매출 4.3591조 · 영업이익 0.566조 · 순이익 0.466조"
                parse_korean_earnings(quarter_entry, actual)
            else:
                # 미국 종목: "EPS $2.02 · 매출 $109.42B"
                parse_us_earnings(quarter_entry, actual)

    return earnings_delta

def parse_us_earnings(quarter_entry, actual_str):
    """미국 실적 문자열 파싱"""
    import re

    parts = actual_str.split("·")
    for part in parts:
        part = part.strip()
        if part.startswith("EPS"):
            # "EPS $2.02" 파싱 - 숫자만 추출
            match = re.search(r"[\d.]+", part)
            if match:
                try:
                    quarter_entry["eps"] = {"act": float(match.group(0)), "cons": None}
                except:
                    pass
        elif "매출" in part or "revenue" in part.lower():
            # "매출 $1.935B" 또는 "매출 $109.42B" 파싱 - 숫자만 추출
            match = re.search(r"[\d.]+", part)
            if match:
                try:
                    quarter_entry["revenue"] = {"act": float(match.group(0)), "cons": None}
                except:
                    pass

def parse_korean_earnings(quarter_entry, actual_str):
    """한국 실적 문자열 파싱"""
    import re

    parts = actual_str.split("·")
    for part in parts:
        part = part.strip()
        if "매출" in part:
            match = re.search(r"[\d.]+", part)
            if match:
                try:
                    quarter_entry["revenueKRW"] = {"act": float(match.group(0)), "cons": None}
                except:
                    pass
        elif "영업이익" in part:
            match = re.search(r"[\d.]+", part)
            if match:
                try:
                    quarter_entry["opIncomeKRW"] = {"act": float(match.group(0)), "cons": None}
                except:
                    pass
        elif "순이익" in part:
            match = re.search(r"[\d.]+", part)
            if match:
                try:
                    quarter_entry["netIncomeKRW"] = {"act": float(match.group(0)), "cons": None}
                except:
                    pass

def extract_period_from_title(title, date):
    """제목과 날짜에서 분기 추출"""
    import re

    # 제목에서 분기 추출 시도
    match = re.search(r"(\d{4})년\s+(\d)분기", title)
    if match:
        year = match.group(1)
        quarter = match.group(2)
        end_month = str((int(quarter) * 3)).zfill(2)
        return f"Q{quarter} {year} ({year}-{end_month})"

    # FY2026 4분기 같은 형식
    match = re.search(r"FY(\d{4})\s+(\d)분기", title)
    if match:
        year = match.group(1)
        quarter = match.group(2)
        end_month = str((int(quarter) * 3)).zfill(2)
        return f"Q{quarter} {year} ({year}-{end_month})"

    # "마이크로소프트 FY2026 4분기·연간 실적" 형식
    match = re.search(r"FY(\d{4})\s+(\d)분기", title)
    if match:
        year = match.group(1)
        quarter = match.group(2)
        end_month = str((int(quarter) * 3)).zfill(2)
        return f"Q{quarter} {year} ({year}-{end_month})"

    # Q3 2026 형식
    match = re.search(r"Q(\d)\s+(\d{4})", title)
    if match:
        quarter = match.group(1)
        year = match.group(2)
        end_month = str((int(quarter) * 3)).zfill(2)
        return f"Q{quarter} {year} ({year}-{end_month})"

    # 위의 모든 경우가 실패하면, date에서 연도 추출하고 "2026년 2분기" 패턴 재시도
    match = re.search(r"(\d)분기", title)
    if match:
        quarter = match.group(1)
        year = date.split("-")[0]
        end_month = str((int(quarter) * 3)).zfill(2)
        return f"Q{quarter} {year} ({year}-{end_month})"

    return None

def build_macro_delta(calendar):
    """macro-series에 추가할 delta 객체 생성"""
    macro_delta = {}

    macro_events = [e for e in calendar if e.get("kind") == "거시"]

    for event in macro_events:
        country = event.get("country")
        title = event.get("title")
        date = event.get("date")
        actual = event.get("actual")
        forecast = event.get("forecast")
        source = event.get("source")

        if not actual or not date:
            continue

        # 지표 ID 매핑
        indicator_id = map_indicator(country, title)
        if not indicator_id:
            continue

        if indicator_id not in macro_delta:
            macro_delta[indicator_id] = {"releases": []}

        # 월 추출 (date: "2026-08-13" -> "2026-07")
        period = date[:7]

        # 해당 회차 찾기 또는 생성
        release_entry = None
        for r in macro_delta[indicator_id]["releases"]:
            if r["period"] == period:
                release_entry = r
                break

        if not release_entry:
            release_entry = {"period": period, "source": source}
            macro_delta[indicator_id]["releases"].append(release_entry)

        # actual/forecast 값 추출
        yoy, mom = extract_metric(actual)
        cons_yoy, cons_mom = extract_metric(forecast)

        if yoy is not None:
            release_entry["act"] = yoy
        if cons_yoy is not None:
            release_entry["cons"] = cons_yoy
        if mom is not None:
            release_entry["momAct"] = mom
        if cons_mom is not None:
            release_entry["momCons"] = cons_mom

    return macro_delta

def map_indicator(country, title):
    """국가와 제목에서 지표 ID 매핑"""
    if country == "미국":
        if "CPI" in title and "Core" not in title:
            return "US_CPI"
        elif "Core CPI" in title:
            return "US_CORE_CPI"
        elif "PPI" in title:
            return "US_PPI"
        elif "소매판매" in title or "Retail Sales" in title:
            return "US_RETAIL"
    elif country == "중국":
        if "산업생산" in title or "Industrial Production" in title:
            return "CN_INDUSTRIAL"
        elif "소매판매" in title or "Retail Sales" in title:
            return "CN_RETAIL"
        elif "CPI" in title:
            return "CN_CPI"
        elif "PPI" in title:
            return "CN_PPI"
    elif country == "한국":
        if "수출" in title:
            return "KR_EXPORTS"
        elif "수입" in title:
            return "KR_IMPORTS"
        elif "CPI" in title or "소비자물가" in title:
            return "KR_CPI"

    return None

def main():
    """메인 프로세스"""
    calendar = load_econ_calendar()

    if not calendar:
        print("❌ econ-calendar.json을 찾을 수 없거나 비어있습니다.")
        return

    # Delta 객체 생성
    earnings_delta = build_earnings_delta(calendar)
    macro_delta = build_macro_delta(calendar)

    # series-delta.json 구조
    series_delta = {
        "earnings": earnings_delta,
        "macro": macro_delta
    }

    # 파일 저장
    with open("series-delta.json", "w", encoding="utf-8") as f:
        json.dump(series_delta, f, ensure_ascii=False, indent=2)

    print("✅ series-delta.json 생성 완료")
    print(f"   - Earnings: {len(earnings_delta)} 종목")
    print(f"   - Macro: {len(macro_delta)} 지표")

if __name__ == "__main__":
    main()
