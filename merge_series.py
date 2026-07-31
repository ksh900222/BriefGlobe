#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
 merge_series.py  ·  AI delta → 시리즈 파일 append-only 병합 (시장 도메인, 결정론)
------------------------------------------------------------
 목적: AI(작업 E-2·G)는 파일을 직접 편집하지 않고 표준 delta JSON 만 낸다.
   이 스크립트가 그 delta 를 macro-series.js / earnings-series.js 에
   안전하게 누적 병합한다(merge_econ.py 의 보존 패턴).

 delta 형식(둘 다 선택):
   {
     "macro":    { "SERIES_ID": { "name","country","unit","match",
                     "releases":[ {"period","cons","act","source"} ] } },
     "earnings": { "TICKER": { "name","metrics":[...],
                     "quarters":[ {"period", "<metric>":{"act","cons"}, "source"} ] } }
   }

 병합 규칙(반드시):
   - append-only: 과거 회차/분기 보존. period 중복은 하나로 합침.
   - non-null 을 null 로 덮지 않음(delta 의 null 은 기존값 유지, non-null 은 갱신=수정 반영).
   - 기존 시리즈의 스키마·match·name·unit·metrics 보존. 신규 시리즈/티커면 생성.
   - 정렬: releases/quarters 는 period 오름차순.

 사용:
   python3 merge_series.py --delta series-delta.json
   python3 merge_series.py --delta d.json --macro-file macro-series.js --earnings-file earnings-series.js
============================================================
"""
import json
import re
import subprocess
import sys
from pathlib import Path


def _period_key(p):
    """정렬용 '시간순' 키 — 모든 period 형식을 YYYY-MM(-DD)로 정규화해 어떤 경우에도 시간순이
    보장되게 한다. period 문자열을 그냥 정렬하면 'Q2'<'Q4' 처럼 분기번호가 연도보다 우선돼
    순서가 뒤죽박죽 됨 → 반드시 이 키로 정렬한다.
      · 'YYYY-MM-DD'(주간 실업수당 등) → 일 단위 그대로   · 'YYYY-MM' → 그대로
      · 'Q2 2026 (2026-06)'·'2026 Q1 (2026-03)' → 괄호 속 YYYY-MM
      · 접미사 없는 'Q2 2026'·'2026 Q2' → 분기말 월로 환산(2026-06)
      · 미상 형식 → 원문 폴백(그래도 안전)."""
    s = str(p or "")
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", s)      # YYYY-MM-DD(일 단위) 우선
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    m = re.search(r"(\d{4})-(\d{2})", s)              # YYYY-MM
    if m:
        return f"{m.group(1)}-{m.group(2)}"
    QM = {"1": "03", "2": "06", "3": "09", "4": "12"}
    m = re.search(r"Q([1-4])\s*(\d{4})", s)           # 'Q2 2026'
    if m:
        return f"{m.group(2)}-{QM[m.group(1)]}"
    m = re.search(r"(\d{4})\s*Q([1-4])", s)           # '2026 Q2' / '2026 Q1'
    if m:
        return f"{m.group(1)}-{QM[m.group(2)]}"
    return s


# 한국 종목 분기 매출(조원) 정상 범위 — Grok(작업 G)이 대형주에서 반기/누적 규모를 잘못 넣는
#   경우가 있어, 최신 분기 매출이 이 범위(±40%)를 벗어나면 스케일 오류로 보고 그 티커를 드롭한다.
KR_EARN_ANCHOR = {   # 실제 2024~2026 분기 매출 반영(메모리 슈퍼사이클로 삼성·하이닉스 상단 높음)
    "005930.KS": (70, 95), "000660.KS": (12, 90), "096770.KS": (18, 26),
    "034730.KS": (28, 40), "373220.KS": (5, 8), "000720.KS": (7, 9),
    "011070.KS": (4, 6), "034020.KS": (4, 5), "035420.KS": (2.5, 3.2),
    "035720.KS": (1.8, 2.4), "003550.KS": (1.8, 2.4),
}


def drop_bad_korean(cur):
    """earnings 시리즈에서 한국 종목의 스케일 오류(반기/누적 등)를 검증해 드롭."""
    dropped = []
    for tk in list(cur):
        if tk not in KR_EARN_ANCHOR:
            continue
        qs = cur[tk].get("quarters") or []
        if not qs:
            continue
        rev = qs[-1].get("revenueKRW") or {}
        v = rev.get("act") if rev.get("act") is not None else rev.get("cons")
        if v is None:
            continue
        lo, hi = KR_EARN_ANCHOR[tk]
        if v < lo * 0.6 or v > hi * 1.4:
            del cur[tk]
            dropped.append((tk, v, lo, hi))
    for tk, v, lo, hi in dropped:
        print(f"  ⚠ 한국 실적 스케일오류 제거: {tk} 최신분기 매출 {v}조 (정상 {lo}~{hi}조) — 반기/누적 의심")
    return dropped

HERE = Path(__file__).resolve().parent
MACRO_FILE = HERE / "macro-series.js"
EARN_FILE = HERE / "earnings-series.js"

MACRO_HEADER = """/* ============================================================
   macro-series.js · 국가 거시지표 컨센서스 vs 실제 추세 (캘린더 '거시' 클릭 모달)
   ------------------------------------------------------------
   구조: MACRO_SERIES = { ID: { name, country, unit, match:{any,not?}, releases:[{period,cons,act,source}] } }
   append-only 누적(merge_series.py). JS 객체 리터럴 — eval 파싱.
   ============================================================ */
