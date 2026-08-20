import json
import subprocess
from datetime import datetime, timedelta
from collections import defaultdict

# 1. news-data.js에서 재사용 가능한 뉴스 추출
d = open('news-data.js', encoding='utf-8').read()
news_data = json.loads(d[d.index('['):d.rindex(']')+1])

KW = {
    'AAPL':['애플','apple'],'MSFT':['마이크로소프트','microsoft'],'GOOGL':['구글','알파벳','google','alphabet'],
    'AMZN':['아마존','amazon'],'NVDA':['엔비디아','nvidia'],'META':['메타','meta','페이스북'],
    'TSLA':['테슬라','tesla'],'SPCX':['스페이스x','spacex','스타링크','starlink'],'PLTR':['팔란티어','palantir'],
    'SMR':['뉴스케일','nuscale'],'LCID':['루시드','lucid'],'PSNY':['폴스타','polestar'],
    'BRK-A':['버크셔','berkshire','버핏','buffett'],'BRK-B':['버크셔','berkshire','버핏','buffett'],
    'XE':['엑스에너지','x-energy','x energy'],'OKLO':['오클로','oklo'],
    'PFE':['화이자','pfizer'],'MRNA':['모더나','moderna'],'BNTX':['바이오엔테크','biontech'],
    '005930.KS':['삼성전자','samsung'],'000660.KS':['sk하이닉스','하이닉스','hynix'],
    '034020.KS':['두산에너빌리티','두산','doosan'],'011070.KS':['lg이노텍','이노텍','innotek'],
    '003550.KS':['(주)lg','엘지','lg corp'],'373220.KS':['lg에너지솔루션','엔솔','energy solution'],
    '035420.KS':['네이버','naver'],'035720.KS':['카카오','kakao'],'000720.KS':['현대건설','hyundai e&c'],
    '034730.KS':['sk(주)','sk이노','sk그룹'],'096770.KS':['sk이노베이션','sk innovation']
}

days = sorted({x['date'] for x in news_data})[-3:]
reusable = {}

for tk, kws in KW.items():
    hits = [x for x in news_data if x['date'] in days and any(k in (x['title']+x.get('summary','')).lower() for k in kws)]
    reusable[tk] = []
    seen_urls = set()
    for x in hits[:6]:
        url = x.get('url', '')
        if url and url not in seen_urls:
            reusable[tk].append({
                "date": x['date'],
                "title": x['title'],
                "source": f"{x.get('source', '뉴스')} | {url}"
            })
            seen_urls.add(url)

# 2. 부족한 종목 식별
tickers_all = list(KW.keys())
need_supplement = [tk for tk in tickers_all if len(reusable.get(tk, [])) < 6]

print(f"재사용 가능한 뉴스: {sum(len(v) for v in reusable.values())}개")
print(f"부족한 종목 ({len(need_supplement)}): {', '.join(need_supplement)}")

# 3. 부족한 뉴스 검색 (Google News via gnews API 대체 사용)
import urllib.request
import urllib.parse

def search_news(ticker, query, days=7):
    """Google News 또는 기타 API를 통해 최신 뉴스 검색"""
    results = []
    try:
        # gnews.io free API 또는 대체 뉴스 소스
        # 여기서는 wget/curl 기반 검색으로 대체
        search_query = f'{query} news -site:twitter.com -site:reddit.com'
        # 실제로는 API 키가 필요함. 현재는 로컬 데이터만 사용
        pass
    except Exception as e:
        print(f"Search error for {ticker}: {e}")
    return results

# 4. 최종 데이터셋 구성
STOCKS_NEWS = {}
for tk in tickers_all:
    is_korean = '.KS' in tk
    news_items = []
    
    # 재사용분 추가
    news_items.extend(reusable.get(tk, []))
    
    # 부족한 경우 검색 필요 (현재는 재사용분만 사용)
    if len(news_items) < 6:
        # TODO: 실시간 검색으로 보충
        pass
    
    # 최종 형식
    STOCKS_NEWS[tk] = {
        "news": news_items[:10],  # 최대 10개
        "sns": [] if is_korean else []  # SNS는 별도 수집
    }

print(json.dumps(STOCKS_NEWS, ensure_ascii=False, indent=2)[:500])
