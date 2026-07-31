#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
split_tasks.py — grok_task.md(마스터)를 작업별 파일로 분할.
목적: AI 호출마다 grok_task.md 전체(~14k 토큰)를 읽던 것을, 해당 작업 파일(~1~3k)만 읽게 해 입력 토큰 절감.
산출: task_common.md(서두 + 시장 파이프라인 공통 계약) + 작업별 task_<슬러그>.md
      (슬러그 = 마스터의 '# <슬러그> —' 헤더: asia-news·translate·brief·stock-fin·stock-news·calendar·tech-deals·earnings)
auto_update.sh 가 AI 작업 전에 이걸 먼저 실행 → 마스터(grok_task.md) 수정분이 자동 반영.
멱등: 매번 덮어씀.
"""
import re, os, glob

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "grok_task.md")
# [레거시 안전망] 혹시 마스터에 옛 letter 표기(작업 A·D2·상호참조·압축리스트)가 남아 있으면
# 생성 시점에 서술형으로 치환 → 다른 AI가 읽어도 혼란 없게. 마스터가 이미 서술형이면 no-op.
# 순서 중요(압축리스트·D2·E-2 먼저).
_DELETTER = [
    ("(A·C·D2)", "(asia-news·brief·stock-news)"),
    ("작업 D·E·E-2·G", "stock-fin·calendar·calendar-delta·earnings"),
    ("작업 A·B", "asia-news·translate"),
    ("작업 E-2", "calendar-delta"), ("작업 D2", "stock-news"),
    ("작업 A", "asia-news"), ("작업 B", "translate"), ("작업 C", "brief"),
    ("작업 D", "stock-fin"), ("작업 E", "calendar"),
    ("작업 F", "tech-deals"), ("작업 G", "earnings"),
]

def deletter(t):
    for a, b in _DELETTER:
        t = t.replace(a, b)
    return t

def main():
    text = open(SRC, encoding="utf-8").read()
    lines = text.splitlines(keepends=True)
    # 작업 헤더 = '# <슬러그> —' (슬러그 = 소문자·숫자·하이픈). 파일명이 곧 슬러그.
    hdr = re.compile(r"^# ([a-z][a-z0-9-]*) —")
    # '# 🔧 … 공통 계약 …' = 시장 파이프라인 공통 계약 → task_common.md 로 라우팅(특정 작업에 딸리면 안 됨).
    contract = re.compile(r"^# .*공통 계약")
    marks = [(i, hdr.match(l).group(1)) for i, l in enumerate(lines) if hdr.match(l)]
    if not marks:
        print("⚠ '# <슬러그> —' 헤더를 못 찾음 — 분할 안 함"); return
    contract_idx = next((i for i, l in enumerate(lines) if contract.match(l)), None)
    # 모든 섹션 경계(작업 헤더 + 공통계약 헤더) — 각 섹션은 다음 경계 직전에서 끝남.
    boundaries = sorted([m[0] for m in marks] + ([contract_idx] if contract_idx is not None else []))
    def sect_end(start):
        nxt = [b for b in boundaries if b > start]
        return nxt[0] if nxt else len(lines)
    # 이전 생성물(구 letter명 포함) 정리 후 재생성 → 고아 파일 방지
    for f in glob.glob(os.path.join(HERE, "task_*.md")):
        os.remove(f)
    written = []
    # 공통 = 서두(첫 경계 이전) + 공통계약 블록(있으면). 둘 다 task_common.md.
    parts = ["".join(lines[:boundaries[0]]).strip()]
    if contract_idx is not None:
        parts.append("".join(lines[contract_idx:sect_end(contract_idx)]).strip())
    common = deletter("\n\n".join(p for p in parts if p))
    if common:
        open(os.path.join(HERE, "task_common.md"), "w", encoding="utf-8").write(common + "\n")
        written.append("task_common.md")
    # 각 작업 섹션 = 슬러그 헤더 ~ 다음 경계 직전. 파일명 = 슬러그.
    for start, slug in marks:
        body = deletter("".join(lines[start:sect_end(start)]).rstrip())
        fn = f"task_{slug}.md"
        open(os.path.join(HERE, fn), "w", encoding="utf-8").write(body + "\n")
        written.append(fn)
    kb = lambda f: os.path.getsize(os.path.join(HERE, f)) / 1024
    print("✔ split_tasks: " + ", ".join(f"{f}({kb(f):.0f}KB)" for f in written))

if __name__ == "__main__":
    main()
