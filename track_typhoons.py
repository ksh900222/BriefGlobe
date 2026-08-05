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


def find_min_near(grid, lat0, lon0, rad_deg):
    """(lat0,lon0) 주변 반경 내 기압 최소점 → (lat,lon,mslp,ring_mean). ring_mean=반경경계 평균(깊이 판정용). wrap 처리."""
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
            v = float(grid[r, c])
            if best is None or v < best[2]:
                best = (lat, c - 180.0, v)
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

    out_storms = []
    for s in storms_in:
        cur = current_position(s)
        if not cur:
            continue
        lat0, lon0 = cur
        mslp0 = s.get("mslp")
        try: mslp0 = float(mslp0) if mslp0 is not None else None
        except (TypeError, ValueError): mslp0 = None
        tracks = {}
        for model in models:
            tr = track_one(grid_fn(model), steps, lat0, lon0, mslp0)
            if len(tr) >= 2:                     # 최소 2점 있어야 선
                tracks[model] = tr
        if tracks:
            out_storms.append({
                "id": s.get("id"), "name": s.get("name"), "fullName": s.get("fullName"),
                "basin": s.get("basin"), "basinLabel": s.get("basinLabel"),
                "start": {"lat": round(lat0, 2), "lon": round(lon0, 2)},
                "tracks": tracks,
            })
        print(f"[track_typhoons] {s.get('name')}: " +
              ", ".join(f"{m}={len(tracks.get(m,[]))}pt" for m in models))

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
