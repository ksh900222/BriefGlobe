#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
 fetch_news.py  ·  GDELT Events → news-data.js (사건 위치 방식)
------------------------------------------------------------
 핵심: "발행 위치"가 아니라 "사건이 실제로 일어난 위치"에 핀.
   GDELT Events 2.0 원본 파일(export.CSV)을 받아서
   ActionGeo(사건 장소) 좌표로 지도에 표시.

 동작:
   1) 최근 N시간치 Events 파일들을 data.gdeltproject.org 에서 다운
   2) 사건 장소 좌표가 있는 행만 추출 + CAMEO 코드로 '사건 종류' 분류
   3) (선택) 출처 기사의 <title>을 긁어 실제 헤드라인 확보
   4) news-store.json 에 누적 → news-data.js 생성

 사용:
   python3 fetch_news.py                 # 최근 3시간, 제목 스크랩 ON
   python3 fetch_news.py --hours 6
   python3 fetch_news.py --conflict      # 무력충돌/군사 사건만
   python3 fetch_news.py --no-titles     # 제목 스크랩 끄기(빠름)

 의존성: 표준 라이브러리만
============================================================
"""

import re
import json
import zipfile
import hashlib
import argparse
import html as htmllib
import io
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
STORE_PATH = HERE / "news-store.json"
OUTPUT_PATH = HERE / "news-data.js"
DIGEST_STORE_PATH = HERE / "digest-store.json"   # 좌표 없는 중요 뉴스(종합) 누적본
DIGEST_MAX = 60          # 종합에 이번 회차 새로 담을 최대 건수
DIGEST_MINARTS = 5       # 종합은 좌표 없이 '큰 사건'만 — 보도량 문턱을 높게
RETENTION_DAYS = 180   # 보관 기간(일). 드롭다운 "최근 N개월"용으로 6개월 누적
GDELT_BASE = "http://data.gdeltproject.org/gdeltv2/"

# ------------------------------------------------------------
# CAMEO EventRootCode(01~20) → 화면 카테고리(사건 종류)
#   index.html 의 CATEGORIES 와 키가 일치해야 함
# ------------------------------------------------------------
ROOT_TO_CAT = {
    1: "정치",  2: "정치",  9: "정치",                      # 발언/호소/조사
    3: "정치",  4: "정치",  5: "정치", 6: "정치", 7: "정치", 8: "정치",  # 협력/원조/양보
    10: "정치", 11: "정치", 12: "정치", 13: "정치",          # 요구/거부/위협
    14: "사회",                                            # 시위/항의
    15: "분쟁", 16: "분쟁", 17: "분쟁",                      # 무력시위/관계축소/강압
    18: "분쟁", 19: "분쟁", 20: "분쟁",                      # 공격/교전/대량폭력
}

# CAMEO 루트코드 → 한글 설명(합성 제목용 폴백)
CAMEO_KO = {
    1: "공개 성명", 2: "호소", 3: "협력 의사 표명", 4: "협의", 5: "외교 협력",
    6: "물질적 협력", 7: "원조 제공", 8: "양보", 9: "조사", 10: "요구",
    11: "비난", 12: "거부", 13: "위협", 14: "시위", 15: "무력 시위",
    16: "관계 축소", 17: "강압", 18: "공격", 19: "교전", 20: "대량 폭력",
}

CONFLICT_CATS = {"분쟁"}

# GDELT Events 2.0 컬럼 인덱스(0-based)
C_SQLDATE = 1
C_A1NAME = 6
C_A2NAME = 16
C_ROOTCODE = 28
C_QUADCLASS = 29
C_NUMARTS = 33
C_GEO_TYPE = 51       # 1=국가 2=미국주 3=미국도시 4=세계도시 5=세계주
C_GEO_FULLNAME = 52
C_GEO_CC = 53         # ActionGeo_CountryCode (FIPS)
C_GEO_LAT = 56
C_GEO_LONG = 57
C_DATEADDED = 59      # YYYYMMDDHHMMSS (UTC) — GDELT가 사건을 수집한 시각(15분 단위)
C_SOURCEURL = 60
MIN_FIELDS = 61


def dateadded_iso(da):
    """DATEADDED(YYYYMMDDHHMMSS, UTC) → ISO 'YYYY-MM-DDTHH:MM:SSZ'. 실패 시 None."""
    da = (da or "").strip()
    if len(da) >= 14 and da[:14].isdigit():
        try:
            dt = datetime.strptime(da[:14], "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except ValueError:
            return None
    return None

# FIPS 국가코드 → 한글 국가명(표시/그룹용). 없으면 FullName에서 폴백.
FIPS_TO_COUNTRY = {
    "US": "미국", "CH": "중국", "JA": "일본", "KS": "대한민국", "KN": "북한",
    "TW": "대만", "HK": "홍콩", "MC": "마카오", "MG": "몽골",
    "UK": "영국", "FR": "프랑스", "GM": "독일", "IT": "이탈리아", "SP": "스페인",
    "NL": "네덜란드", "EZ": "체코", "PL": "폴란드", "RS": "러시아", "UP": "우크라이나",
    "IN": "인도", "PK": "파키스탄", "BG": "방글라데시", "CE": "스리랑카",
    "VM": "베트남", "TH": "태국", "RP": "필리핀", "ID": "인도네시아", "MY": "말레이시아",
    "SN": "싱가포르", "BM": "미얀마", "CB": "캄보디아",
    "CA": "캐나다", "MX": "멕시코", "BR": "브라질", "AR": "아르헨티나", "VE": "베네수엘라",
    "AS": "호주", "NZ": "뉴질랜드", "IS": "이스라엘", "IR": "이란", "IZ": "이라크",
    "SY": "시리아", "LE": "레바논", "SA": "사우디아라비아", "AE": "아랍에미리트",
    "QA": "카타르", "MU": "오만", "TU": "튀르키예", "EG": "이집트", "NI": "나이지리아",
    "GH": "가나", "KE": "케냐", "SF": "남아프리카공화국", "ET": "에티오피아",
}
EAST_ASIA_FIPS = {"CH", "JA", "KS", "KN", "TW", "HK", "MC", "MG"}


def http_bytes(url, timeout=40):
    req = urllib.request.Request(url, headers={"User-Agent": "WorldNewsMap/2.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def recent_export_urls(hours):
    """최근 hours 시간치 export 파일 URL 목록(15분 간격)"""
    # 최신 타임스탬프를 lastupdate.txt 에서 얻음
    txt = http_bytes(GDELT_BASE + "lastupdate.txt").decode("utf-8", "replace")
    m = re.search(r"(\d{14})\.export\.CSV\.zip", txt)
    if not m:
        raise RuntimeError("lastupdate.txt 파싱 실패")
    latest = datetime.strptime(m.group(1), "%Y%m%d%H%M%S")
    steps = max(1, int(hours * 4))
    urls = []
    for i in range(steps):
        ts = latest - timedelta(minutes=15 * i)
        urls.append(GDELT_BASE + ts.strftime("%Y%m%d%H%M%S") + ".export.CSV.zip")
    return urls


def _parse_rows(zip_bytes, want_geo):
    """export.CSV.zip 바이트 → 사건 dict 리스트.
       want_geo=True: 좌표 있는 행(지도용) / False: 좌표 없는 행(종합용)."""
    out = []
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as z:
        name = z.namelist()[0]
        data = z.read(name).decode("utf-8", "replace")
    for line in data.splitlines():
        f = line.split("\t")
        if len(f) < MIN_FIELDS:
            continue
        lat, lng = f[C_GEO_LAT], f[C_GEO_LONG]
        url = f[C_SOURCEURL]
        if not url:
            continue
        has_geo = bool(lat and lng)
        if want_geo != has_geo:          # 원하는 좌표 유무와 다르면 건너뜀
            continue
        try:
            root = int(f[C_ROOTCODE])
        except ValueError:
            continue
        cat = ROOT_TO_CAT.get(root)
        if not cat:
            continue
        try:
            num = int(f[C_NUMARTS] or "0")
        except ValueError:
            num = 0
        row = {
            "fullname": f[C_GEO_FULLNAME], "geotype": f[C_GEO_TYPE],
            "cc": f[C_GEO_CC],
            "a1": f[C_A1NAME].strip(), "a2": f[C_A2NAME].strip(),
            "root": root, "cat": cat, "num": num,
            "date": f[C_SQLDATE], "dateadded": f[C_DATEADDED], "url": url,
        }
        if has_geo:
            row["lat"] = float(lat)
            row["lng"] = float(lng)
        out.append(row)
    return out


def parse_export(zip_bytes):
    """좌표 있는 사건만(지도용). 기존 호출부 호환."""
    return _parse_rows(zip_bytes, want_geo=True)


def parse_nogeo(zip_bytes):
    """좌표 없는 사건만(종합용) — 초국가·추상 이슈 등 지도에 못 올리는 것."""
    return _parse_rows(zip_bytes, want_geo=False)


# ============================================================
#  점수(우선순위) 시스템 — 전부 여기 숫자로 조정 가능
#    점수 = 보도량 + 국가가중 + 동아시아 + 관심주제 보너스
# ============================================================
TIER_A = {"US", "CH", "JA", "KS", "RS"}                 # 미국 중국 일본 한국 러시아
TIER_B = {"UK", "FR", "GM", "IN", "IS", "UP", "TW", "KN"}  # 영국 프랑스 독일 인도 이스라엘 우크라이나 대만 북한
W_TIER_A, W_TIER_B = 8, 4    # 국가 가중은 '살짝 미는' 정도(보너스가 품질 신호를 압도 못하게)
W_EASTASIA = 5               # 동아시아 존재는 아래 '최소 보장(floor)'이 따로 책임짐
W_COVERAGE = 18              # 보도량(품질 신호)을 지배적으로

# 관심 주제(제목 키워드) → 보너스 점수
TOPIC_BONUS = [
    (20, ["outbreak", "virus", "pandemic", "epidemic", "ebola", "cholera", "influenza",
          "disease", "infect", "quarantine", "전염병", "감염", "바이러스", "질병", "역병", "방역"]),
    (15, ["president", "prime minister", "summit", "head of state", "chancellor", "monarch",
          " king ", "leader", "정상회담", "대통령", "총리", "정상 ", "국가수반", "회담"]),
    (12, ["recession", "financial crisis", "central bank", "rate hike", "interest rate",
          "default", "bailout", "crash", "collapse", "금리", "경제위기", "중앙은행",
          "폭락", "디폴트", "구제금융"]),
    (12, ["war", "attack", "missile", "airstrike", "bombing", "invasion", "troops",
          "ceasefire", "offensive", "전쟁", "공격", "미사일", "공습", "침공", "교전", "휴전"]),
]

def base_score(e):
    """제목 없이 매기는 1차 점수: 보도량 + 국가가중 + 동아시아"""
    import math
    s = math.log10(e["num"] + 1) * W_COVERAGE          # 보도량(로그) — 지배적 신호
    if e["cc"] in TIER_A:
        s += W_TIER_A
    elif e["cc"] in TIER_B:
        s += W_TIER_B
    if e["cc"] in EAST_ASIA_FIPS:
        s += W_EASTASIA
    return s

def topic_bonus(title):
    """제목 키워드 기반 관심주제 보너스(최댓값 하나)"""
    low = (title or "").lower()
    best = 0
    for pts, kws in TOPIC_BONUS:
        if any(kw in low for kw in kws):
            best = max(best, pts)
    return best

def top_with_cap(evs, total, per_country, key):
    """key 점수 상위에서 국가당 상한을 두고 total개 추출(다양성 확보)"""
    evs = sorted(evs, key=key, reverse=True)
    cnt, out = {}, []
    for e in evs:
        if len(out) >= total:
            break
        c = e.get("cc") or "?"
        if cnt.get(c, 0) < per_country:
            out.append(e)
            cnt[c] = cnt.get(c, 0) + 1
    return out

def final_select(cands, max_total, per_country, asia_floor):
    """최종 점수 순 + 국가당 상한 + 동아시아 최소 보장"""
    cands = sorted(cands, key=lambda e: e["score"], reverse=True)
    cnt, picked = {}, []
    for e in cands:
        if len(picked) >= max_total:
            break
        c = e.get("cc") or "?"
        if cnt.get(c, 0) < per_country:
            picked.append(e)
            cnt[c] = cnt.get(c, 0) + 1
    # 동아시아 최소 보장: 부족하면 점수 낮은 비-동아시아와 교체
    ea = [e for e in picked if e["cc"] in EAST_ASIA_FIPS]
    if len(ea) < asia_floor:
        have = {e["url"] for e in picked}
        extra = [e for e in cands if e["cc"] in EAST_ASIA_FIPS and e["url"] not in have]
        need = min(asia_floor - len(ea), len(extra))
        non_ea = sorted([e for e in picked if e["cc"] not in EAST_ASIA_FIPS],
                        key=lambda e: e["score"])
        for i in range(need):
            picked.remove(non_ea[i])
            picked.append(extra[i])
    return picked


def split_place(fullname):
    """ActionGeo FullName → (도시, 국가)"""
    parts = [p.strip() for p in (fullname or "").split(",") if p.strip()]
    if not parts:
        return ("", "")
    return (parts[0], parts[-1])


def synth_title(ev):
    """제목을 못 긁었을 때의 합성 라벨"""
    a1, a2 = ev["a1"].title(), ev["a2"].title()
    act = CAMEO_KO.get(ev["root"], "사건")
    if a1 and a2:
        return f"{a1} → {a2} · {act}"
    if a1:
        return f"{a1} · {act}"
    city, _ = split_place(ev["fullname"])
    return f"{city or ev['fullname']} · {act}"


# ---- 출처 기사 <title> 스크랩 (실제 헤드라인 확보) ----
_TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.I | re.S)

def scrape_title(url):
    try:
        raw = http_bytes(url, timeout=6)
    except Exception:
        return None
    try:
        text = raw.decode("utf-8", "replace")
    except Exception:
        return None
    m = _TITLE_RE.search(text)
    if not m:
        return None
    t = htmllib.unescape(re.sub(r"\s+", " ", m.group(1))).strip()
    # 사이트명 꼬리표 제거( " - CNN", " | Reuters" 등)
    t = re.split(r"\s+[\|\-–—]\s+", t)[0].strip() if len(t) > 40 else t
    if not t or len(t) < 5:
        return None
    return t[:140]


def finalize_events(events):
    """선택된 사건 리스트 → 항목 변환 → 저장소 누적 → news-data.js 빌드.
       (일반 fetch / 백필 공통 마무리)"""
    fresh = []
    for ev in events:
        city, fb_country = split_place(ev["fullname"])
        country = FIPS_TO_COUNTRY.get(ev["cc"], fb_country)
        d = ev["date"]
        date_iso = f"{d[0:4]}-{d[4:6]}-{d[6:8]}" if len(d) >= 8 else \
                   datetime.now(timezone.utc).strftime("%Y-%m-%d")
        dt_iso = dateadded_iso(ev.get("dateadded"))   # 수집 시각(UTC ISO) — 없으면 None
        # 실제 헤드라인을 못 긁은 사건은 합성 라벨("British · 공격")뿐이라 내용이 빈약 →
        # 저장·번역·표시 모두에서 제외(토큰 낭비 방지). synth_title 폴백은 쓰지 않는다.
        title = ev.get("title")
        if not title:
            continue
        fresh.append({
            "id": hashlib.md5(ev["url"].encode()).hexdigest()[:12],
            "title": title,
            "summary": f"{CAMEO_KO.get(ev['root'],'사건')} · {ev['num']}개 매체 보도"
                       + (f" · {ev['a1'].title()}" if ev["a1"] else ""),
            "category": ev["cat"],
            "city": city, "country": country,
            "lat": round(ev["lat"], 4), "lng": round(ev["lng"], 4),
            "date": date_iso,
            **({"datetime": dt_iso} if dt_iso else {}),   # 수집 시각(UTC) — 프론트서 KST 표시
            "url": ev["url"],
            "num": ev["num"],          # 보도 매체 수 — 종합 브리핑 중요도 랭킹용
            "src": "gdelt",
        })

    if not fresh:
        print("✖ 표시할 사건이 없습니다. 기존 news-data.js 유지.")
        return

    # 누적 저장소 병합 + 보관기간 정리
    store = json.loads(STORE_PATH.read_text(encoding="utf-8")) if STORE_PATH.exists() else []
    by_id = {it["id"]: it for it in store}
    for it in fresh:
        by_id[it["id"]] = it
    today = datetime.now(timezone.utc).date()
    merged = []
    for it in by_id.values():
        try:
            dd = datetime.strptime(it["date"], "%Y-%m-%d").date()
        except (ValueError, KeyError):
            continue
        if 0 <= (today - dd).days <= RETENTION_DAYS:
            merged.append(it)

    STORE_PATH.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    dates = sorted({it["date"] for it in merged})
    from collections import Counter
    print(f"✔ GDELT 저장소 갱신: {len(merged)}건 / 날짜 {len(dates)}개 ({dates[0]}~{dates[-1]})")
    print(f"  카테고리: {dict(Counter(it['category'] for it in merged))}")

    try:
        import merge_news
        merge_news.build_output()
    except Exception as e:
        print(f"  ⚠ 병합 빌드 실패: {e} (merge_news.py 확인)")


def build_digest(raw_nogeo):
    """좌표 없는 사건 중 '보도량·주제' 상위만 골라 digest-store.json 에 누적.
       (지도에 못 올리는 초국가·추상 이슈의 집. 번역은 merge_news.py 가 담당.)"""
    if not raw_nogeo:
        print("  · 종합(좌표없음): 신규 후보 0건")
        return
    # URL 기준 중복 제거(보도량 큰 것 우선) + 보도 문턱(큰 사건만)
    by_url = {}
    for ev in raw_nogeo:
        if ev["num"] < DIGEST_MINARTS:
            continue
        cur = by_url.get(ev["url"])
        if cur is None or ev["num"] > cur["num"]:
            by_url[ev["url"]] = ev
    pool = list(by_url.values())
    if not pool:
        print("  · 종합(좌표없음): 문턱 통과 0건")
        return

    # 1차 점수(보도량+국가가중)로 후보 추출 → 제목 스크랩 비용 절감
    for e in pool:
        e["base"] = base_score(e)
    cands = top_with_cap(pool, DIGEST_MAX * 2, 8, key=lambda e: e["base"])

    # 후보 제목 스크랩(병렬) — 실제 헤드라인 있는 것만 채택
    titles = {}
    with ThreadPoolExecutor(max_workers=12) as ex:
        for ev, t in zip(cands, ex.map(lambda e: scrape_title(e["url"]), cands)):
            if t:
                titles[ev["url"]] = t
    scored = []
    for e in cands:
        t = titles.get(e["url"])
        if not t:
            continue
        tb = topic_bonus(t)
        # 실속 게이트: 관심주제 키워드(전쟁·정상회담·위기·전염병)가 있거나
        #   무력충돌(분쟁) 사건만 남긴다. 좌표 없는 GDELT 는 연예·가십 비중이
        #   커서, 보도량만으로 뽑으면 유명인 뉴스가 올라오는 걸 막는다.
        if tb == 0 and e["cat"] != "분쟁":
            continue
        e["title"] = t
        e["score"] = e["base"] + tb
        scored.append(e)
    scored.sort(key=lambda e: e["score"], reverse=True)
    picked = top_with_cap(scored, DIGEST_MAX, 6, key=lambda e: e["score"])

    fresh = []
    for ev in picked:
        d = ev["date"]
        date_iso = f"{d[0:4]}-{d[4:6]}-{d[6:8]}" if len(d) >= 8 else \
                   datetime.now(timezone.utc).strftime("%Y-%m-%d")
        fresh.append({
            "id": "d" + hashlib.md5(ev["url"].encode()).hexdigest()[:11],
            "title": ev["title"],
            "summary": f"{CAMEO_KO.get(ev['root'],'사건')} · {ev['num']}개 매체 보도",
            "category": ev["cat"],
            "country": FIPS_TO_COUNTRY.get(ev["cc"], ""),
            "date": date_iso,
            "url": ev["url"],
            "num": ev["num"],
            "src": "gdelt-digest",
        })

    # 누적 저장소 병합 + 보관기간 정리
    store = json.loads(DIGEST_STORE_PATH.read_text(encoding="utf-8")) \
        if DIGEST_STORE_PATH.exists() else []
    by_id = {it["id"]: it for it in store}
    for it in fresh:
        old = by_id.get(it["id"])
        if old is None or it["num"] >= old.get("num", 0):
            by_id[it["id"]] = it
    today = datetime.now(timezone.utc).date()
    merged = []
    for it in by_id.values():
        try:
            dd = datetime.strptime(it["date"], "%Y-%m-%d").date()
        except (ValueError, KeyError):
            continue
        if 0 <= (today - dd).days <= RETENTION_DAYS:
            merged.append(it)
    DIGEST_STORE_PATH.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  · 종합(좌표없음) 저장소: 신규 {len(fresh)}건 → 총 {len(merged)}건")


def backfill_urls(days):
    """최근 days 일치 export 파일 URL 전체(15분 간격, 하루 96개)"""
    txt = http_bytes(GDELT_BASE + "lastupdate.txt").decode("utf-8", "replace")
    m = re.search(r"(\d{14})\.export\.CSV\.zip", txt)
    if not m:
        raise RuntimeError("lastupdate.txt 파싱 실패")
    latest = datetime.strptime(m.group(1), "%Y%m%d%H%M%S")
    steps = int(days * 96)
    return [GDELT_BASE + (latest - timedelta(minutes=15 * i)).strftime("%Y%m%d%H%M%S")
            + ".export.CSV.zip" for i in range(steps)]


def run_backfill(args):
    """백필 모드: 최근 N일치를 병렬 다운로드 → 하루당 쿼터 선별 → 마무리."""
    from collections import defaultdict
    days, perday = args.backfill, args.perday
    urls = backfill_urls(days)
    print(f"▶ 백필: 최근 {days}일치, 파일 {len(urls)}개 다운로드 (시간 좀 걸림)")

    def fetch_parse(u):
        try:
            return [e for e in parse_export(http_bytes(u)) if e["num"] >= args.minarts]
        except Exception:
            return []

    by_day = defaultdict(list)
    done = 0
    with ThreadPoolExecutor(max_workers=16) as ex:
        for evs in ex.map(fetch_parse, urls):
            for e in evs:
                if args.conflict and e["cat"] not in CONFLICT_CATS:
                    continue
                d = e["date"]
                if len(d) < 8:
                    continue
                e["base"] = base_score(e)
                by_day[f"{d[0:4]}-{d[4:6]}-{d[6:8]}"].append(e)
            done += 1
            if done % 200 == 0:
                for k in list(by_day):           # 메모리 제한: 날짜별 상위만 유지
                    if len(by_day[k]) > perday * 8:
                        by_day[k] = sorted(by_day[k], key=lambda x: x["base"],
                                           reverse=True)[:perday * 4]
                print(f"  · 진행 {done}/{len(urls)} 파일…")
    print(f"  · 다운로드 완료. 날짜 {len(by_day)}개 수집")

    # 하루당: URL 중복 제거 후 상위 perday 선별
    selected = []
    for day, evs in by_day.items():
        bu = {}
        for e in evs:
            c = bu.get(e["url"])
            if c is None or e["num"] > c["num"]:
                bu[e["url"]] = e
        selected.extend(top_with_cap(list(bu.values()), perday, args.percountry,
                                     key=lambda x: x["base"]))
    print(f"  · 하루당 ≤{perday}건 선별 → 총 {len(selected)}건")

    # 제목 스크랩(옛 링크는 실패할 수 있음)
    titles = {}
    if args.titles and selected:
        print(f"  · 제목 스크랩 중… ({len(selected)}건, 오래된 링크는 일부 실패)")
        with ThreadPoolExecutor(max_workers=16) as ex:
            for ev, t in zip(selected, ex.map(lambda e: scrape_title(e["url"]), selected)):
                if t:
                    titles[ev["url"]] = t
        print(f"    → {len(titles)}건 제목 확보")
    for e in selected:
        e["title"] = titles.get(e["url"]) or synth_title(e)

    finalize_events(selected)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hours", type=float, default=3, help="수집 시간 범위")
    ap.add_argument("--max", type=int, default=160, help="지도에 올릴 최대 사건 수")
    ap.add_argument("--minarts", type=int, default=2, help="최소 보도 매체 수(중요도)")
    ap.add_argument("--percountry", type=int, default=6, help="국가당 최대 사건 수")
    ap.add_argument("--asia", type=int, default=25, help="동아시아 최소 보장 건수")
    ap.add_argument("--conflict", action="store_true", help="무력충돌/군사 사건만")
    ap.add_argument("--no-titles", dest="titles", action="store_false",
                    help="출처 제목 스크랩 끄기(빠름)")
    ap.add_argument("--backfill", type=int, default=0,
                    help="백필 모드: 최근 N일치를 한 번에 다운로드(예: 30)")
    ap.add_argument("--perday", type=int, default=40, help="백필 시 하루당 최대 사건 수")
    args = ap.parse_args()

    if args.backfill:
        run_backfill(args)
        return

    print(f"▶ GDELT Events 수집 (최근 {args.hours}시간)")
    urls = recent_export_urls(args.hours)
    raw_events = []
    raw_nogeo = []
    for i, u in enumerate(urls):
        try:
            b = http_bytes(u)
        except Exception as e:
            print(f"  ⚠ 파일 {i+1}/{len(urls)} 실패: {e}")
            continue
        raw_events.extend(parse_export(b))
        raw_nogeo.extend(parse_nogeo(b))
    print(f"  · 좌표 있는 사건 {len(raw_events)}건 / 좌표 없는 사건 {len(raw_nogeo)}건 수집")

    # 중복 제거(출처 URL 기준) + 보도 임계 필터
    by_url = {}
    for ev in raw_events:
        if args.conflict and ev["cat"] not in CONFLICT_CATS:
            continue
        if ev["num"] < args.minarts:
            continue
        cur = by_url.get(ev["url"])
        if cur is None or ev["num"] > cur["num"]:
            by_url[ev["url"]] = ev
    pool = list(by_url.values())

    # 1차 점수(보도량+국가가중+동아시아)로 후보 추출 → 제목 스크랩 비용 절감
    for e in pool:
        e["base"] = base_score(e)
    cands = top_with_cap(pool, args.max * 2, args.percountry * 3,
                         key=lambda e: e["base"])
    print(f"  · 1차 점수로 후보 {len(cands)}건 선별")

    # 후보 제목 스크랩(병렬)
    titles = {}
    if args.titles and cands:
        print(f"  · 출처 제목 스크랩 중… ({len(cands)}건)")
        with ThreadPoolExecutor(max_workers=12) as ex:
            for ev, t in zip(cands, ex.map(lambda e: scrape_title(e["url"]), cands)):
                if t:
                    titles[ev["url"]] = t
        print(f"    → {len(titles)}건 실제 제목 확보")

    # 2차 점수(+관심주제 보너스) → 최종 선택(국가 상한·동아시아 보장)
    for e in cands:
        e["title"] = titles.get(e["url"]) or synth_title(e)
        e["score"] = e["base"] + topic_bonus(e["title"])
    events = final_select(cands, args.max, args.percountry, args.asia)
    nea = sum(1 for e in events if e["cc"] in EAST_ASIA_FIPS)
    print(f"  · 최종 {len(events)}건 선택 (점수 상위순, 동아시아 {nea}건)")

    # 종합(좌표 없는 중요 뉴스) 저장소 갱신 — merge 전에 먼저 써둠
    build_digest(raw_nogeo)

    finalize_events(events)


if __name__ == "__main__":
    main()