"""
EARN_HEADER = """/* ============================================================
   earnings-series.js · 실적 컨센서스 vs 실제 분기 추세 (캘린더 실적 클릭 모달)
   ------------------------------------------------------------
   구조: EARNINGS_SERIES = { TICKER: { name, metrics:[...], quarters:[{period,<metric>:{act,cons},source}] } }
   append-only 누적(merge_series.py). JS 객체 리터럴 — eval 파싱.
   ============================================================ */
"""


def read_js(path, name):
    """(header_text, obj) 반환. 파일 없으면 (None, {})."""
    if not path.exists():
        return None, {}
    s = path.read_text(encoding="utf-8")
    m = s.rfind("const " + name)          # 주석 언급 뒤의 실제 선언
    header = s[:m] if m > 0 else None
    node = (
        "var fs=require('fs');var s=fs.readFileSync(process.argv[1],'utf8');"
        "var n=process.argv[2];var m=s.lastIndexOf('const '+n);"
        "if(m<0){process.stdout.write('{}');process.exit(0);}"
        "var a=s.indexOf('{',m);var b=s.lastIndexOf('}');"
        "var o=eval('('+s.slice(a,b+1)+')');process.stdout.write(JSON.stringify(o));"
    )
    r = subprocess.run(["node", "-e", node, str(path), name],
                       capture_output=True, text=True, timeout=40)
    if r.returncode != 0:
        raise RuntimeError(f"{path.name} 파싱 실패: {r.stderr[:300]}")
    return header, json.loads(r.stdout or "{}")


def write_js(path, name, header, obj):
    body = json.dumps(obj, ensure_ascii=False, indent=2)
    text = (header or "") + f"const {name} = " + body + ";\n"
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def _pick(cur, new):
    """non-null new 우선, new 가 null 이면 기존 유지(non-null 을 null 로 덮지 않음)."""
    return new if new is not None else cur


def _merge_metric_obj(cur, new):
    """{act,cons,...} 필드별 병합."""
    cur = dict(cur or {})
    out = dict(cur)
    for k, v in (new or {}).items():
        out[k] = _pick(cur.get(k), v)
    return out


# ---------- macro ----------
def merge_macro(cur, delta):
    added_series, added_rel, updated_rel = 0, 0, 0
    for sid, dser in (delta or {}).items():
        if sid not in cur:
            # 신규 시리즈 생성(메타 + releases)
            rels = {}
            for r in dser.get("releases", []):
                p = r.get("period")
                if p is None:
                    continue
                if r.get("act") is None and r.get("cons") is None \
                        and r.get("momAct") is None and r.get("momCons") is None:
                    continue
                rels[p] = {"period": p, "cons": r.get("cons"),
                           "act": r.get("act"),
                           "momCons": r.get("momCons"), "momAct": r.get("momAct"),
                           "source": r.get("source")}
            cur[sid] = {
                "name": dser.get("name", sid), "country": dser.get("country"),
                "unit": dser.get("unit"), "match": dser.get("match") or {"any": [], "not": []},
                "releases": [rels[p] for p in sorted(rels, key=_period_key)],
            }
            added_series += 1
            added_rel += len(rels)
            continue
        # 기존 시리즈: 메타 보존, releases 병합
        cser = cur[sid]
        cser.setdefault("releases", [])
        by_p = {r.get("period"): r for r in cser["releases"]}
        for r in dser.get("releases", []):
            p = r.get("period")
            if p is None:
                continue
            if p in by_p:
                tgt = by_p[p]
                before = (tgt.get("cons"), tgt.get("act"), tgt.get("momCons"), tgt.get("momAct"))
                tgt["cons"] = _pick(tgt.get("cons"), r.get("cons"))
                tgt["act"] = _pick(tgt.get("act"), r.get("act"))
                tgt["momCons"] = _pick(tgt.get("momCons"), r.get("momCons"))
                tgt["momAct"] = _pick(tgt.get("momAct"), r.get("momAct"))
                tgt["source"] = _pick(tgt.get("source"), r.get("source"))
                if (tgt.get("cons"), tgt.get("act"), tgt.get("momCons"), tgt.get("momAct")) != before:
                    updated_rel += 1
            else:
                if r.get("act") is None and r.get("cons") is None \
                        and r.get("momAct") is None and r.get("momCons") is None:
                    continue
                by_p[p] = {"period": p, "cons": r.get("cons"),
                           "act": r.get("act"),
                           "momCons": r.get("momCons"), "momAct": r.get("momAct"),
                           "source": r.get("source")}
                added_rel += 1
        cser["releases"] = [by_p[p] for p in sorted(by_p, key=_period_key)]
    return added_series, added_rel, updated_rel


# ---------- earnings ----------
def merge_earnings(cur, delta):
    added_tk, added_q, updated_q = 0, 0, 0
    for tk, dtk in (delta or {}).items():
        if tk not in cur:
            cur[tk] = {
                "name": dtk.get("name", tk),
                "metrics": list(dtk.get("metrics", ["revenue", "eps"])),
                "quarters": [],
            }
            added_tk += 1
        ctk = cur[tk]
        # metrics 합집합(기존 순서 + 신규)
        metrics = list(ctk.get("metrics", []))
        for mkey in dtk.get("metrics", []):
            if mkey not in metrics:
                metrics.append(mkey)
        ctk["metrics"] = metrics
        ctk.setdefault("quarters", [])
        by_p = {q.get("period"): q for q in ctk["quarters"]}
        for q in dtk.get("quarters", []):
            p = q.get("period")
            if p is None:
                continue
            if p in by_p:
                tgt = by_p[p]
                changed = False
                for mkey in metrics:
                    if mkey in q and isinstance(q[mkey], dict):
                        merged = _merge_metric_obj(tgt.get(mkey), q[mkey])
                        if merged != tgt.get(mkey):
                            changed = True
                        tgt[mkey] = merged
                if q.get("source"):
                    tgt["source"] = _pick(tgt.get("source"), q.get("source"))
                if changed:
                    updated_q += 1
            else:
                nq = {"period": p}
                for mkey in metrics:
                    if mkey in q and isinstance(q[mkey], dict):
                        nq[mkey] = dict(q[mkey])
                if q.get("source"):
                    nq["source"] = q.get("source")
                by_p[p] = nq
                added_q += 1
        ctk["quarters"] = [by_p[p] for p in sorted(by_p, key=_period_key)]
    return added_tk, added_q, updated_q


def main(argv):
    delta_path = None
    macro_file, earn_file = MACRO_FILE, EARN_FILE
    if "--delta" in argv:
        delta_path = Path(argv[argv.index("--delta") + 1])
    if "--macro-file" in argv:
        macro_file = Path(argv[argv.index("--macro-file") + 1])
    if "--earnings-file" in argv:
        earn_file = Path(argv[argv.index("--earnings-file") + 1])

    def _resort_earn(cur):
        for tk in cur:
            qs = cur[tk].get("quarters")
            if isinstance(qs, list):
                cur[tk]["quarters"] = sorted(qs, key=lambda q: _period_key(q.get("period")))

    def _resort_macro(cur):
        for sid in cur:
            rs = cur[sid].get("releases")
            if isinstance(rs, list):
                cur[sid]["releases"] = sorted(rs, key=lambda r: _period_key(r.get("period")))

    # --resort: delta 없이 기존 두 파일의 전 시리즈를 시간순으로 재정렬만(과거 오정렬 교정).
    if "--resort" in argv:
        for f, name, rs in ((macro_file, "MACRO_SERIES", _resort_macro),
                             (earn_file, "EARNINGS_SERIES", _resort_earn)):
            if f.exists():
                header, cur = read_js(f, name)
                rs(cur)
                if name == "EARNINGS_SERIES":
                    drop_bad_korean(cur)   # 한국 스케일 오류 자동 차단
                write_js(f, name, header or (MACRO_HEADER if "MACRO" in name else EARN_HEADER), cur)
                print(f"✔ 재정렬: {name} {len(cur)}개 시리즈 → {f.name}")
        return 0

    if not delta_path or not delta_path.exists():
        print(f"  ⚠ delta 파일 없음({delta_path}) — 병합 건너뜀")
        return 0
    try:
        delta = json.loads(delta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"  ⚠ delta JSON 파싱 실패: {e} — 병합 건너뜀")
        return 0
    if not isinstance(delta, dict):
        print("  ⚠ delta 형식 이상(dict 아님) — 병합 건너뜀")
        return 0

    if delta.get("macro"):
        header, cur = read_js(macro_file, "MACRO_SERIES")
        a_s, a_r, u_r = merge_macro(cur, delta["macro"])
        _resort_macro(cur)   # delta 밖 시리즈까지 전체 시간순 재정렬(self-heal)
        write_js(macro_file, "MACRO_SERIES", header or MACRO_HEADER, cur)
        print(f"✔ macro 병합: 시리즈 총 {len(cur)} (신규 {a_s}) · 회차 추가 {a_r}·갱신 {u_r} → {macro_file.name}")

    if delta.get("earnings"):
        header, cur = read_js(earn_file, "EARNINGS_SERIES")
        a_t, a_q, u_q = merge_earnings(cur, delta["earnings"])
        _resort_earn(cur)   # delta 밖 티커까지 전체 시간순 재정렬(self-heal)
        drop_bad_korean(cur)   # 한국 스케일 오류(반기/누적) 자동 차단
        write_js(earn_file, "EARNINGS_SERIES", header or EARN_HEADER, cur)
        print(f"✔ earnings 병합: 티커 총 {len(cur)} (신규 {a_t}) · 분기 추가 {a_q}·갱신 {u_q} → {earn_file.name}")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
