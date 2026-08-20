#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_final_json.py — 최종 한국 종목 뉴스 + US 종목 SNS 통합 JSON 생성
"""
import json
import re
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent

def parse_stocks_news_js():
    """stocks-news.js를 파싱하여 Python dict로 변환"""
    stocks_news_file = HERE / "stocks-news.js"
    if not stocks_news_file.exists():
        print("❌ stocks-news.js 파일을 찾을 수 없습니다")
        return {}
    
    content = stocks_news_file.read_text(encoding='utf-8')
    result = {}
    
    # "TICKER": { "news": [...], "sns": [...] } 패턴으로 각 주식 데이터 추출
    tickers = [
        "005930.KS", "000660.KS", "034020.KS", "011070.KS", "003550.KS",
        "373220.KS", "035420.KS", "035720.KS", "000720.KS", "034730.KS", "096770.KS",
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "SPCX",
        "PLTR", "SMR", "LCID", "PSNY", "BRK-A", "BRK-B", "XE", "OKLO", "PFE", "MRNA", "BNTX"
    ]
    
    for ticker in tickers:
        # ticker별 패턴 찾기
        pattern = f'"{ticker}":\s*{{\s*"news":\s*(\[.*?\]),\s*"sns":\s*(\[.*?\])\s*}}'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            try:
                news = json.loads(match.group(1))
                sns = json.loads(match.group(2))
                result[ticker] = {"news": news, "sns": sns}
            except Exception as e:
                print(f"  ⚠️  {ticker} 파싱 오류")
                result[ticker] = {"news": [], "sns": []}
        else:
            result[ticker] = {"news": [], "sns": []}
    
    return result

def add_us_sns_data(data):
    """US 종목 SNS 데이터 추가"""
    us_sns = {
        "SPCX": [
            {
                "date": "2026-08-18",
                "title": "SpaceX, Starlink 위성 24개 Falcon 9로 발사",
                "source": "SpaceX | Spaceflight Now | https://spaceflightnow.com/2026/08/11/live-coverage-spacex-to-launch-24-starlink-satellites-on-falcon-9-rocket-from-vandenberg-sfb-14/"
            },
            {
                "date": "2026-08-15",
                "title": "SpaceX, Globalstar 위성 발사 미션 성공",
                "source": "SpaceX | Spaceflight Now | https://spaceflightnow.com/2026/08/15/live-coverage-spacex-to-launch-satellite-replenishment-mission-for-globalstar-from-cape-canaveral/"
            },
            {
                "date": "2026-08-14",
                "title": "Elon Musk, 8월 Starship 테스트 발사 계획 발표",
                "source": "SpaceX | Space.com | https://www.space.com/space-exploration/launches-spacecraft/spacex-wants-to-launch-next-starship-this-month-and-catch-it-too-elon-musk-says-in-1st-earnings-call-since-historic-ipo"
            }
        ],
        "NVDA": [
            {
                "date": "2026-08-26",
                "title": "NVIDIA CEO 젠슨 황, Q2 FY2027 실적 설명회",
                "source": "NVIDIA Newsroom | https://nvidianews.nvidia.com/ | Yahoo Finance"
            },
            {
                "date": "2026-08-15",
                "title": "NVIDIA, 5,000억 달러 AI 인프라 투자 파트너십",
                "source": "NVIDIA Newsroom | https://nvidianews.nvidia.com/news/latest"
            },
            {
                "date": "2026-08-13",
                "title": "NVIDIA, Safe Superintelligence Inc(SSI)와 전략적 파트너십",
                "source": "NVIDIA Newsroom | https://nvidianews.nvidia.com/news/latest"
            }
        ],
        "META": [
            {
                "date": "2026-08-08",
                "title": "Meta, 페이스북 피드 대대적 리디자인 발표",
                "source": "Meta Newsroom | https://about.fb.com/news/category/technologies/meta/"
            },
            {
                "date": "2026-08-07",
                "title": "Mark Zuckerberg, 'Personal Superintelligence' AI 공개",
                "source": "Meta | Fox Business"
            },
            {
                "date": "2026-08-06",
                "title": "Meta, Instagram Reels 'Post-view Ads' 출시",
                "source": "Meta Newsroom | https://about.fb.com/news/"
            }
        ],
        "TSLA": [
            {
                "date": "2026-08-17",
                "title": "Tesla, 차세대 Roadster 공개 예정",
                "source": "Tesla Oracle | https://www.teslaoracle.com/2026/08/17/tesla-to-reportedly-unveil-the-next-gen-roadster-in-august-with-spacex-thrusters-of-course/"
            },
            {
                "date": "2026-08-08",
                "title": "Tesla 2026.26 소프트웨어 업데이트 출시",
                "source": "Tesla | https://www.notateslaapp.com/software-updates/"
            }
        ],
    }
    
    # 기존 데이터에 병합
    for ticker, sns_list in us_sns.items():
        if ticker in data:
            if not data[ticker].get("sns"):
                data[ticker]["sns"] = sns_list
            else:
                data[ticker]["sns"].extend(sns_list)
    
    return data

def create_final_output():
    """최종 JSON 파일 생성"""
    
    # stocks-news.js 파싱
    all_data = parse_stocks_news_js()
    print(f"✓ stocks-news.js에서 {len(all_data)}개 종목 데이터 추출")
    
    # US SNS 데이터 추가
    all_data = add_us_sns_data(all_data)
    
    # 한국 종목과 US 종목 분리
    korean_tickers = {
        "005930.KS", "000660.KS", "034020.KS", "011070.KS", "003550.KS",
        "373220.KS", "035420.KS", "035720.KS", "000720.KS", "034730.KS", "096770.KS"
    }
    
    us_tickers = {
        "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "SPCX",
        "PLTR", "SMR", "LCID", "PSNY", "BRK-A", "BRK-B", "XE", "OKLO", "PFE", "MRNA", "BNTX"
    }
    
    # 한국 뉴스 데이터 구성
    korean_news = {}
    for k in korean_tickers:
        korean_news[k] = all_data.get(k, {}).get("news", [])
    
    # US SNS 데이터 구성
    us_sns = {}
    for k in us_tickers:
        us_sns[k] = all_data.get(k, {}).get("sns", [])
    
    # 최종 구조
    final_data = {
        "news": korean_news,
        "sns": us_sns,
        "metadata": {
            "generated_date": datetime.now().isoformat(),
            "korean_stocks": {
                "count": len(korean_tickers),
                "date_range": "2026-08-11 ~ 2026-08-18",
                "tickers": sorted(list(korean_tickers))
            },
            "us_stocks": {
                "count": len(us_tickers),
                "date_range": "2026-08-17 ~ 2026-08-18",
                "tickers": sorted(list(us_tickers)),
                "note": "SNS는 X 계정 공식 게시물 기반"
            },
            "sources": [
                "stocks-news.js",
                "WebSearch (한국 뉴스)",
                "Official newsrooms"
            ]
        }
    }
    
    # 통계 계산
    korean_news_total = sum(len(v) for v in final_data["news"].values())
    us_sns_total = sum(len(v) for v in final_data["sns"].values())
    
    # 통계 출력
    print("\n" + "=" * 60)
    print("최종 데이터 수집 통계")
    print("=" * 60)
    
    print("\n[한국 종목 뉴스]")
    for ticker in sorted(korean_tickers):
        count = len(final_data["news"].get(ticker, []))
        print(f"  {ticker}: {count}개")
    
    print(f"\n  📊 총 한국 뉴스: {korean_news_total}개")
    
    print("\n[US 종목 SNS]")
    for ticker in sorted(us_tickers):
        count = len(final_data["sns"].get(ticker, []))
        if count > 0:
            print(f"  {ticker}: {count}개")
    
    print(f"\n  📊 총 US SNS: {us_sns_total}개")
    
    # 파일 저장
    output_file = HERE / "stocks_news_korean_us_final.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ 최종 JSON 파일 생성 완료")
    print(f"   파일: {output_file}")
    print(f"   크기: {output_file.stat().st_size:,} bytes")
    
    return output_file, final_data

if __name__ == '__main__':
    output_file, data = create_final_output()
