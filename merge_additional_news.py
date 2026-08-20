#!/usr/bin/env python3
"""
news-data.js에서 추출한 추가 뉴스를 stocks-news.js에 병합.
"""
import json
import re
from collections import defaultdict

# news-data.js 로드
print("📰 news-data.js 로드 중...")
with open('news-data.js', 'r', encoding='utf-8') as f:
    data = f.read()
json_str = data[data.index('['):data.rindex(']')+1]
j = json.loads(json_str)

# 종목별 확장된 키워드
KW = {
    '000660.KS': ['sk하이닉스', '하이닉스', 'hynix', 'sk'],
    '000720.KS': ['현대건설', 'e&c', 'hyundai e&c'],
    '003550.KS': ['lg', '엘지', 'lg corp'],
    '005930.KS': ['삼성', 'samsung'],
    '011070.KS': ['lg이노텍', '이노텍', 'innotek'],
    '034020.KS': ['두산', 'doosan', '에너빌리티'],
    '034730.KS': ['sk그룹', 'sk주식', 'sk inc'],
    '035420.KS': ['네이버', 'naver'],
    '035720.KS': ['카카오', 'kakao'],
    '096770.KS': ['sk이노베이션', 'sk innovation'],
    '373220.KS': ['lg에너지', '에너지솔루션'],
    'BNTX': ['biontech', 'bntx'],
    'BRK-A': ['berkshire', 'buffett'],
    'BRK-B': ['berkshire', 'buffett'],
    'LCID': ['lucid', 'motor', 'ev'],
    'MRNA': ['moderna', 'mrna'],
    'OKLO': ['oklo', 'nuclear'],
    'PFE': ['pfizer', 'pfe'],
    'PLTR': ['palantir', 'pltr'],
    'PSNY': ['polestar', 'volvo'],
    'SMR': ['nuscale', 'nuclear', 'smr'],
    'XE': ['x-energy', 'x energy'],
}

# 현재 stocks-news.js 로드
print("📁 stocks-news.js 로드 중...")
with open('stocks-news.js', 'r', encoding='utf-8') as f:
    content = f.read()
    match = re.search(r'const STOCKS_NEWS = (.*?);', content, re.DOTALL)
    current = json.loads(match.group(1))

# 각 종목별로 추가 뉴스 병합
print("🔄 뉴스 병합 중...\n")

merged = {}
for ticker in sorted(current.keys()):
    if ticker not in KW:
        merged[ticker] = current[ticker]
        continue

    news_list = current[ticker]['news'].copy()

    # 현재 URLs 수집 (중복 방지)
    seen_urls = set()
    for x in news_list:
        if x.get('source') and '|' in x.get('source', ''):
            url = x['source'].split('|', 1)[1].strip()
            seen_urls.add(url)

    # 추가 뉴스 찾기
    kws = KW[ticker]
    hits = [x for x in j if any(k in (x.get('title', '') + ' ' + x.get('summary', '')).lower() for k in kws)]

    # 중복 제거하고 추가
    added = 0
    for hit in hits:
        if hit.get('url') and hit['url'] not in seen_urls and added < (10 - len(news_list)):
            news_item = {
                'date': hit['date'],
                'title': hit['title'],
                'source': f"뉴스 | {hit['url']}"
            }
            news_list.append(news_item)
            seen_urls.add(hit['url'])
            added += 1

    # 날짜 역순 정렬
    news_list = sorted(news_list, key=lambda x: x['date'], reverse=True)[:10]

    merged[ticker] = {
        'news': news_list,
        'sns': [] if ticker.endswith('.KS') else current[ticker].get('sns', [])
    }

    status = "✓" if len(news_list) >= 6 else "⚠"
    change = "+" + str(added) if added > 0 else ""
    print(f"{status} {ticker}: {len(news_list)} news {change}")

# 파일 저장
print("\n💾 stocks-news.js 저장 중...")
output = f"const STOCKS_NEWS = {json.dumps(merged, ensure_ascii=False, indent=2)};\n\nif (typeof module !== 'undefined' && module.exports) {{\n  module.exports = STOCKS_NEWS;\n}}\n"

with open('stocks-news.js', 'w', encoding='utf-8') as f:
    f.write(output)

# 통계
total_news = sum(len(info['news']) for info in merged.values())
sufficient = sum(1 for info in merged.values() if len(info['news']) >= 6)

print(f"\n✅ 병합 완료!")
print(f"\n📊 최종 통계:")
print(f"  총 뉴스: {total_news}")
print(f"  충분한 종목 (≥6): {sufficient}/30")
print(f"  부족한 종목 (<6): {30-sufficient}/30")
