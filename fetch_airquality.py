#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
 fetch_airquality.py · CAMS 대기질 → 텍스처 PNG (aq-*.png) + aq-meta.json
------------------------------------------------------------
 유럽 코페르니쿠스 CAMS(ECMWF) 전지구 대기조성 예보에서 지표 농도를 받아
 PM2.5·PM10·NO2·SO2·O3·CO 6종을 자체 텍스처(R=값 선형)로 인코딩한다.
 기상(fetch_weather.py)과 동일 아키텍처 — 지구본 색칠 + 마커 픽셀 역산 공용.

 데이터: ADS(Atmosphere Data Store) `cams-global-atmospheric-composition-forecasts`.
   · PM2.5/PM10 = single level(지표) kg/m³
   · NO2/SO2/O3/CO = model_level 137(최하층) kg/kg 질량혼합비 → 농도 환산
 인증: ~/.adsapirc (url + key). 라이선스 사전 동의 필요(1회).
 CAMS 발표: 하루 2회(00·12 UTC). 이 스크립트는 leadtime 0(실황 근사)만 사용.

 출처표시(CC-BY 필수): "대기질 — CAMS / Copernicus Atmosphere Monitoring Service (ECMWF)"

 사용:  python3 fetch_airquality.py
 (독립 launchd 잡 권장 — 매시간 파이프라인과 분리, 하루 몇 회)
