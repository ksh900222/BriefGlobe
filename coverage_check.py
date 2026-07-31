#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
 coverage_check.py  ·  시장 파이프라인 커버리지 검증 (결정론, 시장 도메인)
------------------------------------------------------------
 목적: 사용자가 SERIES(종목)·캘린더(지표)에 항목을 추가해도
   AI가 조용히 누락하지 않도록, "무엇을 아직 조사·저장 안 했는지"를
   데이터 주도로 계산해 작업 큐(pipeline-todo.json)로 남긴다.

 입력(모두 이 폴더):
   - fetch_markets.py 의 SERIES  (ast 로 안전 추출 — 네트워크 코드 실행 안 함)
   - econ-calendar.json (+ econ-calendar-store.json 누적본)
   - stocks-info.js / stocks-news.js / earnings-series.js / macro-series.js
     (JS 객체 리터럴 → node eval 로 읽음)
   - 캘린더 ↔ 시리즈 매핑(macroMatchSeries·EARNINGS ticker 로직)을 결정론으로 재현.

 커버리지 갭:
   (a) '주식' 그룹 티커 중 stocks-info / stocks-news 미등록  → stocks_info_todo / stocks_news_todo
   (b) 실적 이벤트 티커 중 earnings-series 미등록            → earnings_todo
   (c) 캘린더 '거시' 이벤트 중 macro-series 미매핑(신규 지표)  → unmapped[]
   (d) 시리즈 최신 회차가 캘린더 최신 발표보다 오래됨        → macro_todo[].missingPeriods / earnings_stale[]

 출력:
   - pipeline-todo.json  (작업 큐)
   - coverage.log        (미커버 항목 append 로그)

 실행:  python3 coverage_check.py
       python3 coverage_check.py --todo pipeline-todo.json --log coverage.log
