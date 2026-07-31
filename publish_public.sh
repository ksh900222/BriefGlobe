#!/bin/bash
# ============================================================
#  publish_public.sh · 정리된 스냅샷을 공개 저장소로 반영
# ------------------------------------------------------------
#  이 (비공개) 저장소의 최신 커밋(HEAD)에서 'git 추적 파일'만
#  공개 저장소로 추출→커밋한다.
#   · .gitignore 된 데이터·비밀·내부문서·기상이미지·node_modules 는
#     애초에 추적되지 않으므로 자동으로 빠진다.
#   · 공개 저장소의 .git(히스토리)은 보존, 나머지는 매번 스냅샷으로 교체.
#   · push 는 하지 않는다(내용 검토 후 수동).
#
#  ⚠️ HEAD(마지막 커밋) 기준이다. 반영 전에 이 저장소에서 먼저 커밋할 것.
#
#  공개 저장소 경로: 환경변수 PUBLIC_REPO 로 지정, 없으면 기본값 사용.
#    PUBLIC_REPO=/path/to/public ./publish_public.sh
# ============================================================
set -euo pipefail

SRC="$(cd "$(dirname "$0")" && pwd)"
PUB="${PUBLIC_REPO:-$HOME/PycharmProjects/BriefGlobe-public}"

if [ ! -d "$PUB/.git" ]; then
  echo "✖ 공개 저장소가 없습니다: $PUB"
  echo ""
  echo "  먼저 공개용 저장소를 한 번만 만들어 두세요:"
  echo "    gh repo create BriefGlobe --public --description 'World news/geopolitics/market globe'"
  echo "    git clone <생성된 URL> \"$PUB\""
  echo "  또는 다른 위치를 쓰려면:  PUBLIC_REPO=/원하는/경로 ./publish_public.sh"
  exit 1
fi

echo "▶ HEAD 스냅샷 → $PUB (추적 파일만 복사)"

# 공개 저장소 내용 비우기(.git 히스토리는 보존)
find "$PUB" -mindepth 1 -maxdepth 1 -not -name '.git' -exec rm -rf {} +

# 최신 커밋의 추적 파일을 공개 저장소로 추출(gitignore 대상은 자동 제외)
git -C "$SRC" archive HEAD | tar -x -C "$PUB"

cd "$PUB"
git add -A
if git diff --cached --quiet; then
  echo "변경 없음 — 커밋 생략."
  exit 0
fi

git commit -m "스냅샷 $(date +%Y-%m-%d)"
echo ""
echo "✔ 공개 저장소 커밋 완료: $PUB"
echo "  내용을 확인한 뒤 push 하세요:"
echo "    (cd \"$PUB\" && git push)"