============================================================
"""
import json
import os
import sys
import numpy as np
from pathlib import Path

import fetch_weather as fw   # read_values, encode_scalar_save, fill_holes 재사용

HERE = Path(__file__).resolve().parent
DIR = HERE
GLAT, GLON = 451, 900       # CAMS 0.4° 전지구 (위도 90..-90, 경도 0..359.6)
ADS_DATASET = "cams-global-atmospheric-composition-forecasts"
# 예보 스텝(발표 사이클 기준 시간). CAMS global 은 최대 120h(5일). 기상(6h 간격)과 통일.
STEPS = list(range(0, 121, 6))   # 0,6,...,120 = 21스텝

# 지표 근처 공기 밀도(kg/m³) — 질량혼합비(kg/kg)→농도(μg/m³) 근사 환산용.
#   정밀히는 온도·기압 의존이나 지표 표준값으로 충분(대기질 등급 판정 목적).
AIR_DENSITY = 1.2

# (cdsapi 변수명, GRIB shortName, 레벨종류, μg/m³ 환산계수, [vmin,vmax] 인코딩 범위)
#   single: kg/m³ ×1e9 = μg/m³ · ml137: kg/kg ×(ρ·1e9) = μg/m³
AQ_VARS = [
    ("particulate_matter_2.5um", "pm2p5", "single", 1e9,               [0, 200], "PM2.5"),
    ("particulate_matter_10um",  "pm10",  "single", 1e9,               [0, 400], "PM10"),
    ("nitrogen_dioxide",         "no2",   "ml137",  AIR_DENSITY * 1e9, [0, 200], "NO2"),
    ("sulphur_dioxide",          "so2",   "ml137",  AIR_DENSITY * 1e9, [0, 350], "SO2"),
    ("ozone",                    "go3",   "ml137",  AIR_DENSITY * 1e9, [0, 300], "O3"),
    ("carbon_monoxide",          "co",    "ml137",  AIR_DENSITY * 1e9, [0, 15000], "CO"),
]


def _client():
    import cdsapi
    rc = {}
    p = Path.home() / ".adsapirc"
    if not p.exists():
        raise RuntimeError("~/.adsapirc 없음 — ADS 키 등록 필요")
    for line in p.read_text().splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            rc[k.strip()] = v.strip()
    return cdsapi.Client(url=rc["url"], key=rc["key"])


def _cams_dates():
    """최신 발표일 우선 후보(오늘→그제). 오늘 00Z 발표가 준비됐으면 그게 예보오차 최소(leadtime 짧음).
       아직이면 즉시 invalid 로 떨어져 어제로 폴백(값은 어제 발표+예보로 현재 시각 커버)."""
    import datetime
    today = datetime.datetime.now(datetime.timezone.utc).date()
    return [(today - datetime.timedelta(days=k)).isoformat() for k in (0, 1, 2)]


def _download(client):
    """single(PM) + ml137(가스) 두 요청, 각각 전 예보스텝(0~120h) 한 번에.
       최신 발표일 우선 폴백. (single, ml, cycle_iso) 반환."""
    single, ml = "/tmp/cams_single.grib", "/tmp/cams_ml137.grib"
    lts = [str(s) for s in STEPS]
    last_err = None
    for dt in _cams_dates():
        common = {"date": f"{dt}/{dt}", "time": ["00:00"], "leadtime_hour": lts,
                  "type": ["forecast"], "data_format": "grib"}
        try:
            client.retrieve(ADS_DATASET, {**common,
                "variable": [v[0] for v in AQ_VARS if v[2] == "single"]}, single)
            client.retrieve(ADS_DATASET, {**common, "model_level": ["137"],
                "variable": [v[0] for v in AQ_VARS if v[2] == "ml137"]}, ml)
            print(f"  · CAMS 발표일 {dt} 00Z · {len(STEPS)}스텝(0~120h)")
            return single, ml, f"{dt}T00:00:00Z"
        except Exception as e:
            last_err = e
            sys.stderr.write(f"[aq] {dt} 불가({str(e)[:60]}) → 이전 발표일 시도\n")
    raise RuntimeError(f"CAMS 가용 발표일 없음: {last_err}")


def _to_grid(vals, factor):
    """CAMS 전지구 1D → (451,900) 격자, 경도 0..360→-180..180 roll, ×factor(μg/m³)."""
    a = np.asarray(vals, float)
    if a.size != GLAT * GLON:
        raise RuntimeError(f"CAMS 격자 크기 {a.size} (기대 {GLAT*GLON})")
    g = a.reshape(GLAT, GLON) * factor
    return np.roll(g, GLON // 2, axis=1)     # 0°시작 → -180°시작


def main():
    try:
        client = _client()
    except Exception as e:
        sys.stderr.write(f"[aq] ADS 클라이언트 실패: {e}\n")
        return
    try:
        single, ml, cycle = _download(client)
    except Exception as e:
        sys.stderr.write(f"[aq] CAMS 다운로드 실패: {e}\n")
        return

    meta_vars, made = [], set()
    for cds_name, sn, lvl, factor, rng, label in AQ_VARS:
        src = single if lvl == "single" else ml
        ok = 0
        for step in STEPS:
            try:
                g = _to_grid(fw.read_values(src, f"shortName={sn},stepRange={step}"), factor)
                g = np.clip(np.nan_to_num(g, nan=0.0), rng[0], rng[1])
                fw.encode_scalar_save(g, rng[0], rng[1], str(DIR / f"aq-{sn}-f{step:03d}.png"))
                ok += 1
            except Exception as e:
                sys.stderr.write(f"[aq] {label} f{step:03d} 실패: {str(e)[:50]}\n")
        if ok:
            meta_vars.append({"key": sn, "label": label, "range": rng, "unit": "μg/m³"})
            made.add(sn)
            print(f"  ✓ {label}({sn}): {ok}/{len(STEPS)}스텝 → aq-{sn}-f*.png")

    if not meta_vars:
        print("✖ 대기질 텍스처 0개 — aq-meta.json 미갱신")
        return
    import datetime
    stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    (DIR / "aq-meta.json").write_text(json.dumps({
        "updated": stamp, "cycle": cycle,
        "grid": {"lat": GLAT, "lon": GLON, "res": 0.4},
        "steps": [{"step": s, "hours": s} for s in STEPS],
        "source": "CAMS / Copernicus Atmosphere Monitoring Service (ECMWF)",
        "vars": meta_vars,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"✔ aq-meta.json: {len(meta_vars)}종 × {len(STEPS)}스텝 · cycle={cycle}")
    # 옛 단일-시각 텍스처(aq-{sn}.png) 정리
    for sn in made:
        try: os.remove(DIR / f"aq-{sn}.png")
        except OSError: pass
    for f in ("/tmp/cams_single.grib", "/tmp/cams_ml137.grib"):
        try: os.remove(f)
        except OSError: pass


if __name__ == "__main__":
    main()
