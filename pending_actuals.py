#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
 pending_actuals.py · 캘린더 '발표 완료·실제값 미충전' 탐지 (시장 도메인)
------------------------------------------------------------
 발표시각(KST)이 이미 지났는데 actual(실제값)이 아직 비어 있는
 '최근' 캘린더 이벤트를 찾아 pending-actuals.json 으로 내보낸다.

 auto_update.sh 가 매시간 호출한다:
   - 출력(마지막 줄) = 미충전 건수.
   - 건수 > 0 이면 Grok 이 그 이벤트들의 actual 만 채운다
     → '발표 후 1시간 내' 실제값 반영 보장. (하루 1회 작업 E 와 별개)

 사용:
   python3 pending_actuals.py      # pending-actuals.json 생성 + 건수 출력
============================================================
"""
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
    KST = ZoneInfo("Asia/Seoul")
except Exception:               # zoneinfo 없으면 UTC+9 로 근사
    KST = None

HERE = Path(__file__).resolve().parent
LOOKBACK_DAYS = 4   # 이보다 오래된 미충전은 무시(오래된 건 실제값 확보가 어렵거나 의미가 적음)


def _load(name):
    p = HERE / name
    if p.exists():
        try:
            j = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(j, list):
                return j
        except json.JSONDecodeError:
            pass
    return []


def _now_kst():
    if KST:
        return datetime.now(KST)
    return datetime.utcnow() + timedelta(hours=9)


def _evdt(x):
    """이벤트 발표시각 문자열(YYYY-MM-DDTHH:MM). 시각 미상이면 그날 끝으로 간주."""
    return (x.get("date") or "") + "T" + (x.get("time") or "23:59")


def _has_actual(x):
    a = x.get("actual")
    return a is not None and str(a).strip() not in ("", "null", "None")


def main():
    # 누적본(store) 우선 — 모든 이벤트가 여기 있음. 없으면 rolling.
    items = _load("econ-calendar-store.json") or _load("econ-calendar.json")
    now = _now_kst()
    now_s = now.strftime("%Y-%m-%dT%H:%M")
    cutoff = (now - timedelta(days=LOOKBACK_DAYS)).strftime("%Y-%m-%d")

    pending = [x for x in items
               if isinstance(x, dict) and x.get("date")
               and (x.get("date") or "") >= cutoff      # 최근 것만
               and _evdt(x) <= now_s                     # 발표시각 지남
               and not _has_actual(x)]                   # actual 아직 빔

    (HERE / "pending-actuals.json").write_text(
        json.dumps(pending, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(pending))
    return 0


if __name__ == "__main__":
    sys.exit(main())
