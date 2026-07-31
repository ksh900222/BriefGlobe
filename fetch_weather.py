#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_weather.py — 💨 지구본 '흐르는 바람 입자'용 **다모델·다층·다시각(예보) 바람 텍스처** 생성.

모델(3): GFS(NOAA 1°) · ECMWF IFS(open-data 0.25°) · ICON(DWD 비정형→재격자)
고도(4): 지상10m · 850 · 500 · 250 hPa
예보(기본 29): f000..f168 6시간 간격 (미래 예측)

출력(모델×고도×시각 별 plate carrée PNG, RGBA):
  wind-{model}-{level}-f{step:03d}.png
    · R = u(동서), G = v(남북)  → 고도별 **고정** velocityRange 로 0-255 정규화(모델·스텝 공유)
    · B = 255 (유효 마스크) · A = 255
  wind-meta.json = {
    updated, bounds:[-180,90,180,-90],
    models:[{key,label,source,cycle}], levels:[{key,label,velocityRange,unit}],
    steps:[{step,hours}], filePattern
  }
  프론트: 유효시각 = model.cycle + step*1h.  velocityRange 는 레벨별 고정값(인코딩과 일치).

격자 계약: NLAT=181(lat 90→-90, 위=북), NLON=360(lon -180→179, 열0=-180).
견고성: 어느 모델/스텝/레벨이 실패해도 그 텍스처만 건너뛰고(또는 합성 폴백) 나머지는 진행.
       한 모델이 전면 실패하면 meta.models 에서 제외(프론트가 자동으로 안 보여줌).
정적 파일이라 auto_update 주기 또는 수동 갱신. ICON CLAT/CLON 은 로컬 캐시(.npy) 후 재사용.

