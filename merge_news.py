#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
 merge_news.py  ·  GDELT + Grok 병합 → news-data.js 빌더
------------------------------------------------------------
 - news-store.json  : GDELT 사건(fetch_news.py 가 생성)
 - grok-news.json   : Grok CLI 가 조사한 뉴스(선택)
 두 소스를 합쳐 도시 좌표를 보정한 뒤 news-data.js 를 만든다.

 사용:
   python3 merge_news.py        # 둘을 병합해 페이지 데이터 생성
 (fetch_news.py 가 끝에서 자동으로 build_output() 을 호출하기도 함)
============================================================
"""
import json
import hashlib
import math
import re
import statistics
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
STORE_PATH = HERE / "news-store.json"      # GDELT
GROK_PATH = HERE / "grok-news.json"        # Grok 조사 뉴스 (선택)
GROK_TECH_PATH = HERE / "grok-tech-news.json"  # 작업 F: Grok 글로벌 테크 딜 실검색(선택)
TRANS_PATH = HERE / "translations.json"          # Grok 번역(이번 실행 출력)
TRANS_STORE_PATH = HERE / "translations-store.json"  # 번역 영구 누적본
DIGEST_STORE_PATH = HERE / "digest-store.json"   # 좌표 없는 중요 뉴스(종합) 누적본
TOPIC_STORE_PATH = HERE / "topic-store.json"     # GDELT DOC 주제(기업·테크) 뉴스 누적본
BREAKING_STORE_PATH = HERE / "breaking-store.json"     # 속보 트랙 활성 스토어(리스너 생성)
BREAKING_ARCHIVE_PATH = HERE / "breaking-archive.json" # 속보 트랙 장기 아카이브(상한 초과분)
DIGEST_OUTPUT = HERE / "news-digest.js"          # 종합 프론트 산출물
PREV_RANKS_PATH = HERE / "digest-prev-ranks.json"  # 디제스트 순위변동(▲▼/NEW)용 '직전 사이클' 순위 스냅샷(서버 전용)
OUTPUT_PATH = HERE / "news-data.js"
RETENTION_DAYS = 180   # 보관 기간(일). 드롭다운 "최근 N개월"용으로 6개월 누적

CATS = ["분쟁", "정치", "경제", "사회", "기술", "문화"]
RELEVANCE_MIN = 4    # Grok 관련성 점수가 이 미만이면 지도에서 제외(가십·잡문)
# Grok 이 다른 표현을 쓰면 통합 카테고리로 매핑
CAT_ALIAS = {
    "무력충돌": "분쟁", "군사": "분쟁", "안보": "분쟁", "전쟁": "분쟁", "재난": "사회",
    "외교": "정치", "정치외교": "정치", "성명": "정치", "사건사고": "사회",
    "비즈니스": "경제", "산업": "경제", "금융": "경제", "시장": "경제",
    "과학": "기술", "테크": "기술", "it": "기술", "IT": "기술",
    "스포츠": "문화", "연예": "문화", "엔터": "문화", "예술": "문화",
}

def norm_cat(c):
    c = (c or "").strip()
    if c in CATS:
        return c
    return CAT_ALIAS.get(c, CAT_ALIAS.get(c.lower(), "사회"))

# ------------------------------------------------------------
# GDELT 합성 제목 탐지 — 실제 헤드라인을 못 긁은 사건은 fetch_news.py 가
#   "{행위자} · {사건유형}" (예: "British · 공격", "Poland · 요구") 형태로 합성한다.
#   내용이 빈약(행위자+CAMEO 코드뿐)해 지도·번역 모두에서 제외한다.
#   판정: 제목의 마지막 " · " 뒤 조각이 CAMEO 한글 라벨과 정확히 일치.
SYNTH_ACTS = {
    "공개 성명", "호소", "협력 의사 표명", "협의", "외교 협력",
    "물질적 협력", "원조 제공", "양보", "조사", "요구",
    "비난", "거부", "위협", "시위", "무력 시위",
    "관계 축소", "강압", "공격", "교전", "대량 폭력", "사건",
}
def is_synth_title(title):
    t = (title or "").strip()
    if " · " not in t:
        return False
    return t.rsplit(" · ", 1)[-1].strip() in SYNTH_ACTS

# ------------------------------------------------------------
# 제목 키워드 기반 주제 분류 (GDELT 의 CAMEO 분류를 보정)
#   CAMEO 는 경제/기술/문화 분류가 없어 정치에 몰림 → 실제 제목으로 재분류
# ------------------------------------------------------------
TOPIC_KW = {
    "분쟁": ["war", "attack", "missile", "airstrike", "shelling", "bomb", "troops",
            "military", "invasion", "clash", "ceasefire", "drone", "offensive", "warfare",
            "전쟁", "공격", "미사일", "공습", "폭격", "침공", "교전", "휴전", "포격", "병력"],
    "사회": ["earthquake", "quake", "flood", "wildfire", "typhoon", "hurricane", "storm",
            "accident", "crash", "collision", "derail", "protest", "rally", "outbreak",
            "disease", "virus", "epidemic", "crime", "murder", "kill", "killed", "dead",
            "death", "charged", "arrest", "shooting", "stabbing", "explosion", "disaster",
            "famine", "drought", "migrant", "refugee", "wreck", "casualt", "rescue",
            "survivor", "repatriat", "missing", "injured", "victim", "evacuat", "emergency",
            "지진", "홍수", "산불", "태풍", "사고", "추락", "충돌", "시위", "파업", "집회",
            "질병", "바이러스", "감염", "범죄", "살인", "총격", "화재", "폭발", "재난", "난민",
            "구조", "사망", "체포", "실종", "부상", "대피"],
    "경제": ["econom", "market", "stock", "shares", "shareholder", "trade", "tariff",
            "inflation", "gdp", "export", "import", "finance", "financ", "invest", "ipo",
            "currency", "budget", "revenue", "profit", "earnings", "wall street", "nasdaq",
            "oil price", "crypto", "bitcoin", "bank ", "supply chain", "factory",
            "manufactur", "loan", "dividend", "merger", "acquisition", "layoff",
            "unemployment", "wage", "fiscal", "quarterly", "billion", "fund ", "recession",
            "interest rate", "경제", "시장", "증시", "주가", "무역", "관세", "금리", "수출",
            "수입", "투자", "은행", "금융", "예산", "물가", "코스피", "환율", "공장",
            "대출", "합병", "해고", "실적", "분기", "보험", "매출"],
    "기술": ["artificial intelligence", " ai ", " ai,", "ai-", "chip", "semiconductor",
            "tech ", "software", "hardware", "robot", "quantum", "satellite", "spacecraft",
            "rocket", "nasa", "startup", "5g", "6g", "data center", "datacenter", "cloud ",
            "cyber", "algorithm", "app ", "smartphone", "digital", "internet", "platform",
            "battery", "electric vehicle", "ev ", "chipmaker", "gadget",
            "인공지능", "반도체", "기술", "우주", "로켓", "위성", "로봇", "스타트업",
            "소프트웨어", "사이버", "클라우드", "스마트폰", "알고리즘", "디지털", "전기차",
            "배터리", "플랫폼"],
    "문화": ["film", "movie", "cinema", "music", "concert", "album", "festival", "museum",
            "exhibition", "sport", "soccer", "football", "baseball", "basketball", "olympic",
            "world cup", "tournament", "actor", "singer", "drama", "celebrity", " art ",
            "영화", "음악", "드라마", "축제", "예술", "박물관", "전시", "스포츠", "축구",
            "야구", "농구", "올림픽", "월드컵", "경기", "배우", "가수", "콘서트", "앨범"],
    "정치": ["election", "president", "parliament", "congress", "senate", "government",
            "minister", "diplomat", "sanction", "summit", "treaty", "policy", "lawmaker",
            "대통령", "선거", "정부", "국회", "외교", "제재", "정상회담", "장관", "정책", "법안"],
}
# 동점 시 우선순위(사용자 관심: 사건성 우선)
TOPIC_PRIORITY = ["분쟁", "사회", "경제", "기술", "문화", "정치"]

def classify_topic(title):
    """제목에서 주제 카테고리 추정. 키워드 매칭 없으면 None."""
    low = (title or "").lower()
    scores = {}
    for cat, kws in TOPIC_KW.items():
        s = sum(1 for kw in kws if (kw if re.search(r"[가-힣]", kw) else kw) in low)
        if s:
            scores[cat] = s
    if not scores:
        return None
    best = max(scores.values())
    for cat in TOPIC_PRIORITY:           # 최고점 중 우선순위로 결정
        if scores.get(cat) == best:
            return cat
    return None

# ------------------------------------------------------------
# 도시 좌표표 — Grok 이 준 도시명을 신뢰 가능한 좌표로 스냅(동아시아 풍부)
#   키: 소문자/한글 도시명 → (lat, lng)
# ------------------------------------------------------------
def G(lat, lng): return (lat, lng)
GAZ = {
    # 대한민국
    "서울": G(37.5665,126.9780), "seoul": G(37.5665,126.9780),
    "부산": G(35.1796,129.0756), "busan": G(35.1796,129.0756),
    "인천": G(37.4563,126.7052), "incheon": G(37.4563,126.7052),
    "대구": G(35.8714,128.6014), "daegu": G(35.8714,128.6014),
    "대전": G(36.3504,127.3845), "daejeon": G(36.3504,127.3845),
    "광주": G(35.1595,126.8526), "gwangju": G(35.1595,126.8526),
    "울산": G(35.5384,129.3114), "수원": G(37.2636,127.0286),
    "제주": G(33.4996,126.5312), "jeju": G(33.4996,126.5312),
    "세종": G(36.4801,127.2890), "성남": G(37.4200,127.1267),
    "판문점": G(37.9558,126.6770), "panmunjom": G(37.9558,126.6770),
    # 일본
    "도쿄": G(35.6762,139.6503), "tokyo": G(35.6762,139.6503),
    "오사카": G(34.6937,135.5023), "osaka": G(34.6937,135.5023),
    "교토": G(35.0116,135.7681), "kyoto": G(35.0116,135.7681),
    "요코하마": G(35.4437,139.6380), "나고야": G(35.1815,136.9066),
    "삿포로": G(43.0618,141.3545), "sapporo": G(43.0618,141.3545),
    "후쿠오카": G(33.5904,130.4017), "fukuoka": G(33.5904,130.4017),
    "오키나와": G(26.2124,127.6809), "okinawa": G(26.2124,127.6809),
    # 중국
    "베이징": G(39.9042,116.4074), "beijing": G(39.9042,116.4074), "북경": G(39.9042,116.4074),
    "상하이": G(31.2304,121.4737), "shanghai": G(31.2304,121.4737), "상해": G(31.2304,121.4737),
    "광저우": G(23.1291,113.2644), "guangzhou": G(23.1291,113.2644),
    "선전": G(22.5431,114.0579), "shenzhen": G(22.5431,114.0579),
    "청두": G(30.5728,104.0668), "chengdu": G(30.5728,104.0668),
    "우한": G(30.5928,114.3055), "wuhan": G(30.5928,114.3055),
    "시안": G(34.3416,108.9398), "충칭": G(29.4316,106.9123),
    "홍콩": G(22.3193,114.1694), "hong kong": G(22.3193,114.1694),
    "마카오": G(22.1987,113.5439), "macau": G(22.1987,113.5439),
    # 대만/몽골/기타 동아시아
    "타이베이": G(25.0330,121.5654), "taipei": G(25.0330,121.5654), "타이페이": G(25.0330,121.5654),
    "가오슝": G(22.6273,120.3014), "kaohsiung": G(22.6273,120.3014),
    "울란바토르": G(47.8864,106.9057), "ulaanbaatar": G(47.8864,106.9057),
    "평양": G(39.0392,125.7625), "pyongyang": G(39.0392,125.7625),
    # 동남/남아시아
    "싱가포르": G(1.3521,103.8198), "singapore": G(1.3521,103.8198),
    "방콕": G(13.7563,100.5018), "bangkok": G(13.7563,100.5018),
    "하노이": G(21.0278,105.8342), "hanoi": G(21.0278,105.8342),
    "호치민": G(10.8231,106.6297), "자카르타": G(-6.2088,106.8456), "jakarta": G(-6.2088,106.8456),
    "마닐라": G(14.5995,120.9842), "manila": G(14.5995,120.9842),
    "뉴델리": G(28.6139,77.2090), "new delhi": G(28.6139,77.2090), "델리": G(28.6139,77.2090),
    "뭄바이": G(19.0760,72.8777), "mumbai": G(19.0760,72.8777),
    # 세계 주요
    "워싱턴": G(38.9072,-77.0369), "washington": G(38.9072,-77.0369),
    "뉴욕": G(40.7128,-74.0060), "new york": G(40.7128,-74.0060),
    "로스앤젤레스": G(34.0522,-118.2437), "los angeles": G(34.0522,-118.2437),
    "런던": G(51.5074,-0.1278), "london": G(51.5074,-0.1278),
    "파리": G(48.8566,2.3522), "paris": G(48.8566,2.3522),
    "베를린": G(52.5200,13.4050), "berlin": G(52.5200,13.4050),
    "모스크바": G(55.7558,37.6173), "moscow": G(55.7558,37.6173),
    "키이우": G(50.4501,30.5234), "kyiv": G(50.4501,30.5234),
    "두바이": G(25.2048,55.2708), "dubai": G(25.2048,55.2708),
    "테헤란": G(35.6892,51.3890), "tehran": G(35.6892,51.3890),
    "가자": G(31.5,34.47), "gaza": G(31.5,34.47),
    "텔아비브": G(32.0853,34.7818), "예루살렘": G(31.7683,35.2137), "jerusalem": G(31.7683,35.2137),
    "카이로": G(30.0444,31.2357), "시드니": G(-33.8688,151.2093), "sydney": G(-33.8688,151.2093),
}

def geocode(city, fallback_lat=None, fallback_lng=None):
    """도시명을 좌표표에서 찾고, 없으면 Grok 이 준 좌표 사용"""
    key = (city or "").strip().lower()
    if key in GAZ:
        return GAZ[key]
    if (city or "").strip() in GAZ:
        return GAZ[city.strip()]
    if isinstance(fallback_lat, (int, float)) and isinstance(fallback_lng, (int, float)):
        return (float(fallback_lat), float(fallback_lng))
    return None


def load_json(path):
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            print(f"  ⚠ {path.name} JSON 파싱 실패 — 무시")
    return []


def grok_importance(it):
    """Grok 항목의 중요도(0~10). Grok이 매긴 importance/relevance 를 우선 쓰고,
       없으면 '큐레이션을 통과했다'는 사실 자체를 신호로 보아 기본값 6.
       (Grok 항목은 매체수(num)·번역단계 relevance 가 없어 그냥 두면 imp=0 이 됨)"""
    v = it.get("importance", it.get("relevance"))
    try:
        return max(0, min(10, int(v)))
    except (TypeError, ValueError):
        return 6


def normalize_grok(items, src="grok"):
    """Grok 출력 항목을 표준 형식으로 변환 + 좌표 보정.
    src="grok-tech"(작업 F)면 theme(기업·테크 섹터)을 보존해 프론트 테크 칩에 합류."""
    out = []
    for it in items:
        title = (it.get("title") or "").strip()
        if not title:
            continue
        city = (it.get("city") or "").strip()
        country = (it.get("country") or "").strip()
        coord = geocode(city, it.get("lat"), it.get("lng"))
        if not coord:
            # 도시도 좌표도 없으면 지도에 못 올림
            continue
        lat, lng = coord
        url = (it.get("url") or "").strip()
        base = url or (title + city)
        date = (it.get("date") or "").strip()
        if not re.match(r"\d{4}-\d{2}-\d{2}", date):
            date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        item = {
            "id": ("gt" if src == "grok-tech" else "g") + hashlib.md5(base.encode()).hexdigest()[:11],
            "title": title,
            "summary": (it.get("summary") or "").strip(),
            "category": norm_cat(it.get("category")),
            "city": city or country,
            "country": country or city,
            "lat": round(lat, 4), "lng": round(lng, 4),
            "date": date[:10],
            "url": url,
            "relevance": grok_importance(it),   # 종합 브리핑 랭킹용(0 고정 탈출)
            "src": src,
        }
        th = (it.get("theme") or "").strip()    # 작업 F: 기업·테크 섹터(프론트 칩 드릴다운용)
        if th:
            item["theme"] = th
        source = (it.get("source") or "").strip()  # 작업 F: 출처 매체명(Electrek·DCD 등)
        if source:
            item["source"] = source
        out.append(item)
    return out


def load_breaking_press():
    """속보 트랙(breaking-store/archive)에서 '정식 기사'(srcType=press, 국내언론 RSS)만
       지도·디제스트 스키마로 이관. 텔레그램(social)은 미확인 정보라 여기 태우지 않음 —
       ④승격 매칭(정식보도 확인)으로만 간접 진입시킨다.
       반환: (좌표 있음 → 지도 후보, 좌표 없음 → 디제스트 후보)"""
    raw = load_json(BREAKING_STORE_PATH) + load_json(BREAKING_ARCHIVE_PATH)
    KST = timezone(timedelta(hours=9))
    map_items, dig_items = [], []
    for it in raw:
        if not isinstance(it, dict) or it.get("srcType") != "press" or not it.get("title"):
            continue
        try:
            kst = datetime.fromisoformat(it["ts"].replace("Z", "+00:00")).astimezone(KST)
        except (ValueError, KeyError, TypeError):
            continue
        rel = it.get("importance")
        rel = rel if isinstance(rel, int) else 6   # importance 도입 전 항목 기본치
        item = {
            "id": "pr" + hashlib.md5((it.get("url") or it["title"]).encode()).hexdigest()[:11],
            "title": it["title"].strip(),
            "summary": (it.get("summary") or "").strip(),
            "category": norm_cat(it.get("category")),
            "city": (it.get("city") or "").strip(),
            "country": (it.get("country") or "").strip() or (it.get("city") or "").strip(),
            "date": kst.strftime("%Y-%m-%d"),
            "datetime": kst.strftime("%Y-%m-%d %H:%M"),
            "url": it.get("url") or "",
            "relevance": rel,
            "src": "press",
            "source": it.get("channel") or "",
        }
        lat, lng = it.get("lat"), it.get("lng")
        if isinstance(lat, (int, float)) and isinstance(lng, (int, float)):
            item["lat"], item["lng"] = round(lat, 4), round(lng, 4)
            map_items.append(item)
        else:
            item["num"] = 0
            dig_items.append(item)
    return map_items, dig_items


# ------------------------------------------------------------
# 디제스트 순위변동(▲▼/NEW) — '직전 사이클' 순위 스냅샷
#   [버그 배경] merge_news.py 는 한 사이클에 여러 번 실행된다(fetch 1회 + 번역 배치마다).
#   예전엔 직전 순위를 news-digest.js 에서 읽었는데, 사이클 내 2번째+ merge 는 '방금 이
#   사이클이 쓴' 디제스트를 prev 로 읽어 prevRank==rank 가 되어 변동표시가 전부 지워졌다.
#   → 직전 순위를 사이클당 1회만 digest-prev-ranks.json 에 고정하고, 모든 merge 는 이
#     스냅샷만 prev 로 읽는다. merge 는 이 파일을 절대 쓰지 않는다(auto_update.sh 가 사이클
#     시작 시 `merge_news.py --snapshot-prev` 로 1회 갱신).
# ------------------------------------------------------------
def _read_digest_ranks_from_js():
    """현재 news-digest.js 에서 id→순위(1-based) 맵을 읽는다(없으면 {})."""
    try:
        txt = DIGEST_OUTPUT.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return {}
    m = re.search(r"const\s+NEWS_DIGEST\s*=\s*(\[.*?\]);", txt, re.S)
    if not m:
        return {}
    try:
        arr = json.loads(m.group(1))
    except (ValueError, TypeError):
        return {}
    return {it.get("id"): i + 1 for i, it in enumerate(arr)
            if isinstance(it, dict) and it.get("id")}


def snapshot_prev_ranks():
    """사이클 시작 시 1회 호출 — 현재(=직전 사이클 최종) news-digest.js 순위를
       digest-prev-ranks.json 에 고정한다. 사이클 내 반복 merge 는 이 파일을 건드리지
       않으므로 prevRank(직전 사이클 순위)가 덮이지 않는다."""
    ranks = _read_digest_ranks_from_js()
    PREV_RANKS_PATH.write_text(json.dumps(
        {"cycle": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
         "ranks": ranks}, ensure_ascii=False), encoding="utf-8")
    print(f"✔ 디제스트 prev 순위 스냅샷: {len(ranks)}건 → {PREV_RANKS_PATH.name}")
    return ranks


def build_output():
    """news-store.json(GDELT) + grok-news.json(Grok) → news-data.js"""
    gdelt = load_json(STORE_PATH)
    # GDELT 항목을 실제 제목으로 재분류(CAMEO 정치 몰림 보정)
    for it in gdelt:
        t = classify_topic(it.get("title"))
        if t:
            it["category"] = t

    grok_raw = load_json(GROK_PATH)
    grok = normalize_grok(grok_raw)

    # 작업 F: Grok 글로벌 테크 딜 실검색(전문·1차·다국어 소스) → 별도 파일에서 합류.
    #   grok-news.json(작업 A)을 매시간 덮어쓰므로 충돌 피하려 파일 분리. src=grok-tech.
    grok_tech = normalize_grok(load_json(GROK_TECH_PATH), src="grok-tech")

    # GDELT DOC 주제(기업·테크) 뉴스 — 제목 기반 재분류는 하지 않음(테마 카테고리 유지)
    topics = [it for it in load_json(TOPIC_STORE_PATH) if isinstance(it, dict) and it.get("id")]

    # 병합 + 중복 제거(id 기준; Grok 우선)
    by_id = {}
    for it in gdelt:
        by_id[it.get("id")] = it
    for it in topics:                     # 주제 뉴스 합류(지도·목록·종합 후보)
        by_id[it["id"]] = it
    for it in grok:                       # Grok 이 같은 id 면 덮어씀(정제본 우선)
        by_id[it["id"]] = it
    for it in grok_tech:                  # 작업 F: 글로벌 테크 딜(src=grok-tech, theme 보존)
        by_id[it["id"]] = it
    press_map, press_dig = load_breaking_press()   # 속보 트랙 정식기사(RSS) 이관
    for it in press_map:                  # 좌표 있는 정식기사 → 지도 합류(src=press)
        by_id[it["id"]] = it

    # 보관 기간 정리
    today = datetime.now(timezone.utc).date()
    merged = []
    for it in by_id.values():
        try:
            d = datetime.strptime(it["date"], "%Y-%m-%d").date()
        except (ValueError, KeyError, TypeError):
            continue
        if (today - d).days <= RETENTION_DAYS:
            merged.append(it)

    # 재게재 중복 제거: 같은 기사를 여러 매체가 도메인만 달리해 실은 것(URL 경로가 동일)을
    #   하나로 합침(GDELT Events·DOC 등 소스 무관). 중요도(relevance·num) 높은 쪽을 남긴다.
    def _url_path(u):
        m = re.search(r"https?://[^/]+(/[^?#]*)", u or "")
        return (m.group(1).rstrip("/").lower() if m else (u or ""))

    def _weight(it):
        r = it.get("relevance"); r = r if isinstance(r, int) else 0
        has_theme = 1 if it.get("theme") else 0   # 동점이면 주제 라벨 있는 DOC본 우선
        n = it.get("num"); n = n if isinstance(n, int) else 0
        return (r, has_theme, n)

    by_path = {}
    for it in merged:
        p = _url_path(it.get("url"))
        if not p or len(p) < 8:
            by_path.setdefault(id(it), it)   # 경로 없으면 고유 취급(중복 안 침)
            continue
        cur = by_path.get(p)
        if cur is None or _weight(it) > _weight(cur):
            by_path[p] = it
    merged = list(by_path.values())

    # 번역 누적: 이번 Grok 출력(translations.json)을 영구 누적본에 병합 후 적용
    #   → 매 실행마다 일부만 번역해도 사라지지 않고 쌓임
    trans_store = {t["id"]: t for t in load_json(TRANS_STORE_PATH)
                   if isinstance(t, dict) and t.get("id")}
    for t in load_json(TRANS_PATH):                  # 이번 출력 병합(최신 우선)
        if isinstance(t, dict) and t.get("id"):
            trans_store[t["id"]] = t
    TRANS_STORE_PATH.write_text(                      # 누적본 저장(다음에도 유지)
        json.dumps(list(trans_store.values()), ensure_ascii=False, indent=2),
        encoding="utf-8")
    trans_map = trans_store
    n_trans = 0
    if trans_map:
        for it in merged:
            tr = trans_map.get(it.get("id"))
            if not tr:
                continue
            if tr.get("title"):
                it["title"] = tr["title"].strip()
                it["translated"] = True
                n_trans += 1
            if tr.get("summary"):
                it["summary"] = tr["summary"].strip()
            if tr.get("category"):        # Grok 이 번역하며 카테고리도 교정
                it["category"] = norm_cat(tr["category"])
            if tr.get("relevance") is not None:   # Grok 이 매긴 중요도(0~10)
                try:
                    it["relevance"] = int(tr["relevance"])
                except (ValueError, TypeError):
                    pass

    # 관련성 낮은 항목(가십·잡문) 제외 — Grok 이 점수 매긴 것만 대상
    before = len(merged)
    merged = [it for it in merged
              if not (isinstance(it.get("relevance"), int)
                      and it["relevance"] < RELEVANCE_MIN)]
    n_dropped = before - len(merged)

    # GDELT 합성 제목(예: "British · 공격") 제외 — 실제 헤드라인 없는 저품질 사건.
    #   지도·목록·번역 대기목록 모두에서 빠진다(번역 토큰 낭비 방지).
    before_synth = len(merged)
    merged = [it for it in merged if not is_synth_title(it.get("title"))]
    n_synth = before_synth - len(merged)

    items_sorted = sorted(merged, key=lambda x: x.get("date", ""))
    now = datetime.now(timezone.utc)
    stamp = now.strftime("%Y-%m-%d %H:%M UTC")
    iso = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    # 분할 로딩: 첫 화면은 최근 4일치(news-data.js, 오늘~3일 전 커버)만 받아
    #   초기 로딩(파싱)을 가볍게 하고, 그보다 긴 기간(최근 1주·전체)을 고르면
    #   그때 전체(news-archive.js)를 지연 로딩한다. (index.html needsArchive 와 동기화: >3일)
    recent_cutoff = (now - timedelta(days=3)).strftime("%Y-%m-%d")
    recent = [it for it in items_sorted if it.get("date", "") >= recent_cutoff]
    compact = dict(ensure_ascii=False, separators=(",", ":"))
    OUTPUT_PATH.write_text(
        f"/* 자동 생성 · {stamp} · GDELT(사건) + Grok(조사) 병합 — 최근 4일분\n"
        f"   직접 수정 금지. merge_news.py 가 덮어씁니다. 전체는 news-archive.js */\n"
        f"const NEWS_UPDATED = \"{iso}\";\n"
        f"const NEWS_DATA = {json.dumps(recent, **compact)};\n",
        encoding="utf-8",
    )
    (HERE / "news-archive.js").write_text(
        f"/* 자동 생성 · {stamp} · 전체 기간({RETENTION_DAYS}일) 뉴스 — 지연 로딩용 */\n"
        f"const NEWS_ARCHIVE = {json.dumps(items_sorted, **compact)};\n",
        encoding="utf-8",
    )

    # ── 종합 브리핑(중요도 랭킹) → news-digest.js ──
    #   '오늘의 세계 주요 뉴스'를 지도 영역과 무관하게 보도량(매체 수) 순으로.
    #   좌표 없는 실속 뉴스(digest-store)도 같은 번역 누적본을 적용해 합류시킨다.
    digest_raw = load_json(DIGEST_STORE_PATH)
    dig_items = []
    for it in digest_raw:
        try:
            dd = datetime.strptime(it.get("date", ""), "%Y-%m-%d").date()
        except (ValueError, TypeError):
            continue
        if (today - dd).days > RETENTION_DAYS:
            continue
        t = classify_topic(it.get("title"))       # 제목 기반 재분류(정치 몰림 보정)
        if t:
            it["category"] = t
        tr = trans_map.get(it.get("id"))          # 지도와 동일한 번역 누적본 적용
        if tr:
            if tr.get("title"):
                it["title"] = tr["title"].strip()
                it["translated"] = True
            if tr.get("category"):
                it["category"] = norm_cat(tr["category"])
        if is_synth_title(it.get("title")):
            continue
        dig_items.append(it)
    dig_items.extend(press_dig)   # 좌표 없는 정식기사(RSS) → 디제스트 후보 합류(이미 한국어)

    # 국가별 보도량 기준선(중앙값) — '그 나라 평소 대비 얼마나 큰 사건인가'(상대 중요도)용.
    #   언론사 많은 나라(미국 등)는 절대 보도량이 구조적으로 높아 상위를 독식 → 그 나라
    #   평소 수준으로 나눠 보정. 표본 5건 미만 나라는 전역 중앙값으로 폴백.
    _nums = [it["num"] for it in merged if isinstance(it.get("num"), int) and it["num"] > 0]
    _gmed = statistics.median(_nums) if _nums else 10.0
    _cc_nums = {}
    for it in merged:
        n = it.get("num")
        if isinstance(n, int) and n > 0:
            _cc_nums.setdefault(it.get("country") or "?", []).append(n)
    _cc_base = {c: statistics.median(v) for c, v in _cc_nums.items() if len(v) >= 5}

    def _baseline(cc):
        return max(3.0, _cc_base.get(cc, _gmed))

    def _imp(it):
        """중요도 = 보도량(절대 log + 국가상대) + 편집중요도 + 최신성.
           - 절대(va=log2 num): 글로벌 초대형 사건도 반영하되 로그로 압축.
           - 국가상대(vr=log2(num/그 나라 중앙값)): 미디어 많은 나라 편향 완화 —
             '그 나라 평소의 몇 배냐'로 소규모 미디어국의 대형사건도 공정히 부상.
           - relevance(Grok 편집 중요도): 국가·매체수 무관 신호라 가산.
           - 최신성: 오늘/어제 우대 → '오늘의 주요 뉴스'가 새 뉴스로 갱신.
           (예전엔 num + relevance×10 → 누적 보도량 큰 옛 기사·미디어 대국이 상위 고정)"""
        n = it.get("num")
        n = n if isinstance(n, int) and n > 0 else 0
        r = it.get("relevance")
        r = r if isinstance(r, int) else 0
        # Grok 등 매체수(num) 없는 항목: num=0 이면 보도량 항이 0 이 되어 예약석에만
        #   의존하게 됨 → relevance 를 '보도량 등가'로 환산해 오픈 경쟁에 참여시킴.
        #   (Grok 큐레이션 통과 importance 8 ≈ 상당히 보도된 사건으로 취급)
        n_eff = n if n > 0 else (r * r if r > 0 else 0)
        try:
            iage = (brief_max_d - datetime.strptime(it.get("date", ""), "%Y-%m-%d").date()).days
        except (ValueError, TypeError):
            iage = 3
        # 최신성: 당일(최신일)을 우선(보도량 누적 편향 보정 + '오늘의 뉴스' 신선도).
        #   어제는 낮추되 0으로 죽이지 않는다 — 세계뉴스라 ①UTC-어제 밤 = KST-오늘 새벽 뉴스가
        #   이 버킷에 섞이고(시차) ②다일에 걸친 대형 사건도 있기 때문.
        #   당일↔어제 격차는 3.5(=5.0−1.5)로, relevance 항(≤10)이 상쇄 가능하게 둔다:
        #   비슷한 중요도면 today 승, 그러나 어제 대형사건(r 높음)은 relevance 차이로 생존
        #   (예: 어제 r9 코스피 폭락 vs 오늘 r5 평범뉴스 → relevance +4 > 격차 3.5 → 어제가 위).
        recency = {0: 5.0, 1: 1.5}.get(iage, 0.0)
        va = math.log2(1 + n_eff)
        # 국가상대 항은 상한 2.5(기여 최대 1.6×2.5=+4.0 ≈ '평소의 5.7배 보도'까지 인정).
        #   상한 없으면 기준선 낮은 소국의 글로벌 사건(예: 코스타리카 CDC 경보 350매체)이
        #   전쟁급 뉴스를 제치고 1위로 점프 — 소국 '노출 보장'은 유지하되 왕관 독식만 방지.
        vr = min(2.5, math.log2(1 + n_eff / _baseline(it.get("country") or "?")))
        return 0.6 * va + 1.6 * vr + 1.0 * r + recency
    BRIEF_MAX, BRIEF_PER_CC, BRIEF_PER_CAT = 100, 14, 28
    GROK_QUOTA, GROK_PER_CAT = 14, 5   # 동아시아(Grok) 최소 보장 자리
    # 최근 2일(데이터상 최신일 + 전날)만 — 지도 '최신' 필터와 동일, 오늘 뉴스 우선.
    pool_all = merged + dig_items
    _dd = [it.get("date", "") for it in pool_all if it.get("date")]
    brief_max = max(_dd) if _dd else ""
    brief_max_d = datetime.strptime(brief_max, "%Y-%m-%d").date() if brief_max else today
    brief_cut = (brief_max_d - timedelta(days=1)).strftime("%Y-%m-%d") if brief_max else ""
    pool = [it for it in pool_all if it.get("date", "") >= brief_cut]
    seen, ranked = set(), []
    for it in sorted(pool, key=_imp, reverse=True):
        i = it.get("id")
        if not i or i in seen:
            continue
        seen.add(i)
        ranked.append(it)

    # 동아시아(Grok) 최소 보장: Grok 항목은 매체수(num)가 없어 imp 가 낮게 나와
    #   전 세계 보도량 상위(전쟁 등)에 밀려 0건이 됨. 한국 사용자용이므로 자리를
    #   예약해 확보한다(카테고리 쏠림은 GROK_PER_CAT 로 완화). [fetch 의 동아시아 floor 와 같은 취지]
    grok_pick, gcat = [], {}
    for it in ranked:                       # ranked 는 imp 정렬 — Grok끼리도 중요도순
        if it.get("src") != "grok":
            continue
        cat = it.get("category") or "?"
        if gcat.get(cat, 0) >= GROK_PER_CAT:
            continue
        gcat[cat] = gcat.get(cat, 0) + 1
        grok_pick.append(it)
        if len(grok_pick) >= GROK_QUOTA:
            break

    # 선정: Grok 보장분을 먼저 넣어 캡에 반영한 뒤, 나머지를 전체 상위로 채운다.
    chosen, chosen_ids, cc_cnt, cat_cnt = [], set(), {}, {}
    def _take(it):
        chosen.append(it)
        chosen_ids.add(it.get("id"))
        cc_cnt[it.get("country") or "?"] = cc_cnt.get(it.get("country") or "?", 0) + 1
        cat_cnt[it.get("category") or "?"] = cat_cnt.get(it.get("category") or "?", 0) + 1
    for it in grok_pick:
        _take(it)
    for it in ranked:                       # 나머지 슬롯: 국가·카테고리 캡 적용 상위
        if len(chosen) >= BRIEF_MAX:
            break
        if it.get("id") in chosen_ids:
            continue
        c = it.get("country") or "?"
        cat = it.get("category") or "?"
        if cc_cnt.get(c, 0) >= BRIEF_PER_CC or cat_cnt.get(cat, 0) >= BRIEF_PER_CAT:
            continue
        _take(it)
    chosen.sort(key=_imp, reverse=True)     # 표시는 중요도 내림차순

    # 순위 변동/신규(NEW) 표시용 '직전 사이클' 순위 로드.
    #   사이클당 1회 고정된 스냅샷(digest-prev-ranks.json)만 prev 로 사용한다 —
    #   사이클 내 merge 반복 실행이 prevRank 를 덮어쓰던 버그를 막는다(위 snapshot_prev_ranks 참고).
    #   merge 는 이 스냅샷을 절대 쓰지 않는다(갱신은 auto_update.sh 가 사이클 시작 시 1회).
    def _load_prev_digest_ranks():
        if PREV_RANKS_PATH.exists():
            try:
                data = json.loads(PREV_RANKS_PATH.read_text(encoding="utf-8"))
                ranks = data.get("ranks") if isinstance(data, dict) else None
                if isinstance(ranks, dict):
                    return {k: v for k, v in ranks.items() if isinstance(v, int)}
            except (ValueError, TypeError, OSError):
                pass
        # 스냅샷이 아직 없을 때(최초 실행 등)만 레거시 폴백: 현재 디제스트 파일에서 읽음.
        return _read_digest_ranks_from_js()
    prev_ranks = _load_prev_digest_ranks()

    brief = [{
        "id": it.get("id"), "title": it.get("title", ""),
        "summary": it.get("summary", ""), "category": it.get("category", ""),
        "city": it.get("city", ""), "country": it.get("country", ""),
        "lat": it.get("lat"), "lng": it.get("lng"),
        "date": it.get("date", ""), "url": it.get("url", ""),
        "datetime": it.get("datetime"),   # 수집 시각(UTC ISO) — 프론트서 KST 날짜+시간
        "num": it.get("num") if isinstance(it.get("num"), int) else 0,
        "relevance": it.get("relevance") if isinstance(it.get("relevance"), int) else None,
        "src": it.get("src", ""), "theme": it.get("theme"),   # 기업·테크 주제 드릴다운용
        "rank": i + 1,                           # 이번 회차 종합 순위(1-based)
        "prevRank": prev_ranks.get(it.get("id")),  # 직전 회차 순위(없으면 None=신규)
    } for i, it in enumerate(chosen)]
    DIGEST_OUTPUT.write_text(
        f"/* 자동 생성 · {stamp} · 오늘의 세계 주요 뉴스(중요도 랭킹) — 직접 수정 금지 */\n"
        f"const NEWS_DIGEST_UPDATED = \"{iso}\";\n"
        f"const NEWS_DIGEST = {json.dumps(brief, **compact)};\n",
        encoding="utf-8",
    )

    # 번역 필요 목록 자동 추출 → Grok/Claude 가 이 파일을 번역
    #   지도(items_sorted) + 종합(dig_items) 미번역분을 함께 대기열에 올린다.
    #   한글 글자 유무만 보면, 한글 접두어("인공지능 관련 뉴스:")만 붙고 본문이 영문인
    #   가짜 번역을 놓친다 → 한글을 뺀 뒤 영단어 4개 이상 남으면 '미번역'으로 재큐.
    def _needs_translation(t):
        t = t or ""
        if not re.search(r"[가-힣]", t):
            return True   # 한글 전무 = 미번역
        # '[경제]' 같은 대괄호 태그나 '…뉴스:' 라벨 접두어 뒤가 통째로 영문이면
        #   라벨만 붙은 가짜 번역 → 재큐. (회사명 섞인 정상 제목은 오탐 안 함)
        m = re.match(r"^\s*(?:\[[^\]]+\]|[가-힣·\s]{2,15}뉴스:)\s*(.+)$", t)
        if m:
            rest = m.group(1)
            if not re.search(r"[가-힣]", rest) and len(re.findall(r"[A-Za-z]{2,}", rest)) >= 3:
                return True
        return False
    to_translate = [{"id": it["id"], "title": it["title"],
                     "category_guess": it.get("category", "")}
                    for it in (items_sorted + dig_items)
                    if _needs_translation(it.get("title", ""))]
    (HERE / "to_translate.json").write_text(
        json.dumps(to_translate, ensure_ascii=False, indent=2), encoding="utf-8")

    from collections import Counter
    n_grok = sum(1 for x in merged if x.get("src") == "grok")
    n_gdelt = len(merged) - n_grok
    print(f"✔ news-data.js 빌드: 총 {len(merged)}건 "
          f"(GDELT {n_gdelt} + Grok {n_grok}, 번역 {n_trans}건, 가십 제외 {n_dropped}건, "
          f"합성제목 제외 {n_synth}건)")
    print(f"  카테고리: {dict(Counter(x['category'] for x in merged))}")
    print(f"  번역 대기(한글 없는 제목): {len(to_translate)}건 → to_translate.json")
    print(f"  종합 브리핑(중요도 랭킹): {len(brief)}건 → news-digest.js "
          f"(좌표없음 실속 {len(dig_items)}건 포함 후보)")
    return merged


if __name__ == "__main__":
    import sys
    if "--snapshot-prev" in sys.argv:
        # 사이클 시작 시 1회: 직전 사이클 최종 디제스트 순위를 스냅샷(빌드는 안 함)
        snapshot_prev_ranks()
    else:
        build_output()
