#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
 market_guard.py · 시장(실적·캘린더) 데이터 결정론적 검증기
------------------------------------------------------------
 왜 필요한가: 실적/캘린더는 AI(작업 G·calendar)가 조사해 delta 로 낸다.
 task_*.md 에 규칙을 아무리 적어도 AI 는 회사를 혼동하고(LG이노텍↔LG디스플레이),
 이미 발표된 분기를 미래 날짜에 잡고, 매출보다 큰 순이익을 써넣는다.
 프롬프트는 '권고'일 뿐이므로 여기서 **기계적으로** 거른다.

 검증 5종(전부 merge_econ.py·merge_series.py 가 호출):
   ① 유니버스   — market-data.js 주식 그룹에 없는 티커는 받지 않는다.
   ② 회사명     — 티커의 공식 종목명과 다른 회사를 가리키면 버린다.
   ③ 발표일정   — 이미 끝난 분기를 분기말+MAX_LAG 넘겨 미래에 잡으면 버린다.
   ④ 산술       — 영업이익>매출, |순이익|>매출 등 불가능한 값은 버린다.
   ⑤ 대조검증   — 한국 종목은 공시 원본(kr-earnings-ref.json)과 대조해
                  어긋난 act 를 **공시값으로 교정**한다. (범위 추정이 아니라 원문 대조)

 ⑤ 가 핵심이다. '마진 30% 넘으면 이상' 같은 상식 규칙은 쓰지 않는다 —
 실제로 SK하이닉스 2026Q2 영업이익률은 76%(공시)라 그런 규칙은 정상 데이터를 지운다.

 CLI:
   python3 market_guard.py --audit     # 현재 산출물 전수 점검(수정 없음)
   python3 market_guard.py --fix       # 오염 데이터 정리·교정 후 저장
