#!/usr/bin/env python3
"""
pending-actuals와 econ-calendar의 항목들을 매칭해서 series-delta.json을 생성한다.

입력:
- pending-actuals.json: pending items
- econ-calendar-store.json: calendar items with forecast/actual

출력:
- series-delta.json: {earnings: {TICKER: ...}, macro: {ID: ...}}
"""

import json
import re
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path

# 매크로 지표 정의
MACRO_INDICATORS = {
    "CN_CPI": {"name": "중국 CPI (전년비)", "country": "중국", "unit": "%", "match": ["CPI"]},
    "CN_INDPROD": {"name": "중국 산업생산 (전년비)", "country": "중국", "unit": "%", "match": ["산업생산"]},
    "CN_LPR1Y": {"name": "중국 LPR (1년)", "country": "중국", "unit": "%", "match": ["LPR"]},
    "CN_RETAIL": {"name": "중국 소매판매 (전년비)", "country": "중국", "unit": "%", "match": ["소매판매"]},
    "DE_PMI": {"name": "독일 제조업 PMI", "country": "독일", "unit": "지수", "match": ["PMI"]},
    "EU_GDP": {"name": "유로존 GDP 성장률 (QoQ)", "country": "유럽", "unit": "%", "match": ["GDP"]},
    "EU_HICP": {"name": "유로존 HICP (전년비)", "country": "유럽", "unit": "%", "match": ["HICP", "물가", "CPI"]},
    "EU_PMI": {"name": "유로존 제조업 PMI", "country": "유럽", "unit": "지수", "match": ["PMI"]},
    "EU_RATE": {"name": "ECB 기준금리 (MRO)", "country": "유럽", "unit": "%", "match": ["ECB", "금리 결정"]},
    "JP_CPI": {"name": "일본 전국 CPI (전년비)", "country": "일본", "unit": "%", "match": ["CPI", "소비자물가"]},
    "JP_PMI": {"name": "일본 제조업 PMI", "country": "일본", "unit": "지수", "match": ["PMI"]},
    "JP_RATE": {"name": "일본 정책금리 (BOJ)", "country": "일본", "unit": "%", "match": ["BOJ", "정책금리", "정책 성명"]},
    "JP_TOKYO_CORE_CPI": {"name": "일본 도쿄 Core CPI (전년비)", "country": "일본", "unit": "%", "match": ["도쿄 CPI", "도쿄"]},
    "JP_TOKYO_CPI": {"name": "일본 도쿄 CPI (전년비)", "country": "일본", "unit": "%", "match": ["도쿄 CPI", "도쿄 코어 CPI"]},
    "KR_CPI": {"name": "한국 CPI (전년비)", "country": "한국", "unit": "%", "match": ["소비자물가", "CPI"]},
    "KR_RATE": {"name": "한국 기준금리 (한은)", "country": "한국", "unit": "%", "match": ["기준금리", "금통위"]},
    "KR_TRADE": {"name": "한국 수출액 (월)", "country": "한국", "unit": "십억$", "match": ["수출입"]},
    "KR_TRADE_EXP": {"name": "한국 수출액 (월)", "country": "한국", "unit": "십억$", "match": ["한국 수출", "수출액"]},
    "KR_TRADE_IMP": {"name": "한국 수입액 (월)", "country": "한국", "unit": "십억$", "match": ["한국 수입", "수입액"]},
    "ROKU": {"name": "Roku 2분기 실적", "country": "미국", "unit": "$B", "match": ["Roku 2분기"]},
    "UK_CPI": {"name": "영국 CPI (전년비)", "country": "영국", "unit": "%", "match": ["CPI"]},
    "UK_RATE": {"name": "영국 기준금리 (BoE)", "country": "영국", "unit": "%", "match": ["기준금리", "영란은행", "BoE"]},
    "US_ADP": {"name": "미국 ADP 민간고용 변화", "country": "미국", "unit": "천명", "match": ["ADP"]},
    "US_CONF": {"name": "미국 CB 소비자신뢰지수", "country": "미국", "unit": "지수", "match": ["소비자신뢰"]},
    "US_CORE_CPI": {"name": "미국 근원 CPI (Core, 전년비)", "country": "미국", "unit": "%", "match": ["Core CPI", "근원 CPI", "근원CPI"]},
    "US_CORE_PCE": {"name": "미국 근원 PCE (Core, 전년비)", "country": "미국", "unit": "%", "match": ["Core PCE", "근원 PCE"]},
    "US_CPI": {"name": "미국 CPI (전년비)", "country": "미국", "unit": "%", "match": ["CPI"]},
    "US_DURABLE": {"name": "미국 내구재 수주 (전월비)", "country": "미국", "unit": "%", "match": ["내구재"]},
    "US_ECI": {"name": "미국 고용비용지수 (전분기비)", "country": "미국", "unit": "%", "match": ["고용비용", "ECI"]},
    "US_FACTORY_ORDERS": {"name": "미국 공장수주 (전월비)", "country": "미국", "unit": "%", "match": ["공장수주", "Factory Orders"]},
    "US_FFR": {"name": "미국 기준금리 (FOMC 상단)", "country": "미국", "unit": "%", "match": ["FOMC", "기준금리", "금리 결정"]},
    "US_GDP": {"name": "미국 GDP 성장률 (QoQ 연율)", "country": "미국", "unit": "%", "match": ["GDP"]},
    "US_IMPORT_PRICE": {"name": "미국 수입물가 (전월비)", "country": "미국", "unit": "%", "match": ["수입"]},
    "US_INDPRO": {"name": "미국 산업생산 (MoM)", "country": "미국", "unit": "%", "match": ["산업생산"]},
    "US_ISM_MFG": {"name": "미국 ISM 제조업 PMI", "country": "미국", "unit": "지수", "match": ["ISM 제조업", "ISM제조"]},
    "US_ISM_SVC": {"name": "미국 ISM 서비스 PMI", "country": "미국", "unit": "지수", "match": ["ISM 서비스", "ISM비제조", "ISM 비제조"]},
    "US_JOBLESS": {"name": "미국 신규 실업수당 청구", "country": "미국", "unit": "천건", "match": ["신규실업수당", "실업수당"]},
    "US_JOLTS": {"name": "미국 JOLTS 구인건수", "country": "미국", "unit": "백만", "match": ["구인", "JOLTs", "JOLTS", "Job Openings"]},
    "US_MICH": {"name": "미국 미시간대 소비심리", "country": "미국", "unit": "지수", "match": ["미시간"]},
    "US_NEWHOME": {"name": "미국 신규주택판매", "country": "미국", "unit": "천호", "match": ["신규주택"]},
    "US_NFP": {"name": "미국 비농업 고용 변화", "country": "미국", "unit": "천명", "match": ["비농업", "Nonfarm"]},
    "US_PCE": {"name": "미국 PCE 물가 (전년비)", "country": "미국", "unit": "%", "match": ["PCE"]},
    "US_PPI": {"name": "미국 PPI (전년비)", "country": "미국", "unit": "%", "match": ["PPI"]},
    "US_RETAIL": {"name": "미국 소매판매 (전월비)", "country": "미국", "unit": "%", "match": ["소매판매"]},
    "US_SP_PMI": {"name": "미국 S&P글로벌 종합 PMI", "country": "미국", "unit": "지수", "match": ["S&P 글로벌", "S&P글로벌"]},
    "US_TRADE": {"name": "미국 무역수지", "country": "미국", "unit": "십억$", "match": ["무역수지"]},
    "US_UNEMP": {"name": "미국 실업률", "country": "미국", "unit": "%", "match": ["고용상황", "실업률", "NFP"]},
}


