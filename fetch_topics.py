#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_topics.py — GDELT DOC 2.0 API 로 '주제(테마)' 기반 기업·테크 뉴스 수집.

GDELT Events(지정학 사건)엔 안 잡히는 기업/제품/기술 뉴스(테슬라 자율주행, SpaceX 발사,
AI·데이터센터·전력(원전), 반도체·전기차 등)를 키워드 검색으로 받아 topic-store.json 에 누적.
merge_news.py 가 이 스토어를 지도 뉴스에 합류시킨다.

핵심 설계
  - 추적 단위는 '회사'가 아니라 '주제' — 각 주제 = 회사+기술용어 OR 쿼리 하나.
    한 회사가 여러 주제에 걸치면 각 주제에서 자연히 잡히고 URL 로 중복 제거.
  - DOC 응답엔 사건 위치가 없어(출처국만) → 제목에서 회사(엔티티)를 찾아 그 본사 좌표에 배치.
    못 찾으면 주제 기본 좌표(대개 실리콘밸리/케이프커내버럴).
  - seendate(YYYYMMDDTHHMMSSZ, UTC 15분)로 date + datetime(시각) 저장.
  - GDELT DOC 레이트리밋: 5초에 1회 → 주제 사이 SLEEP 넉넉히(기본 15초), 429 시 백오프.
    (반드시 로컬 파이프라인에서 호출 — 클라우드 공유 IP 는 429 잦음)
