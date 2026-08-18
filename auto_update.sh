#!/bin/bash
# ============================================================
#  auto_update.sh — 매시간(정각): 시세·GDELT·조사(뉴스·브리핑=Claude haiku 우선, 종목뉴스=Grok)·번역
#                    + 하루1회: coverage_check(큐) → Grok 재무·캘린더·거시delta·실적delta → merge_econ·merge_series → coverage_check(검증)
#  launchd(com.worldinfo.fetch)가 이 스크립트를 주기 실행함.
# ============================================================
PROJ="/Users/shkim/PycharmProjects/WEB_WORLD_INFO"
PY="/Library/Frameworks/Python.framework/Versions/3.12/bin/python3"
GROK="/Users/shkim/.grok/bin/grok"
CLAUDE="/opt/homebrew/bin/claude"
NPX="/opt/homebrew/bin/npx"
# launchd는 PATH가 최소한이라 Homebrew 경로를 명시해야 npx/node를 찾음
export PATH="/opt/homebrew/bin:/opt/homebrew/sbin:/usr/bin:/bin:/usr/sbin:/sbin"
cd "$PROJ" || exit 1

# ---- 겹침 방지 잠금 (이전 실행이 진행 중이면 이번 건 건너뜀) ----
LOCK="$PROJ/.update.lock"
# 오래된(2시간+) 잔여 잠금은 비정상 종료로 보고 정리
if [ -d "$LOCK" ] && [ -n "$(find "$LOCK" -maxdepth 0 -mmin +120 2>/dev/null)" ]; then
  echo "오래된 잠금 정리"; rmdir "$LOCK" 2>/dev/null
fi
if ! mkdir "$LOCK" 2>/dev/null; then
  echo "$(date '+%H:%M:%S') 이전 실행이 아직 진행 중 → 이번 실행 건너뜀"
  exit 0
fi
trap 'rmdir "$LOCK" 2>/dev/null' EXIT

echo "===== $(date '+%Y-%m-%d %H:%M:%S') 자동 업데이트 시작 ====="

# ---- 실패 알림: macOS 알림센터 + fail.log (+텔레그램: ~/.telegram_notify 있으면) ----
#   ~/.telegram_notify 형식(2줄):  BOT_TOKEN=123:abc  /  CHAT_ID=123456789
notify_fail() {
  local msg="$1"
  echo "$(date '+%Y-%m-%d %H:%M:%S') $msg" >> "$PROJ/fail.log"
  /usr/bin/osascript -e "display notification \"$msg\" with title \"World Info 파이프라인\" sound name \"Basso\"" 2>/dev/null
  if [ -f "$HOME/.telegram_notify" ]; then
    . "$HOME/.telegram_notify"
    [ -n "$BOT_TOKEN" ] && /usr/bin/curl -s -m 10 "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
      -d chat_id="${CHAT_ID}" --data-urlencode text="⚠️ World Info: $msg" >/dev/null 2>&1
  fi
}

# ---- AI 실행기: Grok 우선 ↔ Claude 양방향 폴백 --------------------------------
#   기본: Grok 먼저 → 실패 시 Claude.
#   · Grok 잔액소진(402) → .grok_down (24h) 후 Claude 로.
#   · Claude 한도/레이트리밋 → .claude_down (6h) 후 Grok 만 사용(Claude 호출 스킵).
#   · Claude 한도 중이면 .grok_down 이 있어도 **Grok을 다시 시도**(한쪽이 죽어도 파이프라인 유지).
#   · 둘 다 실패해도 크론은 계속(호출부 || echo). 마커는 mtime 기준 자동 만료.
#   사용:  run_ai "라벨" <max-turns> <claude모델> "프롬프트" [grok모델] [reasoning-effort]
#   Grok 모델 티어(비용 분리):
#     · LIGHT (번역 · 속보 심사): grok-4.5 · effort 기본 low  (2026-07: xAI가 grok-4-fast 제거 → grok-4.5 단일)
#     · HEAVY (뉴스·브리핑·테크딜·재무·캘린더·실적 등 조사·분석): grok-4.5 · effort 기본 low
#     · 종목뉴스(SNS 포함): grok-4.5 · effort medium (= mid)
#   CLI effort 허용값: high | medium | low (mid 아님 → medium)
#   CLI 계정에 light 모델이 없으면 HEAVY로 1회 재시도(로그에 경고).
GROK_MODEL_HEAVY="${GROK_MODEL_HEAVY:-grok-4.5}"
GROK_MODEL_LIGHT="${GROK_MODEL_LIGHT:-grok-4.5}"
GROK_EFFORT_DEFAULT="${GROK_EFFORT_DEFAULT:-low}"
GROK_EFFORT_D2="${GROK_EFFORT_D2:-medium}"
GROK_DOWN="$PROJ/.grok_down"
CLAUDE_DOWN="$PROJ/.claude_down"
# 제3 폴백 Gemini (설치·인증 시에만 활성). flash = 최저가 티어.
GEMINI="${GEMINI:-$(command -v gemini 2>/dev/null || echo /opt/homebrew/bin/gemini)}"
GEMINI_MODEL="${GEMINI_MODEL:-gemini-2.5-flash}"
GEMINI_DOWN="$PROJ/.gemini_down"
# 마커 유효? (파일이 있고 아직 만료 전) — 인자: 경로, 분
_marker_active() {
  local f="$1" mins="$2"
  [ -f "$f" ] && [ -z "$(find "$f" -maxdepth 0 -mmin "+$mins" 2>/dev/null)" ]
}
# Claude 출력/종료코드에서 한도·레이트리밋 패턴 감지
_claude_limited() {
  local log="$1"
  grep -qiE "rate.?limit|usage.?limit|limit.?reached|too many requests|overloaded|exceeded.?your|quota|429|capacity|try again later|out of extra usage|weekly.?limit|session.?limit" "$log" 2>/dev/null
}
# Grok 잔액/결제 실패 패턴
_grok_exhausted() {
  local log="$1"
  # ⚠ 조사 결과 '본문'의 402·billing 오탐 방지 — 광범위 패턴(402·billing) 제거, 실제 xAI 잔액/결제 에러 문구만.
  #   추가로 호출부에서 rc≠0(실패)일 때만 이 검사를 돌려 성공 출력 오탐을 이중 차단한다.
  grep -qiE "usage balance exhausted|402 Payment Required|Payment Required \(402\)|insufficient.?(credit|balance|fund)|billing.?(error|issue|failed)|add.?(credit|fund|balance)" "$log" 2>/dev/null
}
_grok_unknown_model() {
  local log="$1"
  grep -qiE "unknown model id|Couldn't set model|Invalid params" "$log" 2>/dev/null
}

