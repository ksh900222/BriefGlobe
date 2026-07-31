#!/bin/bash
# ============================================================
#  mac_quotes.sh — Mac 실시간 시세 서버 + cloudflared named tunnel (하이브리드 A)
# ------------------------------------------------------------
#  ① fetch_quotes_server.py (127.0.0.1:8787) 기동
#  ② named tunnel 로 노출 → 고정 주소 https://quotes.briefglobe.com
#  launchd(com.worldinfo.macquotes)가 KeepAlive 로 상시 유지.
#  named tunnel이라 URL이 절대 안 바뀜(quick tunnel의 URL 자동교체 문제 해결).
#  설정: ~/.cloudflared/config.yml (tunnel worldinfo-quotes → 127.0.0.1:8787)
# ============================================================
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/bin:/bin:/usr/sbin:/sbin"
PROJ="/Users/shkim/PycharmProjects/WEB_WORLD_INFO"
PY="/Library/Frameworks/Python.framework/Versions/3.12/bin/python3"
cd "$PROJ" || exit 1

# 기존 잔여 프로세스 정리
pkill -f "fetch_quotes_server.py" 2>/dev/null
pkill -f "quotes_ws_server.py" 2>/dev/null
pkill -f "cloudflared tunnel" 2>/dev/null
sleep 1

# ① 시세 서버 기동 (WebSocket 실시간 푸시 + REST. 자식 — 종료 시 함께 정리)
"$PY" quotes_ws_server.py &
SVPID=$!
trap 'kill "$SVPID" 2>/dev/null' EXIT
sleep 3

# ② named tunnel 실행 (고정주소 quotes.briefglobe.com). 블로킹.
echo "[macquotes] named tunnel(quotes.briefglobe.com) 시작…"
cloudflared tunnel run worldinfo-quotes
