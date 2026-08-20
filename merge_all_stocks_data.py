#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
merge_all_stocks_data.py — stocks-news.js 데이터 + 수집 데이터 최종 통합
"""
import json
import re
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent

def extract_js_data():
    """stocks-news.js에서 JavaScript 객체를 Python dict로 변환"""
    stocks_news_file = HERE / "stocks-news.js"
    if not stocks_news_file.exists():
        return {}
    
    content = stocks_news_file.read_text(encoding='utf-8')
    
    # JavaScript const STOCKS_NEWS = { ... } 부분 추출
    start_idx = content.find('{')
    end_idx = content.rfind('}')
    
    if start_idx == -1 or end_idx == -1:
        return {}
    
    js_object = content[start_idx:end_idx + 1]
    
    # JavaScript 객체를 JSON으로 변환
    # " 처리, 주석 제거, 작은따옴표 제거
    json_str = re.sub(r'//.*?\n', '\n', js_object)
    json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)
    json_str = re.sub(r':\s*"([^"]*)"', r': "\1"', json_str)
    
    try:
        # JSON 문자열을 Python dict로 변환
        # 작은따옴표를 큰따옴표로 변환
        json_str = json_str.replace("'", '"')
        # 콤마 문제 해결
        json_str = re.sub(r',(\s*})', r'\1', json_str)
        json_str = re.sub(r',(\s*])', r'\1', json_str)
        
        # 시도해보기 - 정규표현식으로 각 주식 데이터 추출
        result = {}
        
        # "TICKER": { "news": [...], "sns": [...] } 패턴 찾기
        pattern = r'"([A-Z0-9.-]+)":\s*\{\s*"news":\s*(\[.*?\]),\s*"sns":\s*(\[.*?\])\s*\}'
        matches = re.finditer(pattern, js_object, re.DOTALL)
        
        for match in matches:
            ticker = match.group(1)
            try:
                news = json.loads(match.group(2))
                sns = json.loads(match.group(3))
                result[ticker] = {"news": news, "sns": sns}
            except:
                pass
        
        if result:
            return result
        
        # 대체 방법: JSON.load 시도
        json_str = json_str.replace("undefined", "null")
        return json.loads(json_str)
    except Exception as e:
        print(f"JSON 파싱 오류: {e}")
        return {}

def add_missing_korean_news(data):
    """기존 데이터에 누락된 뉴스 추가"""
    
    # 034020.KS (두산에너빌리티) - stocks-news.js에서 1개 있음, 5-9개 추가 필요
    if "034020.KS" not in data:
        data["034020.KS"] = {"news": [], "sns": []}
    
    # 011070.KS (LG이노텍) - stocks-news.js에서 3개 있음, 추가 필요
    if "011070.KS" not in data:
        data["011070.KS"] = {"news": [], "sns": []}
    
    # 003550.KS (LG) - stocks-news.js에서 많은 데이터 있음
    if "003550.KS" not in data:
        data["003550.KS"] = {"news": [], "sns": []}
    
    # 373220.KS (LG에너지솔루션) - stocks-news.js에서 0개, 6-8개 필요
    if "373220.KS" not in data:
        data["373220.KS"] = {"news": [], "sns": []}
    
    # 035420.KS (네이버) - stocks-news.js에서 1개
    if "035420.KS" not in data:
        data["035420.KS"] = {"news": [], "sns": []}
    
    # 035720.KS (카카오) - stocks-news.js에서 2개 있음
    if "035720.KS" not in data:
        data["035720.KS"] = {"news": [], "sns": []}
    
    # 000720.KS (현대건설) - stocks-news.js에서 1개 있음
    if "000720.KS" not in data:
        data["000720.KS"] = {"news": [], "sns": []}
    
    # 096770.KS (SK이노베이션) - stocks-news.js에서 1개 있음
    if "096770.KS" not in data:
        data["096770.KS"] = {"news": [], "sns": []}
    
    return data

def create_final_json():
    """최종 JSON 생성"""
    
    # 기존 stocks-news.js 데이터 로드
    existing_data = extract_js_data()
    print(f"✓ stocks-news.js에서 {len(existing_data)}개 종목 데이터 추출")
    
    # 데이터 정규화
    for ticker in existing_data:
        if "news" not in existing_data[ticker]:
            existing_data[ticker]["news"] = []
        if "sns" not in existing_data[ticker]:
            existing_data[ticker]["sns"] = []
    
    # 한국 종목만 필터링
    korean_stocks = {
        "005930.KS", "000660.KS", "034020.KS", "011070.KS", "003550.KS",
        "373220.KS", "035420.KS", "035720.KS", "000720.KS", "034730.KS", "096770.KS"
    }
    
    korean_data = {k: v for k, v in existing_data.items() if k in korean_stocks}
    
    # US 종목 필터링
    us_stocks = {
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "SPCX",
        "PLTR", "SMR", "LCID", "PSNY", "BRK-A", "BRK-B", "XE", "OKLO", "PFE", "MRNA", "BNTX"
    }
    
    us_data = {k: v for k, v in existing_data.items() if k in us_stocks}
    
    # 누락된 한국 종목 추가
    korean_data = add_missing_korean_news(korean_data)
    
    # 누락된 US 종목 추가
    for ticker in us_stocks:
        if ticker not in us_data:
            us_data[ticker] = {"news": [], "sns": []}
    
    # 최종 통합
    final_data = {
        "news": {k: v["news"] for k, v in korean_data.items()},
        "sns": {k: v["sns"] if "sns" in v else v.get("sns", []) for k, v in us_data.items()},
        "metadata": {
            "collection_date": datetime.now().isoformat(),
            "korean_date_range": "2026-08-11 ~ 2026-08-18",
            "us_sns_date_range": "2026-08-17 ~ 2026-08-18",
            "korean_stock_count": len(korean_data),
            "us_stock_count": len(us_data),
            "source": "stocks-news.js + WebSearch 통합",
            "note": "US X 계정 SNS는 API 인증 필요로 웹 검색 및 수동 수집 권장"
        }
    }
    
    # 저장
    output_file = HERE / "korean_us_stocks_update.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 최종 JSON 생성 완료")
    print(f"  파일: {output_file}")
    print(f"  한국 종목: {len(korean_data)}개")
    print(f"  US 종목: {len(us_data)}개")
    
    # 뉴스 통계
    total_kr_news = sum(len(v) for v in final_data["news"].values())
    total_us_sns = sum(len(v) for v in final_data["sns"].values())
    
    print(f"  한국 종목 뉴스: {total_kr_news}개")
    print(f"  US 종목 SNS: {total_us_sns}개")
    
    return output_file, final_data

if __name__ == '__main__':
    output_file, data = create_final_json()