# Grok 한 번 실행. 성공=0, 잔액소진=2, 기타실패=1
#   인자: label turns prompt [gmodel] [effort]  — gmodel 기본=HEAVY, effort 기본=low
_run_grok_once() {
  local label="$1" turns="$2" prompt="$3"
  local gmodel="${4:-$GROK_MODEL_HEAVY}"
  local effort="${5:-$GROK_EFFORT_DEFAULT}"
  local tmp rc attempt=0
  if [ ! -x "$GROK" ]; then
    echo "  ⚠ Grok 바이너리 없음: $GROK"; return 1
  fi
  while [ "$attempt" -lt 2 ]; do
    attempt=$((attempt + 1))
    tmp="$(mktemp -t runai_grok)"
    echo "  → Grok($gmodel, effort=$effort) 실행: $label (max-turns=$turns)"
    "$GROK" --cwd "$PROJ" --always-approve --max-turns "$turns" -m "$gmodel" \
      --reasoning-effort "$effort" -p "$prompt" 2>&1 | tee "$tmp"
    rc=${PIPESTATUS[0]}
    # 성공(rc=0)이면 무조건 성공 처리 — 출력 본문에 402/billing 있어도 오탐 금지(잔액소진 검사 안 함)
    if [ "$rc" -eq 0 ]; then
      rm -f "$GROK_DOWN"
      RUN_AI_ENGINE="grok"; RUN_AI_MODEL="$gmodel"; RUN_AI_EFFORT="$effort"   # 성공 엔진 기록(브리핑 배지용)
      rm -f "$tmp"; return 0
    fi
    # light 모델이 CLI에 없으면 heavy로 1회 재시도
    if _grok_unknown_model "$tmp" \
       && [ "$gmodel" != "$GROK_MODEL_HEAVY" ] && [ "$attempt" -eq 1 ]; then
      echo "  ⚠ 모델 '$gmodel' 미지원 → $GROK_MODEL_HEAVY 로 재시도"
      gmodel="$GROK_MODEL_HEAVY"
      rm -f "$tmp"
      continue
    fi
    # 실패(rc≠0)일 때만 잔액소진 판정 — 성공 결과 오탐 원천 차단
    if _grok_exhausted "$tmp"; then
      touch "$GROK_DOWN"
      echo "  ⚠ Grok 잔액 소진 → .grok_down (24h Claude 우선)"
      rm -f "$tmp"; return 2
    fi
    echo "  ⚠ Grok 실패(rc=$rc, model=$gmodel, effort=$effort): $label"
    rm -f "$tmp"; return 1
  done
  return 1
}

# Claude 한 번 실행. 성공=0, 한도=2, 기타실패=1
_run_claude_once() {
  local label="$1" model="$2" prompt="$3" effort="${4:-low}"   # effort: low(기본·절약)|medium|high|xhigh|max
  local tmp rc
  if [ ! -x "$CLAUDE" ]; then
    echo "  ⚠ Claude 바이너리 없음: $CLAUDE"; return 1
  fi
  tmp="$(mktemp -t runai_claude)"
  echo "  → Claude($model, effort=$effort) 실행: $label"
  "$CLAUDE" --dangerously-skip-permissions --model "$model" --effort "$effort" -p "$prompt" < /dev/null >"$tmp" 2>&1
  rc=$?
  cat "$tmp"
  if _claude_limited "$tmp" || [ "$rc" -eq 429 ]; then
    touch "$CLAUDE_DOWN"
    echo "  ⚠ Claude 한도/레이트리밋 → .claude_down (6h Grok 전용)"
    rm -f "$tmp"; return 2
  fi
  if [ "$rc" -eq 0 ]; then
    rm -f "$CLAUDE_DOWN"
    RUN_AI_ENGINE="claude"; RUN_AI_MODEL="$model"; RUN_AI_EFFORT="$effort"   # 성공 엔진 기록(브리핑 배지용)
    rm -f "$tmp"; return 0
  fi
  # 종료코드 비0이어도 한도 문구가 있으면 한도로 취급(이미 위에서 처리)
  echo "  ⚠ Claude 실패(rc=$rc): $label"
  rm -f "$tmp"; return 1
}