def extract_numbers(text: str) -> List[float]:
    """텍스트에서 숫자 추출 (범위 포함)"""
    if not text:
        return []
    # 패턴: 숫자.숫자, 숫자%, 범위 등
    matches = re.findall(r'-?\d+\.?\d*', text)
    return [float(m) for m in matches if m and m != '.']


def parse_range_consensus(text: str) -> Optional[float]:
    """범위 컨센서스를 중간값으로 변환 (예: '90–120K' -> 105)"""
    if not text:
        return None

    numbers = extract_numbers(text)
    if len(numbers) >= 2:
        return (numbers[0] + numbers[1]) / 2
    elif len(numbers) == 1:
        return numbers[0]
    return None


def extract_single_value(text: str) -> Optional[float]:
    """텍스트에서 첫 번째 숫자값 추출"""
    if not text:
        return None
    numbers = extract_numbers(text)
    return numbers[0] if numbers else None


def extract_eps_value(text: str) -> Optional[float]:
    """텍스트에서 EPS 값 추출 (예: "EPS $4.74", "EPS ~$4.22–4.24", "GAAP EPS $9.11")"""
    if not text:
        return None

    # "EPS" 또는 "GAAP EPS" 포함하는 부분 찾기
    # 패턴: (GAAP )EPS (추가정보) ~$숫자(-숫자)?
    # 중요: $ 기호를 요구하여 실제 EPS 값만 추출
    pattern = r'(?:GAAP\s+|non-GAAP\s+)?EPS(?:\(adj\))?\s+(?:~\s*)?\$\s*([\d.–-]+)'
    matches = re.finditer(pattern, text, re.IGNORECASE)

    for match in matches:
        val_str = match.group(1).strip()
        # 범위인 경우 중간값 계산
        if '–' in val_str or '-' in val_str:
            parts = re.split(r'[–-]', val_str)
            nums = [extract_single_value(p) for p in parts if extract_single_value(p) is not None]
            if len(nums) >= 2:
                return (nums[0] + nums[1]) / 2
        else:
            num = extract_single_value(val_str)
            if num is not None:
                return num

    return None


