#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
text_corrections.py · 뉴스/속보 텍스트 교정(반복 사실오류·외래어표기 표준화)
------------------------------------------------------------------------
왜: 뉴스 연구가 Grok 다운 시 Claude Haiku(실시간 검색 없음)로 폴백되면
    현직 인물/직책을 환각하거나(예: 대한민국 대통령을 '이준석'으로) 외래어를
    제각각 표기(쿠슈너/쿠시너)하는 문제가 있다. 프롬프트 앵커(예방)만으로는
    100% 못 막으므로, 저장 직전 결정론적 교정을 안전망으로 둔다.

규칙: text_corrections.json 의 replacements(앞→뒤 부분문자열 치환).
     오탐이 없는(항상 참인) 교정만 등재한다.
     예) '이준석 대통령'은 항상 오류(이준석은 대통령인 적 없음) → 안전.

사용:
    from text_corrections import apply_corrections, correct_item
    title = apply_corrections(title)
    correct_item(news_dict)            # dict 의 텍스트 필드 in-place 교정
"""
import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_PATH = os.path.join(_HERE, "text_corrections.json")
_CACHE = None

# 교정 대상 기본 필드(dict 교정 시). 존재하는 것만 건드린다.
DEFAULT_FIELDS = ("title", "summary", "name", "note", "text", "desc", "detail")


def _rules():
    global _CACHE
    if _CACHE is None:
        try:
            with open(_PATH, encoding="utf-8") as f:
                _CACHE = json.load(f).get("replacements", {}) or {}
        except (OSError, ValueError):
            _CACHE = {}
    return _CACHE


def apply_corrections(text):
    """문자열에 모든 교정 규칙을 순서대로 부분문자열 치환."""
    if not text or not isinstance(text, str):
        return text
    for bad, good in _rules().items():
        if bad and bad in text:
            text = text.replace(bad, good)
    return text


def correct_item(it, fields=DEFAULT_FIELDS):
    """dict 의 지정 텍스트 필드를 in-place 교정(있는 것만). dict 를 그대로 반환."""
    if isinstance(it, dict):
        for k in fields:
            v = it.get(k)
            if isinstance(v, str):
                it[k] = apply_corrections(v)
    return it


if __name__ == "__main__":       # 간이 테스트: python3 text_corrections.py
    tests = ["이준석 대통령이 광복절 경축사를 발표했다",
             "한국 대통령 이준석, 북한과 협상",
             "재러드 쿠시너가 중동 순방에 나섰다",
             "이재명 대통령(정상)과 쿠슈너(정상)"]
    for t in tests:
        print(repr(t), "→", repr(apply_corrections(t)))
