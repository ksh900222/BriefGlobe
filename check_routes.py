#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""항로-육지 교차 검사기 (shipping.js 수정 후 반드시 실행!)
   사용: python3 check_routes.py   → '0건'이 나와야 커밋"""
import json, sys, os, subprocess, urllib.request

if not os.path.exists("land.geojson"):
    print("land.geojson 다운로드 중 (Natural Earth 50m)…")
    urllib.request.urlretrieve(
        "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_land.geojson",
        "land.geojson")
subprocess.run(["node", "-e",
    "const fs=require('fs');const src=fs.readFileSync('shipping.js','utf8');"
    "const d=new Function(src+'; return {SHIPPING_ROUTES, PORTS};')();"
    "fs.writeFileSync('routes.json', JSON.stringify(d));"], check=True)

LAND = json.load(open("land.geojson"))
DATA = json.load(open("routes.json"))

# 정당한 육지 통과 구역 (운하·해협)
CANAL_ZONES = [
    (29.3, 31.8, 31.8, 33.2),    # 수에즈 운하 (latmin, latmax, lngmin, lngmax)
    (8.4, 9.7, -80.3, -79.1),    # 파나마 운하
    (40.9, 41.35, 28.85, 29.35), # 보스포루스 해협 (폭 ~700m — 50m 지도에선 육지로 나옴)
    (39.9, 40.5, 26.0, 26.9),    # 다르다넬스 해협
]
PORT_RADIUS = 0.7  # 항구/끝점 근처 허용 반경(도)

ports = [(p["lat"], p["lng"]) for p in DATA["PORTS"]]
# 항로 끝점들도 허용점에 추가
for r in DATA["SHIPPING_ROUTES"]:
    for seg in (r.get("segments") or [r["coords"]]):
        ports.append(tuple(seg[0])); ports.append(tuple(seg[-1]))

def in_canal(lat, lng):
    return any(a <= lat <= b and c <= lng <= d for a, b, c, d in CANAL_ZONES)

def near_port(lat, lng):
    return any(abs(lat - p[0]) < PORT_RADIUS and abs(lng - p[1]) < PORT_RADIUS
               for p in ports)

# 폴리곤 준비: (bbox, ring) 리스트로 평탄화
rings = []
for f in LAND["features"]:
    g = f["geometry"]
    polys = g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]
    for poly in polys:
        outer = poly[0]
        xs = [p[0] for p in outer]; ys = [p[1] for p in outer]
        rings.append(((min(xs), min(ys), max(xs), max(ys)), outer, poly[1:]))

def pip(lng, lat, ring):
    inside = False
    n = len(ring)
    j = n - 1
    for i in range(n):
        xi, yi = ring[i][0], ring[i][1]
        xj, yj = ring[j][0], ring[j][1]
        if (yi > lat) != (yj > lat) and lng < (xj - xi) * (lat - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside

def on_land(lat, lng):
    for (x0, y0, x1, y1), outer, holes in rings:
        if not (x0 <= lng <= x1 and y0 <= lat <= y1):
            continue
        if pip(lng, lat, outer):
            if any(pip(lng, lat, h) for h in holes):
                continue  # 호수 등 구멍 안 = 물
            return True
    return False

STEP = 0.15
violations = []
for r in DATA["SHIPPING_ROUTES"]:
    segs = r.get("segments") or [r["coords"]]
    for si, seg in enumerate(segs):
        for i in range(len(seg) - 1):
            (la1, ln1), (la2, ln2) = seg[i], seg[i + 1]
            dist = max(abs(la2 - la1), abs(ln2 - ln1))
            n = max(2, int(dist / STEP) + 1)
            bad = []
            for k in range(n + 1):
                t = k / n
                la = la1 + (la2 - la1) * t
                ln = ln1 + (ln2 - ln1) * t
                if in_canal(la, ln) or near_port(la, ln):
                    continue
                if on_land(la, ln):
                    bad.append((round(la, 2), round(ln, 2)))
            if bad:
                violations.append({
                    "route": r["name"], "seg": si, "wp": i,
                    "from": seg[i], "to": seg[i + 1],
                    "samples": bad[:4], "count": len(bad),
                })

if not violations:
    print("✅ 전 항로 육지 교차 0건 (운하·항구 제외)")
else:
    print(f"❌ 육지 교차 위반 {len(violations)}개 구간:\n")
    for v in violations:
        print(f"[{v['route']}] 세그{v['seg']} 웨이포인트{v['wp']}: "
              f"{v['from']}→{v['to']}")
        print(f"   육지 샘플 {v['count']}개, 예: {v['samples']}")
sys.exit(0 if not violations else 1)