# Gemini 한 번 실행. 성공=0, 한도=2, 기타실패=1. (CLI: gemini -m <model> -p <prompt>)
_run_gemini_once() {
  local label="$1" model="$2" prompt="$3" tmp rc
  if [ ! -x "$GEMINI" ]; then return 1; fi
  tmp="$(mktemp -t runai_gemini)"
  echo "  → Gemini($model) 실행: $label"
  "$GEMINI" -m "$model" -p "$prompt" < /dev/null >"$tmp" 2>&1
  rc=$?
  cat "$tmp"
  if grep -qiE "quota|rate.?limit|resource.?exhausted|429|exceeded|permission denied|unauthenticated" "$tmp"; then
    touch "$GEMINI_DOWN"
    echo "  ⚠ Gemini 한도/미인증 → .gemini_down (6h 스킵)"
    rm -f "$tmp"; return 2
  fi
  if [ "$rc" -eq 0 ]; then RUN_AI_ENGINE="gemini"; RUN_AI_MODEL="$model"; RUN_AI_EFFORT=""; rm -f "$tmp"; return 0; fi
  echo "  ⚠ Gemini 실패(rc=$rc): $label"
  rm -f "$tmp"; return 1
}

# 사용: run_ai "라벨" <turns> <claude모델> "프롬프트" [grok모델=HEAVY] [grok effort=low] [claude effort=low] [prefer_claude=0]
#   prefer_claude=1 → Claude(haiku) 우선 위임·Grok 폴백. 조사작업은 종목뉴스 빼고 전부 이 모드(2026-07-30~).
#   0(기본) → 기존 Grok 우선·Claude 폴백(종목뉴스 전용).
run_ai() {
  local label="$1" turns="$2" model="$3" prompt="$4"
  local gmodel="${5:-$GROK_MODEL_HEAVY}"
  local effort="${6:-$GROK_EFFORT_DEFAULT}"   # Grok reasoning effort
  RUN_AI_ENGINE=""; RUN_AI_MODEL=""; RUN_AI_EFFORT=""   # 이번 호출 성공 엔진 기록(성공 시 _run_*_once가 세팅)
  local ceffort="${7:-low}"                   # Claude effort (기본 low=절약; 판단작업만 medium)
  local prefer_claude="${8:-0}"               # 1=Claude(haiku) 우선 위임·Grok 폴백(종목뉴스 제외 조사작업). 0=기존 Grok 우선.
  local grok_skip=0 claude_skip=0 grc=1 crc=1

  # 마커 상태 (Grok 24h, Claude 6h — Claude 한도는 보통 수 시간 단위)
  if _marker_active "$GROK_DOWN" 1440; then grok_skip=1; fi
  if _marker_active "$CLAUDE_DOWN" 360; then claude_skip=1; fi

  # Claude 한도 중이면 Grok 스킵 해제(한쪽에 몰리지 않게)
  if [ "$claude_skip" = 1 ]; then
    grok_skip=0
    echo "  · Claude 한도 마커 유효 → Grok 전용 모드 (model=$gmodel effort=$effort)"
  elif [ "$grok_skip" = 1 ]; then
    echo "  · Grok 잔액소진 마커 유효 → Claude 우선"
  fi

  if [ "$prefer_claude" = 1 ]; then
    # ══ Claude(haiku) 우선 위임 모드 (종목뉴스 제외 조사작업) ══
    # 1) Claude 우선
    if [ "$claude_skip" = 0 ]; then
      _run_claude_once "$label" "$model" "$prompt" "$ceffort"
      crc=$?
      [ "$crc" -eq 0 ] && return 0
    fi
    # 2) Grok 폴백 (Claude 실패/한도)
    if [ "$grok_skip" = 0 ]; then
      echo "  ↪ Grok 폴백(Claude 실패/한도): $label ($gmodel effort=$effort)"
      _run_grok_once "$label" "$turns" "$prompt" "$gmodel" "$effort"
      grc=$?
      [ "$grc" -eq 0 ] && return 0
    fi
  else
    # ══ (기존) Grok 우선 모드 (종목뉴스 등) ══
    # 1) Grok 우선 (스킵 아닐 때)
    if [ "$grok_skip" = 0 ]; then
      _run_grok_once "$label" "$turns" "$prompt" "$gmodel" "$effort"
      grc=$?
      [ "$grc" -eq 0 ] && return 0
    fi

    # 2) Claude 폴백 (스킵 아닐 때)
    if [ "$claude_skip" = 0 ]; then
      if [ "$grok_skip" = 0 ]; then
        echo "  ↪ Claude($model) 폴백: $label"
      fi
      _run_claude_once "$label" "$model" "$prompt" "$ceffort"
      crc=$?
      [ "$crc" -eq 0 ] && return 0
      # Claude가 한도에 걸리면 Grok을 아직 안 했거나 이전에 스킵했으면 즉시 Grok 재시도
      if [ "$crc" -eq 2 ] && [ "$grok_skip" = 1 ]; then
        echo "  ↪ Claude 한도 → 스킵했던 Grok 재시도: $label ($gmodel effort=$effort)"
        _run_grok_once "$label" "$turns" "$prompt" "$gmodel" "$effort"
        grc=$?
        [ "$grc" -eq 0 ] && return 0
      fi
    fi

    # 3) 최후: Claude만 돌렸다가 실패했고 Grok을 안 쓴 경우(마커 만료 직전 등)
    if [ "$grok_skip" = 1 ] && [ "$grc" -ne 0 ]; then
      echo "  ↪ 최후 Grok 시도: $label ($gmodel effort=$effort)"
      _run_grok_once "$label" "$turns" "$prompt" "$gmodel" "$effort"
      grc=$?
      [ "$grc" -eq 0 ] && return 0
    fi
  fi

  # 4) 제3 폴백: Gemini CLI (설치+인증돼 있을 때만). Grok·Claude 둘 다 실패 시.
  #    미설치면 조용히 건너뜀(파이프라인 무영향). 설치: AI_PIPELINE_MANUAL.md 참조.
  if [ -x "$GEMINI" ] && ! _marker_active "$GEMINI_DOWN" 360; then
    _run_gemini_once "$label" "$GEMINI_MODEL" "$prompt"
    [ "$?" -eq 0 ] && return 0
  fi

  echo "  ⚠ AI 전부 실패: $label (Grok rc≈$grc, Claude rc≈$crc)"
  return 1
}