def normalize_value(value: Any) -> Optional[float]:
    """값을 정규화하여 float로 변환"""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        # EPS 값 추출 시도
        eps_val = extract_eps_value(value)
        if eps_val is not None:
            return eps_val
        # 범위 컨센서스 시도
        range_val = parse_range_consensus(value)
        if range_val is not None:
            return range_val
        # 첫 번째 숫자 추출
        single_val = extract_single_value(value)
        if single_val is not None:
            return single_val
    return None


def match_macro_indicator(title: str, country: str) -> Optional[str]:
    """calendar item의 title/country로부터 macro indicator ID 찾기"""
    title_lower = title.lower()
    country_lower = country.lower()

    for ind_id, ind_config in MACRO_INDICATORS.items():
        # country 매칭
        if country_lower != ind_config["country"].lower():
            continue

        # title 매칭 (match 리스트)
        for match_term in ind_config["match"]:
            if match_term.lower() in title_lower:
                return ind_id

    return None


def extract_mom_values(text: str) -> Tuple[Optional[float], Optional[float]]:
    """MoM 컨센서스와 실제값 추출 (특히 물가/소비 지표)"""
    if not text:
        return None, None

    # "MoM +0.3%" 형태 찾기
    mom_pattern = r'MoM\s*([±+-]?\d+\.?\d*)'
    matches = re.findall(mom_pattern, text, re.IGNORECASE)

    if len(matches) >= 2:
        return float(matches[0]), float(matches[1])
    elif len(matches) == 1:
        return float(matches[0]), None

    return None, None


def get_quarter_period(date_str: str) -> str:
    """날짜로부터 분기 정보 생성 (예: '2026-07-29' -> 'Q2 2026 (2026-07)')"""
    # 문자열로부터 연도와 월 추출
    parts = date_str.split('-')
    if len(parts) >= 2:
        year = parts[0]
        month = int(parts[1])
        # 월로부터 분기 계산
        quarter = (month - 1) // 3 + 1
        return f"Q{quarter} {year} ({date_str[:7]})"
    return f"Q2 {date_str[:4]} ({date_str[:7]})"


