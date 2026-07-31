#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
 fetch_typhoons.py · 열대저기압(태풍·허리케인) 공식 예보 수집 → typhoons.json
------------------------------------------------------------
 미국 NOAA/NHC 의 무료·무키 ArcGIS REST(GeoJSON)에서 현재 활성 중인
 대서양(AL)·동태평양(EP)·중태평양(CP) 열대저기압의 **공식 예보 그대로**를
 수집한다. AI 예측·가공 없음. 활성 폭풍이 없으면 storms=[] (오버레이 자동 숨김).

  ➕ 미국령 밖 전 지구(서태평양 WP·북인도양 IO·남반구 SH)는 JTWC(미 합동태풍경보센터)
     RSS+경고텍스트로 병합. TD(열대저압부)도 포함. NHC(AL/EP/CP)와 basin 중복 없음.
     → 지구 어디서 생겨도 잡힘(한국행 태풍 누락 방지). 옛 HKO(홍콩 중심) 소스는 폐기.

 데이터: NHC_tropical_weather MapServer 의 슬롯형 레이어(AT1~5·EP1~5·CP1~5).
   슬롯 base id: AT1=4, 이후 +26. EP1=134, CP1=264.
   슬롯 내 오프셋: +2 예보점, +3 예보진로선, +4 예보원뿔, +7 과거점, +8 과거진로선.

 표준 라이브러리만 사용. 키·토큰 불필요.
 사용:  python3 fetch_typhoons.py   (auto_update.sh 가 매시간 실행)
