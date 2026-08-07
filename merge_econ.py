#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
 merge_econ.py  ·  경제·실적 캘린더 누적 병합 (시장 도메인)
------------------------------------------------------------
 문제: 작업 E(Grok, 하루 1회)가 만드는 econ-calendar.json 은
   "최근 3일 발표분 + 향후 2~4주"만 담아 매번 통째로 덮어쓴다.
   → 3일 넘게 지난 발표(특히 발표된 actual 실제값)가 영구히 사라짐.

 해결: 이 스크립트가 매일 econ-calendar.json 을 누적본
   econ-calendar-store.json 에 병합한다.
   - 병합 키: date + (ticker | title)  → 같은 발표는 하나로.
   - actual(실제값)은 한 번 채워지면 보존(새 rolling window 에서
     빠져도 store 엔 남는다).
   - forecast/prev/importance/source/time 등은 최신 rolling 값으로 갱신.
   - 보관 기간 약 1년(RETENTION_DAYS) — 그보다 오래된 건 정리.

 사용:
   python3 merge_econ.py                # 병합 1회
   python3 merge_econ.py --in FILE --store FILE   # 경로 지정(테스트)

 프론트(loadEconCalendar)는 econ-calendar-store.json 을 우선 읽어
 과거 발표까지 조회한다(없으면 econ-calendar.json 폴백).
============================================================
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROLLING_PATH = HERE / "econ-calendar.json"          # Grok 작업 E rolling window
STORE_PATH = HERE / "econ-calendar-store.json"      # 과거까지 누적 보존본
RETENTION_DAYS = 400   # 약 1년 보관(여유 포함). 그보다 오래된 발표는 정리.


def _load(path):
    if path.exists():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            print(f"  ⚠ {path.name} JSON 파싱 실패 — 빈 목록으로 처리")
    return []


def _key(it):
    """병합 키: 날짜 + (티커 | 제목). 같은 날 같은 발표는 하나로 취급."""
    date = (it.get("date") or "").strip()
    ident = (it.get("ticker") or it.get("title") or "").strip()
    return f"{date}|{ident}"


def _has_actual(it):
    a = it.get("actual")
    return a is not None and str(a).strip() != ""


def is_bad_earnings(it):
    """실적 이벤트인데 실제 발표가 아닌 것을 판정(True=제외).
       AI(특히 폴백)가 확정 발표일을 모를 때 미래 분기를 현재 날짜에 당겨 넣거나
       '가이던스'(전망) 같은 비(非)이벤트를 만들어내던 문제를 결정론적으로 차단.
       ⚠️ 이미 실제값(actual)이 있는 발표는 진짜 이벤트이므로 절대 제외하지 않는다."""
    if not isinstance(it, dict) or it.get("kind") != "실적":
        return False
    if _has_actual(it):                      # 실제값 있으면 확정된 발표 → 보존
        return False
    title = it.get("title") or ""
    # (a) 가이던스·전망은 실적 '발표' 이벤트가 아님
    if re.search(r"가이던스|guidance|전망치", title, re.I):
        return True
    # (b) 'N월말'(회계분기 종료월)이 발표일보다 1~6개월 뒤 = 아직 끝나지도 않은 분기를
    #     현재/과거 날짜에 배치한 것 → 실적 발표 불가(발표는 분기 종료 후).
    date = it.get("date") or ""
    m = re.search(r"(\d{1,2})\s*월말", title)
    if m and re.match(r"\d{4}-\d{2}", date):
        end_month = int(m.group(1))
        d_year, d_month = int(date[:4]), int(date[5:7])
        if 0 < ((d_year * 12 + end_month) - (d_year * 12 + d_month)) <= 6:
            return True
    return False


def merge(rolling, store):
    """store(누적) 위에 rolling(최신 window)을 병합한 새 목록을 돌려준다.
       - actual 은 한 번 채워지면 보존.
       - 그 외 필드는 rolling(최신)으로 갱신.
    """
    by_key = {}
    # 1) 기존 누적본을 먼저 깐다(과거 발표 보존).
    for it in store:
        if isinstance(it, dict) and it.get("date"):
            by_key[_key(it)] = dict(it)
    # 2) 최신 rolling 을 덮되 actual 은 보존.
    for it in rolling:
        if not (isinstance(it, dict) and it.get("date")):
            continue
        k = _key(it)
        old = by_key.get(k)
        if old is None:
            by_key[k] = dict(it)
            continue
        merged = dict(old)          # 기존값 기반
        merged.update(it)           # 최신 rolling 으로 갱신(forecast/prev/time 등)
        # actual 보존: rolling 에 실제값이 없고 기존에 있으면 기존 유지.
        if not _has_actual(it) and _has_actual(old):
            merged["actual"] = old["actual"]
        by_key[k] = merged
    return list(by_key.values())


def prune(items, today=None):
    """보관 기간(약 1년) 지난 항목 정리."""
    today = today or datetime.now(timezone.utc).date()
    kept = []
    for it in items:
        try:
            d = datetime.strptime((it.get("date") or "")[:10], "%Y-%m-%d").date()
        except (ValueError, TypeError):
            continue
        if (today - d).days <= RETENTION_DAYS:
            kept.append(it)
    return kept


def main(argv):
    rolling_path, store_path = ROLLING_PATH, STORE_PATH
    if "--in" in argv:
        rolling_path = Path(argv[argv.index("--in") + 1])
    if "--store" in argv:
        store_path = Path(argv[argv.index("--store") + 1])

    rolling = _load(rolling_path)
    store = _load(store_path)
    if not rolling and not store:
        print("  ⚠ econ 캘린더 입력이 비어 있음 — 병합 건너뜀")
        return 0

    merged = merge(rolling, store)
    merged = prune(merged)
    # sanity: 미래 분기 오배치·가이던스 등 '실제 발표가 아닌' 실적 이벤트 제거(actual 있는 건 보존)
    bad = [x for x in merged if is_bad_earnings(x)]
    if bad:
        print(f"  🧹 실적 캘린더 정리: 미래분기 오배치·가이던스 {len(bad)}건 제외")
        for x in bad:
            print(f"     − {x.get('date')} {x.get('ticker') or ''} {x.get('title')}")
    merged = [x for x in merged if not is_bad_earnings(x)]
    merged.sort(key=lambda x: ((x.get("date") or ""), (x.get("time") or "")))

    store_path.write_text(
        json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")

    n_actual = sum(1 for x in merged if _has_actual(x))
    print(f"✔ econ 캘린더 누적: rolling {len(rolling)}건 + store → 총 {len(merged)}건 "
          f"(actual 보존 {n_actual}건) → {store_path.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