def match_pending_to_calendar(pending: Dict[str, Any], calendar: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """pending item을 calendar에서 매칭"""
    pending_date = pending.get("date")
    pending_ticker = pending.get("ticker")
    pending_title = pending.get("title", "")

    for cal_item in calendar:
        cal_date = cal_item.get("date")
        cal_ticker = cal_item.get("ticker")
        cal_title = cal_item.get("title", "")

        # date 일치 필수
        if cal_date != pending_date:
            continue

        # ticker 기반 매칭
        if pending_ticker and cal_ticker:
            if pending_ticker == cal_ticker:
                return cal_item

        # title 기반 매칭 (부분 일치)
        if pending_title and cal_title:
            if pending_title.strip() == cal_title.strip():
                return cal_item

    return None


def build_series_delta():
    """series-delta.json 생성"""
    base_path = Path("/Users/shkim/PycharmProjects/WEB_WORLD_INFO")

    # 파일 로드
    with open(base_path / "econ-calendar-store.json", "r", encoding="utf-8") as f:
        calendar_list = json.load(f)

    earnings = {}
    macro = {}
    processed_count = 0
    skipped_count = 0

    # econ-calendar-store의 모든 항목을 처리 (actual이 있는 것만)
    for calendar_item in calendar_list:
        # actual이 없으면 스킵
        actual = calendar_item.get("actual")
        if actual is None:
            skipped_count += 1
            continue

        ticker = calendar_item.get("ticker")
        country = calendar_item.get("country", "")
        title = calendar_item.get("title", "")
        forecast = calendar_item.get("forecast")
        date_str = calendar_item.get("date", "")

        # Earnings vs Macro 분류
        if ticker:
            # Earnings
            actual_val = normalize_value(actual)
            cons_val = normalize_value(forecast)

            if ticker not in earnings:
                earnings[ticker] = {
                    "name": title,
                    "metrics": ["revenue", "eps"],
                    "quarters": []
                }

            quarter_period = get_quarter_period(date_str)
            earnings[ticker]["quarters"].append({
                "period": quarter_period,
                "eps": {
                    "act": actual_val,
                    "cons": cons_val
                },
                "source": f"econ-calendar (forecast: {forecast}) | (actual: {actual})"
            })
            processed_count += 1
        else:
            # Macro
            ind_id = match_macro_indicator(title, country)
            if not ind_id:
                print(f"⚠️  매크로 지표 매칭 실패: {title} ({country})")
                skipped_count += 1
                continue

            if ind_id not in macro:
                ind_config = MACRO_INDICATORS[ind_id]
                macro[ind_id] = {
                    "name": ind_config["name"],
                    "country": ind_config["country"],
                    "unit": ind_config["unit"],
                    "match": {"any": ind_config["match"], "not": []},
                    "releases": []
                }

            # 월별 기간 (YYYY-MM)
            period = date_str[:7] if date_str else "unknown"

            actual_val = normalize_value(actual)
            cons_val = normalize_value(forecast)

            # MoM 값 추출 (물가/소비 지표)
            mom_cons = None
            mom_act = None
            if ind_id in ["US_PCE", "US_CORE_PCE", "US_CPI", "US_CORE_CPI", "US_PPI", "KR_CPI"]:
                forecast_mom = extract_mom_values(forecast)
                actual_mom = extract_mom_values(actual)
                mom_cons = forecast_mom[0]
                mom_act = actual_mom[1]

            release_item = {
                "period": period,
                "cons": cons_val,
                "act": actual_val,
                "source": f"econ-calendar (forecast: {forecast}) | (actual: {actual})"
            }

            if mom_cons is not None or mom_act is not None:
                release_item["momCons"] = mom_cons
                release_item["momAct"] = mom_act

            macro[ind_id]["releases"].append(release_item)
            processed_count += 1

    # series-delta.json 저장
    output = {
        "earnings": earnings,
        "macro": macro
    }

    with open(base_path / "series-delta.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n✓ series-delta.json 생성 완료")
    print(f"  - 처리됨: {processed_count} 항목")
    print(f"  - 스킵됨: {skipped_count} 항목")
    print(f"  - Earnings: {len(earnings)} 종목")
    print(f"  - Macro: {len(macro)} 지표")


if __name__ == "__main__":
    build_series_delta()
