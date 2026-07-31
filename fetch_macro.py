#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_macro.py — 사용자 선택 FRED 매크로 지표(79종) 수집 → macro-data.js

읽기: fred_selection.json (order/names/transforms/group_*), fred_selection_meta.json (units/freq/title)
동작:
  - 각 시리즈를 FRED observations API 로 최근 ~11년 수집(YoY 계산용 1년 버퍼)
  - transforms 에 mom/yoy 있는 지표(물가·소비 18종, 월별)는 MoM·YoY(%) 계산
  - 표시용으로 최근 10년만 남기고, 점이 많으면(일별) 스파크라인용으로 ≤MAXPTS 다운샘플
출력: macro-data.js = window.MACRO_DATA = {updated, years, series:[{id,name,group,groupName,super,
       freq,unit,dates,raw,mom,yoy,last:{date,raw,mom,yoy}}...], groupOrder, groupNames}
키: ~/.fred_api_key (없으면 종료). 무키 폴백 없음(FRED 공식 API).
견고성: 개별 시리즈 실패해도 건너뛰고 계속. 전량 실패 시 기존 파일 유지.
"""
import json, os, sys, time, urllib.request, urllib.error, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SEL  = os.path.join(HERE, "fred_selection.json")
META = os.path.join(HERE, "fred_selection_meta.json")
OUT  = os.path.join(HERE, "macro-data.js")
YEARS = 10           # 표시 기간
BUFFER_YEARS = 11    # 수집 기간(YoY 버퍼 포함)
MAXPTS = 520         # 시리즈당 표시 점 상한(일별 10년≈2500 → 주별 수준으로 다운샘플)
MIN_INTERVAL = 0.6   # FRED 요청 간 최소 간격(초) — 분당 120회 제한 아래(~100/분)로 유지
DIGEST = os.path.join(HERE, "macro-digest.json")
# 일일 브리핑(작업 C) '왜 돈이 움직였나'용 핵심 거시 20종(신호성 높은 것)
DIGEST_IDS = ["CPIAUCSL", "CPILFESL", "PCEPILFE", "GDPNOW", "INDPRO",
              "UNRATE", "ICSA", "SAHMREALTIME", "EFFR", "SOFR",
              "DGS2", "DGS10", "T10Y2Y", "DFII10", "T5YIE",
              "BAMLH0A0HYM2", "STLFSI4", "WALCL", "M2REAL", "WTREGEN"]

_last_req = [0.0]
def fred_get(url, timeout=30, tries=4):
    """모든 FRED 호출 공통: throttle(요청 간격 확보) + 429/일시오류 재시도."""
    for a in range(tries):
        dt = time.monotonic() - _last_req[0]
        if dt < MIN_INTERVAL:
            time.sleep(MIN_INTERVAL - dt)
        _last_req[0] = time.monotonic()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "world-info-macro/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429 and a < tries - 1:
                time.sleep(2.5 * (a + 1)); continue      # 레이트리밋 → 백오프 후 재시도
            raise
        except Exception:
            if a < tries - 1:
                time.sleep(1.2 * (a + 1)); continue
            raise
    raise RuntimeError("fred_get 재시도 소진")


def key():
    p = os.path.expanduser("~/.fred_api_key")
    if not os.path.exists(p):
        print("✖ ~/.fred_api_key 없음 — FRED 키 등록 필요"); sys.exit(1)
    return open(p).read().strip()


def fetch_obs(sid, k, start):
    url = ("https://api.stlouisfed.org/fred/series/observations"
           f"?series_id={sid}&api_key={k}&file_type=json&observation_start={start}")
    d = fred_get(url)
    dates, vals = [], []
    for o in d.get("observations", []):
        v = o.get("value", ".")
        dates.append(o["date"])
        vals.append(None if v in (".", "", None) else float(v))
    return dates, vals


def pct(a, b):
    if a is None or b is None or b == 0:
        return None
    return round((a - b) / abs(b) * 100, 2)


YOY_LAG = {"M": 12, "Q": 4, "W": 52, "D": 252}   # 전년동기 lookback(주기별)

def raw_tag(unit, freq):
    """원본값 자체가 이미 증감률인 지표(예: GDPNow=% Chg. at Annual Rate)에 붙일 마커."""
    u = (unit or "")
    if "Annual Rate" in u and "Chg" in u:
        return {"Q": "QoQ·연율", "M": "MoM·연율"}.get(freq, "연율")
    if "Chg" in u and "Year Ago" in u:
        return "YoY"
    if "Chg" in u:
        return {"Q": "QoQ", "M": "MoM"}.get(freq, "전기比")
    return ""

def transforms_for(unit, freq):
    """지표 성격별 제공 변환. %·비율·표준화지수·이미-성장률 → 원본만.
       레벨/금액/건수/물가지수 → 주기에 따라 MoM(월)·QoQ(분기)·YoY."""
    u = (unit or "").strip()
    if ("%" in u) or (u == "Index") or ("Ratio" in u) or ("Percentage Points" in u):
        return ["raw"]                       # 금리·스프레드·BEI·실업률·스트레스지수·유통속도·GDPNow 등
    if freq == "Q":
        return ["raw", "qoq", "yoy"]
    if freq == "M":
        return ["raw", "mom", "yoy"]
    if freq in ("W", "D"):
        return ["raw", "yoy"]                # 주·일별 금액(연준자산·M2·레포·청구건수 등)
    return ["raw"]


_REL_ID = {}       # series_id -> (release_id, release_name)
_REL_DATES = {}    # release_id -> sorted[str] (과거+미래 발표일)
_REL_SRC = {}      # release_id -> 발표기관명(source)

def release_source(rid, k):
    if rid is None:
        return ""
    if rid in _REL_SRC:
        return _REL_SRC[rid]
    try:
        src = fred_get(f"https://api.stlouisfed.org/fred/release/sources?release_id={rid}&api_key={k}&file_type=json").get("sources", [])
        _REL_SRC[rid] = src[0]["name"] if src else ""
    except Exception:
        _REL_SRC[rid] = ""
    return _REL_SRC[rid]

def release_of(sid, k):
    if sid in _REL_ID:
        return _REL_ID[sid]
    try:
        rel = fred_get(f"https://api.stlouisfed.org/fred/series/release?series_id={sid}&api_key={k}&file_type=json")["releases"][0]
        _REL_ID[sid] = (rel["id"], rel.get("name", ""))
    except Exception:
        _REL_ID[sid] = (None, "")
    return _REL_ID[sid]

def release_dates(rid, k):
    if rid is None:
        return []
    if rid in _REL_DATES:
        return _REL_DATES[rid]
    try:
        u = (f"https://api.stlouisfed.org/fred/release/dates?release_id={rid}&api_key={k}"
             "&file_type=json&sort_order=asc&include_release_dates_with_no_data=true")
        d = fred_get(u)
        _REL_DATES[rid] = sorted(x["date"] for x in d.get("release_dates", []))
    except Exception:
        _REL_DATES[rid] = []
    return _REL_DATES[rid]

def release_info(sid, k, today_iso):
    rid, name = release_of(sid, k)
    dates = release_dates(rid, k)
    nxt = next((d for d in dates if d >= today_iso), None)
    past = [d for d in dates if d < today_iso]
    return {"name": name, "agency": release_source(rid, k),
            "next": nxt, "last": past[-1] if past else None,
            "recent": past[-6:][::-1]}   # 최근 발표일 6개(내림차순)


def downsample(dates, cols, maxpts):
    """dates 와 cols(딕셔너리 name->list)를 같은 인덱스로 ≤maxpts 로 축약. 마지막 점 항상 포함."""
    n = len(dates)
    if n <= maxpts:
        return dates, cols
    step = -(-n // maxpts)                      # ceil
    idx = list(range(0, n, step))
    if idx[-1] != n - 1:
        idx.append(n - 1)
    dd = [dates[i] for i in idx]
    cc = {name: [col[i] for i in idx] for name, col in cols.items()}
    return dd, cc


def last_valid(arr):
    for v in reversed(arr or []):
        if v is not None:
            return v
    return None


def main():
    k = key()
    cfg = json.load(open(SEL, encoding="utf-8"))
    meta = json.load(open(META, encoding="utf-8")) if os.path.exists(META) else {}
    today = datetime.date.today()
    today_iso = today.isoformat()
    start = today.replace(year=today.year - BUFFER_YEARS).isoformat()
    cutoff = today.replace(year=today.year - YEARS).isoformat()
    meanings = cfg.get("meanings", {})
    mm_path = os.path.join(HERE, "fred_market_meaning.json")
    market_meaning = json.load(open(mm_path, encoding="utf-8")) if os.path.exists(mm_path) else {}

    series = []
    ok = fail = 0
    for sid in cfg["order"]:
        try:
            m = meta.get(sid, {})
            unit = m.get("units", ""); freq = m.get("freq", "")
            tfs = transforms_for(unit, freq)
            lag = YOY_LAG.get(freq, 12)
            dates, vals = fetch_obs(sid, k, start)
            if len(vals) < 2:
                raise RuntimeError(f"포인트 부족({len(vals)})")
            mom = [pct(vals[i], vals[i-1]) if i >= 1 else None for i in range(len(vals))] if "mom" in tfs else None
            qoq = [pct(vals[i], vals[i-1]) if i >= 1 else None for i in range(len(vals))] if "qoq" in tfs else None
            yoy = [pct(vals[i], vals[i-lag]) if i >= lag else None for i in range(len(vals))] if "yoy" in tfs else None
            # 표시 10년으로 트림
            keep = [i for i, d in enumerate(dates) if d >= cutoff]
            if not keep:
                keep = list(range(len(dates)))
            s0 = keep[0]
            dates = dates[s0:]; vals = vals[s0:]
            if mom is not None: mom = mom[s0:]
            if qoq is not None: qoq = qoq[s0:]
            if yoy is not None: yoy = yoy[s0:]
            # 모달 '최근 관측 내역'용: 다운샘플 안 한 실제 최근 관측 15개(일별도 진짜 일별 날짜)
            tn = min(15, len(dates))
            tail = [{"d": dates[i], "raw": vals[i],
                     "mom": (mom[i] if mom is not None else None),
                     "qoq": (qoq[i] if qoq is not None else None),
                     "yoy": (yoy[i] if yoy is not None else None)}
                    for i in range(len(dates) - tn, len(dates))][::-1]   # 최신순
            # 다운샘플(일별 등) — 스파크라인용
            cols = {"raw": vals}
            if mom is not None: cols["mom"] = mom
            if qoq is not None: cols["qoq"] = qoq
            if yoy is not None: cols["yoy"] = yoy
            dates, cols = downsample(dates, cols, MAXPTS)
            gid = cfg["group_of"].get(sid)
            rel = release_info(sid, k, today_iso)
            series.append({
                "id": sid,
                "name": cfg["names"].get(sid, sid),
                "group": gid,
                "groupName": cfg["group_names"].get(gid, gid),
                "super": cfg.get("group_super", {}).get(gid, ""),
                "freq": m.get("freq", ""),
                "unit": m.get("units", ""),
                "title": m.get("title", ""),
                "rawTag": raw_tag(unit, freq),
                "meaning": meanings.get(sid, ""),
                "marketMeaning": market_meaning.get(sid, ""),
                "release": rel,
                "tail": tail,
                "tf": tfs,
                "dates": dates,
                "raw": cols["raw"],
                "mom": cols.get("mom"),
                "qoq": cols.get("qoq"),
                "yoy": cols.get("yoy"),
                "last": {"date": dates[-1] if dates else None,
                         "raw": last_valid(cols["raw"]),
                         "mom": last_valid(cols.get("mom")),
                         "qoq": last_valid(cols.get("qoq")),
                         "yoy": last_valid(cols.get("yoy"))},
            })
            ok += 1
            print(f"  ✓ {sid:16} {len(dates):4}pt  ({m.get('freq','?')})  최신 {dates[-1] if dates else '?'}")
        except Exception as e:
            fail += 1
            print(f"  ⚠ {sid:16} 실패: {e}")
        # 요청 간격은 fred_get 이 전역 throttle 로 관리(레이트리밋 방지)

    if ok == 0:
        print("✖ 전량 실패 — 기존 macro-data.js 유지"); sys.exit(1)

    payload = {
        "updated": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "years": YEARS,
        "groupOrder": cfg["group_order"],
        "groupNames": cfg["group_names"],
        "series": series,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("/* 자동 생성 · FRED 매크로 지표 · fetch_macro.py */\n")
        f.write("window.MACRO_DATA = ")
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
    sz = os.path.getsize(OUT) / 1024
    print(f"\n✔ macro-data.js 생성: {ok}개 시리즈(실패 {fail}) · {sz:.0f} KB")

    # ── 일일 브리핑(작업 C)용 거시 다이제스트 — 핵심 20종만 압축 ──
    by_id = {s["id"]: s for s in series}
    dig = []
    for sid in DIGEST_IDS:
        s = by_id.get(sid)
        if not s:
            continue
        L = s["last"]
        dig.append({
            "name": s["name"], "group": s["groupName"], "date": L["date"],
            "value": L["raw"], "unit": s["unit"], "tag": s.get("rawTag", ""),
            "mom": L.get("mom"), "qoq": L.get("qoq"), "yoy": L.get("yoy"),
            "nextRelease": (s.get("release") or {}).get("next"),
        })
    digest = {
        "updated": payload["updated"],
        "note": "미국 거시 배경(FRED). 지표별 기준일(date) 상이(발표지연). value=원본, mom/qoq/yoy=%변화, tag=원본이 이미 증감률인 경우.",
        "indicators": dig,
    }
    with open(DIGEST, "w", encoding="utf-8") as f:
        json.dump(digest, f, ensure_ascii=False, indent=1)
    print(f"✔ macro-digest.json 생성: {len(dig)}개 핵심 지표 (일일 브리핑용)")


if __name__ == "__main__":
    main()