# ── 디제스트 순위변동(▲▼/NEW) 스냅샷 — 사이클당 1회, 직전 사이클 최종 순위 고정 ──
#   이 사이클에서 merge_news.py 가 여러 번 실행돼도(fetch 1회 + 번역 배치마다) prevRank 가
#   덮이지 않도록, 사이클 시작 시 '현재 news-digest.js 순위'를 digest-prev-ranks.json 에
#   1회 고정한다. 이후 이 사이클의 모든 merge 는 이 스냅샷만 prev 로 읽는다(merge 는 안 씀).
"$PY" merge_news.py --snapshot-prev || echo "  ⚠ 디제스트 prev 스냅샷 실패(이번 회차 변동표시 생략 가능)"

# 0) 시장 데이터 (야후 일봉, 무료·토큰0) — 실패해도 뉴스 진행
echo "[0/2] 시장 데이터 수집…"
"$PY" fetch_markets.py || echo "  ⚠ 시장 데이터 실패(건너뜀)"
# 0b) KIS(한국투자증권) 주식 시세 보강 — 야후로 만든 market-data.js의 주식(한국·미국)+국내채권ETF를
#     KIS 실시세로 덮는다(정확도↑·현재가·추후 시간외). .kis_secret 있을 때만, 실패해도 야후값 유지(폴백).
if [ -f "$PROJ/.kis_secret" ]; then
  echo "[0b] KIS 주식 시세 보강…"
  "$PY" fetch_markets_kis.py --enrich || echo "  ⚠ KIS 보강 실패(야후값 유지)"
fi
# 0c) 한국은행 ECOS 시장금리(일별) — 국고채 3/5/10년·CD91·콜금리·기준금리를 %수익률로 append.
#     .ecos_secret 있을 때만, 실패해도 나머지 시세는 그대로(멱등 append).
if [ -f "$PROJ/.ecos_secret" ]; then
  echo "[0c] ECOS 한국 금리지표 보강…"
  "$PY" fetch_rates_ecos.py --append || echo "  ⚠ ECOS 금리 보강 실패(건너뜀)"
fi
# 0d) FRED 거시지표(사용자 선택 78종, 10년·MoM/YoY) → macro-data.js. ~/.fred_api_key 있을 때만.
if [ -f "$HOME/.fred_api_key" ]; then
  echo "[0d] FRED 거시지표 수집…"
  "$PY" fetch_macro.py || echo "  ⚠ 거시지표 수집 실패(기존 macro-data.js 유지)"
fi
# 0e) 시장 구조일(네 마녀의 날·옵션/선물 만기) — 규칙 기반 계산 → 캘린더 store 병합(멱등, 매 주기)
"$PY" market_dates.py || echo "  ⚠ 시장 구조일 계산 실패(건너뜀)"
"$PY" fetch_typhoons.py || echo "  ⚠ 태풍 예보 수집 실패(건너뜀)"
# 💨 기상 텍스처(GFS/ECMWF/ICON 바람·기온·구름·강수·기압·해수온)는 이 파이프라인에서 분리됨.
#   → 독립 launchd 잡(com.worldinfo.weather · fetch_weather.sh)이 3h마다 생성.
#   이유: GFS 다운로드가 멈추면(과거 hang) 이 순차 파이프라인 전체가 잠겨 뉴스·배포까지 마비됐음.
#   생성된 wind-*.png 등은 여기서 배포만 실어감(deploy_cf.sh 화이트리스트).
# 🌀 태풍 모델별 진로(GFS·ECMWF·AI-GFS) — 각 기관 공식 보텍스 트래커 산출물을 원격에서 직접 받는다.
#   NCEP ATCF(NOMADS) + ECMWF Open Data TC 트랙 BUFR. 기상 텍스처와 무관해졌고 typhoons.json 만 선행 필요.
"$PY" track_typhoons.py || echo "  ⚠ 태풍 모델진로 추적 실패(건너뜀)"

# 해수면 이상수온(OISST) + 엘니뇨/라니냐(ONI) — 하루 1회(관측분석·느리게 변함). 산출: sst-anom.png · enso-status.json
SSTA_MARK="$PROJ/.last_sst_anom"
if [ "$(( $(date +%s) - $(stat -f %m "$SSTA_MARK" 2>/dev/null || echo 0) ))" -gt 72000 ]; then
  echo "[이상수온] OISST 이상수온 + ENSO 상태 갱신…"
  if "$PY" fetch_sst_anomaly.py; then touch "$SSTA_MARK"; else echo "  ⚠ 이상수온 갱신 실패(다음 기회에)"; fi
fi

