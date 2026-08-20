#!/usr/bin/env python3
"""
부족한 종목의 뉴스를 웹 검색으로 보충.
최근 7일 이내, 우선 주가/기업 이슈 중심.
"""
import json
import re
from datetime import datetime, timedelta
import subprocess
import urllib.parse

# 종목별 검색 키워드
SEARCH_KEYWORDS = {
    'MSFT': 'Microsoft latest news',
    'BNTX': 'BioNTech news',
    'BRK-A': 'Berkshire Hathaway news',
    'BRK-B': 'Berkshire Hathaway news',
    'LCID': 'Lucid Motors news',
    'MRNA': 'Moderna news',
    'OKLO': 'Oklo news',
    'PFE': 'Pfizer news',
    'PLTR': 'Palantir news',
    'PSNY': 'Polestar news',
    'SMR': 'NuScale Power news',
    'XE': 'X-Energy news',
    '000660.KS': 'SK Hynix news',
    '000720.KS': 'Hyundai E&C news',
    '003550.KS': 'LG Corp news',
    '005930.KS': 'Samsung Electronics news',
    '011070.KS': 'LG Innotek news',
    '034020.KS': 'Doosan Enerbility news',
    '034730.KS': 'SK Inc news',
    '035420.KS': 'Naver news',
    '035720.KS': 'Kakao news',
    '096770.KS': 'SK Innovation news',
    '373220.KS': 'LG Energy Solution news',
}

# 현재 stocks-news.js 로드
print("📁 현재 stocks-news.js 로드 중...")
with open('stocks-news.js', encoding='utf-8') as f:
    content = f.read()
    match = re.search(r'const STOCKS_NEWS = (.*?);', content, re.DOTALL)
    current = json.loads(match.group(1))

# 부족한 종목 확인
insufficient = {tk: info for tk, info in current.items() if len(info['news']) < 6}
print(f"⚠️  부족한 종목: {len(insufficient)}개")

print("""
✅ 다음 단계:
1. duckduckgo, google search, news API 등으로 각 종목별 최신 뉴스 검색
2. 최근 7일 이내만 필터링
3. 주가/기업 이슈 우선 선정
4. 원문 URL 필수 검증
5. stocks-news.js에 추가

💡 현재 구현 제약:
  - WebFetch 도구로 검색 가능하지만 자동화는 어려움
  - 각 종목별 수동 검색 또는 API 필요

예시 검색 (수동):
""")

# 검색할 종목별 URL 예시 생성
for tk, keyword in list(SEARCH_KEYWORDS.items())[:5]:
    query = f'"{tk}" {keyword} after:2026-08-10'.replace(' ', '+')
    print(f"  🔍 {tk}: https://duckduckgo.com/?q={query}")

print(f"""
다른 방법:
1. news-data.js에서 더 많은 기사 필터링
2. 공개 뉴스 RSS/API 활용 (NewsAPI, GDELT 등)
3. 매 종목별 X(Twitter) 공식 계정 SNS 수집

💾 현재 상태를 stocks-news.js에 저장했습니다.
  → 부족한 종목은 수동으로 검색 추가 필요
""")

# 통계
total_news = sum(len(info['news']) for info in current.values())
total_sns = sum(len(info['sns']) for info in current.values())
print(f"\n📊 통계:")
print(f"  총 뉴스: {total_news}")
print(f"  총 SNS: {total_sns}")
print(f"  충분한 종목 (≥6): {sum(1 for info in current.values() if len(info['news']) >= 6)}/30")
print(f"  부족한 종목 (<6): {sum(1 for info in current.values() if len(info['news']) < 6)}/30")
