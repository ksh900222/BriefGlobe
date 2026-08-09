#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
track_typhoons.py — 🌀 태풍 **모델별 진로**(GFS/ECMWF/AI-GFS)를 각 기관의 **공식 보텍스 트래커
산출물**에서 가져온다.

왜 자체추적을 버렸나
--------------------
이전 버전은 기상 오버레이용 기압 텍스처(pressure-{model}-f{step}.png, 1° 격자)에서 MSLP 최소점을
직접 따라가는 DIY 추적이었다. 강한 태풍 옆에 약한 태풍이 오면 약한 쪽 추적기가 '반경 내 최소점'
규칙 때문에 자기 얕은 저기압을 버리고 옆의 깊은 중심으로 넘어가, 두 태풍 트랙이 완전히 겹쳤다
(실측: Kujira 25kt 가 Dolphin 85kt 로 흡수 → 24h 이후 두 트랙 거리 0km). 상호배제·수렴시 종료
등을 시도했으나 전부 다른 부작용(지그재그, 조기소멸)을 낳아 접었다.

각 기관은 이미 자기 모델에 대해 제대로 된 보텍스 트래커를 돌려 **태풍별로 분리된** 경로를
발표한다. 그걸 그대로 받아쓰면 합쳐짐이 원천 차단된다(태풍마다 고유 스톰번호/이름 보유).

데이터 소스 (전부 무료·재배포 가능)
-----------------------------------
· GFS    : NCEP 글로벌 보텍스 트래커 ATCF — NOMADS, 미 공공도메인
           .../ens_tracker/prod/gfs.YYYYMMDD/HH/tctrack/avno.tHHz.cyclone.trackatcfunix