============================================================
"""
import json
import math
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "typhoons.json"

BASE = ("https://mapservices.weather.noaa.gov/tropical/rest/services/"
        "tropical/NHC_tropical_weather/MapServer")

# 슬롯: (접두, base id). 슬롯 내 레이어는 base+offset.
SLOTS = ([("AT%d" % (i + 1), 4 + i * 26) for i in range(5)]
         + [("EP%d" % (i + 1), 134 + i * 26) for i in range(5)]
         + [("CP%d" % (i + 1), 264 + i * 26) for i in range(5)])
OFF_FCST_PTS, OFF_FCST_TRK, OFF_CONE, OFF_PAST_PTS, OFF_PAST_TRK = 2, 3, 4, 7, 8
# 슬롯 내 +12 = "Forecast Wind Radii" 레이어(예 AT1 base 4 → id 16, AT2 base 30 → id 42).
# 34/50/64kt 바람이 미치는 사분면 반경(NE/SE/SW/NW, 해리 nm)을 tau(예보시각)별로 담음.
OFF_FCST_WIND_RADII = 12

BASIN_LABEL = {"AL": "대서양", "EP": "동태평양", "CP": "중태평양", "WP": "북서태평양",
               "IO": "북인도양", "SH": "남반구"}

SOURCE_NOTE = ("NOAA/NHC (National Hurricane Center) 공식 자문 — "
               "mapservices.weather.noaa.gov NHC_tropical_weather")

# ─────────────────────────────────────────────────────────────
#  HKO (홍콩기상청) — 북서태평양(한·일·중, WPac) 태풍 소스
# ─────────────────────────────────────────────────────────────
#  진입점: tc_list.xml (활성 태풍 목록). 비활성기엔 빈 <TropicalCycloneList/>.
#  활성 시 storm 항목마다 per-storm 상세 링크가 채워지고, 그 안에 예보 위치
#  (24/48/72/96/120h)·중심최대풍속·등급이 들어온다.
#
#  ⚠️ per-storm 상세의 "실제" 반환 포맷(태그 구조/GeoJSON·KML·XML)은 현재
#     비활성기라 tc_list.xml 이 비어 있어 **검증 불가**. 아래 파서는 HKO 공개
#     문서 기준 best-effort 로, 위경도·예보시각·풍속을 가진 노드를 태그명에
#     의존하지 않고 관용적으로 찾아낸다. **다음 활성 태풍 시 실포맷 검증 필요**.
#     포맷이 예상과 다르면 파싱이 0건이 되어 HKO 기여만 스킵되고 NHC·전체
#     파이프라인은 정상 동작한다(지어내기 없음).
HKO_LIST_URL = "https://www.weather.gov.hk/wxinfo/currwx/tc_list.xml"
HKO_SOURCE_NOTE = ("홍콩기상청(HKO) 공식 예보 — weather.gov.hk tc_list.xml "
                   "(북서태평양). 원뿔=Potential Track Area(70% 확률).")
# HKO Potential Track Area(70% 확률) 반경(km): 예보시각(h) → 반경.
HKO_PTA_RADIUS_KM = {24: 100, 48: 170, 72: 255, 96: 345, 120: 465}
# HKO 풍속은 km/h → 스키마(NHC)는 kt. 1 kt = 1.852 km/h.
KMH_PER_KT = 1.852


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode("utf-8"))


def _geojson(layer, count_only=False):
    q = "returnCountOnly=true" if count_only else "outFields=*&f=geojson&outSR=4326"
    url = f"{BASE}/{layer}/query?where=1%3D1&{q}"
    if count_only:
        url += "&f=json"
    return _get(url)


def _count(layer):
    try:
        return int(_geojson(layer, count_only=True).get("count", 0))
    except Exception:
        return 0


def _r(v, n=3):
    try:
        return round(float(v), n)
    except (TypeError, ValueError):
        return None


def _clean(v):
    """NHC 결측 센티널(9999/-9999 등) → None."""
    try:
        f = float(v)
    except (TypeError, ValueError):
        return v
    return None if abs(f) >= 9000 else v


def _line_coords(geojson, n=3):
    """GeoJSON LineString/MultiLineString feature 모음 → [[lat,lng],...] 세그먼트 리스트."""
    segs = []
    for f in (geojson or {}).get("features", []):
        g = f.get("geometry") or {}
        t = g.get("type")
        cs = g.get("coordinates") or []
        parts = [cs] if t == "LineString" else (cs if t == "MultiLineString" else [])
        for part in parts:
            seg = [[_r(pt[1], n), _r(pt[0], n)] for pt in part
                   if pt and len(pt) >= 2 and pt[0] is not None and pt[1] is not None]
            if len(seg) >= 2:
                segs.append(seg)
    return segs


def _ring(ring, n=2, maxpts=160):
    """폴리곤 링 좌표 반올림 + 과밀 다운샘플(부드러운 원뿔이라 형태 보존)."""
    pts = [[_r(pt[0], n), _r(pt[1], n)] for pt in ring if pt and len(pt) >= 2]
    if len(pts) > maxpts:
        step = len(pts) / maxpts
        keep = [pts[int(i * step)] for i in range(maxpts)]
        keep.append(pts[-1])           # 닫힘 보장
        pts = keep
    return pts


def _polygon_geom(geojson, n=2):
    """예보 원뿔 폴리곤 → GeoJSON Polygon geometry([lng,lat], 반올림·다운샘플). 없으면 None."""
    for f in (geojson or {}).get("features", []):
        g = f.get("geometry") or {}
        if g.get("type") == "Polygon":
            rings = [r for r in (_ring(ring, n) for ring in g.get("coordinates", [])) if len(r) >= 4]
            if rings:
                return {"type": "Polygon", "coordinates": rings}
        if g.get("type") == "MultiPolygon":
            polys = []
            for poly in g.get("coordinates", []):
                rings = [r for r in (_ring(ring, n) for ring in poly) if len(r) >= 4]
                if rings:
                    polys.append(rings)
            if polys:
                return {"type": "MultiPolygon", "coordinates": polys}
    return None


def _fmt_dtg(dtg):
    """2026071712 → '2026-07-17 12:00 UTC'. 실패 시 문자열/빈값."""
    s = str(dtg or "")
    if len(s) == 10 and s.isdigit():
        return f"{s[0:4]}-{s[4:6]}-{s[6:8]} {s[8:10]}:00 UTC"
    return s


def _pt_props(f, kind):
    """예보점(maxwind/tau/fldatelbl)·과거점(intensity/dtg) 스키마 모두 대응."""
    p = f.get("properties") or {}
    g = f.get("geometry") or {}
    coords = g.get("coordinates") or [None, None]
    lng = _r(coords[0]) if coords[0] is not None else _r(p.get("lon"))
    lat = _r(coords[1]) if coords[1] is not None else _r(p.get("lat"))
    if lat is None or lng is None:
        return None
    time = (p.get("fldatelbl") or p.get("datelbl")
            or (_fmt_dtg(p.get("dtg")) if p.get("dtg") is not None else ""))
    wind = p.get("maxwind")
    if wind is None:
        wind = p.get("intensity")           # 과거점
    return {
        "lat": lat, "lng": lng, "kind": kind, "time": time,
        "windKt": _clean(wind), "gustKt": _clean(p.get("gust")),
        "mslp": _clean(p.get("mslp")),
        "ss": p.get("ssnum") if p.get("ssnum") is not None else p.get("ss"),
        "dev": p.get("tcdvlp") or p.get("stormtype") or "",
        "tau": p.get("tau"),
    }


def _sort_key(f, kind):
    p = f.get("properties") or {}
    if kind == "forecast":
        t = p.get("tau")
        return t if isinstance(t, (int, float)) else 0
    d = p.get("dtg")                          # 과거점: YYYYMMDDHH 정수
    try:
        return int(d)
    except (TypeError, ValueError):
        return 0


def _sorted_points(geojson, kind):
    feats = sorted((geojson or {}).get("features", []), key=lambda f: _sort_key(f, kind))
    return [rec for rec in (_pt_props(f, kind) for f in feats) if rec]


def _wind_radii(geojson):
    """
    "Forecast Wind Radii" 레이어 → 태풍 현재 크기(초기 시점, tau 최소=보통 0)의
    34/50/64kt 사분면 반경. 반환: {"r34":[NE,SE,SW,NW], "r50":[...], "r64":[...]}
    (nm 단위, 값은 숫자 또는 null). 실제로 파싱된 등급만 채움 — 데이터 없는 등급은
    [null,null,null,null], 아무 등급도 없으면 None(지어내기 없음).

    NHC 자문은 초기 시점(tau 0)에 현재 폭풍 크기를, 이후 tau 에 예보 크기를 준다.
    지도에 '현재 크기'를 그리기 위해 존재하는 tau 중 최소값(초기 시점)을 사용.
    """
    feats = (geojson or {}).get("features", [])
    if not feats:
        return None
    rows = []
    for f in feats:
        p = f.get("properties") or {}
        radii = _clean(p.get("radii"))
        tau = p.get("tau")
        if radii is None or tau is None:
            continue
        try:
            rows.append((int(float(tau)), int(float(radii)), p))
        except (TypeError, ValueError):
            continue
    if not rows:
        return None
    tau0 = min(r[0] for r in rows)                 # 초기 시점(보통 0)
    out, any_band = {}, False
    for band in (34, 50, 64):
        match = next((p for (t, rd, p) in rows if t == tau0 and rd == band), None)
        if match is None:
            out["r%d" % band] = [None, None, None, None]   # 해당 등급 데이터 없음
            continue
        quad = [_r(_clean(match.get(q)), 0) for q in ("ne", "se", "sw", "nw")]
        out["r%d" % band] = [int(v) if v is not None else None for v in quad]
        any_band = True
    return out if any_band else None               # 아무 등급도 없으면 windRadii=null


def collect_storm(pfx, base):
    """활성 슬롯 하나 → 폭풍 dict. 실패 시 None."""
    fpts = _geojson(base + OFF_FCST_PTS)
    feats = fpts.get("features", [])
    if not feats:
        return None
    # 현재 상태 = tau 0(또는 최소) 예보점
    fcst_points = _sorted_points(fpts, "forecast")
    cur = fcst_points[0] if fcst_points else {}
    p0 = feats[0].get("properties", {})
    basin = (p0.get("basin") or pfx[:2]).upper()
    name_full = p0.get("stormname") or "Unknown"
    name = name_full.split()[-1] if name_full else "Unknown"

    past_pts = _sorted_points(_safe(base + OFF_PAST_PTS), "past")
    forecast_line = _line_coords(_safe(base + OFF_FCST_TRK))
    past_line = _line_coords(_safe(base + OFF_PAST_TRK))
    cone = _polygon_geom(_safe(base + OFF_CONE))
    try:                                            # 풍속 반경(크기) — 실패해도 나머지 무손상
        wind_radii = _wind_radii(_safe(base + OFF_FCST_WIND_RADII))
    except Exception:
        wind_radii = None

    points = past_pts + fcst_points
    return {
        "id": (p0.get("idp_source") or "")[:9].upper() or f"{basin}{p0.get('stormnum','')}",
        "slot": pfx,
        "name": name,
        "fullName": name_full,
        "basin": basin,
        "basinLabel": BASIN_LABEL.get(basin, basin),
        "category": p0.get("tcdvlp") or p0.get("stormtype") or "",
        "ss": cur.get("ss") if cur else p0.get("ssnum"),
        "maxWindKt": cur.get("windKt") if cur else p0.get("maxwind"),
        "gustKt": cur.get("gustKt") if cur else p0.get("gust"),
        "mslp": cur.get("mslp") if cur else p0.get("mslp"),
        "advDate": p0.get("advdate") or "",
        "advisoryNum": p0.get("advisnum") or "",
        "points": points,
        "pastLine": past_line,
        "forecastLine": forecast_line,
        "cone": cone,
        "windRadii": wind_radii,
        "source": SOURCE_NOTE,
    }


def _safe(layer):
    try:
        return _geojson(layer)
    except Exception:
        return {"features": []}


# ─────────────────────────────────────────────────────────────
#  HKO 수집 (best-effort · 태그명 비의존 관용 파서)
# ─────────────────────────────────────────────────────────────
def _get_text(url):
    """정부 사이트 대비 UA·timeout 지정, 표준 urllib 만. 텍스트(bytes→str) 반환."""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", "replace")


def _local(tag):
    """{ns}Tag → 'tag'(소문자, 네임스페이스 제거)."""
    return (tag.split("}")[-1] if "}" in tag else tag).lower()


def _parse_coord(v):
    """'22.5', '22.5N', 'N22.5', '114.2E', '-114.2' 등 → float(남/서는 음수). 실패 None."""
    if v is None:
        return None
    s = str(v).strip().upper()
    if not s:
        return None
    neg = ("S" in s) or ("W" in s)
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    if not m:
        return None
    try:
        val = float(m.group(0))
    except ValueError:
        return None
    return -abs(val) if neg else val


def _first_num(v):
    """'150 km/h' 등 문자열에서 첫 숫자만 → float. 실패 None."""
    if v is None:
        return None
    m = re.search(r"-?\d+(?:\.\d+)?", str(v))
    try:
        return float(m.group(0)) if m else None
    except ValueError:
        return None


def _node_kv(elem):
    """elem 의 속성 + 직속 자식(텍스트) 을 {소문자키: 값} 로. 위치 노드 판별용."""
    kv = {}
    for k, v in (elem.attrib or {}).items():
        kv[_local(k)] = v
    for ch in list(elem):
        if len(list(ch)) == 0:  # 리프만(값 노드)
            kv.setdefault(_local(ch.tag), (ch.text or "").strip())
    return kv


def _extract_positions(root):
    """
    per-storm XML 트리에서 위경도를 가진 노드를 태그명에 의존하지 않고 수집.
    반환: [{lat,lng,tau,time,windKmh,pressure,cls}], tau 는 예보시각(h)·없으면 None.
    ⚠️ 실포맷 미검증 — 활성 태풍 시 태그 매핑 재확인 필요.
    """
    out = []
    for elem in root.iter():
        kv = _node_kv(elem)
        if not kv:
            continue
        lat_k = next((k for k in kv if "lat" in k), None)
        lng_k = next((k for k in kv if ("lon" in k or k == "lng")), None)
        if not lat_k or not lng_k:
            continue
        lat = _parse_coord(kv.get(lat_k))
        lng = _parse_coord(kv.get(lng_k))
        if lat is None or lng is None:
            continue
        # 예보시각(h): tau/hour/forecast-hour/valid 계열 키에서.
        tau = None
        for k in kv:
            if any(t in k for t in ("tau", "hour", "fhr", "leadtime")):
                tau = _first_num(kv[k])
                if tau is not None:
                    break
        time = ""
        for k in kv:
            if any(t in k for t in ("time", "valid", "date")):
                time = str(kv[k]).strip()
                if time:
                    break
        wind = None
        for k in kv:
            if any(t in k for t in ("wind", "speed", "maxwind")):
                wind = _first_num(kv[k])
                if wind is not None:
                    break
        pres = None
        for k in kv:
            if any(t in k for t in ("pressure", "mslp", "hpa")):
                pres = _first_num(kv[k])
                if pres is not None:
                    break
        cls = ""
        for k in kv:
            if any(t in k for t in ("intensity", "class", "category", "type", "grade")):
                val = str(kv[k]).strip()
                if val and _first_num(val) is None:  # 숫자 아닌 분류명만
                    cls = val
                    break
        out.append({"lat": _r(lat), "lng": _r(lng), "tau": int(tau) if tau is not None else None,
                    "time": time, "windKmh": wind, "pressure": pres, "cls": cls})
    return out


def _circle_ring(lat, lng, radius_km, n=24):
    """(lat,lng) 중심 radius_km 원 근사 → [[lng,lat],...] (GeoJSON 경도·위도 순)."""
    if radius_km <= 0:
        return []
    dlat = radius_km / 111.32
    coslat = math.cos(math.radians(lat))
    dlng = radius_km / (111.32 * coslat) if abs(coslat) > 1e-6 else radius_km / 111.32
    return [[_r(lng + dlng * math.cos(2 * math.pi * i / n)),
             _r(lat + dlat * math.sin(2 * math.pi * i / n))] for i in range(n)]


def _convex_hull(pts):
    """Andrew monotone chain. pts=[[x,y],...] → 볼록껍질 링([x,y], 닫힘). 3점 미만 None."""
    P = sorted(set((p[0], p[1]) for p in pts if p and len(p) >= 2))
    if len(P) < 3:
        return None

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower = []
    for p in P:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(P):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    hull = lower[:-1] + upper[:-1]
    if len(hull) < 3:
        return None
    ring = [[x, y] for x, y in hull]
    ring.append(ring[0])  # 닫힘
    return ring


def _hko_cone(fcst_points, radius_table=None):
    """
    예보점들에 예보시각(tau)별 오차 반경 원을 합성 → 볼록껍질로 예보 오차원뿔 폴리곤 근사.
    radius_table: {tau(h): 반경(km)}. 기본은 HKO PTA(70%). JTWC 는 표준 예보오차 반경 전달.
    반환: GeoJSON Polygon geometry([lng,lat]) 또는 None.
    (진짜 union 대신 볼록껍질 근사 — 외부 패키지 없이 유효한 단일 링 보장. 문서화된
     근사이며 지어낸 값 아님.)
    """
    rt = radius_table if radius_table is not None else HKO_PTA_RADIUS_KM
    samples = []
    for p in fcst_points:
        if p.get("lat") is None or p.get("lng") is None:
            continue
        tau = p.get("tau")
        r = rt.get(tau) if tau is not None else None
        if r:
            samples.extend(_circle_ring(p["lat"], p["lng"], r))
        else:
            samples.append([p["lng"], p["lat"]])  # tau 0/불명 — 점만
    ring = _convex_hull(samples)
    return {"type": "Polygon", "coordinates": [ring]} if ring else None


def _hko_sections(root):
    """
    HKO 실제 스키마로 분류: <PastInformation>(과거) · <AnalysisInformation>(현재 실황) ·
    <ForecastInformation>(예보). 각 노드는 Index/Intensity/MaximumWind/Time/Latitude/Longitude.
    (예보 노드 다수는 좌표만 있고 주요 시각에만 Intensity/Time 이 붙는다)
    스키마가 다르면 (None, None, None) → 호출부가 관용 파서로 폴백.
    """
    def grab(tag):
        out = []
        for e in root.iter():
            if _local(e.tag) != tag:
                continue
            kv = _node_kv(e)
            lat = _parse_coord(kv.get("latitude"))
            lng = _parse_coord(kv.get("longitude"))
            if lat is None or lng is None:
                continue
            out.append({"lat": _r(lat), "lng": _r(lng),
                        "time": (kv.get("time") or "").strip(),
                        "windKmh": _first_num(kv.get("maximumwind")),
                        "pressure": None,
                        "cls": (kv.get("intensity") or "").strip(),
                        "tau": None})
        return out
    past, ana, fcst = grab("pastinformation"), grab("analysisinformation"), grab("forecastinformation")
    if not (past or ana or fcst):
        return None, None, None
    # 예보점의 tau(h) = 예보시각 − 현재(실황)시각. Time 이 있는 점만 계산(원뿔 반경용).
    base = None
    for p in (ana + past[::-1]):
        try:
            base = datetime.fromisoformat(p["time"]); break
        except Exception:
            continue
    if base:
        for p in fcst:
            try:
                p["tau"] = int(round((datetime.fromisoformat(p["time"]) - base).total_seconds() / 3600))
            except Exception:
                pass
    return past, ana, fcst


def _hko_storm(tc_id, name, detail_url, errors):
    """per-storm 상세 → NHC 동일 스키마 storm dict. 파싱 실패/무포인트 시 None."""
    try:
        raw = _get_text(detail_url)
        root = ET.fromstring(raw)
    except Exception as e:
        errors.append(f"HKO {name or tc_id}: 상세 파싱 실패 {type(e).__name__}: {e}")
        return None

    # ① 실제 스키마(Past/Analysis/Forecast) 우선 — 현재 위치·강도를 정확히 잡는다.
    past, ana, fcst = _hko_sections(root)
    if past is None:
        # ② 폴백: 태그명 비의존 관용 파서(스키마 변경 대비)
        positions = _extract_positions(root)
        if not positions:
            errors.append(f"HKO {name or tc_id}: 상세에서 예보점 0건(포맷 상이 가능 — 실포맷 검증 필요)")
            return None
        fcst = sorted([p for p in positions if p.get("tau") is not None], key=lambda p: p["tau"])
        past = [p for p in positions if p.get("tau") is None]
        ana = []
    # 현재 = 실황(Analysis) → 없으면 과거 마지막 → 그래도 없으면 예보 첫점
    cur = (ana[0] if ana else (past[-1] if past else (fcst[0] if fcst else {})))
    if ana:
        past = past + ana        # 실황점을 과거 경로 끝에 포함(선이 현재까지 이어지도록)

    def mk_point(p, kind):
        w = p.get("windKmh")
        wkt = round(w / KMH_PER_KT) if w is not None else None
        return {"lat": p.get("lat"), "lng": p.get("lng"), "kind": kind,
                "time": p.get("time") or "", "windKt": wkt, "gustKt": None,
                "mslp": int(p["pressure"]) if p.get("pressure") is not None else None,
                "ss": None, "dev": p.get("cls") or "", "tau": p.get("tau")}

    points = [mk_point(p, "past") for p in past] + [mk_point(p, "forecast") for p in fcst]
    if not points:
        return None
    cur_kmh = cur.get("windKmh")
    cur_wkt = round(cur_kmh / KMH_PER_KT) if cur_kmh is not None else None

    past_line = [[[p["lat"], p["lng"]] for p in past]] if len(past) >= 2 else []
    fcst_line = [[[p["lat"], p["lng"]] for p in fcst]] if len(fcst) >= 2 else []
    cone = _hko_cone(fcst)

    return {
        "id": (tc_id or name or "WP").upper()[:9] or "WP",
        "slot": "HKO",
        "name": name or (tc_id or "Unknown"),
        "fullName": name or (tc_id or "Unknown"),
        "basin": "WP",
        "basinLabel": BASIN_LABEL["WP"],
        "category": cur.get("cls") or "",
        "ss": None,
        "maxWindKt": cur_wkt,
        "gustKt": None,
        "mslp": int(cur["pressure"]) if cur.get("pressure") is not None else None,
        "advDate": "",
        "advisoryNum": "",
        "points": points,
        "pastLine": past_line,
        "forecastLine": fcst_line,
        "cone": cone,
        "windRadii": None,   # HKO tc_list.xml 에는 사분면 풍속 반경 미제공 → null
        "source": HKO_SOURCE_NOTE,
    }


def collect_hko(errors):
    """
    HKO tc_list.xml → 활성 태풍마다 per-storm 상세 파싱 → NHC 동일 스키마 storm 리스트.
    비활성/파싱 실패 시 [] 반환(전체 파이프라인 무영향). 절대 예외로 죽지 않음.
    """
    try:
        raw = _get_text(HKO_LIST_URL)
    except Exception as e:
        errors.append(f"HKO 목록 요청 실패 {type(e).__name__}: {e} — HKO 스킵")
        return []
    try:
        root = ET.fromstring(raw)
    except Exception as e:
        errors.append(f"HKO 목록 XML 파싱 실패 {type(e).__name__}: {e} — HKO 스킵")
        return []

    # <TropicalCyclone> 항목만 수집(네임스페이스 관용). 자식 노드(…ID·…Name·…URL)도
    # 태그에 'cyclone' 이 들어가 후보로 잡히던 문제 → **자식 요소를 가진 컨테이너**만 남긴다.
    entries = [e for e in root.iter()
               if "cyclone" in _local(e.tag)
               and _local(e.tag) not in ("tropicalcyclonelist",)
               and len(list(e)) > 0]
    if not entries:
        # 비활성기: 빈 <TropicalCycloneList/> → 정상. 스킵 사유 로그만.
        print("HKO: 활성 태풍 없음(tc_list.xml 비어 있음) — HKO 기여 0")
        return []

    storms = []
    for e in entries:
        kv = _node_kv(e)
        tc_id = next((kv[k] for k in kv if "id" in k), "") or ""
        name = ""
        for k in kv:
            if "name" in k and kv[k].strip():
                name = kv[k].strip()
                break
        # per-storm 링크: url/link/href 계열 키. 상대경로면 목록 URL 기준 절대화.
        url = ""
        for k in kv:
            if any(t in k for t in ("url", "link", "href")) and str(kv[k]).strip():
                url = str(kv[k]).strip()
                break
        if not url:
            errors.append(f"HKO {name or tc_id}: per-storm 링크 없음 — 스킵(실포맷 검증 필요)")
            continue
        url = urllib.parse.urljoin(HKO_LIST_URL, url)
        st = _hko_storm(tc_id, name, url, errors)
        if st and st.get("points"):
            storms.append(st)
    print(f"HKO: 활성 후보 {len(entries)}개 → 수집 {len(storms)}개")
    return storms


# ─────────────────────────────────────────────────────────────
#  JTWC (미 합동태풍경보센터) — 전 지구(미국령 밖): 서태평양·북인도양·남반구
#    RSS 로 활성 스톰 목록 → 각 스톰 경고 텍스트(products/{id}web.txt) 파싱.
#    NHC(AL/EP/CP)와 중복 방지: basin 접두어 wp/io/sh 만 취함(ep/cp=NHC, al=JTWC 미담당).
#    경고 기반이라 과거경로/원뿔은 없음 → 현재위치(마커+풍속원) + 예보경로(점선)+예보점.
# ─────────────────────────────────────────────────────────────
JTWC_RSS = "https://www.metoc.navy.mil/jtwc/rss/jtwc.rss"
JTWC_TXT = "https://www.metoc.navy.mil/jtwc/products/%sweb.txt"
JTWC_SOURCE_NOTE = ("미 합동태풍경보센터(JTWC) 공식 경고 — metoc.navy.mil "
                    "(서태평양·북인도양·남반구). 현재위치+예보(12~120h)·풍속반경. "
                    "원뿔=표준 예보오차 반경 기반 근사(JTWC는 기계판독 원뿔 미제공).")
# JTWC 표준 예보오차 반경(km): 예보시각(h) → 반경. JTWC 연평균 위치오차(nm→km, ×1.852) 근사.
#   JTWC 는 공식 예보 원뿔을 좌표/GeoJSON 으로 배포하지 않으므로(그래픽만), HKO 처럼 이 반경으로 합성.
JTWC_ERROR_RADIUS_KM = {12: 56, 24: 93, 36: 130, 48: 167, 72: 241, 96: 333, 120: 426}
JTWC_BASIN = {"wp": "WP", "io": "IO", "sh": "SH"}    # 채택 basin(나머지는 NHC 담당)
_JTWC_CATS = ["SUPER TYPHOON", "TYPHOON", "HURRICANE", "TROPICAL STORM",
              "SUBTROPICAL STORM", "TROPICAL DEPRESSION", "TROPICAL CYCLONE"]
_JTWC_POS = re.compile(r"(\d{6})Z\s*---\s*(?:NEAR\s+)?(\d+\.?\d*)([NS])\s+(\d+\.?\d*)([EW])")
_JTWC_HDR = re.compile(r"\b(" + "|".join(c.replace(" ", r"\s+") for c in _JTWC_CATS) +
                       r")\s+(\d{2}[A-Z])\s*\(([^)]+)\)", re.I)
_JTWC_FCST = re.compile(
    r"(\d{1,3})\s*HRS?,\s*VALID AT:\s*(\d{6})Z\s*---\s*(\d+\.?\d*)([NS])\s+(\d+\.?\d*)([EW])"
    r".*?MAX SUSTAINED WINDS\s*-\s*(\d+)\s*KT", re.S)
_JTWC_RAD = re.compile(
    r"RADIUS OF\s*0?(\d{2,3})\s*KT WINDS\s*-\s*(\d+)\s*NM NORTHEAST\s+(\d+)\s*NM SOUTHEAST"
    r"\s+(\d+)\s*NM SOUTHWEST\s+(\d+)\s*NM NORTHWEST", re.S)


def _jtwc_ll(latv, ns, lonv, ew):
    return [round(float(latv) * (-1 if ns == "S" else 1), 2),
            round(float(lonv) * (-1 if ew == "W" else 1), 2)]


def _jtwc_dt(dtg):
    """DDHHMMZ → UTC datetime(현재 기준 월/년 보정)."""
    now = datetime.now(timezone.utc)
    dd, hh, mm = int(dtg[:2]), int(dtg[2:4]), int(dtg[4:6])
    for md in (0, -1, 1):
        y, m = now.year, now.month + md
        if m < 1: m += 12; y -= 1
        if m > 12: m -= 12; y += 1
        try:
            t = datetime(y, m, dd, hh, mm, tzinfo=timezone.utc)
        except ValueError:
            continue
        if abs((t - now).days) <= 20:
            return t
    return now


def _jtwc_storm(sid, txt):
    """경고 텍스트 → 스톰 dict(스키마=collect_storm 과 동일 핵심 필드)."""
    hdr = _JTWC_HDR.search(txt)
    if not hdr:
        return None
    cat_raw, code, name_raw = hdr.group(1).upper(), hdr.group(2).upper(), hdr.group(3).strip()
    catmap = {"SUPER TYPHOON": "Super Typhoon", "TYPHOON": "Typhoon", "HURRICANE": "Hurricane",
              "TROPICAL STORM": "Tropical Storm", "SUBTROPICAL STORM": "Subtropical Storm",
              "TROPICAL DEPRESSION": "Tropical Depression", "TROPICAL CYCLONE": "Tropical Cyclone"}
    category = catmap.get(re.sub(r"\s+", " ", cat_raw), cat_raw.title())
    basin = JTWC_BASIN.get(sid[:2].lower())
    if not basin:
        return None
    # 현재 위치(WARNING POSITION 첫 블록)
    head = txt.split("FORECASTS:")[0]
    pm = _JTWC_POS.search(head)
    if not pm:
        return None
    cur_dt = _jtwc_dt(pm.group(1))
    cur_ll = _jtwc_ll(pm.group(2), pm.group(3), pm.group(4), pm.group(5))
    vm = re.search(r"MAX SUSTAINED WINDS\s*-\s*(\d+)\s*KT", head)
    cur_vmax = int(vm.group(1)) if vm else None
    # 현재 중심기압: "CENTRAL PRESSURE AT ...Z IS 941 MB". REMARKS(FORECASTS 뒤)에 있으므로 txt 전체 검색.
    pm = re.search(r"CENTRAL PRESSURE.*?IS\s*(\d+)\s*MB", txt)
    cur_mslp = int(pm.group(1)) if pm else None
    # 현재 풍속반경(head 구간). 없으면 null.
    radii = {}
    for r in _JTWC_RAD.finditer(head):
        band = int(r.group(1))
        radii["r%d" % band] = [int(r.group(i)) for i in (2, 3, 4, 5)]
    wind_radii = radii or None
    # 포인트: 현재(tau0) + 예보(tau12..) 모두 forecast(현재도 마커·중심 표시)
    pts = [{"kind": "forecast", "tau": 0, "lat": cur_ll[0], "lng": cur_ll[1],
            "time": cur_dt.strftime("%Y-%m-%dT%H:%M:%SZ"), "windKt": cur_vmax, "mslp": cur_mslp}]
    line = [cur_ll]
    for f in _JTWC_FCST.finditer(txt):
        tau = int(f.group(1))
        ll = _jtwc_ll(f.group(3), f.group(4), f.group(5), f.group(6))
        pts.append({"kind": "forecast", "tau": tau, "lat": ll[0], "lng": ll[1],
                    "time": (cur_dt + timedelta(hours=tau)).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "windKt": int(f.group(7))})
        line.append(ll)
    nm = name_raw.title()
    return {
        "id": sid.upper(), "slot": sid.upper(), "name": nm, "fullName": f"{code} ({nm})",
        "basin": basin, "basinLabel": BASIN_LABEL.get(basin, basin),
        "category": category, "ss": None, "maxWindKt": cur_vmax, "gustKt": None, "mslp": None,
        "advDate": cur_dt.strftime("%Y-%m-%dT%H:%M:%SZ"), "advisoryNum": "",
        "points": pts, "pastLine": [], "forecastLine": [line] if len(line) > 1 else [],
        "cone": _hko_cone(pts, JTWC_ERROR_RADIUS_KM),   # 표준 예보오차 반경 기반 근사 원뿔
        "windRadii": wind_radii, "source": JTWC_SOURCE_NOTE,
    }


def collect_jtwc(errors):
    """JTWC RSS → wp/io/sh 활성 스톰 목록 → 각 경고 텍스트 파싱. 실패해도 죽지 않음."""
    try:
        rss = _get_text(JTWC_RSS)
    except Exception as e:
        errors.append(f"JTWC RSS 실패 {type(e).__name__}: {e}")
        return []
    ids = []
    for sid in re.findall(r"products/([a-z]{2}\d{4})web\.txt", rss):
        if sid[:2].lower() in JTWC_BASIN and sid not in ids:
            ids.append(sid)
    storms = []
    for sid in ids:
        try:
            st = _jtwc_storm(sid, _get_text(JTWC_TXT % sid))
            if st and st["points"]:
                storms.append(st)
        except Exception as e:
            errors.append(f"JTWC {sid} 실패 {type(e).__name__}: {e}")
    return storms


def main():
    storms = []
    errors = []
    for pfx, base in SLOTS:
        try:
            if _count(base + OFF_FCST_PTS) <= 0:
                continue
            st = collect_storm(pfx, base)
            if st and st["points"]:
                storms.append(st)
        except Exception as e:  # 슬롯 하나 실패해도 전체는 계속
            errors.append(f"{pfx}: {type(e).__name__}: {e}")

    # 미국령 밖 전 지구(서태평양·북인도양·남반구) — JTWC 병합. 절대 예외로 죽지 않음.
    try:
        jtwc = collect_jtwc(errors)
    except Exception as e:
        errors.append(f"JTWC 최상위 예외 {type(e).__name__}: {e} — JTWC 스킵")
        jtwc = []
    storms.extend(jtwc)  # basin=WP/IO/SH, NHC(AL/EP/CP)와 중복 없음

    out = {
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": len(storms),
        "storms": storms,
        "sources": [BASE, JTWC_RSS],
        "wpacNote": ("전 지구: NHC(대서양·동/중태평양) + JTWC(서태평양·북인도양·남반구, TD 포함). "
                     "JTWC는 경고 기반이라 현재위치+예보(과거경로/원뿔 없음)."),
        "errors": errors,
    }
    OUTPUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"typhoons.json 작성: 활성 {len(storms)}개"
          + (f" ({', '.join(s['fullName'] for s in storms)})" if storms else " (활성 태풍 없음)")
          + (f" · 오류 {len(errors)}건" if errors else ""))


if __name__ == "__main__":
    main()