============================================================
"""
import ast
import json
import re
import subprocess
import sys
from datetime import datetime, timezone, date
from pathlib import Path

HERE = Path(__file__).resolve().parent


# ---------- 입력 로더 ----------
def read_series():
    """fetch_markets.py 의 SERIES 를 ast 로 안전 추출 → [(sym,name,group,unit), ...]."""
    src = (HERE / "fetch_markets.py").read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name) and t.id == "SERIES":
                    return list(ast.literal_eval(node.value))
    return []


def read_js_const(filename, name):
    """JS 데이터 파일의 `const NAME = {...}` 를 node eval 로 읽어 dict 반환(실패 시 {})."""
    p = HERE / filename
    if not p.exists():
        return {}
    node = (
        "var fs=require('fs');var s=fs.readFileSync(process.argv[1],'utf8');"
        "var n=process.argv[2];var m=s.lastIndexOf('const '+n);"      # 주석 언급 뒤의 실제 선언
        "if(m<0){process.stdout.write('{}');process.exit(0);}"
        "var a=s.indexOf('{',m);var b=s.lastIndexOf('}');"
        "var o=eval('('+s.slice(a,b+1)+')');process.stdout.write(JSON.stringify(o));"
    )
    try:
        r = subprocess.run(["node", "-e", node, str(p), name],
                           capture_output=True, text=True, timeout=40)
        if r.returncode != 0:
            sys.stderr.write(f"[coverage] {filename} 읽기 실패: {r.stderr[:300]}\n")
            return {}
        return json.loads(r.stdout or "{}")
    except Exception as e:  # noqa: BLE001
        sys.stderr.write(f"[coverage] {filename} 예외: {e}\n")
        return {}


def load_calendar():
    """store(누적) 우선 + rolling 병합, date+(ticker|title) 로 중복 제거."""
    events = {}
    for f in ("econ-calendar-store.json", "econ-calendar.json"):
        p = HERE / f
        if not p.exists():
            continue
        try:
            j = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if not isinstance(j, list):
            continue
        for e in j:
            if not isinstance(e, dict):
                continue
            key = ((e.get("date") or ""), (e.get("ticker") or e.get("title") or ""))
            old = events.get(key)
            # actual 이 있는 쪽을 우선 보존
            if old is not None and _has(old.get("actual")) and not _has(e.get("actual")):
                continue
            events[key] = e
    return list(events.values())


def _has(v):
    return v is not None and str(v).strip() != ""


# ---------- 매핑(프론트 로직 재현) ----------
def macro_match(ev, macro):
    """macroMatchSeries 재현: country 일치 + 제목에 any 포함 + not 미포함."""
    t = ev.get("title") or ""
    out = []
    for sid, m in macro.items():
        if m.get("country") != ev.get("country"):
            continue
        mt = m.get("match") or {}
        if not any(k in t for k in (mt.get("any") or [])):
            continue
        if any(k in t for k in (mt.get("not") or [])):
            continue
        out.append(sid)
    return out


_MONTH_RE = re.compile(r"(\d{1,2})\s*월")


def period_hint(ev):
    """캘린더 '거시' 이벤트 제목의 'N월' + 발표일 → 참조월 'YYYY-MM'(월간 지표). 없으면 None."""
    t = ev.get("title") or ""
    d = (ev.get("date") or "")[:10]
    mo = _MONTH_RE.search(t)
    if not mo or len(d) < 7:
        return None
    try:
        rel_y, rel_m = int(d[:4]), int(d[5:7])
    except ValueError:
        return None
    M = int(mo.group(1))
    if not (1 <= M <= 12):
        return None
    y = rel_y if M <= rel_m else rel_y - 1   # 발표는 참조월 다음달 → 연도 보정
    return f"{y:04d}-{M:02d}"


_YM_RE = re.compile(r"\((\d{4})-(\d{2})\)")


def period_end_date(period):
    """실적 시리즈 period 문자열 'Q2 2026 (2026-06)' → date(2026,6,1). 없으면 None."""
    m = _YM_RE.search(period or "")
    if not m:
        return None
    try:
        return date(int(m.group(1)), int(m.group(2)), 1)
    except ValueError:
        return None


# ---------- 메인 ----------
def build(today=None):
    today = today or datetime.now(timezone.utc).date()
    series = read_series()
    stocks_info = read_js_const("stocks-info.js", "STOCKS_INFO")
    stocks_news = read_js_const("stocks-news.js", "STOCKS_NEWS")
    earnings = read_js_const("earnings-series.js", "EARNINGS_SERIES")
    macro = read_js_const("macro-series.js", "MACRO_SERIES")
    cal = load_calendar()

    # (a) 주식 그룹 티커 커버리지
    stock_tickers = [(sym, nm, grp) for (sym, nm, grp, unit) in series
                     if str(grp).startswith("주식")]
    stocks_info_todo = [s for (s, n, g) in stock_tickers if s not in stocks_info]
    stocks_news_todo = [s for (s, n, g) in stock_tickers if s not in stocks_news]

    # (b) 실적 이벤트 티커 커버리지
    earn_events = [e for e in cal if e.get("kind") == "실적" and e.get("ticker")]
    earn_tickers = sorted({e["ticker"] for e in earn_events})
    earnings_todo = [t for t in earn_tickers if t not in earnings]

    # (c) 거시 이벤트 매핑 + (d) 시리즈별 누락 회차
    macro_events = [e for e in cal if e.get("kind") == "거시"]
    unmapped = {}
    series_expected = {}   # sid -> set(period)
    for e in macro_events:
        ids = macro_match(e, macro)
        if not ids:
            k = (e.get("country"), e.get("title"))
            unmapped.setdefault(k, {
                "country": e.get("country"),
                "title": e.get("title"),
                "hint": "MACRO_SERIES 미매핑 — 신규 지표면 id·name·country·unit·match 정의 후 delta 반환",
            })
            continue
        ph = period_hint(e)
        if ph:
            for sid in ids:
                series_expected.setdefault(sid, set()).add(ph)

    macro_todo = []
    for sid, periods in series_expected.items():
        have = {r.get("period") for r in (macro.get(sid, {}).get("releases") or [])}
        missing = sorted(p for p in periods if p not in have)
        if missing:
            m = macro[sid]
            macro_todo.append({
                "seriesId": sid, "name": m.get("name"),
                "country": m.get("country"), "unit": m.get("unit"),
                "missingPeriods": missing,
            })
    macro_todo.sort(key=lambda x: x["seriesId"])

    # (d) 실적 신선도: 발표 지난(오늘 이전) 실적이 시리즈 최신 분기보다 120일+ 최신이면 신규분기 의심
    earnings_stale = []
    for tk in earnings:
        ends = [period_end_date(q.get("period")) for q in (earnings[tk].get("quarters") or [])]
        ends = [d for d in ends if d]
        if not ends:
            continue
        latest_end = max(ends)
        released = [(e.get("date") or "")[:10] for e in earn_events
                    if e.get("ticker") == tk and (e.get("date") or "")[:10] <= today.isoformat()]
        released = [d for d in released if len(d) == 10]
        if not released:
            continue
        latest_evt = max(released)
        try:
            evt_d = datetime.strptime(latest_evt, "%Y-%m-%d").date()
        except ValueError:
            continue
        if (evt_d - latest_end).days > 120:
            earnings_stale.append({
                "ticker": tk, "latestSeriesPeriodEnd": latest_end.isoformat(),
                "latestReleasedEvent": latest_evt,
            })

    # 자산·부채 추이(재무상태표) 백필 대상.
    #   ① 데이터가 전혀 없음 → 5년치 최초 백필
    #   ② 있지만 '최신 분기'에 자산/부채가 빔 → 신규 분기만 채움(새 사업보고서 반영)
    #   → 5년치를 매번 다시 조사하지 않고, 새 분기가 나올 때만 그 분기를 채운다.
    _BAL_KEYS = ("totalAssets", "totalAssetsKRW")
    def _q_has_bal(q):
        return any((q.get(k) or {}).get("act") is not None for k in _BAL_KEYS)
    balance_backfill = []
    for tk in earnings:
        qs = earnings[tk].get("quarters") or []
        if not qs:
            continue
        has_any = any(_q_has_bal(q) for q in qs)
        latest_q = max(qs, key=lambda q: (period_end_date(q.get("period")) or date.min))
        if (not has_any) or (not _q_has_bal(latest_q)):
            balance_backfill.append(tk)

    todo = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "stocks_info_todo": sorted(set(stocks_info_todo)),
        "stocks_news_todo": sorted(set(stocks_news_todo)),
        "earnings_todo": sorted(set(earnings_todo)),
        "earnings_stale": earnings_stale,
        "balance_backfill": sorted(set(balance_backfill)),
        "macro_todo": macro_todo,
        "unmapped": list(unmapped.values()),
        "summary": {
            "series_stock_tickers": len(stock_tickers),
            "stocks_info_missing": len(stocks_info_todo),
            "stocks_news_missing": len(stocks_news_todo),
            "earnings_missing": len(earnings_todo),
            "earnings_stale": len(earnings_stale),
            "balance_backfill": len(balance_backfill),
            "macro_series": len(macro),
            "macro_needing_periods": len(macro_todo),
            "macro_unmapped_events": len(unmapped),
        },
    }
    return todo


def write_outputs(todo, todo_path, log_path):
    # 원자적 쓰기(temp → replace)
    tmp = todo_path.with_suffix(todo_path.suffix + ".tmp")
    tmp.write_text(json.dumps(todo, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(todo_path)

    s = todo["summary"]
    lines = [f"===== coverage {todo['generated']} ====="]
    lines.append(
        "  요약: 주식티커 {series_stock_tickers} · info누락 {stocks_info_missing} · "
        "news누락 {stocks_news_missing} · 실적누락 {earnings_missing} · 실적신선도 {earnings_stale} · "
        "거시시리즈 {macro_series} · 회차보충 {macro_needing_periods} · 미매핑 {macro_unmapped_events}".format(**s)
    )
    for t in todo["stocks_info_todo"]:
        lines.append(f"  [stocks_info_todo] {t}")
    for t in todo["stocks_news_todo"]:
        lines.append(f"  [stocks_news_todo] {t}")
    for t in todo["earnings_todo"]:
        lines.append(f"  [earnings_todo] {t}")
    for e in todo["earnings_stale"]:
        lines.append(f"  [earnings_stale] {e['ticker']} (시리즈 {e['latestSeriesPeriodEnd']} < 발표 {e['latestReleasedEvent']})")
    for m in todo["macro_todo"]:
        lines.append(f"  [macro_todo] {m['seriesId']} 누락회차 {','.join(m['missingPeriods'])}")
    for u in todo["unmapped"]:
        lines.append(f"  [unmapped] {u['country']} | {u['title']}")
    with log_path.open("a", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main(argv):
    todo_path = HERE / "pipeline-todo.json"
    log_path = HERE / "coverage.log"
    if "--todo" in argv:
        todo_path = Path(argv[argv.index("--todo") + 1])
    if "--log" in argv:
        log_path = Path(argv[argv.index("--log") + 1])

    todo = build()
    write_outputs(todo, todo_path, log_path)

    s = todo["summary"]
    total_gaps = (s["stocks_info_missing"] + s["stocks_news_missing"] + s["earnings_missing"]
                  + s["earnings_stale"] + s["macro_needing_periods"] + s["macro_unmapped_events"])
    print(f"✔ coverage: 갭 {total_gaps}건 → {todo_path.name} "
          f"(info {s['stocks_info_missing']}·news {s['stocks_news_missing']}·"
          f"실적 {s['earnings_missing']}·거시회차 {s['macro_needing_periods']}·미매핑 {s['macro_unmapped_events']})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