# 1) 뉴스 수집 + merge (GDELT, 무료)
#    이 명령이 '완전히 끝나고 성공(exit 0)'해야만 아래 grok으로 넘어감.
echo "[1/2] GDELT 수집 시작…"
if ! "$PY" fetch_news.py --hours 4; then
  echo "✖ fetch 실패 → grok 건너뜀 (불완전 데이터로 번역 안 함)"
  notify_fail "GDELT 뉴스 수집 실패 — 이번 주기 중단"
  exit 1
fi
echo "[1/2] ✓ 수집·저장 완료 (다운로드가 100% 끝난 뒤에만 이 줄이 보임)"

# 1b) 기업·테크 주제 뉴스(GDELT DOC API, 무료·5초제한) — 실패해도 진행
echo "[1b] GDELT DOC 주제 뉴스(테슬라·AI·우주·반도체 등)…"
"$PY" fetch_topics.py || echo "  ⚠ 주제 뉴스 수집 실패(건너뜀)"

# 1c) 작업 지시서 분할 — grok_task.md(마스터) → task_*.md. AI 호출이 전체(14k토큰) 대신
#     해당 작업 파일만 읽게 해 입력 토큰 절감. 매 실행 재생성(마스터 수정 자동 반영).
"$PY" split_tasks.py || echo "  ⚠ split_tasks 실패 — 프롬프트가 task_*.md 못 읽으면 그 작업만 스킵될 수 있음"

# 2) 번역(translate) — 기본 Claude haiku, 한도면 Grok 폴백(run_ai 양방향).
#    Grok 기사는 한국어 직작성 → 번역 불필요. GDELT 영어만 여기서 처리.
#    Claude 한도 중(.claude_down)이면 run_ai 가 Grok 전용으로 돌린다.
TRANSLATE_PROMPT="이 폴더의 task_translate.md를 읽고 그 지시(번역)를 수행해줘. \
너가 직접 번역가다 — ANTHROPIC_API_KEY나 batch_translate.py 같은 스크립트를 찾지 말고(불필요), 각 제목을 네가 직접 한국어로 번역해 저장해. \
to_translate.json의 모든 항목을 번역해 translations.json에 저장하고 'python3 merge_news.py'를 실행하기를, \
to_translate.json이 빈 배열([])이 될 때까지 반복. 끝나면 종료."
# 번역 Grok→Gemini 최종 폴백: Grok 실패(잔액/한도) 시 Gemini(설치·인증돼 있으면)로 넘김.
#   Claude+Grok 동시 소진 때 번역이 멈춰 뉴스 디제스트가 정체되던 문제 대응(2026-08).
_translate_grok_then_gemini() {
  _run_grok_once "번역·Grok폴백" 120 "$TRANSLATE_PROMPT" "$GROK_MODEL_LIGHT"
  local rc=$?
  if [ "$rc" -ne 0 ] && [ -x "$GEMINI" ] && ! _marker_active "$GEMINI_DOWN" 360; then
    echo "  ⚠ Grok 번역 실패 → Gemini($GEMINI_MODEL) 폴백"
    _run_gemini_once "번역·Gemini폴백" "$GEMINI_MODEL" "$TRANSLATE_PROMPT"; rc=$?
  fi
  return $rc
}
run_translate() {
  # 번역=LIGHT 모델(grok-4.5). Claude 한도면 Grok → Gemini.
  if _marker_active "$CLAUDE_DOWN" 360; then
    echo "  · Claude 한도 중 → 번역 Grok($GROK_MODEL_LIGHT)"
    _translate_grok_then_gemini
    return $?
  fi
  # 평시: haiku 직접(저렴) → 실패/한도면 Grok → Gemini
  local tmp rc
  tmp="$(mktemp -t runai_tr)"
  echo "  → Claude(haiku, effort=low) 번역"
  "$CLAUDE" --dangerously-skip-permissions --model haiku --effort low -p "$TRANSLATE_PROMPT" < /dev/null >"$tmp" 2>&1
  rc=$?
  cat "$tmp"
  if [ "$rc" -eq 0 ] && ! _claude_limited "$tmp"; then
    rm -f "$CLAUDE_DOWN" "$tmp"
    return 0
  fi
  if _claude_limited "$tmp" || [ "$rc" -ne 0 ]; then
    if _claude_limited "$tmp"; then
      touch "$CLAUDE_DOWN"
      echo "  ⚠ Claude 번역 한도 → .claude_down, Grok($GROK_MODEL_LIGHT) 폴백"
    else
      echo "  ⚠ Claude 번역 실패(rc=$rc) → Grok($GROK_MODEL_LIGHT) 폴백"
    fi
    rm -f "$tmp"
    _translate_grok_then_gemini
    return $?
  fi
  rm -f "$tmp"; return 1
}
REMAIN=$("$PY" -c "import json;print(len(json.load(open('to_translate.json'))))" 2>/dev/null || echo 0)
if [ "$REMAIN" -gt 0 ]; then
  echo "[2/4] 번역(Claude haiku→Grok 폴백): 대기 ${REMAIN}건"
  run_translate || echo "  ⚠ 번역 1차 실패 (10분 후 재시도)"
  REMAIN2=$("$PY" -c "import json;print(len(json.load(open('to_translate.json'))))" 2>/dev/null || echo 0)
  if [ "$REMAIN2" -gt 0 ]; then
    sleep 600
    echo "[2/4·재시도] 남은 ${REMAIN2}건 번역 재시도…"
    run_translate || { echo "  ⚠ 재시도도 실패 — 다음 주기에 만회"; notify_fail "번역 2회 연속 실패 (${REMAIN2}건 대기) — Claude 한도·Grok 실패 가능성"; }
  fi
  "$PY" merge_news.py