"""
import json
import time
import hashlib
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
STORE_PATH = HERE / "topic-store.json"
RETENTION_DAYS = 21
DOC_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
SLEEP_BETWEEN = 15          # 주제 간 대기(초) — 5초 제한 여유 있게
MAXRECORDS = 75
TIMESPAN = "3d"

# ── 주제(테마) 정의: 이름 → (검색쿼리, 카테고리) ──
#   쿼리는 GDELT DOC 문법: 공백=AND, (a OR b)=OR그룹, "구문", sourcelang:english
THEMES = {
    "자율주행·로보틱스": (
        '(robotaxi OR "self-driving" OR "autonomous driving" OR "full self-driving" '
        'OR humanoid OR Optimus OR Waymo OR "Boston Dynamics" OR "Figure AI") sourcelang:english',
        "기술"),
    "AI·연산·전력": (
        '("artificial intelligence" OR OpenAI OR "xAI" OR Anthropic OR "large language model" '
        'OR "AI data center" OR "AI datacenter" OR "AI chip" OR "nuclear power" OR "small modular reactor" '
        'OR SMR OR "data center power") sourcelang:english',
        "기술"),
    "우주·발사": (
        '(SpaceX OR Starship OR Starlink OR "rocket launch" OR "satellite launch" '
        'OR "Blue Origin" OR "space launch") sourcelang:english',
        "기술"),
    "반도체·전기차·배터리": (
        '(semiconductor OR TSMC OR "chip export" OR "EV battery" OR "electric vehicle" '
        'OR "solid-state battery" OR ASML OR "battery plant") sourcelang:english',
        "경제"),
    "양자컴퓨터": (
        '("quantum computing" OR "quantum computer" OR qubit OR "quantum supremacy" '
        'OR "quantum processor" OR IonQ OR Rigetti OR "D-Wave" OR PsiQuantum) sourcelang:english',
        "기술"),
}

# ── 엔티티(회사) → 본사 좌표·표기: 제목에 등장하면 그 위치에 배치 ──
ENTITY_COORDS = {
    "tesla": (30.2672, -97.7431, "오스틴", "미국"),
    "spacex": (25.997, -97.157, "스타베이스", "미국"),
    "starship": (25.997, -97.157, "스타베이스", "미국"),
    "starlink": (25.997, -97.157, "스타베이스", "미국"),
    "xai": (37.4419, -122.1430, "팰로앨토", "미국"),
    "openai": (37.7749, -122.4194, "샌프란시스코", "미국"),
    "anthropic": (37.7749, -122.4194, "샌프란시스코", "미국"),
    "nvidia": (37.3541, -121.9552, "산타클라라", "미국"),
    "waymo": (37.3861, -122.0839, "마운틴뷰", "미국"),
    "boston dynamics": (42.3765, -71.2356, "월섬", "미국"),
    "figure": (37.3688, -122.0363, "서니베일", "미국"),
    "tsmc": (24.7814, 120.9948, "신주", "대만"),
    "samsung": (37.2636, 127.0286, "수원", "대한민국"),
    "sk hynix": (37.2410, 127.4890, "이천", "대한민국"),
    "intel": (37.3875, -121.9636, "산타클라라", "미국"),
    "microsoft": (47.6740, -122.1215, "레드먼드", "미국"),
    "amazon": (47.6062, -122.3321, "시애틀", "미국"),
    "google": (37.4220, -122.0841, "마운틴뷰", "미국"),
    "apple": (37.3349, -122.0090, "쿠퍼티노", "미국"),
    "meta": (37.4847, -122.1477, "멘로파크", "미국"),
    "nasa": (28.3922, -80.6077, "케이프커내버럴", "미국"),
    "blue origin": (47.3809, -122.2348, "켄트", "미국"),
    "byd": (22.5431, 114.0579, "선전", "중국"),
    "catl": (26.6617, 119.5478, "닝더", "중국"),
    "asml": (51.4200, 5.4000, "펠트호번", "네덜란드"),
    "rivian": (33.6846, -117.8265, "어바인", "미국"),
    "ionq": (38.9897, -76.9378, "칼리지파크", "미국"),
    "rigetti": (37.8716, -122.2727, "버클리", "미국"),
    "d-wave": (49.2488, -122.9805, "버나비", "캐나다"),
    "psiquantum": (37.4419, -122.1430, "팰로앨토", "미국"),
    "ibm": (41.2098, -73.7998, "요크타운하이츠", "미국"),
}
# 주제 기본 좌표(엔티티 못 찾을 때)
THEME_DEFAULT = {
    "자율주행·로보틱스": (37.5, -122.2, "실리콘밸리", "미국"),
    "AI·연산·전력": (37.7749, -122.4194, "샌프란시스코", "미국"),
    "우주·발사": (28.3922, -80.6077, "케이프커내버럴", "미국"),
    "반도체·전기차·배터리": (37.3541, -121.9552, "산타클라라", "미국"),
    "양자컴퓨터": (38.9897, -76.9378, "칼리지파크", "미국"),
}


# 제목 내용으로 theme 재판정 — '어느 쿼리가 찾았나'만 믿으면 여러 쿼리에 걸린 기사가
#   엉뚱한 주제로 태깅됨(예: AI 기사가 양자 쿼리에도 걸려 '양자컴퓨터'로). 제목 키워드로 보정.
THEME_KW = {
    "자율주행·로보틱스": ["robotaxi", "self-driving", "self driving", "autonomous driving", "autonomous vehicle",
                    "humanoid", "optimus", "waymo", "boston dynamics", "figure ai", " robot"],
    "우주·발사": ["spacex", "starship", "starlink", "rocket", "satellite", "blue origin", "space launch",
              " nasa ", "orbital", "spaceport"],
    "양자컴퓨터": ["quantum comput", "quantum processor", "qubit", "quantum supremacy", "quantum entangle",
              "ionq", "rigetti", "d-wave", "psiquantum"],
    "반도체·전기차·배터리": ["semiconductor", "tsmc", "asml", "chip export", "chipmaker", " chip ", "foundry",
                    "ev battery", "electric vehicle", "solid-state battery", "battery plant", "lithium"],
    "AI·연산·전력": ["artificial intelligence", " ai ", " ai,", " ai-", "openai", "xai", "anthropic",
                "large language model", "llm", "data center", "datacenter", "gpu", "chatgpt",
                "machine learning", "nuclear power", "small modular reactor", " smr "],
}
CAT_OF_THEME = {t: c for t, (q, c) in THEMES.items()}


def derive_theme(title, fallback):
    """제목 키워드로 가장 잘 맞는 theme 선택.
    제목에 어느 주제 키워드도 없으면 None — DOC이 본문만 보고 물어온 노이즈(제목은
    금융·정치인데 본문에 'quantum'이 한 번 스친 류)라 제외 대상."""
    low = " " + (title or "").lower() + " "
    best, score = None, 0
    for th, kws in THEME_KW.items():
        s = sum(1 for kw in kws if kw in low)
        if s > score:
            best, score = th, s
    return best   # 매칭 0이면 None


def doc_query(query, tries=3):
    """DOC API 호출(429 백오프). 실패 시 [] 반환."""
    u = DOC_URL + "?" + urllib.parse.urlencode({
        "query": query, "mode": "ArtList", "format": "json",
        "maxrecords": MAXRECORDS, "sort": "datedesc", "timespan": TIMESPAN})
    for attempt in range(tries):
        try:
            req = urllib.request.Request(u, headers={"User-Agent": "world-info-map/1.0 (news map research)"})
            with urllib.request.urlopen(req, timeout=40) as r:
                raw = r.read().decode("utf-8", "replace")
            if not raw.strip().startswith("{"):
                # 레이트리밋/에러 텍스트
                if "5 seconds" in raw or "Too Many" in raw:
                    time.sleep(20 * (attempt + 1))
                    continue
                return []
            return (json.loads(raw).get("articles") or [])
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(20 * (attempt + 1))
                continue
            return []
        except Exception:
            return []
    return []


def seendate_iso(sd):
    """seendate(YYYYMMDDTHHMMSSZ) → (date_iso, datetime_iso)."""
    sd = (sd or "").replace("T", "").replace("Z", "")
    if len(sd) >= 14 and sd[:14].isdigit():
        try:
            dt = datetime.strptime(sd[:14], "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
            return dt.strftime("%Y-%m-%d"), dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            pass
    return datetime.now(timezone.utc).strftime("%Y-%m-%d"), None


# 투자 클릭베이트·저품질 소스 제외 — 넓은 키워드가 주식추천/블로그 스팸을 긁어오는 것 차단
import re as _re
SPAM_DOMAINS = {"fool.com", "investorplace.com", "marketbeat.com", "24_7wallst.com",
                "247wallst.com", "benzinga.com", "tipranks.com", "zacks.com"}
SPAM_TITLE = _re.compile(
    r"should you buy|best stock|better buy|stocks? to buy|\b10x\b|net worth|motley fool|"
    r"which .*better buy|\bETF\b|dividend|price target|could make you|millionaire|"
    r"buy before|piling into|\bvs\.?\s", _re.IGNORECASE)


def is_spam(title, domain):
    d = (domain or "").lower()
    if any(sd in d for sd in SPAM_DOMAINS):
        return True
    return bool(SPAM_TITLE.search(title or ""))


def geolocate(title, theme):
    """제목에서 회사(엔티티)를 찾아 본사 좌표. 없으면 주제 기본 좌표."""
    low = (title or "").lower()
    for ent, coord in ENTITY_COORDS.items():
        if ent in low:
            return coord, ent
    return THEME_DEFAULT.get(theme, (37.5, -122.2, "실리콘밸리", "미국")), None


def main():
    fresh = []
    for i, (theme, (query, cat)) in enumerate(THEMES.items()):
        if i:
            time.sleep(SLEEP_BETWEEN)
        arts = doc_query(query)
        n = 0
        for a in arts:
            title = (a.get("title") or "").strip()
            url = (a.get("url") or "").strip()
            if not title or not url:
                continue
            if is_spam(title, a.get("domain")):    # 투자 클릭베이트·스팸 제외
                continue
            eff_theme = derive_theme(title, theme)         # 제목 내용으로 theme 보정
            if eff_theme is None:                          # 제목에 주제 키워드 없음 = 본문만 스친 노이즈
                continue
            eff_cat = CAT_OF_THEME.get(eff_theme, cat)     # 보정된 theme의 카테고리
            (lat, lng, city, country), ent = geolocate(title, eff_theme)
            date_iso, dt_iso = seendate_iso(a.get("seendate"))
            item = {
                "id": "t" + hashlib.md5(url.encode()).hexdigest()[:11],
                "title": title,
                "summary": f"{eff_theme} · 출처 {a.get('domain', '')}",
                "category": eff_cat,
                "city": city, "country": country,
                "lat": round(lat, 4), "lng": round(lng, 4),
                "date": date_iso,
                "url": url,
                "theme": eff_theme,
                "src": "gdelt-doc",
            }
            if dt_iso:
                item["datetime"] = dt_iso
            fresh.append(item)
            n += 1
        print(f"■ {theme}: {n}건")

    # 누적 저장(중복 제거 id 우선 최신) + 보관기간 정리
    store = {}
    if STORE_PATH.exists():
        try:
            for it in json.loads(STORE_PATH.read_text(encoding="utf-8")):
                if isinstance(it, dict) and it.get("id"):
                    store[it["id"]] = it
        except Exception:
            store = {}
    for it in fresh:
        store[it["id"]] = it   # 최신 갱신
    # 같은 기사를 여러 매체가 재게재(다른 URL)한 중복을 제목 기준으로 제거(최신 우선)
    seen_title, deduped = set(), {}
    for it in sorted(store.values(), key=lambda z: z.get("date", ""), reverse=True):
        k = _re.sub(r"[^a-z가-힣0-9]", "", (it.get("title") or "").lower())[:50]
        if k and k in seen_title:
            continue
        seen_title.add(k)
        deduped[it["id"]] = it
    store = deduped
    today = datetime.now(timezone.utc).date()
    kept = []
    for it in store.values():
        try:
            dd = datetime.strptime(it.get("date", ""), "%Y-%m-%d").date()
        except (ValueError, TypeError):
            continue
        if (today - dd).days <= RETENTION_DAYS:
            kept.append(it)
    STORE_PATH.write_text(json.dumps(kept, ensure_ascii=False, indent=1), encoding="utf-8")
    dates = sorted({it["date"] for it in kept})
    print(f"✔ topic-store 갱신: 신규 {len(fresh)}건 / 보관 {len(kept)}건"
          + (f" ({dates[0]}~{dates[-1]})" if dates else ""))


if __name__ == "__main__":
    main()