CLI(테스트용): --models gfs,ecmwf,icon  --steps 0,6,12  --max-step 168
"""
import argparse, bz2, datetime, json, math, os, socket, subprocess, sys, urllib.request
import numpy as np
from PIL import Image

# 모든 소켓 작업에 기본 타임아웃 — GFS urlretrieve(타임아웃 인자 없음) 포함.
#   NOAA 서버가 연결만 받고 데이터를 안 주면 무한 대기하던 문제 방지(파이프라인 락 hang의 원인).
socket.setdefaulttimeout(120)

DIR = os.path.dirname(os.path.abspath(__file__))
GRIB_GET = "/opt/homebrew/bin/grib_get_data"
NLAT, NLON = 181, 360
# 고해상도 격자(0.25°). 구름·강수는 국지성이 커 필수, 바람·기온도 배경 색래스터 화질을 위해 상향.
#   ECMWF: 이미 0.25° 다운로드 → 다운샘플 폐지(_ec_full, 추가 다운로드 0)
#   ICON:  원본 ~13km → 0.25° 재격자(icon_field_hi, 추가 다운로드 0)
#   GFS:   본 파일이 1°(pgrb2.1p00)라 바람·기온은 1° 유지(0.25°는 0p25 대용량 다운로드 필요).
#          구름·강수만 0p25 서브셋(gfs_hi_download)으로 0.25°.
HLAT, HLON = 721, 1440

# 구름 렌더 변수 — GFS·ICON 은 **구름물(cloud water, kg/m²)**, ECMWF 는 전운량(%)만 제공.
#   전운량(TCDC)은 지구 절반이 ≥93%로 포화돼 흰 판이 되지만, 구름물은 연속분포라
#   두꺼운 적란운/얇은 층운의 명암이 살아난다(진함 51%→5%, 중간톤 20%→36%).
#   동적범위가 커(중앙 0.01·최대 ~5) **log10 으로 인코딩**해 저농도 계조를 보존한다.
CLOUD_VAR = {"gfs": "water", "ecmwf": "cover", "icon": "water"}
CLOUDW_LOG_RANGE = [-3.0, 0.7]        # log10(kg/m²): 0.001 ~ 5.01

# ── 고도별 고정 velocityRange(대칭 ±m/s). 모델·스텝 공유 → 프론트는 레벨만 보면 됨.
#    상층 제트가 강해 위로 갈수록 넓게. 극단 폭풍은 드물게 클립되나 입자 시각화엔 무방. ──
# temp 은 SCALAR — 고도별 **고정 온도범위(°C)** 로 정규화. 10m 레벨은 지상 2m 기온을 씀.
#   gfs_t = grib_get_data -w 필터(2m=2t / 기압면=t,level=L)
#   icon_t = (dir, 파일태그, kind) — 2m=t_2m/T_2M/single-level, 기압면=t/{L}_T/pressure-level
LEVELS = [
    {"key": "10m", "label": "지상 10m",        "range": 35.0, "tempRange": [-40.0, 45.0],
     "gfs": "shortName=10u|shortName=10v",  "ec_lt": "sfc", "ec_lev": None,
     "icon_dir": ("u_10m", "v_10m"), "icon_kind": "single-level", "icon_tag": ("U_10M", "V_10M"),
     "gfs_t": "shortName=2t", "icon_t": ("t_2m", "T_2M", "single-level")},
    {"key": "850", "label": "850hPa (~1.5km)", "range": 50.0, "tempRange": [-35.0, 35.0],
     "gfs": "shortName=u,level=850|shortName=v,level=850", "ec_lt": "pl", "ec_lev": 850,
     "icon_dir": ("u", "v"), "icon_kind": "pressure-level", "icon_tag": ("850_U", "850_V"),
     "gfs_t": "shortName=t,level=850", "icon_t": ("t", "850_T", "pressure-level")},
    {"key": "500", "label": "500hPa (~5.5km)", "range": 75.0, "tempRange": [-45.0, 20.0],
     "gfs": "shortName=u,level=500|shortName=v,level=500", "ec_lt": "pl", "ec_lev": 500,
     "icon_dir": ("u", "v"), "icon_kind": "pressure-level", "icon_tag": ("500_U", "500_V"),
     "gfs_t": "shortName=t,level=500", "icon_t": ("t", "500_T", "pressure-level")},
    {"key": "250", "label": "250hPa 제트 (~10km)", "range": 120.0, "tempRange": [-70.0, -20.0],
     "gfs": "shortName=u,level=250|shortName=v,level=250", "ec_lt": "pl", "ec_lev": 250,
     "icon_dir": ("u", "v"), "icon_kind": "pressure-level", "icon_tag": ("250_U", "250_V"),
     "gfs_t": "shortName=t,level=250", "icon_t": ("t", "250_T", "pressure-level")},
]
MODELS = [
    {"key": "gfs",   "label": "GFS",   "source": "NOAA"},
    {"key": "ecmwf", "label": "ECMWF", "source": "ECMWF IFS"},
    {"key": "icon",  "label": "ICON",  "source": "DWD"},
]

# ── 추가 스칼라 필드(고도 무관, 모델×스텝) 고정 인코딩 범위 ──
PRESSURE_RANGE = [920.0, 1080.0]   # 해면기압 MSLP (hPa) — 등압선용, 넉넉히
PRECIP_RANGE   = [0.0, 30.0]       # 강수강도 (mm/h) — 0 근처가 대부분(팔레트가 처리)
SST_RANGE      = [-2.0, 34.0]      # 해수면온도 (°C, 바다만)
SST_MASK_LO, SST_MASK_HI = -5.0, 40.0   # 이 범위 밖(결측·육지 표면온도)은 A=0 마스크


# ─────────────────────────── 공용 ───────────────────────────
def read_values(path, wfilter=None, missing=None):
    """grib_get_data → float 배열(Value 열). 비정형(ICON)은 Value 만, 정형은 lat/lon/value.
    missing 지정 시 grib_get_data -m 로 결측셀을 그 값(예 9999)으로 채워 **격자 크기 유지**
    (기본은 결측셀을 건너뛰어 크기가 어긋남 — SST 등 마스크 필드는 반드시 missing 지정)."""
    cmd = [GRIB_GET]
    if missing is not None:
        cmd += ["-m", str(missing)]
    if wfilter:
        cmd += ["-w", wfilter]
    cmd += [path]
    out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True)
    # 방어적 파싱: 마지막 열이 float 인 줄만 값으로. 헤더("Latitude Longitude Value"/"Value")는
    # 스킵하되, **값을 읽기 시작한 뒤 다시 헤더(비-float)를 만나면 중단**(다중 메시지면 첫 메시지만).
    vals = []
    for ln in out.splitlines():
        p = ln.split()
        if not p:
            continue
        try:
            v = float(p[-1])
        except ValueError:
            if vals:            # 두 번째 메시지 헤더 → 첫 메시지만 사용
                break
            continue            # 첫 헤더 스킵
        vals.append(v)
    if not vals:
        raise RuntimeError("grib 값 없음(필터 불일치?)")
    return np.asarray(vals, np.float32)


def encode_and_save(U, V, rng, path):
    """U,V(181x360) → RGBA PNG(R=u,G=v,B=255,A=255), 고정 ±rng 정규화."""
    def enc(a):
        return np.clip((a + rng) / (2 * rng) * 255.0, 0, 255).astype(np.uint8)
    U = np.nan_to_num(U, nan=0.0); V = np.nan_to_num(V, nan=0.0)
    R, G = enc(U), enc(V)
    B = np.full_like(R, 255); A = np.full_like(R, 255)
    Image.fromarray(np.dstack([R, G, B, A]), "RGBA").save(path)


def encode_scalar_save(val, vmin, vmax, path):
    """스칼라 필드(181x360) → RGBA PNG(R=값, G=0, B=255 마스크, A=255), 고정 [vmin,vmax] 정규화.
    프론트는 R 채널만 읽어 vmin..vmax 로 역변환. NaN 은 범위 중앙으로."""
    val = np.nan_to_num(val, nan=(vmin + vmax) / 2.0)
    R = np.clip((val - vmin) / (vmax - vmin) * 255.0, 0, 255).astype(np.uint8)
    G = np.zeros_like(R)
    B = np.full_like(R, 255); A = np.full_like(R, 255)
    Image.fromarray(np.dstack([R, G, B, A]), "RGBA").save(path)


def encode_scalar_masked_save(val, vmin, vmax, mask, path):
    """마스크 스칼라(181x360) → RGBA PNG(R=값, G=0, B=255, A=mask?255:0).
    바다만 유효한 SST 등에 사용. mask=False 셀은 A=0(투명) — fill_holes 적용 금지."""
    val = np.nan_to_num(val, nan=(vmin + vmax) / 2.0)
    R = np.clip((val - vmin) / (vmax - vmin) * 255.0, 0, 255).astype(np.uint8)
    G = np.zeros_like(R)
    B = np.full_like(R, 255)
    A = np.where(mask, 255, 0).astype(np.uint8)
    Image.fromarray(np.dstack([R, G, B, A]), "RGBA").save(path)


def encode_cloudwater_save(val, path):
    """구름물(kg/m²) → log10 스케일로 R 채널 저장. 프론트는 imageUnscale=CLOUDW_LOG_RANGE 로 역변환."""
    lo, hi = CLOUDW_LOG_RANGE
    v = np.clip(np.nan_to_num(np.asarray(val, np.float32), nan=0.0), 10.0 ** lo, 10.0 ** hi)
    encode_scalar_save(np.log10(v), lo, hi, path)


def precip_rate_from_accum(cur, prev, to_mm):
    """누적강수(cur,prev) 차분 → mm/h 강도. to_mm: 누적단위→mm 배수(ECMWF m→1000, ICON mm→1).
    6h 간격 가정(÷6). 음수(수치잡음)는 0으로 클립."""
    inten = (cur - prev) * to_mm / 6.0
    return np.clip(inten, 0.0, None)


def to_celsius(a):
    """기온 단위 자동 통일 → °C. 값이 ~250-320 이면 켈빈으로 보고 -273.15."""
    m = float(np.nanmean(a))
    return a - 273.15 if m > 100.0 else a


def to_percent(a):
    """전운량 단위 자동 통일 → %(0-100). 최댓값이 ≤1.5 면 0-1 분율로 보고 ×100."""
    mx = float(np.nanmax(a))
    return a * 100.0 if mx <= 1.5 else a


def fill_holes(g):
    """NaN 셀을 같은 위도행 평균으로 채움(극지 소수 홀 대비). 행 전체 NaN 이면 0."""
    g = g.copy()
    for r in range(g.shape[0]):
        row = g[r]
        m = np.isnan(row)
        if m.any():
            valid = row[~m]
            row[m] = valid.mean() if valid.size else 0.0
    return g


# ─────────────────────────── GFS ───────────────────────────
def gfs_cycles(now=None):
    now = now or datetime.datetime.now(datetime.timezone.utc)
    base = (now - datetime.timedelta(hours=5)).replace(minute=0, second=0, microsecond=0)
    base = base.replace(hour=(base.hour // 6) * 6)
    return [base - datetime.timedelta(hours=6 * k) for k in range(4)]


def gfs_download(steps):
    """가용 최신 GFS 사이클의 요청 스텝들을 받아 {step: gribpath} + cycle(datetime) 반환."""
    # wind(UGRD/VGRD@10m/850/500/250) + temp(TMP@2m/850/500/250) + cloud(TCDC@entire atm)
    #  + pressure(PRMSL@mean sea level) + precip(PRATE@surface) + sst(TMP@surface=skin, LAND 마스크) 를 한 요청에.
    #  (1° pgrb2 에 WTMP 는 없음 → 지표 skin TMP 를 쓰고 lsm==육지 셀은 마스크)
    lev = ("&lev_10_m_above_ground=on&lev_2_m_above_ground=on"
           "&lev_850_mb=on&lev_500_mb=on&lev_250_mb=on&lev_entire_atmosphere=on"
           "&lev_mean_sea_level=on&lev_surface=on")
    for cyc in gfs_cycles():
        ymd, hh = cyc.strftime("%Y%m%d"), cyc.strftime("%H")
        paths, ok = {}, True
        for st in steps:
            url = ("https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_1p00.pl"
                   f"?dir=%2Fgfs.{ymd}%2F{hh}%2Fatmos&file=gfs.t{hh}z.pgrb2.1p00.f{st:03d}"
                   "&var_UGRD=on&var_VGRD=on&var_TMP=on&var_TCDC=on"
                   "&var_PRMSL=on&var_PRATE=on&var_LAND=on" + lev)
            p = f"/tmp/gfs_{st:03d}.grib2"
            try:
                urllib.request.urlretrieve(url, p)
                if os.path.getsize(p) < 50000:
                    raise RuntimeError("too small")
                paths[st] = p
            except Exception as e:
                sys.stderr.write(f"[gfs] {ymd}/{hh}z f{st:03d} 실패: {e}\n")
                ok = False; break
        if ok and paths:
            print(f"[gfs] cycle {ymd}/{hh}z, {len(paths)} steps")
            return paths, cyc.replace(tzinfo=datetime.timezone.utc)
        for p in paths.values():
            try: os.remove(p)
            except OSError: pass
    return {}, None


def gfs_uv(path, lv):
    """GFS grib → (U,V) 181x360. lon 0..359 → roll 180(열0=-180)."""
    uf, vf = lv["gfs"].split("|")
    def grid(f):
        a = read_values(path, f)
        if a.size != NLAT * NLON:
            raise RuntimeError(f"gfs 크기 {a.size}")
        return np.roll(a.reshape(NLAT, NLON), NLON // 2, axis=1)
    return grid(uf), grid(vf)


def gfs_scalar(path, wfilter, missing=None):
    """GFS grib 단일 스칼라 → 181x360. lon 0..359 → roll 180(열0=-180)."""
    a = read_values(path, wfilter, missing=missing)
    if a.size != NLAT * NLON:
        raise RuntimeError(f"gfs scalar 크기 {a.size}")
    return np.roll(a.reshape(NLAT, NLON), NLON // 2, axis=1)


def gfs_hi_download(cyc, st):
    """GFS 0.25° 서브셋 다운로드 → 경로. 구름·강수(TCDC/PRATE/CWAT) + 바람·기온(UGRD/VGRD/TMP@4층).
       1° 본 파일(1p00)과 별도 요청. 바람·기온 0.25° 상향으로 스텝당 ~10MB(0p25 격자 11.5×).
       실패하면 호출부가 1° 본 파일로 폴백."""
    ymd, hh = cyc.strftime("%Y%m%d"), cyc.strftime("%H")
    url = ("https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl"
           f"?dir=%2Fgfs.{ymd}%2F{hh}%2Fatmos&file=gfs.t{hh}z.pgrb2.0p25.f{st:03d}"
           "&var_TCDC=on&var_PRATE=on&var_CWAT=on"
           "&var_UGRD=on&var_VGRD=on&var_TMP=on"           # 바람·기온 0.25° 상향
           "&lev_entire_atmosphere=on&lev_surface=on"
           "&lev_entire_atmosphere_%28considered_as_a_single_layer%29=on"   # CWAT 는 이 레벨에 있음
           "&lev_10_m_above_ground=on&lev_2_m_above_ground=on"              # 10m 바람 · 2m 기온
           "&lev_850_mb=on&lev_500_mb=on&lev_250_mb=on")                    # 상층 바람·기온
    p = f"/tmp/gfs_hi_{st:03d}.grib2"
    urllib.request.urlretrieve(url, p)
    if os.path.getsize(p) < 20000:
        raise RuntimeError("too small")
    return p


def gfs_uv_hi(path, lv):
    """GFS 0.25° grib → (U,V) 721x1440. lon 0..359.75 → roll 720(열0=-180)."""
    uf, vf = lv["gfs"].split("|")
    def grid(f):
        a = read_values(path, f)
        if a.size != HLAT * HLON:
            raise RuntimeError(f"gfs hi uv 크기 {a.size}")
        return np.roll(a.reshape(HLAT, HLON), HLON // 2, axis=1)
    return grid(uf), grid(vf)


def gfs_scalar_hi(path, wfilter, missing=None):
    """GFS 0.25° grib 스칼라 → 721x1440(열0=-180)."""
    a = read_values(path, wfilter, missing=missing)
    if a.size != HLAT * HLON:
        raise RuntimeError(f"gfs hi scalar 크기 {a.size}")
    return np.roll(a.reshape(HLAT, HLON), HLON // 2, axis=1)


# ─────────────────────────── ECMWF ───────────────────────────
def ecmwf_setup():
    from ecmwf.opendata import Client
    return Client(source="ecmwf")


def ecmwf_cycle(client):
    try:
        return client.latest(type="fc", param="10u", step=0)
    except Exception:
        return None


def ecmwf_download(client, steps):
    """스텝별 sfc(10u/10v/2t)+pl(u/v/t@lvls)+cld(tcc) grib 다운로드 → {step:(sfc,pl,cld)}.
    cld 는 독립 요청(실패해도 wind/temp 유지). sfc/pl 실패 시 그 스텝 전체 스킵."""
    paths = {}
    for st in steps:
        sfc, pl = f"/tmp/ec_sfc_{st:03d}.grib2", f"/tmp/ec_pl_{st:03d}.grib2"
        cld = f"/tmp/ec_cld_{st:03d}.grib2"
        try:
            client.retrieve(type="fc", step=st,
                            param=["10u", "10v", "2t", "msl", "skt", "lsm", "tp"], target=sfc)
            client.retrieve(type="fc", step=st, levtype="pl", levelist=[250, 500, 850],
                            param=["u", "v", "t"], target=pl)
        except Exception as e:
            sys.stderr.write(f"[ecmwf] f{st:03d} 실패: {e}\n")
            continue
        try:
            client.retrieve(type="fc", step=st, param=["tcc"], target=cld)
        except Exception as e:
            sys.stderr.write(f"[ecmwf] f{st:03d} cloud 실패: {e}\n")
            cld = None
        paths[st] = (sfc, pl, cld)
    return paths


def _ec_ds(a):
    """ECMWF 0.25°(1440x721, lat90..-90, lon-180..179.75) → [::4] 다운샘플 181x360."""
    if a.size != 1440 * 721:
        raise RuntimeError(f"ecmwf 크기 {a.size}")
    return a.reshape(721, 1440)[::4, ::4]


def _ec_full(a):
    """ECMWF 0.25° → 원본 그대로 721x1440(다운샘플 없이 고해상 유지). 바람·기온 배경용."""
    if a.size != 1440 * 721:
        raise RuntimeError(f"ecmwf 크기 {a.size}")
    return a.reshape(721, 1440)


def ecmwf_uv(sfc, pl, lv):
    if lv["ec_lt"] == "sfc":
        u = read_values(sfc, "shortName=10u"); v = read_values(sfc, "shortName=10v")
    else:
        L = lv["ec_lev"]
        u = read_values(pl, f"shortName=u,level={L}"); v = read_values(pl, f"shortName=v,level={L}")
    return _ec_full(u), _ec_full(v)   # 0.25° 원본 유지(다운샘플 폐지) — 배경·입자 고해상


def ecmwf_scalar(path, wfilter, missing=None):
    """ECMWF 단일 스칼라 → 다운샘플 181x360."""
    return _ec_ds(read_values(path, wfilter, missing=missing))


def ecmwf_scalar_hi(path, wfilter, missing=None):
    """ECMWF 단일 스칼라 → 원본 0.25° 그대로 721x1440(구름·강수용, 다운샘플 생략)."""
    a = read_values(path, wfilter, missing=missing)
    if a.size != HLAT * HLON:
        raise RuntimeError(f"ecmwf hi 크기 {a.size}")
    return a.reshape(HLAT, HLON)


# ─────────────────────────── ICON ───────────────────────────
ICON_BASE = "https://opendata.dwd.de/weather/nwp/icon/grib"
_ICON_ROW = _ICON_COL = None                          # 재격자 인덱스 캐시(프로세스 내)
_ICON_ROW_HI = _ICON_COL_HI = None                    # 0.25° 인덱스(구름·강수)


def icon_cycles(now=None):
    # ICON global: 00/12Z 런만 180h(7일+)까지 제공, 06/18Z 는 120h 뿐 → 7일 커버 위해 00/12 만 사용.
    now = now or datetime.datetime.now(datetime.timezone.utc)
    base = (now - datetime.timedelta(hours=5)).replace(minute=0, second=0, microsecond=0)
    base = base.replace(hour=(base.hour // 12) * 12)
    return [base - datetime.timedelta(hours=12 * k) for k in range(3)]


def _dl_bz2(url, out):
    with urllib.request.urlopen(url, timeout=120) as r:
        data = bz2.decompress(r.read())
    with open(out, "wb") as f:
        f.write(data)


def icon_latlon_index(cyc):
    """CLAT/CLON(시불변) 로 각 셀의 (row,col) 인덱스 계산. 로컬 .npy 캐시."""
    global _ICON_ROW, _ICON_COL, _ICON_ROW_HI, _ICON_COL_HI
    if _ICON_ROW is not None:
        return
    rc = os.path.join(DIR, "icon_regrid_index.npz")
    if os.path.exists(rc):
        d = np.load(rc)
        _ICON_ROW, _ICON_COL = d["row"], d["col"]
        if "row_hi" in d.files:                       # 구버전 캐시엔 없음 → 아래에서 재생성
            _ICON_ROW_HI, _ICON_COL_HI = d["row_hi"], d["col_hi"]
            return
        os.remove(rc)                                  # hi 인덱스 없는 캐시는 버리고 재생성
        _ICON_ROW = _ICON_COL = None
    ymd, hh = cyc.strftime("%Y%m%d"), cyc.strftime("%H")
    lat = lon = None
    for name, tag in (("clat", "CLAT"), ("clon", "CLON")):
        url = f"{ICON_BASE}/{hh}/{name}/icon_global_icosahedral_time-invariant_{ymd}{hh}_{tag}.grib2.bz2"
        tmp = f"/tmp/icon_{name}.grib2"
        _dl_bz2(url, tmp)
        v = read_values(tmp)
        if name == "clat": lat = v
        else: lon = ((v + 180) % 360) - 180
    row = np.clip(np.round(90 - lat).astype(int), 0, NLAT - 1)
    col = np.clip(np.round(lon + 180).astype(int), 0, NLON - 1)
    _ICON_ROW, _ICON_COL = row, col
    # 구름·강수용 0.25° 인덱스도 같은 좌표에서 함께 생성(ICON 원본 ~13km라 0.25°도 충분히 조밀)
    _ICON_ROW_HI = np.clip(np.round((90 - lat) * 4).astype(np.int32), 0, HLAT - 1)
    _ICON_COL_HI = np.clip(np.round((lon + 180) * 4).astype(np.int32), 0, HLON - 1)
    np.savez(rc, row=row, col=col, row_hi=_ICON_ROW_HI, col_hi=_ICON_COL_HI)
    print(f"[icon] 재격자 인덱스 생성·캐시({row.size} 셀, 1°+0.25°)")


def icon_regrid(vals):
    idx = _ICON_ROW * NLON + _ICON_COL
    s = np.bincount(idx, weights=vals, minlength=NLAT * NLON)
    c = np.bincount(idx, minlength=NLAT * NLON)
    g = np.where(c > 0, s / np.maximum(c, 1), np.nan).reshape(NLAT, NLON)
    return fill_holes(g)


def icon_regrid_hi(vals):
    """0.25° 재격자(구름·강수). 인덱스 캐시에 hi 가 없으면(구버전 캐시) RuntimeError → 호출부가 1°로 폴백."""
    if _ICON_ROW_HI is None:
        raise RuntimeError("icon hi 인덱스 없음")
    idx = _ICON_ROW_HI * HLON + _ICON_COL_HI
    s = np.bincount(idx, weights=vals, minlength=HLAT * HLON)
    c = np.bincount(idx, minlength=HLAT * HLON)
    g = np.where(c > 0, s / np.maximum(c, 1), np.nan).reshape(HLAT, HLON)
    return fill_holes(g)


def icon_field(cyc, st, vdir, vtag, kind):
    """ICON 단일 필드 bz2 다운로드→재격자 181x360(temp/cloud/wind 공용, 같은 인덱스 재사용)."""
    ymd, hh = cyc.strftime("%Y%m%d"), cyc.strftime("%H")
    url = (f"{ICON_BASE}/{hh}/{vdir}/"
           f"icon_global_icosahedral_{kind}_{ymd}{hh}_{st:03d}_{vtag}.grib2.bz2")
    tmp = f"/tmp/icon_{vdir}_{vtag}_{st:03d}.grib2"
    _dl_bz2(url, tmp)
    v = read_values(tmp)
    try: os.remove(tmp)
    except OSError: pass
    return icon_regrid(v)


def icon_field_hi(cyc, st, vdir, vtag, kind):
    """ICON 단일 필드 → 0.25° 재격자(구름·강수 전용). 다운로드는 icon_field 와 동일."""
    ymd, hh = cyc.strftime("%Y%m%d"), cyc.strftime("%H")
    url = (f"{ICON_BASE}/{hh}/{vdir}/"
           f"icon_global_icosahedral_{kind}_{ymd}{hh}_{st:03d}_{vtag}.grib2.bz2")
    tmp = f"/tmp/icon_hi_{vdir}_{vtag}_{st:03d}.grib2"
    _dl_bz2(url, tmp)
    v = read_values(tmp)
    try: os.remove(tmp)
    except OSError: pass
    return icon_regrid_hi(v)


_ICON_OCEAN = None                                    # 바다 마스크 캐시(시불변 fr_land)


def icon_ocean_mask(cyc):
    """ICON 시불변 FR_LAND(육지분율) 재격자 → 바다 마스크(fr_land<0.5). t_s 는 육지서도 유효
    (지표온도)하므로 SST 용 육지 마스크가 필수. icon_latlon_index 선행 필요."""
    global _ICON_OCEAN
    if _ICON_OCEAN is not None:
        return _ICON_OCEAN
    ymd, hh = cyc.strftime("%Y%m%d"), cyc.strftime("%H")
    url = (f"{ICON_BASE}/{hh}/fr_land/"
           f"icon_global_icosahedral_time-invariant_{ymd}{hh}_FR_LAND.grib2.bz2")
    tmp = "/tmp/icon_fr_land.grib2"
    _dl_bz2(url, tmp)
    v = read_values(tmp)
    try: os.remove(tmp)
    except OSError: pass
    frland = icon_regrid(v)                            # 0..1
    _ICON_OCEAN = np.isfinite(frland) & (frland < 0.5)
    return _ICON_OCEAN


def icon_uv(cyc, st, lv):
    """ICON 필드 2개(u,v) 다운로드→0.25° 재격자 721x1440(원본 ~13km라 0.25°도 충분히 조밀). 배경·입자 고해상."""
    (ud, vd), kind, (utag, vtag) = lv["icon_dir"], lv["icon_kind"], lv["icon_tag"]
    return icon_field_hi(cyc, st, ud, utag, kind), icon_field_hi(cyc, st, vd, vtag, kind)


def icon_probe(steps):
    """가용 ICON 사이클 탐색 — **마지막(최대) 스텝** u_10m HEAD 로 전체 범위 완비 확인."""
    for cyc in icon_cycles():
        ymd, hh = cyc.strftime("%Y%m%d"), cyc.strftime("%H")
        url = (f"{ICON_BASE}/{hh}/u_10m/"
               f"icon_global_icosahedral_single-level_{ymd}{hh}_{steps[-1]:03d}_U_10M.grib2.bz2")
        try:
            req = urllib.request.Request(url, method="HEAD")
            with urllib.request.urlopen(req, timeout=30) as r:
                if r.status == 200:
                    return cyc.replace(tzinfo=datetime.timezone.utc)
        except Exception:
            continue
    return None


# ─────────────────────────── main ───────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", default="gfs,ecmwf,icon")
    ap.add_argument("--steps", default="")
    ap.add_argument("--max-step", type=int, default=168)
    args = ap.parse_args()
    want = [m.strip() for m in args.models.split(",") if m.strip()]
    if args.steps:
        steps = [int(s) for s in args.steps.split(",")]
    else:
        steps = list(range(0, args.max_step + 1, 6))    # f000..f168 6h = 29
    print(f"[fetch_weather] models={want} steps={len(steps)}({steps[0]}..{steps[-1]})")

    models_meta, ok_models = [], set()
    got_temp, got_cloud = set(), set()      # temp/cloud 를 실제로 하나라도 만든 모델
    got_pressure, got_precip, got_sst = set(), set(), set()  # 추가 3필드 성공 모델

    # GFS
    if "gfs" in want:
        gp, cyc = gfs_download(steps)
        if gp:
            for st, path in gp.items():
                # 0.25° 서브셋을 먼저 받는다(바람·기온·구름·강수 공용). 실패하면 1° 본 파일로 폴백.
                hi = None
                try:
                    hi = gfs_hi_download(cyc, st)
                except Exception as e:
                    sys.stderr.write(f"[gfs] f{st:03d} 0.25° 서브셋 실패({str(e)[:40]}) → 1° 폴백\n")
                for lv in LEVELS:
                    try:
                        U, V = gfs_uv_hi(hi, lv) if hi else gfs_uv(path, lv)   # 0.25° 우선, 없으면 1°
                        encode_and_save(U, V, lv["range"],
                                        os.path.join(DIR, f"wind-gfs-{lv['key']}-f{st:03d}.png"))
                    except Exception as e:
                        sys.stderr.write(f"[gfs] f{st:03d} {lv['key']} 실패: {e}\n")
                    try:
                        T = to_celsius(gfs_scalar_hi(hi, lv["gfs_t"]) if hi else gfs_scalar(path, lv["gfs_t"]))
                        encode_scalar_save(T, lv["tempRange"][0], lv["tempRange"][1],
                                           os.path.join(DIR, f"temp-gfs-{lv['key']}-f{st:03d}.png"))
                        got_temp.add("gfs")
                    except Exception as e:
                        sys.stderr.write(f"[gfs] f{st:03d} {lv['key']} temp 실패: {e}\n")
                # 구름 = 구름물(CWAT, kg/m²) — 전운량보다 명암이 살아남. 실패 시 전운량(%)로 폴백.
                try:
                    if hi:
                        W = gfs_scalar_hi(hi, "shortName=cwat")
                        encode_cloudwater_save(W, os.path.join(DIR, f"cloud-gfs-f{st:03d}.png"))
                    else:
                        # tcc 는 기압면에도 존재 → 전대기(atmosphere) 층만 선택
                        C = to_percent(gfs_scalar(path, "shortName=tcc,typeOfLevel=atmosphere"))
                        encode_scalar_save(C, 0.0, 100.0,
                                           os.path.join(DIR, f"cloud-gfs-f{st:03d}.png"))
                        CLOUD_VAR["gfs"] = "cover"      # 폴백 시 프론트가 % 로 해석하도록
                    got_cloud.add("gfs")
                except Exception as e:
                    sys.stderr.write(f"[gfs] f{st:03d} cloud 실패: {e}\n")
                # pressure(PRMSL Pa→hPa)
                try:
                    P = gfs_scalar(path, "shortName=prmsl") / 100.0
                    encode_scalar_save(P, PRESSURE_RANGE[0], PRESSURE_RANGE[1],
                                       os.path.join(DIR, f"pressure-gfs-f{st:03d}.png"))
                    got_pressure.add("gfs")
                except Exception as e:
                    sys.stderr.write(f"[gfs] f{st:03d} pressure 실패: {e}\n")
                # precip(PRATE kg/m²/s → ×3600 mm/h, 순간값이라 차분 불필요)
                try:
                    src = (lambda f: gfs_scalar_hi(hi, f)) if hi else (lambda f: gfs_scalar(path, f))
                    PR = np.clip(src("shortName=prate") * 3600.0, 0.0, None)
                    encode_scalar_save(PR, PRECIP_RANGE[0], PRECIP_RANGE[1],
                                       os.path.join(DIR, f"precip-gfs-f{st:03d}.png"))
                    got_precip.add("gfs")
                except Exception as e:
                    sys.stderr.write(f"[gfs] f{st:03d} precip 실패: {e}\n")
                if hi:
                    try: os.remove(hi)
                    except OSError: pass
                # sst(지표 skin TMP K→°C, lsm(육지=1) 마스크 → 바다만)
                try:
                    S = to_celsius(gfs_scalar(path, "shortName=t,typeOfLevel=surface"))
                    lsm = gfs_scalar(path, "shortName=lsm,typeOfLevel=surface")
                    mask = (lsm < 0.5) & np.isfinite(S) & (S > SST_MASK_LO) & (S < SST_MASK_HI)
                    encode_scalar_masked_save(S, SST_RANGE[0], SST_RANGE[1], mask,
                                              os.path.join(DIR, f"sst-gfs-f{st:03d}.png"))
                    got_sst.add("gfs")
                except Exception as e:
                    sys.stderr.write(f"[gfs] f{st:03d} sst 실패: {e}\n")
                try: os.remove(path)
                except OSError: pass
            models_meta.append({**next(m for m in MODELS if m["key"] == "gfs"),
                                "cycle": cyc.isoformat()})
            ok_models.add("gfs")
            print(f"[gfs] 완료 cycle={cyc.isoformat()}")

    # ECMWF
    if "ecmwf" in want:
        try:
            client = ecmwf_setup()
            cyc = ecmwf_cycle(client)
            ep = ecmwf_download(client, steps)
            if ep and cyc:
                ec_tp = {}      # 누적강수 tp(m) 스텝별 캐시 → 차분(step-6)
                for st, (sfc, pl, cld) in ep.items():
                    for lv in LEVELS:
                        try:
                            U, V = ecmwf_uv(sfc, pl, lv)
                            encode_and_save(U, V, lv["range"],
                                            os.path.join(DIR, f"wind-ecmwf-{lv['key']}-f{st:03d}.png"))
                        except Exception as e:
                            sys.stderr.write(f"[ecmwf] f{st:03d} {lv['key']} 실패: {e}\n")
                        try:
                            if lv["ec_lt"] == "sfc":
                                T = to_celsius(ecmwf_scalar_hi(sfc, "shortName=2t"))   # 0.25° 원본
                            else:
                                T = to_celsius(ecmwf_scalar_hi(pl, f"shortName=t,level={lv['ec_lev']}"))
                            encode_scalar_save(T, lv["tempRange"][0], lv["tempRange"][1],
                                               os.path.join(DIR, f"temp-ecmwf-{lv['key']}-f{st:03d}.png"))
                            got_temp.add("ecmwf")
                        except Exception as e:
                            sys.stderr.write(f"[ecmwf] f{st:03d} {lv['key']} temp 실패: {e}\n")
                    if cld:
                        try:
                            C = to_percent(ecmwf_scalar_hi(cld, "shortName=tcc"))   # 원본 0.25° 유지
                            encode_scalar_save(C, 0.0, 100.0,
                                               os.path.join(DIR, f"cloud-ecmwf-f{st:03d}.png"))
                            got_cloud.add("ecmwf")
                        except Exception as e:
                            sys.stderr.write(f"[ecmwf] f{st:03d} cloud 실패: {e}\n")
                    # pressure(msl Pa→hPa)
                    try:
                        P = ecmwf_scalar(sfc, "shortName=msl") / 100.0
                        encode_scalar_save(P, PRESSURE_RANGE[0], PRESSURE_RANGE[1],
                                           os.path.join(DIR, f"pressure-ecmwf-f{st:03d}.png"))
                        got_pressure.add("ecmwf")
                    except Exception as e:
                        sys.stderr.write(f"[ecmwf] f{st:03d} pressure 실패: {e}\n")
                    # precip(tp 누적 m → step-6 차분 ×1000/6 = mm/h, step0=0)
                    try:
                        cur = ecmwf_scalar_hi(sfc, "shortName=tp")   # 원본 0.25° 유지
                        ec_tp[st] = cur
                        if st == 0:
                            PR = np.zeros((HLAT, HLON), np.float32)
                        elif (st - 6) in ec_tp:
                            PR = precip_rate_from_accum(cur, ec_tp[st - 6], 1000.0)
                        else:
                            raise RuntimeError(f"이전 누적(step {st-6}) 없음")
                        encode_scalar_save(PR, PRECIP_RANGE[0], PRECIP_RANGE[1],
                                           os.path.join(DIR, f"precip-ecmwf-f{st:03d}.png"))
                        got_precip.add("ecmwf")
                    except Exception as e:
                        sys.stderr.write(f"[ecmwf] f{st:03d} precip 실패: {e}\n")
                    # sst(open-data 에 sst 없음 → skt 스킨온도 K→°C, lsm(육지분율) 마스크)
                    try:
                        S = to_celsius(ecmwf_scalar(sfc, "shortName=skt"))
                        lsm = ecmwf_scalar(sfc, "shortName=lsm")
                        mask = (lsm < 0.5) & np.isfinite(S) & (S > SST_MASK_LO) & (S < SST_MASK_HI)
                        encode_scalar_masked_save(S, SST_RANGE[0], SST_RANGE[1], mask,
                                                  os.path.join(DIR, f"sst-ecmwf-f{st:03d}.png"))
                        got_sst.add("ecmwf")
                    except Exception as e:
                        sys.stderr.write(f"[ecmwf] f{st:03d} sst 실패: {e}\n")
                    for p in (sfc, pl, cld):
                        if not p:
                            continue
                        try: os.remove(p)
                        except OSError: pass
                models_meta.append({**next(m for m in MODELS if m["key"] == "ecmwf"),
                                    "cycle": cyc.replace(tzinfo=datetime.timezone.utc).isoformat()
                                    if cyc.tzinfo is None else cyc.isoformat()})
                ok_models.add("ecmwf")
                print(f"[ecmwf] 완료 cycle={cyc.isoformat()}")
        except Exception as e:
            sys.stderr.write(f"[ecmwf] 전면 실패: {e}\n")

    # ICON
    if "icon" in want:
        try:
            cyc = icon_probe(steps)
            if cyc:
                icon_latlon_index(cyc)
                icon_tp = {}    # 누적강수 tot_prec(mm) 스텝별 캐시 → 차분(step-6)
                done = 0
                for st in steps:
                    try:
                        for lv in LEVELS:
                            U, V = icon_uv(cyc, st, lv)
                            encode_and_save(U, V, lv["range"],
                                            os.path.join(DIR, f"wind-icon-{lv['key']}-f{st:03d}.png"))
                            try:
                                td, ttag, tkind = lv["icon_t"]
                                T = to_celsius(icon_field_hi(cyc, st, td, ttag, tkind))   # 0.25° 재격자
                                encode_scalar_save(T, lv["tempRange"][0], lv["tempRange"][1],
                                                   os.path.join(DIR, f"temp-icon-{lv['key']}-f{st:03d}.png"))
                                got_temp.add("icon")
                            except Exception as e:
                                sys.stderr.write(f"[icon] f{st:03d} {lv['key']} temp 실패: {e}\n")
                        try:
                            # 구름 = 구름물(TQC 액상 + TQI 빙정, kg/m²). 실패 시 전운량(CLCT %)로 폴백.
                            try:
                                W = icon_field_hi(cyc, st, "tqc", "TQC", "single-level") \
                                    + icon_field_hi(cyc, st, "tqi", "TQI", "single-level")
                                encode_cloudwater_save(W, os.path.join(DIR, f"cloud-icon-f{st:03d}.png"))
                            except Exception as e2:
                                sys.stderr.write(f"[icon] f{st:03d} 구름물 실패({str(e2)[:40]}) → 전운량 폴백\n")
                                C = to_percent(icon_field_hi(cyc, st, "clct", "CLCT", "single-level"))
                                encode_scalar_save(C, 0.0, 100.0,
                                                   os.path.join(DIR, f"cloud-icon-f{st:03d}.png"))
                                CLOUD_VAR["icon"] = "cover"
                            got_cloud.add("icon")
                        except Exception as e:
                            sys.stderr.write(f"[icon] f{st:03d} cloud 실패: {e}\n")
                        # pressure(pmsl Pa→hPa)
                        try:
                            P = icon_field(cyc, st, "pmsl", "PMSL", "single-level") / 100.0
                            encode_scalar_save(P, PRESSURE_RANGE[0], PRESSURE_RANGE[1],
                                               os.path.join(DIR, f"pressure-icon-f{st:03d}.png"))
                            got_pressure.add("icon")
                        except Exception as e:
                            sys.stderr.write(f"[icon] f{st:03d} pressure 실패: {e}\n")
                        # precip(tot_prec 누적 mm → step-6 차분 ÷6 = mm/h, step0=0)
                        try:
                            cur = icon_field_hi(cyc, st, "tot_prec", "TOT_PREC", "single-level")  # 0.25°
                            icon_tp[st] = cur
                            if st == 0:
                                PR = np.zeros((HLAT, HLON), np.float32)
                            elif (st - 6) in icon_tp:
                                PR = precip_rate_from_accum(cur, icon_tp[st - 6], 1.0)
                            else:
                                raise RuntimeError(f"이전 누적(step {st-6}) 없음")
                            encode_scalar_save(PR, PRECIP_RANGE[0], PRECIP_RANGE[1],
                                               os.path.join(DIR, f"precip-icon-f{st:03d}.png"))
                            got_precip.add("icon")
                        except Exception as e:
                            sys.stderr.write(f"[icon] f{st:03d} precip 실패: {e}\n")
                        # sst(t_g 지표온도 K→°C, 바다=fr_land<0.5 마스크)
                        try:
                            ocean = icon_ocean_mask(cyc)
                            S = to_celsius(icon_field(cyc, st, "t_g", "T_G", "single-level"))
                            mask = ocean & np.isfinite(S) & (S > SST_MASK_LO) & (S < SST_MASK_HI)
                            encode_scalar_masked_save(S, SST_RANGE[0], SST_RANGE[1], mask,
                                                      os.path.join(DIR, f"sst-icon-f{st:03d}.png"))
                            got_sst.add("icon")
                        except Exception as e:
                            sys.stderr.write(f"[icon] f{st:03d} sst 실패: {e}\n")
                        done += 1
                    except Exception as e:
                        sys.stderr.write(f"[icon] f{st:03d} 실패(스텝 스킵): {e}\n")
                if done:
                    models_meta.append({**next(m for m in MODELS if m["key"] == "icon"),
                                        "cycle": cyc.isoformat()})
                    ok_models.add("icon")
                    print(f"[icon] 완료 cycle={cyc.isoformat()} steps={done}")
        except Exception as e:
            sys.stderr.write(f"[icon] 전면 실패: {e}\n")

    if not models_meta:
        sys.stderr.write("[fetch_weather] 모든 모델 실패 — meta 미갱신\n")
        sys.exit(1)

    # 성공한 필드만 노출(temp/cloud/precip/sst/pressure 전면 실패 시 제외)
    fields = ["wind"]
    if got_temp:     fields.append("temp")
    if got_cloud:    fields.append("cloud")
    if got_precip:   fields.append("precip")
    if got_sst:      fields.append("sst")
    if got_pressure: fields.append("pressure")

    # meta 는 실제로 성공한 모델·스텝 순서 유지
    meta = {
        "updated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "bounds": [-180, 90, 180, -90],
        "fields": fields,
        "models": models_meta,
        "levels": [{"key": lv["key"], "label": lv["label"],
                    "velocityRange": [-lv["range"], lv["range"]], "unit": "m/s",
                    "tempRange": lv["tempRange"]} for lv in LEVELS],
        "cloudRange": [0, 100],
        # 모델별 구름 변수: "water"=구름물(log10 kg/m², cloudWaterLogRange) · "cover"=전운량(%, cloudRange)
        "cloudVar": {k: CLOUD_VAR[k] for k in sorted(got_cloud)} or CLOUD_VAR,
        "cloudWaterLogRange": CLOUDW_LOG_RANGE,
        "precipRange": PRECIP_RANGE,
        "sstRange": SST_RANGE,
        "pressureRange": PRESSURE_RANGE,
        "steps": [{"step": s, "hours": s} for s in steps],
        "filePattern": "wind-{model}-{level}-f{step}.png",
        "tempPattern": "temp-{model}-{level}-f{step}.png",
        "cloudPattern": "cloud-{model}-f{step}.png",
        "precipPattern": "precip-{model}-f{step}.png",
        "sstPattern": "sst-{model}-f{step}.png",
        "pressurePattern": "pressure-{model}-f{step}.png",
    }
    with open(os.path.join(DIR, "wind-meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"[fetch_weather] wind-meta.json: models={sorted(ok_models)} "
          f"fields={fields} temp={sorted(got_temp)} cloud={sorted(got_cloud)} "
          f"precip={sorted(got_precip)} sst={sorted(got_sst)} pressure={sorted(got_pressure)} "
          f"steps={len(steps)}")


if __name__ == "__main__":
    main()