else
  echo "[2/4] 번역 대기 0건 — 건너뜀"
fi

# 3) 뉴스(동아시아) + 브리핑 + 종목뉴스 — 번역 뒤 실행.
#    ★ 원래 주기(매시간)로 복원(2026-07-29). Grok 상시 운용이라 절감용 3h 게이트 해제.
#    게이트 값(초)만 3000(=50분)으로 두어 매시간 확실히 발화하되, 마커 구조는 유지
#    → 나중에 다시 조이려면 이 값을 10800(3h) 등으로 올리면 됨.
#    뉴스(조사)=Claude haiku(low) 우선·Grok 폴백 / 브리핑(분석)=Grok 4.5 우선·Sonnet5(mid) 폴백 / 종목뉴스=Grok 4.5(mid) 우선·haiku 폴백.
ACD2_MARK="$PROJ/.last_task_acd2"
ACD2_AGE=$(( $(date +%s) - $(stat -f %m "$ACD2_MARK" 2>/dev/null || echo 0) ))
if [ "$ACD2_AGE" -gt 3000 ]; then
  AC_OK=0; BRIEF_OK=0; D2_OK=0
  # 뉴스(조사) = Claude haiku effort low 우선·Grok 폴백
  echo "[3/4] 뉴스(동아시아 조사) (Claude haiku effort=low 우선·Grok 폴백)…"
  if run_ai "뉴스(동아시아)" 200 haiku \
"이 폴더의 task_asia-news.md 를 읽고 그 지시만 수행해줘 (브리핑·번역·종목뉴스는 다른 단계가 담당하니 하지 마). \
동아시아 중심 최신 뉴스를 조사해 grok-news.json에 저장한 뒤 종료해 (merge_news.py 실행은 아래 셸이 자동 처리하니 하지 마)." \
    "$GROK_MODEL_HEAVY" "$GROK_EFFORT_DEFAULT" "low" "1"; then
    AC_OK=1
    # 실제 조사 엔진/모델(run_ai 폴백 반영)을 라벨용으로 기록 후 merge → 뉴스 배지에 실제 AI/모델 표시
    printf '{"engine":"%s","model":"%s"}\n' "$RUN_AI_ENGINE" "$RUN_AI_MODEL" > "$PROJ/.news_engine.json"
    "$PY" merge_news.py || true
  else
    echo "  ⚠ 뉴스 조사 종료(에러 가능)"
  fi
  # 시장 브리핑(분석) = Grok grok-4.5 우선 → Sonnet5 effort medium 폴백 (분석형이라 강한 모델)
  echo "[3/4] 시장 브리핑 (Grok $GROK_MODEL_HEAVY 우선 → Sonnet5 effort=mid 폴백)…"
  if run_ai "시장 브리핑" 120 sonnet \
"이 폴더의 task_brief.md 를 읽고 그 지시만 수행해줘 (뉴스 조사·번역·종목뉴스는 하지 마). \
market-digest.json·macro-digest.json과 오늘 뉴스를 종합 분석해 시장 브리핑(돈의 흐름)을 market-brief.json에 저장하고 종료해." \
    "$GROK_MODEL_HEAVY" "$GROK_EFFORT_DEFAULT" "medium"; then
    BRIEF_OK=1
    "$PY" stamp_brief_gen.py "$RUN_AI_ENGINE" "$RUN_AI_MODEL" "$RUN_AI_EFFORT"   # 생성 AI/모델/effort 배지 기록
  else
    echo "  ⚠ 시장 브리핑 종료(에러 가능)"
  fi
  echo "[3/4] 종목뉴스 (Grok $GROK_MODEL_HEAVY effort=$GROK_EFFORT_D2)…"
  if run_ai "종목뉴스" 150 haiku \
"이 폴더의 task_stock-news.md를 읽고 그 파일의 지시만 수행해줘 (다른 작업은 하지 마). \
task_stock-news.md에 명시된 전 종목(미국 19 + 한국 11 = 30종목) 최신 뉴스·SNS를 stocks-news.js에 저장 \
(원문 URL 필수, 한국종목은 news만·sns:[], SNS 규칙 준수). \
news-data.js 재사용을 우선하고 부족분만 검색 보충. 끝나면 종료해." \
    "$GROK_MODEL_HEAVY" "$GROK_EFFORT_D2" "medium"; then
    D2_OK=1
    # 방어: Claude 폴백 등이 ES모듈 구문(export default/export {})을 붙이면
    #   일반 <script> 로드가 'Unexpected token export'로 통째 실패 → STOCKS_NEWS 미정의 →
    #   종목 뉴스·SNS 전부 안 뜸. 저장 직후 해당 구문 제거(멱등).
    sed -i '' '/^[[:space:]]*export default/d; /^[[:space:]]*export {/d' "$PROJ/stocks-news.js" 2>/dev/null || true
  else
    echo "  ⚠ 종목뉴스 종료(에러 가능)"
  fi
  if [ "$AC_OK" = 1 ] || [ "$BRIEF_OK" = 1 ] || [ "$D2_OK" = 1 ]; then
    touch "$ACD2_MARK"
  else
    echo "  ⚠ 뉴스·브리핑·종목뉴스 전부 실패 — 다음 기회에 재시도"
  fi
else
  echo "[3/4] 뉴스·브리핑·종목뉴스 — $((ACD2_AGE/60))분 전 실행됨(3h 미만) → 건너뜀"
fi