· AI-GFS : 같은 트래커를 NCEP AI 모델에 적용 — 동일 경로 aigfs.../agfs.tHHz...
· ECMWF  : ECMWF Open Data TC 트랙 BUFR (CC-BY-4.0)
           data.ecmwf.int/forecasts/YYYYMMDD/HHz/ifs/0p25/oper/*-360h-oper-tf.bufr
           → eccodes CLI(bufr_dump)로 디코드. 파이썬 eccodes 바인딩 불필요.

ICON 은 DWD 가 TC 트랙 산출물을 공개하지 않아(격자 GRIB·그림 차트만) 사용 불가 → AI-GFS 로 대체.

태풍 매칭: typhoons.json(JTWC/NHC 공식)의 활성 태풍 ↔ 소스의 스톰번호(ATCF) / 이름(BUFR).
  ECMWF 는 자체 번호를 붙여 JTWC 번호와 어긋나므로(예: JTWC 12W Dolphin = ECMWF 15W DOLPHIN)
  이름 우선 매칭. 어느 쪽도 안 맞으면 해석시각(t=0) 위치 최근접으로 폴백.

출력: typhoon-tracks.json = {updated, cycle:{model:ISO}, steps:[...],
        storms:[{id,name,basin,start,tracks:{gfs:[{step,lat,lon,mslp}],ecmwf:[...],aigfs:[...]}}]}
  — 스키마는 이전과 동일(프론트 glDrawTyphoonModels 무변경 가능). 모델 키만 icon→aigfs.

견고성: 소스 하나가 죽어도 나머지로 진행. 전부 실패해도 빈 결과를 쓰고 정상 종료(파이프라인 무영향).
"""
import json, os, re, math, subprocess, datetime, urllib.request, urllib.error

DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(DIR, "typhoon-tracks.json")

HORIZON_H = 168     # 표시 상한(7일). ATCF 는 240h 까지 주지만 프론트 계약(steps)에 맞춰 자른다.
                    #   120h 초과분은 프론트에서 흐린 점선(저신뢰)으로 구분 렌더.
STEP_H = 6
STEPS = list(range(0, HORIZON_H + 1, STEP_H))

MAX_CYCLE_BACK = 6          # 최신 사이클부터 이만큼 뒤로 물러나며 탐색(데이터 지연 대비)
MATCH_KM = 550.0            # 위치 폴백 매칭 허용 반경
TIMEOUT = 60

NOMADS = "https://nomads.ncep.noaa.gov/pub/data/nccf/com/ens_tracker/prod"
# (출력 모델키, NOMADS 디렉터리 접두, ATCF 파일 접두)
ATCF_MODELS = [("gfs", "gfs", "avno"), ("aigfs", "aigfs", "agfs")]
ECMWF_BASE = "https://data.ecmwf.int/forecasts"

UA = {"User-Agent": "BriefGlobe/1.0 (typhoon model tracks; contact via github)"}


# ─────────────────────────────── 공통 유틸 ───────────────────────────────

def _get(url, binary=False):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        raw = r.read()
    return raw if binary else raw.decode("utf-8", "replace")


def km_dist(lat1, lon1, lat2, lon2):
    dlon = abs(((lon2 - lon1 + 180) % 360) - 180)
    return math.hypot((lat2 - lat1) * 111.0,
                      dlon * 111.0 * math.cos(math.radians((lat1 + lat2) / 2)))


def recent_cycles(now=None, every=6):
    """현재시각 기준 최신 사이클부터 과거로 (datetime, ...) 나열. every=6 → 00/06/12/18Z."""
    now = now or datetime.datetime.now(datetime.timezone.utc)
    h = (now.hour // every) * every
    base = now.replace(hour=h, minute=0, second=0, microsecond=0)
    return [base - datetime.timedelta(hours=every * i) for i in range(MAX_CYCLE_BACK)]


# ─────────────────────────── ATCF (GFS · AI-GFS) ───────────────────────────

def parse_atcf(text):
    """ATCF a-deck/atcfunix 텍스트 → {(basin, num): {tau: {lat,lon,vmax,mslp}}}.

    한 tau 에 34/50/64kt 풍속반경 행이 중복 등장하므로 tau 별 첫 행만 취한다.
    좌표는 십분의1도 정수+반구문자: '268N'→26.8N, '1317E'→131.7E, 'W'→음수.
    """
    storms = {}
    for line in text.splitlines():
        f = [x.strip() for x in line.split(",")]
        if len(f) < 10:
            continue
        basin, num = f[0].upper(), f[1]
        if not re.fullmatch(r"[A-Z]{2}", basin) or not num.isdigit():
            continue
        try:
            tau = int(f[5])
        except ValueError:
            continue
        if tau < 0 or tau > HORIZON_H or tau % STEP_H:
            continue
        m_lat = re.fullmatch(r"(\d+)([NS])", f[6])
        m_lon = re.fullmatch(r"(\d+)([EW])", f[7])
        if not (m_lat and m_lon):
            continue
        lat = int(m_lat.group(1)) / 10.0 * (1 if m_lat.group(2) == "N" else -1)
        lon = int(m_lon.group(1)) / 10.0 * (1 if m_lon.group(2) == "E" else -1)
        if lon > 180:
            lon -= 360
        def _num(s):
            try:
                v = int(s)
                return v if v > 0 else None      # ATCF 결측 = 0 또는 -99
            except ValueError:
                return None
        rec = storms.setdefault((basin, int(num)), {})
        if tau not in rec:
            rec[tau] = {"lat": lat, "lon": lon, "vmax": _num(f[8]), "mslp": _num(f[9])}
    return storms


def fetch_atcf(dir_prefix, file_prefix, errors):
    """최신 사이클부터 뒤로 탐색해 ATCF 를 받는다 → (storms, cycle_dt) / (None, None)."""
    for cyc in recent_cycles():
        url = (f"{NOMADS}/{dir_prefix}.{cyc:%Y%m%d}/{cyc:%H}/tctrack/"
               f"{file_prefix}.t{cyc:%H}z.cyclone.trackatcfunix")
        try:
            txt = _get(url)
        except urllib.error.HTTPError as e:
            if e.code not in (403, 404):   # 아직 안 나온 사이클 = 404, NOMADS 는 403 을 주기도 함
                errors.append(f"{file_prefix} {cyc:%Y%m%d%H}: HTTP {e.code}")
            continue
        except Exception as e:
            errors.append(f"{file_prefix} {cyc:%Y%m%d%H}: {type(e).__name__}: {e}")
            continue
        st = parse_atcf(txt)
        if st:
            return st, cyc
    return None, None


# ──────────────────────────── ECMWF TC 트랙 BUFR ────────────────────────────

def parse_tf_bufr(path):
    """ECMWF TC 트랙 BUFR → [{'sid','name','points':{tau:{lat,lon,mslp}}}].

    bufr_dump -p 출력(키=값)을 문서순 상태머신으로 읽는다. 메시지(=태풍 1개) 경계는 'edition='.
    한 시각 블록 구조:
        [#k#timePeriod=H]                     ← t=0 블록에는 없음
        #n#meteorologicalAttributeSignificance=1   ← 1 = 태풍 중심
        #n#latitude / #n#longitude
        #n#pressureReducedToMeanSeaLevel=Pa        ← 중심기압(sig=5 위치 블록 뒤에 오기도 함)
        #n#meteorologicalAttributeSignificance=3   ← 최대풍 위치(사용 안 함)
    """
    try:
        out = subprocess.run(["bufr_dump", "-p", path], capture_output=True,
                             text=True, timeout=180).stdout
    except Exception:
        return []

    storms, cur = [], None
    tau, sig, lat = 0, None, None
    for line in out.splitlines():
        if "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = re.sub(r"^#\d+#", "", key.strip())
        val = val.strip()

        if key == "edition":                      # 새 메시지 = 새 태풍
            cur = None
            tau, sig, lat = 0, None, None
            continue
        if key == "stormIdentifier":
            cur = {"sid": val.strip('"').strip(), "name": "", "points": {}}
            storms.append(cur)
            continue
        if cur is None:
            continue
        if key == "longStormName":
            cur["name"] = val.strip('"').strip()
        elif key == "timePeriod":
            try:
                tau = int(val)
            except ValueError:
                tau = None
            sig, lat = None, None
        elif key == "meteorologicalAttributeSignificance":
            sig = val
            lat = None
        elif key == "latitude":
            lat = None if val == "MISSING" else float(val)
        elif key == "longitude":
            if sig == "1" and lat is not None and val != "MISSING" and tau is not None:
                lon = float(val)
                if lon > 180:
                    lon -= 360
                cur["points"].setdefault(tau, {}).update({"lat": lat, "lon": lon})
            lat = None
        elif key == "pressureReducedToMeanSeaLevel":
            if val != "MISSING" and tau is not None and tau in cur["points"]:
                try:
                    cur["points"][tau]["mslp"] = round(float(val) / 100.0)
                except ValueError:
                    pass
    return [s for s in storms if s["points"]]


def fetch_ecmwf(errors):
    """ECMWF HRES TC 트랙 BUFR → ({name_or_sid: {tau:{...}}}, cycle_dt) / (None, None).

    360h HRES 는 00/12Z 만 나오므로 12시간 간격으로 탐색한다.
    """
    tmp = os.path.join(DIR, ".tc-tracks.bufr.tmp")
    for cyc in recent_cycles(every=12):
        url = (f"{ECMWF_BASE}/{cyc:%Y%m%d}/{cyc:%H}z/ifs/0p25/oper/"
               f"{cyc:%Y%m%d%H}0000-360h-oper-tf.bufr")
        try:
            raw = _get(url, binary=True)
        except urllib.error.HTTPError as e:
            if e.code not in (403, 404):   # 아직 안 나온 사이클 = 404, NOMADS 는 403 을 주기도 함
                errors.append(f"ecmwf {cyc:%Y%m%d%H}: HTTP {e.code}")
            continue
        except Exception as e:
            errors.append(f"ecmwf {cyc:%Y%m%d%H}: {type(e).__name__}: {e}")
            continue
        try:
            with open(tmp, "wb") as f:
                f.write(raw)
            storms = parse_tf_bufr(tmp)
        finally:
            try:
                os.remove(tmp)
            except OSError:
                pass
        if storms:
            return storms, cyc
        errors.append(f"ecmwf {cyc:%Y%m%d%H}: BUFR 파싱 결과 없음")
    return None, None


# ───────────────────────────── 태풍 매칭 ─────────────────────────────

def storm_key(s):
    """typhoons.json storm → (basin, 스톰번호) — ATCF 매칭용. 못 구하면 (basin, None)."""
    basin = (s.get("basin") or "").upper()
    num = None
    m = re.match(r"^([A-Z]{2})(\d{2})", (s.get("id") or "").upper())
    if m and m.group(1) == basin:
        num = int(m.group(2))
    if num is None:                                     # fullName '12W (Dolphin)' 폴백
        m = re.match(r"^(\d{1,2})[A-Z]\b", (s.get("fullName") or "").upper())
        if m:
            num = int(m.group(1))
    return basin, num


def current_position(storm):
    """태풍 현재 위치 = 마지막 past 점, 없으면 첫 점(JTWC 는 past 없이 tau0 부터)."""
    pts = storm.get("points") or []
    past = [p for p in pts if p.get("kind") == "past" and p.get("lat") is not None]
    cand = past[-1] if past else next((p for p in pts if p.get("lat") is not None), None)
    if not cand:
        return None
    return float(cand["lat"]), float(cand.get("lng", cand.get("lon")))


def pick_atcf(atcf, storm, pos):
    """활성 태풍 하나에 대응하는 ATCF 트랙 선택: (basin,num) 우선 → t=0 위치 최근접 폴백."""
    basin, num = storm_key(storm)
    if num is not None and (basin, num) in atcf:
        return atcf[(basin, num)]
    if not pos:
        return None
    best, best_km = None, MATCH_KM
    for (b, _n), rec in atcf.items():
        if basin and b != basin:
            continue
        p0 = rec.get(0) or rec.get(min(rec))
        if not p0:
            continue
        d = km_dist(pos[0], pos[1], p0["lat"], p0["lon"])
        if d < best_km:
            best, best_km = rec, d
    return best


def pick_ecmwf(ec_storms, storm, pos):
    """ECMWF BUFR 트랙 선택: 이름 일치 우선(번호는 JTWC 와 어긋남) → t=0 위치 최근접 폴백."""
    name = (storm.get("name") or "").strip().upper()
    if name:
        for s in ec_storms:
            if s["name"].strip().upper() == name:
                return s["points"]
    if not pos:
        return None
    best, best_km = None, MATCH_KM
    for s in ec_storms:
        p0 = s["points"].get(0) or s["points"].get(min(s["points"]))
        if not p0:
            continue
        d = km_dist(pos[0], pos[1], p0["lat"], p0["lon"])
        if d < best_km:
            best, best_km = s["points"], d
    return best


def to_track(points):
    """{tau:{lat,lon,mslp}} → 프론트 계약의 [{step,lat,lon,mslp}] (STEPS 격자, 시간순)."""
    out = []
    for st in STEPS:
        p = points.get(st)
        if not p or p.get("lat") is None or p.get("lon") is None:
            continue
        out.append({"step": st, "lat": round(p["lat"], 2), "lon": round(p["lon"], 2),
                    "mslp": p.get("mslp")})
    return out


# ──────────────────────────────── main ────────────────────────────────

def main():
    errors = []

    try:
        typ = json.load(open(os.path.join(DIR, "typhoons.json"), encoding="utf-8"))
        storms_in = typ.get("storms") or []
    except Exception as e:
        print(f"[track_typhoons] typhoons.json 없음: {e}")
        _write({"updated": _now(), "cycle": {}, "steps": STEPS, "storms": [],
                "errors": [f"typhoons.json: {e}"]})
        return

    if not storms_in:
        print("[track_typhoons] 활성 태풍 없음")
        _write({"updated": _now(), "cycle": {}, "steps": STEPS, "storms": []})
        return

    # 소스 수집 — 하나가 실패해도 나머지로 진행
    sources, cycles = {}, {}
    for key, dprefix, fprefix in ATCF_MODELS:
        st, cyc = fetch_atcf(dprefix, fprefix, errors)
        if st:
            sources[key] = st
            cycles[key] = cyc.isoformat()
            print(f"[track_typhoons] {key}: {cyc:%Y-%m-%d %HZ} · {len(st)} storms")
        else:
            errors.append(f"{key}: 사용 가능한 사이클 없음")
    ec, ec_cyc = fetch_ecmwf(errors)
    if ec:
        sources["ecmwf"] = ec
        cycles["ecmwf"] = ec_cyc.isoformat()
        print(f"[track_typhoons] ecmwf: {ec_cyc:%Y-%m-%d %HZ} · {len(ec)} storms")
    else:
        errors.append("ecmwf: 사용 가능한 사이클 없음")

    out_storms = []
    for s in storms_in:
        pos = current_position(s)
        tracks = {}
        for key in ("gfs", "ecmwf", "aigfs"):
            src = sources.get(key)
            if not src:
                continue
            pts = pick_ecmwf(src, s, pos) if key == "ecmwf" else pick_atcf(src, s, pos)
            if not pts:
                continue
            tr = to_track(pts)
            if len(tr) >= 2:                 # 최소 2점 있어야 선을 그린다
                tracks[key] = tr
        if tracks:
            out_storms.append({
                "id": s.get("id"), "name": s.get("name"), "fullName": s.get("fullName"),
                "basin": s.get("basin"), "basinLabel": s.get("basinLabel"),
                "start": ({"lat": round(pos[0], 2), "lon": round(pos[1], 2)} if pos else None),
                "tracks": tracks,
            })
        print(f"[track_typhoons] {s.get('name')}: " +
              ", ".join(f"{m}={len(tracks.get(m, []))}pt" for m in ("gfs", "ecmwf", "aigfs")))

    _write({
        "updated": _now(),
        "cycle": cycles,
        "steps": STEPS,
        "storms": out_storms,
        "source": ("모델 진로 = 각 기관 공식 보텍스 트래커 산출물. "
                   "GFS·AI-GFS: NCEP 글로벌 트래커 ATCF(NOMADS, 미 공공도메인). "
                   "ECMWF: ECMWF Open Data TC 트랙 BUFR(CC-BY-4.0). "
                   "태풍별로 분리 산출되어 인접 태풍이 섞이지 않음."),
        "errors": errors,
    })
    print(f"[track_typhoons] {len(out_storms)} storms → typhoon-tracks.json"
          + (f" · 오류 {len(errors)}건" if errors else ""))


def _now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def _write(obj):
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
