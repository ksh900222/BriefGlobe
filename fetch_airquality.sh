#!/bin/bash
# ============================================================
#  fetch_airquality.sh — 대기질 텍스처 생성 (메인 파이프라인과 분리된 독립 잡)
# ------------------------------------------------------------
#  CAMS(Copernicus/ECMWF) PM2.5·PM10·NO2·SO2·O3·CO 텍스처(aq-*.png)를 생성.
#  launchd(com.worldinfo.airquality)가 주기 실행. auto_update.sh·기상 잡과 별개 프로세스라
#  CAMS ADS 큐가 아무리 느려도(또는 hang) 뉴스·시세·기상·배포를 절대 막지 않는다.
#  배포는 하지 않는다 — 생성된 PNG 는 다음 정각 auto_update.sh 의 deploy_cf.sh 가 실어간다.
#  (기상이 GFS hang 으로 전체 파이프라인을 마비시켰던 교훈을 그대로 적용한 구조)
# ============================================================
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/bin:/bin:/usr/sbin:/sbin"
PROJ="/Users/shkim/PycharmProjects/WEB_WORLD_INFO"
PY="/Library/Frameworks/Python.framework/Versions/3.12/bin/python3"
cd "$PROJ" || exit 1

# ---- 겹침 방지 잠금(메인 파이프라인·기상과 별도) ----
LOCK="$PROJ/.airquality.lock"
if [ -d "$LOCK" ] && [ -n "$(find "$LOCK" -maxdepth 0 -mmin +40 2>/dev/null)" ]; then
  echo "오래된 대기질 잠금 정리"; rmdir "$LOCK" 2>/dev/null
fi
if ! mkdir "$LOCK" 2>/dev/null; then
  echo "$(date '+%H:%M:%S') 대기질 잡이 이미 실행 중 → 이번 건 건너뜀"; exit 0
fi
trap 'rmdir "$LOCK" 2>/dev/null' EXIT

echo "===== $(date '+%Y-%m-%d %H:%M:%S') 대기질 텍스처 생성 시작 ====="
# 하드 타임아웃 30분 — CAMS ADS 는 큐 방식이라 피크 시 지연 가능. 정상은 2~5분.
#   무한 대기(큐 적체·hang)는 반드시 끊는다. (cdsapi 자체 재시도/타임아웃도 있으나 최종 안전장치)
"$PY" fetch_airquality.py &
_APID=$!
( sleep 1800; kill -0 "$_APID" 2>/dev/null && { echo "  ⚠ 대기질 30분 초과 → 강제 종료"; kill -9 "$_APID" 2>/dev/null; } ) &
_AWATCH=$!
wait "$_APID" 2>/dev/null || echo "  ⚠ 대기질 텍스처 생성 실패(기존 텍스처 유지)"
kill "$_AWATCH" 2>/dev/null || true
echo "===== $(date '+%H:%M:%S') 대기질 텍스처 완료 ====="