# 3b) Grok 테크딜(글로벌 테크 딜 실검색) — 하루 2회(마커가 11시간+ 묵었을 때).
#   GDELT DOC(어그리게이터 편중)이 못 보는 전문·1차·다국어 테크 소스를 Grok 웹 실검색으로 보강.
F_MARK="$PROJ/.last_task_f"
F_AGE=$(( $(date +%s) - $(stat -f %m "$F_MARK" 2>/dev/null || echo 0) ))
if [ "$F_AGE" -gt 39600 ]; then
  echo "[테크딜] 테크딜 조사(Claude haiku 우선·Grok 폴백, 글로벌 테크 딜 실검색)…"
  if run_ai "테크딜" 200 haiku \
"이 폴더의 task_tech-deals.md를 읽고 그 파일의 지시만 수행해줘 (다른 작업은 하지 마). \
AI·반도체·양자·우주·자율주행·데이터센터·국방테크·로보틱스 8개 섹터의 딜·발표 뉴스를 \
전문·1차·다국어 소스(Electrek·DIGITIMES·SpaceNews·DCD·Quantum Insider·NHTSA·SEC 등)에서 실검색해 \
grok-tech-news.json에 저장하고 'python3 merge_news.py'를 실행한 뒤 종료해." \
    "$GROK_MODEL_HEAVY" "$GROK_EFFORT_DEFAULT" "low" "1"; then
    touch "$F_MARK"
  else
    echo "  ⚠ 테크딜 실패(다음 기회에)"
  fi
fi

# 3c) 캘린더 실제값(actual) 시간내 충전 — '발표시각(KST) 지났는데 actual 빈' 이벤트가 있으면
#   Grok 으로 즉시 채운다. 하루 1회 캘린더 갱신과 별개로 매시간(정각) 확인 → 발표 후 1시간 내 반영 보장.
PEND=$("$PY" pending_actuals.py 2>/dev/null | tail -1)
if [ "${PEND:-0}" -gt 0 ] 2>/dev/null; then
  echo "[캘린더 actual+그래프] 발표완료·미충전 ${PEND}건 → 실제값+시리즈 조사(Claude haiku 우선·Grok 폴백)"
  run_ai "캘린더 actual+시리즈" 100 haiku \
"이 폴더 pending-actuals.json = '발표시각이 이미 지났는데 실제값(actual)이 아직 빈' 캘린더 이벤트 목록이다. \
각 이벤트의 실제 발표값을 공식·신뢰 출처(Trading Economics·Investing·회사 IR·거래소 공시)로 확인하라(지어내기 절대 금지, 미공표는 null). \
① econ-calendar.json 을 읽어(없으면 새 배열로) 같은 date+(ticker|title) 항목의 actual 만 채운다(다른 항목·필드 손대지 말 것). \
② ⭐그래프(추세 차트)도 채운다 — task_earnings.md·task_calendar.md 의 형식대로 series-delta.json 을 만든다: \
  · 실적(ticker 있는 이벤트) → earnings 섹션에 그 티커의 새 분기 {period:'QN YYYY (YYYY-MM)', <각 metric>:{act,cons}, source} 추가. metric 종류·단위는 earnings-series.js 의 그 티커 metrics 기준(revenue·eps 등, \$B·\$). cons=컨센서스(forecast)에서 수치 추출·act=실제 — act만 넣지 말고 cons도 반드시 함께(둘이 같아도 둘 다 기록). \
  · 거시(ticker 없는 이벤트) → macro 섹션에 해당 지표 releases 새 항목 {period,cons,act,source} 추가(지표 매칭·형식은 macro-series.js 참고). \
  · 기존 종목/지표면 새 분기/회차만 내도 됨(merge 가 과거 보존·중복 정리). \
③ 'python3 merge_econ.py' 와 'python3 merge_series.py --delta series-delta.json' 을 둘 다 실행하고 종료." \
    "$GROK_MODEL_HEAVY" "$GROK_EFFORT_DEFAULT" "low" "1" \
    || echo "  ⚠ 캘린더 actual/그래프 충전 실패(다음 시간 재시도)"
fi

# 2-일일) 종목 재무(stock-fin) + 거시 캘린더(calendar) — 하루 1회만(전용 마커 .last_daily_de 기준).
#   재무는 분기 실적 때만 바뀌고 발표일정도 자주 안 바뀌므로 매시간 조사는 낭비.
#   ※ 예전엔 stocks-info.js mtime 으로 게이팅했으나, 마켓 세션이 그 파일을 자주 갱신해
#     20h 게이트가 계속 리셋 → 캘린더 actual 갱신이 못 도는 문제가 있었다. 전용 마커로 분리.
DE_MARK="$PROJ/.last_daily_de"
DDE_AGE=$(( $(date +%s) - $(stat -f %m "$DE_MARK" 2>/dev/null || echo 0) ))
if [ "$DDE_AGE" -gt 72000 ]; then
  # 방향 B: 커버리지 검증(결정론) → AI 조사(큐 기반, delta) → 결정론 병합 → 재검증.
  #   각 단계 실패해도 크론은 계속(|| echo). 사용자가 새 종목·지표를 넣어도 큐에 자동으로 잡힌다.
  echo "[일일·큐] coverage_check.py — 커버리지 갭 → pipeline-todo.json"
  "$PY" coverage_check.py || echo "  ⚠ coverage_check(큐 생성) 실패 — 이번 주기는 큐 없이 진행"
  echo "[일일] 재무(stock-fin)+캘린더(calendar)+거시delta(calendar-delta)+실적delta(earnings) — Claude haiku 우선·Grok 폴백…"
  run_ai "일일 재무·캘린더·delta" 200 haiku \
