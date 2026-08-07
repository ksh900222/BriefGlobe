#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
track_typhoons.py — 🌀 태풍 **모델별 진로**(GFS/ECMWF/ICON)를 자체 MSLP 에서 추적.

방법(vortex tracking, 앵커링):
  1) typhoons.json 의 활성 태풍 **현재 위치**를 시작점으로.
  2) 각 모델의 해면기압 텍스처(pressure-{model}-f{step}.png)에서, 직전 위치 주변
     탐색반경 안의 **기압 최소점**을 다음 중심으로 스텝별 추적.
  3) 최소기압이 임계 이상(소멸)이거나 급점프(추적실패)면 중단.
출력: typhoon-tracks.json = {updated, storms:[{id,name,basin,start,tracks:{gfs:[{step,lat,lon,mslp}],...}}]}

계약: pressure 텍스처는 fetch_weather.py 산출(R=MSLP, 범위 meta.pressureRange, 181x360 lat90→-90/lon-180→179).
견고성: 데이터/태풍 없거나 실패해도 안 죽고 빈/부분 결과. 정적 산출물이라 auto_update 로 갱신.
"""
import json, os, math, datetime
import numpy as np
from PIL import Image

DIR = os.path.dirname(os.path.abspath(__file__))
NLAT, NLON = 181, 360
SEARCH_DEG = 4.0        # 스텝당 중심 탐색 반경(도) — 실제 TC 이동 <~4°/6h
MAX_JUMP_DEG = 5.0      # 한 스텝 이동이 이보다 크면 추적 실패로 간주
DEPTH_MIN = 1.5         # 중심이 탐색환(ring) 평균보다 최소 이만큼 깊어야 '진짜 저기압'(평평한 골 배제)
EXCL_DEG = 3.0          # 다중 태풍 상호배제 반경(도): 한 태풍이 선점한 중심 이내는 다른 태풍이 못 씀 → 트랙 합쳐짐 방지
HARD_STOP_HPA = 1008.0  # 최소기압 상한(소멸)
FILL_MARGIN = 16.0      # 초기기압+이만큼 넘으면 채워짐(약화)으로 보고 중단(강한 태풍도 일생 추적)
HORIZON_H = 168         # 모델 진로 표시 상한(7일) — 기상 텍스처가 f168까지 있어 무료로 여기까지.
                        #   단 5일(120h) 초과분은 TC 진로 신뢰도 급락 → 프론트에서 흐린 점선으로 구분 표시.
LOWCONF_H = 120         # 이 시각(5일) 초과 진로점은 저신뢰(lowConf) 플래그 → 흐린 점선 렌더


def load_meta():
    m = json.load(open(os.path.join(DIR, "wind-meta.json"), encoding="utf-8"))
    if "pressure" not in (m.get("fields") or []):
        raise RuntimeError("meta 에 pressure 필드 없음")
    return m


def decode_pressure(model, step, prange):
    """pressure-{model}-f{step:03d}.png → MSLP(hPa) 181x360 배열(R 채널 역변환)."""
    p = os.path.join(DIR, f"pressure-{model}-f{step:03d}.png")
    if not os.path.exists(p):
        return None
    a = np.asarray(Image.open(p)).astype(np.float32)
    return a[:, :, 0] / 255.0 * (prange[1] - prange[0]) + prange[0]


def rc_of(lat, lon):
    """(lat,lon) → (row,col). lat90→-90(row0=90N), lon-180→179(col0=-180)."""
    r = int(round(90.0 - lat)); c = int(round(((lon + 180) % 360)))
    return max(0, min(NLAT - 1, r)), max(0, min(NLON - 1, c))


def find_min_near(grid, lat0, lon0, rad_deg, exclude=None):
    """(lat0,lon0) 주변 반경 내 기압 최소점 → (lat,lon,mslp,ring_mean). ring_mean=반경경계 평균(깊이 판정용). wrap 처리.
       exclude: [(lat,lon), ...] 다른 태풍이 이미 선점한 중심들. 이 근처(EXCL_DEG) 셀은 후보에서 제외(트랙 합쳐짐 방지)."""
    r0, c0 = rc_of(lat0, lon0)
    rr = int(math.ceil(rad_deg))
    best = None
    ring = []
    for dr in range(-rr, rr + 1):
        r = r0 + dr
        if r < 0 or r >= NLAT:
            continue
        lat = 90.0 - r
        for dc in range(-rr, rr + 1):
            d2 = dr * dr + dc * dc
            if d2 > rr * rr:                     # 원형 반경 밖
                continue
            c = (c0 + dc) % NLON
            lon = c - 180.0
            if exclude:                          # 다른 태풍 선점 영역 배제
                ex = False
                for (elat, elon) in exclude:
                    dl = abs(((lon - elon + 180) % 360) - 180)
                    if math.hypot(lat - elat, dl) < EXCL_DEG:
                        ex = True; break
                if ex:
                    continue
            v = float(grid[r, c])
            if best is None or v < best[2]:
                best = (lat, lon, v)
            if d2 >= (rr - 1) * (rr - 1):        # 반경 경계부 = ring(환경 기압)
                ring.append(v)
    if best is None:
        return None
    ring_mean = float(np.mean(ring)) if ring else best[2]
    return best[0], best[1], best[2], ring_mean


def current_position(storm):
    """태풍 현재 위치 = 마지막 past 점, 없으면 tau0/첫 forecast, 없으면 첫 점."""
    pts = storm.get("points") or []
    past = [p for p in pts if p.get("kind") == "past" and p.get("lat") is not None]
    if past:
        p = past[-1]
    else:
        fc = [p for p in pts if p.get("lat") is not None]
        if not fc:
            return None
        p = fc[0]
    return float(p["lat"]), float(p.get("lng", p.get("lon")))


def track_one(grid_fn, steps, lat0, lon0, mslp0):
    """한 모델의 스텝별 진로 추적. grid_fn(step)→MSLP grid(or None). mslp0=초기 기압(약화 판정 기준)."""
    track = []
    lat, lon = lat0, lon0
    fill_stop = min(HARD_STOP_HPA, (mslp0 or 1008) + FILL_MARGIN)   # 이 기압 넘으면 소멸/약화로 중단
    for st in steps:
        g = grid_fn(st)
        if g is None:
            break
        found = find_min_near(g, lat, lon, SEARCH_DEG)
        if not found:
            break
        nlat, nlon, mslp, ring = found
        # ① 급점프 → 추적 실패
        dlon = abs(((nlon - lon + 180) % 360) - 180)
        if math.hypot(nlat - lat, dlon) > MAX_JUMP_DEG:
            break
        # ② 국지최소 깊이 부족(평평한 골) → 진짜 저기압 아님, 중단
        if ring - mslp < DEPTH_MIN:
            break
        # ③ 약화/소멸(첫 스텝은 시작 허용)
        if st > 0 and mslp > fill_stop:
            break
        track.append({"step": st, "lat": round(nlat, 2), "lon": round(nlon, 2), "mslp": round(mslp)})
        lat, lon = nlat, nlon
    return track


def track_all(grid_fn, steps, seeds):
    """여러 태풍을 한 모델에서 '동시' 추적하며 상호 배제 → 각 태풍의 트랙 리스트(입력 순서 유지).
       seeds: [(lat0,lon0,mslp0), ...]. 매 스텝, 강한(깊은) 태풍부터 저기압을 선점하고, 이후 태풍은
       그 선점 중심 근처(EXCL_DEG)를 제외해 탐색 → 두 태풍이 같은 저기압으로 수렴해 트랙이 합쳐지는 것 방지.
       자기 저기압이 사라져(선점영역 밖에 유효 최소 없음) 못 찾으면 그 태풍은 그 스텝에서 종료(약한 쪽 흡수)."""
    n = len(seeds)
    tracks = [[] for _ in range(n)]
    pos = [(s[0], s[1]) for s in seeds]
    fill_stop = [min(HARD_STOP_HPA, (s[2] if s[2] is not None else 1008) + FILL_MARGIN) for s in seeds]
    active = [True] * n
    # 깊은(강한) 태풍 먼저 선점 → 공유 저기압은 강한 쪽이 갖고 약한 쪽이 밀려남/종료
    order = sorted(range(n), key=lambda i: (seeds[i][2] if seeds[i][2] is not None else 9999.0))
    for st in steps:
        g = grid_fn(st)
        if g is None:
            break
        claimed = []
        for i in order:
            if not active[i]:
                continue
            found = find_min_near(g, pos[i][0], pos[i][1], SEARCH_DEG, exclude=claimed)
            if not found:
                active[i] = False; continue
            nlat, nlon, mslp, ring = found
            dlon = abs(((nlon - pos[i][1] + 180) % 360) - 180)
            if math.hypot(nlat - pos[i][0], dlon) > MAX_JUMP_DEG:
                active[i] = False; continue
            if ring - mslp < DEPTH_MIN:
                active[i] = False; continue
            if st > 0 and mslp > fill_stop[i]:
                active[i] = False; continue
            tracks[i].append({"step": st, "lat": round(nlat, 2), "lon": round(nlon, 2), "mslp": round(mslp)})
            pos[i] = (nlat, nlon)
            claimed.append((nlat, nlon))
    return tracks


def main():
    try:
        meta = load_meta()
    except Exception as e:
        print(f"[track_typhoons] meta 실패: {e}")
        _write({"updated": None, "storms": [], "note": str(e)})
        return
    prange = meta.get("pressureRange", [920, 1080])
    steps = [s["step"] for s in meta["steps"] if s["step"] <= HORIZON_H]   # 7일까지(120h 초과분은 프론트에서 저신뢰 점선)
    models = [m["key"] for m in meta["models"]]

    try:
        typ = json.load(open(os.path.join(DIR, "typhoons.json"), encoding="utf-8"))
    except Exception as e:
        print(f"[track_typhoons] typhoons.json 없음: {e}")
        _write({"updated": meta.get("updated"), "storms": []})
        return
    storms_in = typ.get("storms") or []

    # 모델별 grid 캐시(스텝 재사용)
    cache = {}
    def grid_fn(model):
        def f(step):
            key = (model, step)
            if key not in cache:
                cache[key] = decode_pressure(model, step, prange)
            return cache[key]
        return f

    # 모든 태풍의 시드(현재위치·초기기압) 수집
    seeds, smeta = [], []
    for s in storms_in:
        cur = current_position(s)
        if not cur:
            continue
        lat0, lon0 = cur
        mslp0 = s.get("mslp")
        try: mslp0 = float(mslp0) if mslp0 is not None else None
        except (TypeError, ValueError): mslp0 = None
        seeds.append((lat0, lon0, mslp0)); smeta.append(s)

    # 모델별로 전체 태풍을 '동시' 추적(상호배제) → 인덱스별 트랙. 두 태풍이 같은 저기압으로 합쳐짐 방지.
    model_tracks = {model: track_all(grid_fn(model), steps, seeds) for model in models}

    out_storms = []
    for idx, s in enumerate(smeta):
        tracks = {}
        for model in models:
            tr = model_tracks[model][idx]
            if len(tr) >= 2:                     # 최소 2점 있어야 선
                tracks[model] = tr
        if tracks:
            lat0, lon0, _ = seeds[idx]
            out_storms.append({
                "id": s.get("id"), "name": s.get("name"), "fullName": s.get("fullName"),
                "basin": s.get("basin"), "basinLabel": s.get("basinLabel"),
                "start": {"lat": round(lat0, 2), "lon": round(lon0, 2)},
                "tracks": tracks,
            })
        print(f"[track_typhoons] {s.get('name')}: " +
              ", ".join(f"{m}={len(model_tracks[m][idx])}pt" for m in models))

    _write({
        "updated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "cycle": {m["key"]: m["cycle"] for m in meta["models"]},
        "steps": steps,
        "storms": out_storms,
    })
    print(f"[track_typhoons] {len(out_storms)} storms tracked → typhoon-tracks.json")


def _write(obj):
    with open(os.path.join(DIR, "typhoon-tracks.json"), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
