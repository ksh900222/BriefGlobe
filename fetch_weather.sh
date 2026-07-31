#!/bin/bash
# ============================================================
#  fetch_weather.sh — 기상 텍스처 생성 (메인 파이프라인과 분리된 독립 잡)
# ------------------------------------------------------------
#  GFS/ECMWF/ICON 바람·기온·구름·강수·기압·해수온 텍스처(wind-*.png 등)를 생성.
#  launchd(com.worldinfo.weather)가 3시간마다 실행. auto_update.sh 와 별개 프로세스라
#  기상 다운로드가 아무리 오래 걸려도(또는 hang) 뉴스·시세·배포를 절대 막지 않는다.
#  배포는 하지 않는다 — 생성된 PNG는 다음 정각 auto_update.sh 의 deploy_cf.sh 가 실어간다.
# ============================================================
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/bin:/bin:/usr/sbin:/sbin"
PROJ="/Users/shkim/PycharmProjects/WEB_WORLD_INFO"
PY="/Library/Frameworks/Python.framework/Versions/3.12/bin/python3"
cd "$PROJ" || exit 1

# ---- 겹침 방지 잠금(메인 파이프라인과 별도) ----
LOCK="$PROJ/.weather.lock"
if [ -d "$LOCK" ] && [ -n "$(find "$LOCK" -maxdepth 0 -mmin +30 2>/dev/null)" ]; then
  echo "오래된 기상 잠금 정리"; rmdir "$LOCK" 2>/dev/null
fi
if ! mkdir "$LOCK" 2>/dev/null; then
  echo "$(date '+%H:%M:%S') 기상 잡이 이미 실행 중 → 이번 건 건너뜀"; exit 0
fi
trap 'rmdir "$LOCK" 2>/dev/null' EXIT

echo "===== $(date '+%Y-%m-%d %H:%M:%S') 기상 텍스처 생성 시작 ====="
# 하드 타임아웃 75분 — macOS엔 timeout 없어 배경+워치독 kill.
#   정상 1회 생성이 ~45분(3모델×29스텝, 구름·강수는 0.25°)이라 여유를 두되, 무한 hang 은 반드시 끊는다.
#   (fetch_weather.py 자체도 socket 120초 타임아웃 있으나, 이건 최종 안전장치)
"$PY" fetch_weather.py &
_WPID=$!
( sleep 4500; kill -0 "$_WPID" 2>/dev/null && { echo "  ⚠ 기상 75분 초과 → 강제 종료"; kill -9 "$_WPID" 2>/dev/null; } ) &
_WWATCH=$!
wait "$_WPID" 2>/dev/null || echo "  ⚠ 기상 텍스처 생성 실패(기존 텍스처 유지)"
kill "$_WWATCH" 2>/dev/null || true
echo "===== $(date '+%H:%M:%S') 기상 텍스처 완료 ====="