"이 폴더의 task_common.md·task_stock-fin.md·task_calendar.md·task_earnings.md 를 읽어라. **task_common.md의 '시장 파이프라인 공통 계약'을 준수**하고 pipeline-todo.json 큐 기반으로 각 파일의 지시를 수행해줘 (뉴스·번역·종목뉴스·테크딜은 하지 마). \
calendar: 캘린더 모든 거시·실적 이벤트의 신규 발표일·forecast·actual를 econ-calendar.json에 저장. \
stock-fin: pipeline-todo.json의 stocks_info_todo(신규 종목 포함) + 기존 종목 재무·자산·부채·밸류에이션을 stocks-info.js에 갱신(과거 종목 보존, 한국종목 조원₩). \
calendar-delta: pipeline-todo.json의 macro_todo(각 seriesId·missingPeriods)와 unmapped(신규 지표)를 조사해 series-delta.json의 macro 섹션으로 낸다(파일 직접 편집 금지). \
earnings: pipeline-todo.json의 earnings_todo·earnings_stale를 조사해 series-delta.json의 earnings 섹션으로 낸다. \
검증된 사실만·불확실 null·과거 삭제 금지·지시서 self-edit 금지. 끝나면 종료." \
    "$GROK_MODEL_HEAVY" "$GROK_EFFORT_DEFAULT" "low" "1" \
    || echo "  ⚠ 일일 재무·캘린더·delta 실패(다음 기회에)"
  # 공시 대조표 갱신 — market_guard 가 AI 실적값을 DART 원문과 맞춰보는 정답지.
  #   반드시 merge 앞에 둔다(대조표가 낡으면 최신 분기를 검증 못 함). 실패해도 기존 캐시로 진행.
  echo "[일일] 한국 실적 공시 대조표 갱신(fetch_kr_earnings_ref.py)…"
  "$PY" fetch_kr_earnings_ref.py || echo "  ⚠ 공시 대조표 갱신 실패(기존 캐시 사용)"
  # 결정론 저장: 캘린더 누적 + series delta append-only 병합.
  #   두 merge 모두 market_guard 로 유니버스·회사명·발표일정·산술·공시대조를 검증한다.
  echo "[일일] econ 캘린더 누적(merge_econ.py) + series delta 병합(merge_series.py)…"
  "$PY" merge_econ.py || echo "  ⚠ econ 캘린더 병합 실패(다음 기회에)"
  "$PY" merge_series.py --delta series-delta.json || echo "  ⚠ series delta 병합 실패(delta 없음/오류 — 기존 유지)"
  # 최종 안전망: 병합 후 산출물을 전수 재점검·교정(어느 경로로 들어왔든 오염 잔류 금지).
  "$PY" market_guard.py --fix || echo "  ⚠ market_guard 최종 점검 실패(건너뜀)"
  # 재검증: 남은 갭을 coverage.log에 기록(어떤 항목도 조용히 누락 금지).
  echo "[일일·검증] coverage_check.py 재실행 — 남은 갭 로그"
  "$PY" coverage_check.py || echo "  ⚠ coverage_check(재검증) 실패"
  touch "$DE_MARK"   # 일일 블록 실행 완료 표시(다음 실행은 20h 후). stocks-info.js 갱신과 무관.
fi

# (번역은 위 GDELT 수집 직후·Grok 전으로 이동함 — Grok 기사는 한국어라 기다릴 필요 없음)

# 3-폴백) 브리핑(brief)이 4시간+ 묵으면 run_ai 로 재시도(Grok grok-4.5 우선 → Sonnet5 effort mid 폴백)
#    브리핑은 분석 품질이 핵심 → 강한 모델 유지(조사작업과 달리 haiku-low 안 씀).
BRIEF_AGE=$(( $(date +%s) - $(stat -f %m "$PROJ/market-brief.json" 2>/dev/null || echo 0) ))
if [ "$BRIEF_AGE" -gt 14400 ]; then
  echo "[폴백] 브리핑이 ${BRIEF_AGE}초 묵음(4시간+) → run_ai 브리핑 (Grok 우선·Sonnet5 mid 폴백)"
  run_ai "브리핑 폴백" 100 sonnet \
"이 폴더의 task_brief.md를 읽고 시장 브리핑만 수행해줘. \
market-digest.json·macro-digest.json과 오늘 뉴스를 분석해 market-brief.json에 저장하고 종료해." \
    "$GROK_MODEL_HEAVY" "$GROK_EFFORT_DEFAULT" "medium" \
    && "$PY" stamp_brief_gen.py "$RUN_AI_ENGINE" "$RUN_AI_MODEL" "$RUN_AI_EFFORT" \
    || { echo "  ⚠ 브리핑 폴백 실패"; notify_fail "시장 브리핑 4시간+ 미갱신 — Grok·Claude 모두 실패"; }
fi

# 4) Cloudflare Pages 배포 (wrangler 로그인돼 있을 때만 — 미로그인이면 조용히 건너뜀)
if "$NPX" wrangler whoami >/dev/null 2>&1; then
  echo "[배포] Cloudflare Pages…"
  /bin/bash "$PROJ/deploy_cf.sh" || { echo "  ⚠ 배포 실패 (다음 주기에 재시도)"; notify_fail "Cloudflare Pages 배포 실패"; }
else
  echo "[배포] wrangler 미로그인 — 건너뜀"
fi

echo "===== $(date '+%Y-%m-%d %H:%M:%S') 완료 ====="
