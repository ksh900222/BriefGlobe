#!/usr/bin/env python3
# 시장 브리핑(market-brief.json)에 생성 AI/모델/effort 를 기록 → 프런트가 색 배지로 표시.
#   사용: python3 stamp_brief_gen.py <ai> <model> <effort>
#   run_ai 성공 후 auto_update.sh 가 RUN_AI_ENGINE/MODEL/EFFORT 를 넘겨 호출.
import json, sys

ai     = sys.argv[1] if len(sys.argv) > 1 else ""
model  = sys.argv[2] if len(sys.argv) > 2 else ""
effort = sys.argv[3] if len(sys.argv) > 3 else ""

if not ai:
    sys.exit(0)   # 엔진 미상이면 기록 안 함(기존 필드 유지)

PATH = "market-brief.json"
try:
    with open(PATH, encoding="utf-8") as f:
        d = json.load(f)
    d["generator"] = {"ai": ai, "model": model, "effort": effort}
    with open(PATH, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    print(f"  · 브리핑 생성기 기록: {ai}/{model}/{effort}")
except Exception as e:
    print(f"  ⚠ 브리핑 생성기 스탬프 실패: {e}")