============================================================
"""
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
MARKET_DATA = HERE / "market-data.js"
CALENDAR = HERE / "econ-calendar.json"
CALENDAR_STORE = HERE / "econ-calendar-store.json"
EARN_FILE = HERE / "earnings-series.js"
KR_REF = HERE / "kr-earnings-ref.json"      # fetch_kr_earnings_ref.py 산출(공시 원본 캐시)

MAX_LAG_DAYS = 60      # 분기말 이후 이 날짜를 넘겨 '예정'으로 잡히면 오배치로 본다
REF_TOL = 0.05         # 공시값과 5% 넘게 벌어지면 교정


# ------------------------------------------------------------
# ① 유니버스 — market-data.js 가 유일한 정답지(종목 추가 시 자동 반영)
# ------------------------------------------------------------
def load_universe():
    """{ticker: 표시명} — '주식 - 미국'·'주식 - 한국' 그룹 전체."""
    if not MARKET_DATA.exists():
        return {}
    s = MARKET_DATA.read_text(encoding="utf-8")
    return dict(re.findall(
        r'\{"id": "([^"]+)", "name": "([^"]+)", "group": "주식 - (?:미국|한국)"', s))


def _ko(name):
    """'삼성전자 (Samsung Elec)' → '삼성전자'"""
    return (name or "").split(" (")[0].strip()


# 유니버스 밖이지만 AI 가 자주 혼동해 끌어오는 회사들 — 이름 충돌 판정에만 쓴다.
#   한국: 계열사끼리(LG·현대·SK) / 미국: 티커 약자가 비슷한 회사(XE=엑스에너지 vs Xerox).
CONFUSABLE = [
    "LG화학", "LG디스플레이", "LG전자", "LG유플러스", "LG생활건강",
    "현대자동차", "현대차", "현대모비스", "현대글로비스", "현대엔지니어링",
    "현대증권", "현대제철", "기아", "카카오뱅크", "카카오페이", "네이버파이낸셜",
    "삼성SDI", "삼성물산", "삼성바이오로직스", "SK스퀘어", "SK텔레콤", "포스코",
    "Xerox", "제록스", "Exelon", "Eni",
]


def _aliases(display):
    """'엑스에너지 (X-Energy)' → {'엑스에너지', 'X-Energy'} — 한글·영문 표기 둘 다."""
    out = set()
    ko = _ko(display)
    if ko:
        out.add(ko)
    m = re.search(r"\(([^)]+)\)", display or "")
    if m:
        out.add(m.group(1).strip())
    return out


def name_conflict(ticker, text, universe=None):
    """text 안에서 가장 구체적으로 언급된 회사가 ticker 의 회사가 아니면 그 이름을 돌려준다.

    가장 긴 이름을 우선 매칭한다 — 'LG화학'이 있는 문장에서 'LG'만 보고
    003550(LG 지주)으로 오인하는 것을 막기 위해서다.
    한글·영문 표기를 모두 본다 — 미국 종목 제목은 영문이라('Xerox 2분기 실적' on XE)
    한글만 대조하면 통과해 버린다.
    """
    universe = universe if universe is not None else load_universe()
    own = _aliases(universe.get(ticker, ""))
    text = text or ""
    names = set(CONFUSABLE)
    for disp in universe.values():
        names |= _aliases(disp)
    hits = sorted((n for n in names if n and n in text), key=len, reverse=True)
    if not hits:
        return None                      # 회사명 언급 없음 → 판단 보류(통과)
    best = hits[0]
    # 정확히 일치할 때만 통과. 부분일치를 허용하면 짧은 이름이 뚫린다 —
    #   003550(LG 지주)의 'LG' 가 'LG화학' 안에 들어 있어 오검증을 통과했었다.
    return None if best in own else best


# ------------------------------------------------------------
# ③ 발표일정 — 분기 종료 후 MAX_LAG_DAYS 안에 발표된다
# ------------------------------------------------------------
_Q_PAT = re.compile(r"(20\d\d)\s*년?\s*[·\s]*([1-4])\s*분기|Q([1-4])\s*(20\d\d)")


def quarter_end(title):
    """제목에서 회계분기를 읽어 그 분기의 마지막 날을 돌려준다(없으면 None)."""
    m = _Q_PAT.search(title or "")
    if not m:
        return None
    if m.group(1):
        year, q = int(m.group(1)), int(m.group(2))
    else:
        year, q = int(m.group(4)), int(m.group(3))
    end_month = q * 3
    nxt = date(year + (end_month == 12), (end_month % 12) + 1, 1)
    return date.fromordinal(nxt.toordinal() - 1)


def schedule_bad(item, today=None, ref=None):
    """이미 끝난 분기를 미래에 '예정'으로 잡았으면 사유 문자열.

    두 가지로 잡는다:
      (a) 분기말 + MAX_LAG_DAYS 초과 — 일반 규칙(미국 종목 포함)
      (b) 그 분기 공시가 **이미 존재** — 한국 종목은 대조표로 정확히 판정한다.
          LG이노텍 2026Q2 는 7월 발표인데 8/23 예정으로 잡혀 있었다(분기말+54일이라
          (a) 만으로는 못 걸렀다). 실제 발표 여부보다 확실한 근거는 공시 그 자체다.
    """
    today = today or date.today()
    try:
        d = datetime.strptime((item.get("date") or "")[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None
    qe = quarter_end(item.get("title"))
    if not qe:
        return None
    if d <= today:
        return None
    lag = (d - qe).days
    if lag > MAX_LAG_DAYS:
        return f"분기말({qe})+{lag}일 미래 배치 — 발표는 분기말 {MAX_LAG_DAYS}일 이내"
    tk = item.get("ticker")
    if ref and tk in ref:
        col = f"{qe.year}{qe.month:02d}"
        if (ref[tk] or {}).get(col):
            return f"{qe.year}Q{(qe.month - 1) // 3 + 1} 공시가 이미 존재 — 미래 '예정'일 수 없음"
    return None


# ------------------------------------------------------------
# ④ 산술 — 조/억 혼용까지 정규화해 불가능한 조합을 잡는다
# ------------------------------------------------------------
_NUM = r"[-+]?[\d,]+(?:\.\d+)?"


def _to_jo(val, unit):
    v = float(str(val).replace(",", ""))
    return v / 10000.0 if unit == "억" else v


def parse_krw(text):
    """'매출 14.17조 · 영업이익 5996억' → {'매출':14.17,'영업이익':0.5996} (조원)."""
    out = {}
    for label in ("매출", "영업이익", "순이익", "당기순이익"):
        # 범위(5.3–5.6조)는 상단값을 취한다 — 과대 판정에 보수적
        m = re.search(rf"{label}\s*~?\s*(?:{_NUM}\s*[–\-~]\s*)?({_NUM})\s*(조|억)", text or "")
        if m:
            out["순이익" if label == "당기순이익" else label] = _to_jo(m.group(1), m.group(2))
    return out


def arithmetic_bad(text):
    """산술적으로 불가능한 조합이면 사유 문자열."""
    v = parse_krw(text)
    rev = v.get("매출")
    if not rev or rev <= 0:
        return None
    op, net = v.get("영업이익"), v.get("순이익")
    if op is not None and op > rev:
        return f"영업이익({op}조) > 매출({rev}조)"
    if net is not None and abs(net) > rev:
        return f"순이익({net}조) > 매출({rev}조)"
    return None


# ------------------------------------------------------------
# ⑤ 대조검증 — 공시 원본(kr-earnings-ref.json)과 맞춰본다
# ------------------------------------------------------------
REF_KEYS = {"revenueKRW": "매출액", "opIncomeKRW": "영업이익", "netIncomeKRW": "당기순이익"}


def load_ref():
    """{ticker: {'YYYYMM': {'매출액':조원, ...}}} — 없으면 {} (검증 건너뜀)."""
    if not KR_REF.exists():
        return {}
    try:
        return json.loads(KR_REF.read_text(encoding="utf-8")).get("data", {})
    except (ValueError, OSError):
        return {}


def period_col(period):
    """'Q2 2026 (2026-06)' → '202606'. 괄호의 기말월이 분기 앵커다."""
    m = re.search(r"\((\d{4})-(\d{2})\)", period or "")
    return (m.group(1) + m.group(2)) if m else None


REF_SOURCE = "DART 전자공시(분기보고서) 대조검증 | https://dart.fss.or.kr/"


def correct_quarter(ticker, q, ref, universe=None):
    """분기 객체의 act 를 공시값과 대조·교정. 교정 내역 리스트를 돌려준다."""
    fixed = []
    col = period_col(q.get("period"))
    table = ref.get(ticker) or {}
    row = table.get(col) if col else None
    if not row:
        return fixed
    for key, label in REF_KEYS.items():
        real = row.get(label)
        if real is None or key not in q or not isinstance(q[key], dict):
            continue
        act = q[key].get("act")
        if act is None:
            continue
        if abs(real) < 0.005:                      # 0 근처는 상대오차가 무의미
            continue
        if abs(act - real) / abs(real) > REF_TOL:
            q[key]["act"] = real
            fixed.append((q.get("period"), key, act, real))
    # cons(컨센서스)는 예측치라 공시로 대체할 수 없다. 다만 **산술적으로 불가능한** 값은
    #   틀렸다고 단정할 수 있으므로 지운다(지어내지 않고 null 로).
    #   예: SK하이닉스 2026Q2 순이익 컨센서스 95조 — 같은 분기 매출(공시 84.17조)보다 크다.
    rev = row.get("매출액")
    if rev and rev > 0:
        for key in ("opIncomeKRW", "netIncomeKRW"):
            cell = q.get(key)
            if not isinstance(cell, dict):
                continue
            cons = cell.get("cons")
            if cons is not None and abs(cons) > rev:
                cell["cons"] = None
                fixed.append((q.get("period"), f"{key}.cons", cons, "null(매출 초과)"))

    # 값을 공시로 교정했거나 출처가 다른 회사를 가리키면 출처도 바로잡는다.
    #   (틀린 값을 지우면서 그 값의 근거였던 오출처를 남겨두면 추적이 안 된다)
    other = name_conflict(ticker, q.get("source"), universe)
    if fixed or other:
        old = q.get("source")
        if old != REF_SOURCE:
            q["source"] = REF_SOURCE
            fixed.append((q.get("period"), "source", (old or "")[:40], "DART 대조"))
    return fixed


# ------------------------------------------------------------
# 캘린더 이벤트 1건 판정
# ------------------------------------------------------------
def duplicate_earnings(items):
    """같은 티커·같은 회계분기가 두 번 이상 잡힌 이벤트 중 버릴 것들의 id 집합.

    AI 가 같은 발표를 날짜·컨센서스만 달리해 중복 생성한다
    (엔비디아 FY2027 2분기가 8/26·8/27 두 줄, 컨센서스도 서로 다름).
    남길 기준: actual 있는 것 > 날짜 빠른 것 (실제 발표가 확정된 쪽을 신뢰).
    """
    groups = {}
    for it in items:
        if not isinstance(it, dict) or it.get("kind") != "실적":
            continue
        qe = quarter_end(it.get("title"))
        tk = it.get("ticker")
        if not qe or not tk:
            continue
        groups.setdefault((tk, qe), []).append(it)
    drop = set()
    for (tk, qe), grp in groups.items():
        if len(grp) < 2:
            continue
        grp.sort(key=lambda x: (0 if _has_actual_str(x.get("actual")) else 1,
                                x.get("date") or ""))
        for extra in grp[1:]:
            drop.add(id(extra))
    return drop


def _has_actual_str(a):
    return a is not None and str(a).strip() != ""


def correct_calendar_actual(it, ref):
    """캘린더 실적 이벤트의 actual 문자열을 공시값과 대조해 교정(교정하면 True).

    이벤트를 통째로 버리면 발표 일정 자체가 사라지므로, 값만 공시로 바로잡는다.
    (SK이노베이션 2026Q2 'actual 영업이익 3.5조' → 공시 1.5582조)
    """
    tk = it.get("ticker")
    row = (ref or {}).get(tk)
    if not row or not it.get("actual"):
        return False
    qe = quarter_end(it.get("title"))
    if not qe:
        return False
    real = row.get(f"{qe.year}{qe.month:02d}")
    if not real:
        return False
    got = parse_krw(it["actual"])
    pairs = (("매출", "매출액"), ("영업이익", "영업이익"), ("순이익", "당기순이익"))
    off = any(
        got.get(k) is not None and real.get(label) is not None
        and abs(real[label]) >= 0.005
        and abs(got[k] - real[label]) / abs(real[label]) > REF_TOL
        for k, label in pairs
    )
    if not off:
        return False
    parts = [f"{k} {real[label]}조" for k, label in pairs if real.get(label) is not None]
    it["actual"] = " · ".join(parts) + " (DART 공시)"
    return True


def check_calendar_item(it, universe=None, today=None, ref=None):
    """실적 이벤트의 결격 사유 목록(빈 목록=통과)."""
    if not isinstance(it, dict) or it.get("kind") != "실적":
        return []
    universe = universe if universe is not None else load_universe()
    ref = ref if ref is not None else load_ref()
    tk = it.get("ticker")
    reasons = []
    if tk and tk not in universe:
        reasons.append(f"유니버스 밖 티커({tk})")
    if tk in universe:
        other = name_conflict(tk, it.get("title"), universe)
        if other:
            reasons.append(f"제목이 다른 회사({other}) — {tk}={_ko(universe[tk])}")
    s = schedule_bad(it, today, ref)
    if s:
        reasons.append(s)
    for field in ("forecast", "actual"):
        a = arithmetic_bad(it.get(field))
        if a:
            reasons.append(f"{field}: {a}")
    return reasons


# ------------------------------------------------------------
# 전수 점검 / 정리 CLI
# ------------------------------------------------------------
def _load_earnings():
    from merge_series import read_js
    return read_js(EARN_FILE, "EARNINGS_SERIES")


def audit(fix=False):
    universe = load_universe()
    ref = load_ref()
    today = date.today()
    print(f"유니버스 {len(universe)}종목 · 공시 대조표 {len(ref)}종목"
          f"{' (없음 — 대조검증 건너뜀)' if not ref else ''}\n")

    # ---- 캘린더 ----
    total_drop = 0
    for path in (CALENDAR, CALENDAR_STORE):
        if not path.exists():
            continue
        items = json.loads(path.read_text(encoding="utf-8"))
        dup = duplicate_earnings(items)
        kept, dropped, retouched = [], [], []
        for it in items:
            r = check_calendar_item(it, universe, today, ref)
            if id(it) in dup:
                r = r + ["같은 티커·분기 중복 이벤트"] if r else ["같은 티커·분기 중복 이벤트"]
            if r:
                dropped.append((it, r))
                continue
            before = it.get("actual")
            if correct_calendar_actual(it, ref):
                retouched.append((it, before))
            kept.append((it, r))
        print(f"### {path.name}: {len(items)}건 중 결격 {len(dropped)}건 · actual 교정 {len(retouched)}건")
        for it, r in dropped:
            print(f"  ✗ {it.get('date')} {it.get('ticker') or '-':<10} {(it.get('title') or '')[:32]:<34} :: {'; '.join(r)}")
        for it, before in retouched:
            print(f"  ✎ {it.get('date')} {it.get('ticker')} actual: {(before or '')[:46]} → {it['actual']}")
        total_drop += len(dropped) + len(retouched)
        if fix and (dropped or retouched):
            path.write_text(json.dumps([i for i, _ in kept], ensure_ascii=False, indent=2) + "\n",
                            encoding="utf-8")
            print(f"  → 제거 {len(dropped)}건·교정 {len(retouched)}건 저장")
        print()

    # ---- 실적 시리즈 ----
    header, cur = _load_earnings()
    drop_tk, corrections, dup = [], [], []
    for tk in list(cur):
        name = cur[tk].get("name", "")
        if tk not in universe:
            drop_tk.append((tk, name, "유니버스 밖"))
            continue
        official = _ko(universe[tk])
        if _ko(name) != official:
            cur[tk]["name"] = universe[tk]          # 이름은 정답지로 교정(데이터는 유지)
            corrections.append((tk, "name", name, universe[tk]))
        # 같은 기말월을 가리키는 중복 period 통합(표기만 다른 것 — 'Q2 2026' vs '2026 Q2').
        #   삭제가 아니라 **병합**한다. 한쪽에만 있는 값이 사라지면 안 되므로,
        #   먼저 나온 엔트리에 뒤 엔트리의 빈칸을 채워 넣는다.
        seen = {}
        uniq = []
        for q in cur[tk].get("quarters", []):
            col = period_col(q.get("period"))
            if col and col in seen:
                base = seen[col]
                for k, v in q.items():
                    if k == "period":
                        continue
                    if isinstance(v, dict) and isinstance(base.get(k), dict):
                        for sub in ("act", "cons"):
                            if base[k].get(sub) is None and v.get(sub) is not None:
                                base[k][sub] = v[sub]
                    elif base.get(k) in (None, ""):
                        base[k] = v
                dup.append((tk, base.get("period"), q.get("period")))
                continue
            if col:
                seen[col] = q
            uniq.append(q)
        cur[tk]["quarters"] = uniq
        for q in uniq:
            for period, key, old, new in correct_quarter(tk, q, ref, universe):
                corrections.append((tk, f"{period} {key}", old, new))

    print(f"### earnings-series.js")
    print(f"  유니버스 밖 티커 {len(drop_tk)}건")
    for tk, name, why in drop_tk:
        print(f"  ✗ {tk:<12} '{name}' — {why}")
    print(f"  중복 분기 통합 {len(dup)}건")
    for tk, keep, merged in dup:
        print(f"  ⇢ {tk:<12} '{merged}' → '{keep}' 로 병합")
    print(f"  공시 대조 교정 {len(corrections)}건")
    for tk, what, old, new in corrections:
        print(f"  ✎ {tk:<12} {what:<26} {old} → {new}")

    if fix:
        from merge_series import write_js
        for tk, _, _ in drop_tk:
            del cur[tk]
        write_js(EARN_FILE, "EARNINGS_SERIES", header, cur)
        print(f"  → 저장 완료 (티커 {len(cur)}종)")

    return total_drop + len(drop_tk) + len(dup) + len(corrections)


def main(argv):
    fix = "--fix" in argv
    n = audit(fix=fix)
    print(f"\n{'교정 완료' if fix else '점검 완료'} — 문제 {n}건"
          f"{'' if fix else ' (--fix 로 정리)'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
