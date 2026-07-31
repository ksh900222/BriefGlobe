#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
market_dates.py — 시장 '구조일'(네 마녀의 날·옵션/선물 만기)을 **규칙으로 계산**해
econ-calendar-store.json 에 병합(멱등). AI 추측이 아니라 확정 규칙이라 날짜가 정확하다.

규칙(고정):
  🇺🇸 미국  = 매월 **셋째 금요일**
       · 3·6·9·12월 → 네 마녀의 날(쿼드러플 위칭): 지수선물·지수옵션·개별주식옵션·개별주식선물 동시만기
       · 그 외 달   → 월간 옵션 만기
  🇰🇷 한국  = 매월 **둘째 목요일** (KRX 파생 만기, 장 마감 동시호가 ~15:20)
       · 3·6·9·12월 → 선물·옵션 동시만기(네 마녀의 날, KOSPI200)
       · 그 외 달   → KOSPI200 옵션 만기

창: 오늘 ~ +150일(다음 분기 만기까지 항상 노출). dedup 키 = "date|title"(merge_econ 과 동일).
kind="시장" → 프론트에서 ec-mkt 배지(호박색)로 표시. prev/forecast/actual 없음(구조일이라 값 없음).
"""
import json, os, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
STORE = os.path.join(HERE, "econ-calendar-store.json")
WINDOW_DAYS = 150
QUAD = {3, 6, 9, 12}


def nth_weekday(y, m, weekday, n):
    """그 달의 n번째 특정 요일(weekday: 월0..일6) 날짜."""
    first = datetime.date(y, m, 1)
    shifted = first + datetime.timedelta(days=(weekday - first.weekday()) % 7)
    return shifted + datetime.timedelta(weeks=n - 1)


def months(start, end):
    y, m = start.year, start.month
    while datetime.date(y, m, 1) <= end:
        yield y, m
        m += 1
        if m > 12:
            m, y = 1, y + 1


def build(today):
    end = today + datetime.timedelta(days=WINDOW_DAYS)
    out = []
    for y, m in months(today.replace(day=1), end):
        us = nth_weekday(y, m, 4, 3)          # 셋째 금요일
        if today <= us <= end:
            out.append({"date": us.isoformat(), "time": "", "country": "미국", "kind": "시장",
                        "title": ("네 마녀의 날 (쿼드러플 위칭) — 지수·개별주식 선물·옵션 동시만기"
                                  if m in QUAD else "월간 옵션 만기 (미 증시)"),
                        "importance": 3 if m in QUAD else 1})
        kr = nth_weekday(y, m, 3, 2)          # 둘째 목요일
        if today <= kr <= end:
            out.append({"date": kr.isoformat(), "time": "15:20", "country": "한국", "kind": "시장",
                        "title": ("선물·옵션 동시만기 (네 마녀의 날, KOSPI200)"
                                  if m in QUAD else "KOSPI200 옵션 만기"),
                        "importance": 3 if m in QUAD else 1})
    return out


def main():
    store = []
    if os.path.exists(STORE):
        try:
            d = json.loads(open(STORE, encoding="utf-8").read())
            if isinstance(d, list):
                store = d
        except json.JSONDecodeError:
            print("  ⚠ econ-calendar-store.json 파싱 실패 — 빈 목록으로 시작")
    have = {f'{it.get("date","")}|{it.get("title","")}' for it in store if isinstance(it, dict)}
    added = 0
    for it in build(datetime.date.today()):
        k = f'{it["date"]}|{it["title"]}'
        if k not in have:
            store.append(it); have.add(k); added += 1
    store.sort(key=lambda x: (x.get("date", ""), x.get("time", "")))
    open(STORE, "w", encoding="utf-8").write(json.dumps(store, ensure_ascii=False, indent=1))
    print(f"✔ market_dates: 시장 구조일 {added}건 신규 추가 (스토어 총 {len(store)}건)")


if __name__ == "__main__":
    main()
