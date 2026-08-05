#!/bin/bash
# ============================================================
#  deploy_cf.sh · Cloudflare Pages 배포
# ------------------------------------------------------------
#  공개용 파일만 .cf_public/ 에 모아 wrangler 로 배포.
#  파이썬 스크립트·원본 저장소·작업지시(md)·로그는 올리지 않음.
#  사전조건: npx wrangler login (최초 1회)
#  auto_update.sh 가 매 갱신 끝에 자동 호출.
# ============================================================
set -e
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/bin:/bin:/usr/sbin:/sbin"
PROJ="$(cd "$(dirname "$0")" && pwd)"
PUB="$PROJ/.cf_public"
PROJECT_NAME="world-info"

cd "$PROJ"
rm -rf "$PUB"; mkdir -p "$PUB"

# 페이지가 실제로 로드하는 파일만
cp index.html "$PUB/"
cp _headers "$PUB/"   # 캐시 규칙(HTML/데이터 no-cache) — 옛 버전 고착 방지
cp favicon.ico favicon-16.png favicon-32.png apple-touch-icon.png icon-192.png icon-512.png site.webmanifest "$PUB/" 2>/dev/null || true   # 🌍 favicon/앱아이콘(남색 지구본·금색 배경)
cp news-data.js news-archive.js news-digest.js market-data.js market-brief.json stocks-info.js stocks-news.js earnings-series.js macro-series.js macro-data.js chartjs-plugin-zoom.min.js econ-calendar.json econ-calendar-store.json "$PUB/" 2>/dev/null || true
cp mac-quotes.json "$PUB/" 2>/dev/null || true   # 하이브리드: Mac 실시간 시세 터널 URL(프런트가 우선 폴링, 실패 시 /api/quotes 폴백)
cp land-lite.json countries-defense.geojson "$PUB/" 2>/dev/null || true
cp commodities.js semi-supply.js shipping.js military.js economy.js country-profiles.js country-resources.js bri.js pipelines.js \
   refineries.js armed-groups.js semis.js nuclear.js tech-plants.js strategic.js seismic.js countries-defense.geojson "$PUB/"
cp typhoons.json typhoon-tracks.json "$PUB/" 2>/dev/null || true   # 태풍 예보(있을 때만; fetch_typhoons.py 산출)
cp wind-*-f*.png temp-*-f*.png cloud-*-f*.png precip-*-f*.png sst-*-f*.png pressure-*-f*.png wind-meta.json "$PUB/" 2>/dev/null || true   # 💨🌡️☁️ 다모델·다층·다시각 바람(R=u·G=v)+기온·구름(R=값) 텍스처+메타(fetch_weather.py)
cp aq-*-f*.png aq-meta.json "$PUB/" 2>/dev/null || true   # 🌫️ 대기질(CAMS) PM2.5·PM10·NO2·SO2·O3·CO 다시각 텍스처+메타(fetch_airquality.py)
cp sst-anom.png enso-status.json "$PUB/" 2>/dev/null || true   # 🌡️ 이상수온(OISST) 텍스처 + ENSO 상태(fetch_sst_anomaly.py)

echo "배포 파일: $(ls "$PUB" | wc -l | tr -d ' ')개 ($(du -sh "$PUB" | cut -f1))"
/opt/homebrew/bin/npx wrangler pages deploy "$PUB" --project-name "$PROJECT_NAME" --commit-dirty=true
