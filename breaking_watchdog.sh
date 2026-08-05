#!/bin/bash
# ============================================================
#  breaking_watchdog.sh · 속보 장애 자동 감지·알림
# ------------------------------------------------------------
#  breaking-store.json 이 STALE_MIN(60분) 이상 갱신 안 되면 알림.
#  = 리스너 멈춤/죽음, claude·Grok 심사 실패, 텔레그램·네트워크 장애 등을 포착.
#  중복 알림 방지: staleness 진입 시 1회만(.breaking_stale_alerted 마커).
#   정상 복귀 시 마커 정리 → 다음 staleness 때 다시 알림.
#  알림 채널: macOS 알림 + (~/.telegram_notify 있으면) 텔레그램.
#  launchd(com.worldinfo.breakingwatch)가 15분마다 실행.
# ============================================================
export PATH="/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
PROJ="/Users/shkim/PycharmProjects/WEB_WORLD_INFO"
STORE="$PROJ/breaking-store.json"
MARK="$PROJ/.breaking_stale_alerted"
STALE_MIN=60

notify() {
  local msg="$1"
  echo "$(date '+%Y-%m-%d %H:%M:%S') [속보감시] $msg" >> "$PROJ/fail.log"
  /usr/bin/osascript -e "display notification \"$msg\" with title \"⚡ 속보 감시\" sound name \"Basso\"" 2>/dev/null
  if [ -f "$HOME/.telegram_notify" ]; then
    . "$HOME/.telegram_notify"
    [ -n "$BOT_TOKEN" ] && /usr/bin/curl -s -m 10 "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
      -d chat_id="${CHAT_ID}" --data-urlencode text="⚠️ 속보 감시: $msg" >/dev/null 2>&1
  fi
}

[ -f "$STORE" ] || exit 0   # store 파일 없으면(최초 가동 전) 스킵

if [ -n "$(find "$STORE" -maxdepth 0 -mmin "+$STALE_MIN" 2>/dev/null)" ]; then
  # STALE — 아직 알리지 않았으면 1회 알림
  if [ ! -f "$MARK" ]; then
    age=$(( ( $(date +%s) - $(stat -f %m "$STORE") ) / 60 ))
    if pgrep -f breaking_listener.py >/dev/null; then
      proc="리스너는 살아있음 → 심사(claude/Grok)·텔레그램·네트워크 점검 필요"
    else
      proc="⚠️ 리스너 프로세스 죽음 → launchctl 재기동 필요"
    fi
    notify "속보가 ${age}분째 갱신 안 됨 — ${proc}"
    touch "$MARK"
  fi
else
  rm -f "$MARK"   # 정상 갱신 중 → 마커 정리(다음 장애 때 재알림 가능하게)
fi
