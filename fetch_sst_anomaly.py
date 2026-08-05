#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_sst_anomaly.py · 해수면 이상수온(SST anomaly) + 엘니뇨/라니냐(ENSO) 상태
------------------------------------------------------------
 - OISST v2.1 NRT(NOAA, 관측분석·2일 지연) 이상수온 격자를 CoastWatch ERDDAP(HTTP CSV)로 받아
   기상 텍스처 계약(181×360, lat 90→-90, lon -180→179, R=값·A=바다마스크)에 맞춰 sst-anom.png 생성.
 - 엘니뇨 공식지수 ONI(NOAA CPC, ERSSTv5 기반) 텍스트를 파싱해 현재 국면·강도를 enso-status.json 으로.
 예보 아님(관측분석) → 모델/스텝 없음. 단일 텍스처 1장. 하루 1회 갱신이면 충분.
 새 파이썬 의존성 없음(urllib+numpy+PIL). 재배포 안전(NOAA 공공도메인).
"""
import json, math, socket, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path
import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
socket.setdefaulttimeout(90)

# 텍스처 격자 계약(fetch_weather.py 와 동일): NLAT=181(90→-90, 위=북), NLON=360(-180→179, 열0=-180)
NLAT, NLON = 181, 360
ANOM_RANGE = [-4.0, 4.0]      # 이상수온 색맵 범위(°C, 발산). 대부분 ±3 내, 극단 클립
TEX_PATH = HERE / "sst-anom.png"
JSON_PATH = HERE / "enso-status.json"

# NRT(근실시간, 2일 지연). 없으면 Final(2주 지연)로 폴백.
ERDDAP = "https://coastwatch.pfeg.noaa.gov/erddap/griddap"
OISST_NRT = "ncdcOisst21NrtAgg_LonPM180"
OISST_FINAL = "ncdcOisst21Agg_LonPM180"
# ONI(Oceanic Niño Index) — 공식 엘니뇨/라니냐 판정(ERSSTv5, Niño3.4)
ONI_URL = "https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt"


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "briefglobe-sst-anom/1.0"})
    with urllib.request.urlopen(req) as r:
        return r.read().decode("utf-8", "replace")


def fetch_oisst_grid():
    """ERDDAP CSV 로 전지구 anom(1° stride) → (181×360 값, 바다마스크, 데이터날짜). 실패 시 예외."""
    # stride 4 * 0.25° = 1°. lat -89.875..89.875(180), lon -179.875..179.875(360)
    q = "%5B(last)%5D%5B(0.0)%5D%5B(-89.875):4:(89.875)%5D%5B(-179.875):4:(179.875)%5D"
    last_err = None
    for ds in (OISST_NRT, OISST_FINAL):
        try:
            txt = _get(f"{ERDDAP}/{ds}.csv?anom{q}")
        except Exception as e:
            last_err = e; continue
        lines = txt.splitlines()
        if len(lines) < 3 or not lines[0].startswith("time"):
            last_err = RuntimeError(f"{ds}: 예상 CSV 아님"); continue
        # O[la][lo]: la=0..179(lat -89.875..89.875 오름), lo=0..359(lon -179.875..179.875 오름)
        O = np.full((180, 360), np.nan, dtype=np.float32)
        data_date = None
        for ln in lines[2:]:
            p = ln.split(",")
            if len(p) < 5:
                continue
            if data_date is None:
                data_date = p[0][:10]     # 2026-08-02T12:00:00Z → 2026-08-02
            try:
                lat, lon, v = float(p[2]), float(p[3]), p[4].strip()
            except ValueError:
                continue
            la = int(round(lat + 89.875)); lo = int(round(lon + 179.875))
            if 0 <= la < 180 and 0 <= lo < 360:
                O[la, lo] = np.nan if (v == "" or v.upper() == "NAN") else float(v)
        if np.isfinite(O).sum() < 1000:
            last_err = RuntimeError(f"{ds}: 유효값 부족"); continue
        # 앱 격자(181×360, lat 90→-90, lon -180→179)로 최근접 리샘플
        G = np.full((NLAT, NLON), np.nan, dtype=np.float32)
        for i in range(NLAT):
            app_lat = 90 - i
            la = min(179, max(0, int(round(app_lat + 89.875))))
            for j in range(NLON):
                app_lon = -180 + j
                lo = min(359, max(0, int(round(app_lon + 179.875))))
                G[i, j] = O[la, lo]
        # 빙하 가장자리·내해에서 나오는 극단 이상치(|anom|>8°C)는 아티팩트로 보고 마스킹
        mask = np.isfinite(G) & (np.abs(G) <= 8.0)
        return G, mask, data_date, ("NRT" if ds == OISST_NRT else "Final")
    raise last_err or RuntimeError("OISST 접근 실패")


def encode_masked(val, vmin, vmax, mask, path):
    """마스크 스칼라(181×360) → RGBA PNG(R=값 선형[vmin,vmax], G=0, B=255, A=mask?255:0).
    fetch_weather.py encode_scalar_masked_save 와 동일 계약 → 프론트가 SST와 같은 방식으로 디코드."""
    v = np.nan_to_num(val, nan=(vmin + vmax) / 2.0)
    R = np.clip((v - vmin) / (vmax - vmin) * 255.0, 0, 255).astype(np.uint8)
    G = np.zeros_like(R); B = np.full_like(R, 255)
    A = np.where(mask, 255, 0).astype(np.uint8)
    Image.fromarray(np.dstack([R, G, B, A]), "RGBA").save(path)


def classify_enso(oni):
    """ONI 값 → (국면, 강도). ±0.5 문턱, |ONI| 로 강도(공식은 event peak 기준이나 현재값 근사)."""
    a = abs(oni)
    level = "약" if a < 1.0 else ("중간" if a < 1.5 else ("강" if a < 2.0 else "매우 강"))
    if oni >= 0.5:
        return "엘니뇨", level
    if oni <= -0.5:
        return "라니냐", level
    return "중립", "-"


def fetch_oni():
    """oni.ascii.txt 마지막 줄(최근 3개월 시즌) → (값, 시즌라벨). 형식: SEAS YR TOTAL ANOM."""
    txt = _get(ONI_URL)
    rows = [ln.split() for ln in txt.splitlines() if ln.strip()]
    for r in reversed(rows):
        if len(r) >= 4:
            try:
                val = float(r[3])
            except ValueError:
                continue
            return val, f"{r[0]} {r[1]}"     # 예: "AMJ 2026"
    raise RuntimeError("ONI 파싱 실패")


def main():
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    # ① OISST 이상수온 텍스처
    G, mask, sst_date, src_tag = fetch_oisst_grid()
    encode_masked(G, ANOM_RANGE[0], ANOM_RANGE[1], mask, TEX_PATH)
    print(f"✔ sst-anom.png 생성: OISST {src_tag} {sst_date} · 유효 {int(mask.sum())}셀 · "
          f"범위 {np.nanmin(G):.1f}~{np.nanmax(G):.1f}°C")
    # ② ENSO 상태(ONI)
    try:
        oni, season = fetch_oni()
        phase, level = classify_enso(oni)
        oni_ok = True
    except Exception as e:
        oni, season, phase, level, oni_ok = None, None, None, None, False
        print(f"  ⚠ ONI 파싱 실패({e}) — 상태 라벨 없이 진행")
    status = {
        "updated": now,
        "sst": {"date": sst_date, "source": f"NOAA OISST v2.1 {src_tag}", "range": ANOM_RANGE},
        "oni": ({"value": round(oni, 2), "season": season, "phase": phase, "level": level,
                 "source": "NOAA CPC ONI (ERSSTv5·Niño3.4)"} if oni_ok else None),
    }
    JSON_PATH.write_text(json.dumps(status, ensure_ascii=False, indent=1), encoding="utf-8")
    if oni_ok:
        print(f"✔ enso-status.json: {phase}({level}) · ONI {oni:+.2f} [{season}]")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"✗ 실패: {e}", file=sys.stderr); sys.exit(1)
