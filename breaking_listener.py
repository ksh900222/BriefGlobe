#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
breaking_listener.py — ⚡속보 트랙 ③: 텔레그램 공개채널 상시 리스너.

구조 (SBH 분석에서 확정한 설계):
  텔레그램 메시지 도착(push, 초 단위)
    → 20초 배치로 모아 AI 1콜(평시 Claude haiku → 한도면 Grok): 한국어 요약·좌표·카테고리
      + 최근 6h 사건과 뼈대(무엇·어디·언제) 대조 → 신규/병합 판정
    → POST /api/breaking (Bearer ~/.breaking_token)  → 프론트 60초 폴링
    → 전체 이력은 breaking-store.json 로컬 누적(채널 성적표·승격매칭 ④용)

실행 모드:
  --login     최초 1회 대화식 로그인(인증코드 입력) 후 종료
  --check     채널 username 실존 확인만 하고 종료
  --selftest  텔레그램 없이 가짜 메시지 1건을 Haiku 처리 파이프라인에 통과(POST 안 함)
  (무인자)    상시 리스너 — launchd(com.worldinfo.breaking)가 돌림

주의: 포워드 메시지는 원출처 채널을 소스로 계산(같은 글 퍼나르기를 교차확인으로 오인 방지).
"""
import asyncio, json, os, re, subprocess, sys, uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from urllib import request as urlreq

HERE = Path(__file__).resolve().parent
STORE = HERE / "breaking-store.json"
CHANNELS_FILE = HERE / "breaking_channels.json"
LOG = HERE / "breaking.log"
SESSION = str(Path.home() / ".telegram_worldinfo")
API_URL = "https://world-info.pages.dev/api/breaking"
CLAUDE = "/opt/homebrew/bin/claude"
GROK = str(Path.home() / ".grok/bin/grok")
# 속보 심사 = LIGHT 티어 (번역 B 와 동일). auto_update.sh 의 GROK_MODEL_LIGHT 와 맞춤.
# CLI에 모델이 없으면 HEAVY(grok-4.5)로 1회 재시도.
# (2026-07: xAI가 grok-4-fast 제거 — 현재 계정 유효 모델은 grok-4.5 뿐. `grok models`로 확인.)
GROK_MODEL_LIGHT = os.environ.get("GROK_MODEL_LIGHT", "grok-4.5")
GROK_MODEL_HEAVY = os.environ.get("GROK_MODEL_HEAVY", "grok-4.5")
# auto_update.sh run_ai 와 공유 — Claude 한도면 속보 심사는 Grok 전용
CLAUDE_DOWN = HERE / ".claude_down"
CLAUDE_DOWN_MIN = 360   # 6시간(분)
BATCH_SEC = 20          # 메시지 모아서 처리(CLI 호출 절약)
BATCH_MAX = 20          # AI 1콜당 최대 메시지 — 청크가 크면 심사 프롬프트가 커져 180s 타임아웃(특히 메인
                        #   파이프라인 claude 와 동시 실행 시). 20건이면 타임아웃 내 안정 처리, 대형 백로그도 소화.
REQUEUE_MAX = 500       # 심사 실패 시 큐 복원 상한(장시간 장애 대비 — 초과 시 가장 오래된 것부터 폐기)
PENDING_FILE = HERE / ".breaking_pending.json"   # 심사 실패 백로그 디스크 저장(프로세스 크래시·재부팅에도 유실 방지)
POLL_SEC = 60           # 폴링 안전망 주기(푸시 누락 대비 주 수신 경로)
RSS_SEC = 90            # 국내언론 RSS 폴링 주기(정식 보도 트랙, srcType=press)
RSS_SEEN = HERE / "breaking-rss-seen.json"
# RSS 노이즈 선차단 — Haiku까지 보낼 필요 없는 정형 잡물(시세표·포토·인사·부고 등).
#   [속보]·[1보]·[긴급]·[단독]은 매치 안 되므로 안전. 텔레그램에는 미적용(RSS 전용).
RSS_BLOCK = re.compile(r"^\s*\[(표|사진|포토|그래픽|게시판|인사|부음|부고|동정|날씨|오늘의|북한날씨)")
RECENT_HOURS = 6        # 뼈대 대조 창
MIN_TEXT = 15           # 너무 짧은 메시지(이모지·링크만) 제외

def log(msg):
    # launchd가 stdout을 breaking.log로 리다이렉트하므로 print만으로 충분(이중기록 방지)
    print(f"{datetime.now().strftime('%m-%d %H:%M:%S')} {msg}", flush=True)

def load_env(path):
    d = {}
    for ln in Path(path).read_text().splitlines():
        if "=" in ln:
            k, v = ln.split("=", 1)
            d[k.strip()] = v.strip()
    return d

def load_store():
    try:
        return json.loads(STORE.read_text())
    except Exception:
        return []

ARCHIVE = HERE / "breaking-archive.json"
STORE_MAX = 3000   # 활성 스토어 상한 — 초과분은 삭제가 아니라 아카이브로 이동(영구 보관)

def save_store(items):
    if len(items) > STORE_MAX:
        old, items = items[:-STORE_MAX], items[-STORE_MAX:]
        try:
            arch = json.loads(ARCHIVE.read_text()) if ARCHIVE.exists() else []
        except Exception:
            arch = []
        arch.extend(old)
        ARCHIVE.write_text(json.dumps(arch, ensure_ascii=False, indent=1))
    STORE.write_text(json.dumps(items, ensure_ascii=False, indent=1))

def recent_events(items):
    cut = datetime.now(timezone.utc) - timedelta(hours=RECENT_HOURS)
    out = []
    for it in items:
        try:
            if datetime.fromisoformat(it["ts"].replace("Z", "+00:00")) > cut:
                out.append({"id": it["id"], "title": it["title"], "lat": it.get("lat"),
                            "lng": it.get("lng"), "category": it.get("category"), "ts": it["ts"]})
        except Exception:
            pass
    return out[:40]

PROMPT = """너는 국제 속보 데스크다. 아래 메시지들을 심사해 JSON만 출력해라(설명 금지).

각 메시지에 대해:
1. 뉴스 가치 없으면 버려라: 광고, 채널 홍보, 후원 요청, 잡담, 밈, 링크만 있는 글, 기존 사건의 단순 반복 논평,
   연예·스포츠 결과·인물 동정 등 연성 뉴스.
   ⚠ 경제 뉴스 판별에 주의: "지수 마감 요약·개별 가격 나열"(예: S&P 0.3% 상승 마감)만 버리고,
   **경제지표 발표(CPI·고용 등), 중앙은행 결정·발언, 기업 실적·M&A·대형 계약, 관세·무역 조치,
   에너지·원자재 가격 급변동은 중요한 경제 뉴스이므로 반드시 통과(category=경제)**시켜라.
   ⚠ 한반도·동아시아 지정학도 주의: 북한·중국·일본·대만 관련 **당국의 공식 입장·정책 발표,
   비핵화/핵·미사일 동향, 군사 활동, 남북·북중러 관계, 정부 대북·대중 정책 발표는 반드시 통과**
   (이 서비스의 핵심 도메인). 다만 "[북한단신]·[북한날씨]"류 정형 단신, 내부 기념행사·현장시찰·
   화환/추모 등 의례성 보도, 인물 동정은 버려라.
2. 가치 있으면 recent(최근 사건 목록)와 대조 — 같은 사건(유형 동일 + 위치 ~50km + 시간대 겹침)이면 merge, 아니면 new.
3. new 항목: 한국어 제목(간결한 사실 서술)과 2문장 요약을 써라.
   - srcType이 "social"(텔레그램 등 미확인 소셜)이면 "~로 전해졌다", "확인되지 않았다" 같은 유보 표현 필수.
   - srcType이 "press"(정식 언론 보도)면 유보 표현 없이 보도 내용을 사실 서술로.
   위치(lat/lng)와 도시·국가명(한국어): 사건 발생 도시가 있으면 그 도시 좌표.
   특정 도시가 없어도 사건의 주 무대가 되는 '국가'가 있으면 그 나라 수도 좌표를 넣어라
   (예: "일본-필리핀 협정 발효" → 도쿄 or 마닐라 중 중심 주체). 어느 나라와도 연결되지
   않는 뉴스(글로벌 시장 헤드라인·국제기구 일반 발표 등)만 null.
   category는 분쟁|정치|경제|사회|기술|문화 중 하나.
   importance(0~10): 9~10=개전·정상급변·금리서프라이즈급 / 7~8=분쟁 전환점·주요국 정책·대기업 쇼크 /
   5~6=통상적 중요 뉴스 / 3~4=국지·후속 / 0~2=연성. 망설여지면 낮게.

출력 형식(JSON만):
{"results":[
  {"action":"new","msgIdx":0,"item":{"title":"...","summary":"...","lat":28.9,"lng":50.8,"city":"부셰르","country":"이란","category":"분쟁","importance":7}},
  {"action":"merge","msgIdx":1,"matchId":"기존id"},
  {"action":"drop","msgIdx":2}
]}

recent(최근 사건): __RECENT__
messages(새 메시지): __MSGS__"""

def _claude_limited_text(text: str) -> bool:
    return bool(re.search(
        r"rate.?limit|usage.?limit|limit.?reached|too many requests|overloaded|"
        r"exceeded.?your|quota|weekly.?limit|session.?limit|out of extra usage|"
        r"try again later|You've hit your",
        text or "", re.I))

def _marker_active(path: Path, mins: int) -> bool:
    if not path.exists():
        return False
    age_min = (datetime.now().timestamp() - path.stat().st_mtime) / 60.0
    return age_min < mins

def _parse_json_obj(out: str):
    m = re.search(r"\{.*\}", out or "", re.S)   # 앞뒤 잡담 방어 — 첫 {부터 끝 }까지
    if not m:
        raise ValueError(f"JSON 없음: {(out or '')[:200]}")
    return json.loads(m.group(0))

def _call_claude_haiku(prompt: str) -> str:
    if not Path(CLAUDE).exists():
        raise FileNotFoundError(f"Claude 없음: {CLAUDE}")
    r = subprocess.run(
        [CLAUDE, "--dangerously-skip-permissions", "--model", "haiku", "--effort", "low", "-p", prompt],
        capture_output=True, text=True, timeout=180)
    out = (r.stdout or "") + ("\n" + r.stderr if r.stderr else "")
    if r.returncode != 0 and not out.strip():
        raise RuntimeError(f"Claude rc={r.returncode}, 출력 없음")
    return out

def _call_grok(prompt: str) -> str:
    if not Path(GROK).exists():
        raise FileNotFoundError(f"Grok 없음: {GROK}")
    # 속보 심사는 JSON만 — turns 적게. LIGHT 모델 우선(번역 B 와 동일 티어).
    full = (
        "프로젝트 파일은 수정하지 마라. 도구 호출 없이 아래 지시의 JSON만 출력해라.\n\n"
        + prompt
    )
    models = [GROK_MODEL_LIGHT]
    if GROK_MODEL_HEAVY not in models:
        models.append(GROK_MODEL_HEAVY)
    last_err = ""
    for i, model in enumerate(models):
        log(f"  · Grok 심사 model={model}")
        r = subprocess.run(
            [GROK, "--cwd", str(HERE), "--always-approve", "--max-turns", "3",
             "--disable-web-search", "-m", model, "-p", full],
            capture_output=True, text=True, timeout=240)
        out = (r.stdout or "") + ("\n" + r.stderr if r.stderr else "")
        if re.search(r"unknown model id|Couldn't set model|Invalid params", out or "", re.I):
            last_err = f"모델 미지원({model}): {(out or '')[:120]}"
            if i + 1 < len(models):
                log(f"  ⚠ {last_err} → {models[i+1]} 재시도")
                continue
            raise RuntimeError(last_err)
        if r.returncode != 0 and not re.search(r"\{", out or ""):
            last_err = f"Grok rc={r.returncode} model={model}: {(out or '')[:200]}"
            if i + 1 < len(models):
                log(f"  ⚠ {last_err} → {models[i+1]} 재시도")
                continue
            raise RuntimeError(last_err)
        return out
    raise RuntimeError(last_err or "Grok 호출 실패")

def call_haiku(recent, msgs):
    """속보 심사 AI 호출. 평시 Claude haiku, 한도/실패 시 Grok 폴백.
    (함수명 call_haiku 유지 — 호출부 호환. 실제로는 양방향.)"""
    prompt = PROMPT.replace("__RECENT__", json.dumps(recent, ensure_ascii=False)) \
                   .replace("__MSGS__", json.dumps(
                       [{"idx": i, "channel": m["channel"], "srcType": m.get("srcType", "social"),
                         "text": m["text"][:600], "ts": m["ts"]}
                        for i, m in enumerate(msgs)], ensure_ascii=False))

    prefer_grok = _marker_active(CLAUDE_DOWN, CLAUDE_DOWN_MIN)
    errors = []

    if not prefer_grok:
        try:
            out = _call_claude_haiku(prompt)
            if _claude_limited_text(out):
                CLAUDE_DOWN.touch()
                log("  · Claude 한도 감지 → .claude_down, Grok 폴백")
                errors.append(f"Claude 한도: {out[:120]}")
            else:
                data = _parse_json_obj(out)
                try:
                    CLAUDE_DOWN.unlink(missing_ok=True)
                except Exception:
                    pass
                return data
        except Exception as ex:
            errors.append(f"Claude: {ex}")
            # 바이너리 없음·한도 유사 문구면 마커
            if "limit" in str(ex).lower() or "No such file" in str(ex):
                pass

    try:
        if prefer_grok:
            log("  · Claude 한도 마커 → Grok 심사")
        else:
            log("  · Claude 실패 → Grok 심사 폴백")
        out = _call_grok(prompt)
        return _parse_json_obj(out)
    except Exception as ex:
        errors.append(f"Grok: {ex}")
        raise ValueError(" | ".join(errors)) from ex

def post_items(items):
    token = load_env(Path.home() / ".breaking_token").get("BREAKING_TOKEN", "")
    req = urlreq.Request(API_URL, data=json.dumps(items, ensure_ascii=False).encode(),
                         headers={"content-type": "application/json",
                                  "authorization": f"Bearer {token}",
                                  # CF가 Python-urllib UA를 봇 차단(403) — 식별 가능한 UA 명시
                                  "user-agent": "worldinfo-breaking-listener/1.0"}, method="POST")
    with urlreq.urlopen(req, timeout=15) as r:
        return json.loads(r.read())

_pending_post = []   # POST 실패분 — 다음 틱 재시도(유실 방지)

def load_pending_queue():
    """디스크에 저장된 심사 실패 백로그를 읽어온다(재기동 시 이어서 처리)."""
    try:
        if PENDING_FILE.exists():
            data = json.loads(PENDING_FILE.read_text())
            if isinstance(data, list):
                return data
    except Exception as ex:
        log(f"⚠ pending 백로그 로드 실패(무시): {str(ex)[:80]}")
    return []

def save_pending_queue(items):
    """심사 실패 백로그를 디스크에 동기화. 비면 파일 제거(정상 상태엔 파일 없음)."""
    try:
        if items:
            tmp = PENDING_FILE.with_suffix(".tmp")   # 원자적 쓰기(쓰다 크래시해도 원본 안 깨짐)
            tmp.write_text(json.dumps(items, ensure_ascii=False))
            tmp.replace(PENDING_FILE)
        else:
            PENDING_FILE.unlink(missing_ok=True)
    except Exception as ex:
        log(f"⚠ pending 백로그 저장 실패(무시): {str(ex)[:80]}")

def flush_posts(new_items=None):
    """새 항목 + 이전 실패분을 함께 POST. 실패하면 보관했다가 다음에 재시도."""
    global _pending_post
    batch = _pending_post + (new_items or [])
    if not batch:
        return
    try:
        post_items(batch)
        if _pending_post:
            log(f"  ↻ 밀린 {len(_pending_post)}건 포함 {len(batch)}건 POST 완료")
        _pending_post = []
    except Exception as ex:
        _pending_post = batch[-100:]
        log(f"⚠ POST 실패({len(batch)}건 보관, 다음 틱 재시도): {str(ex)[:80]}")

def process_batch(msgs, do_post=True):
    """메시지 배치 → Haiku 심사 → 스토어 갱신 + POST. 반환: 반영된 항목들."""
    store = load_store()
    res = call_haiku(recent_events(store), msgs)
    by_id = {it["id"]: it for it in store}
    changed = []
    for r in res.get("results", []):
        try:
            m = msgs[r["msgIdx"]]
        except Exception:
            continue
        if r.get("action") == "new" and r.get("item", {}).get("title"):
            it = r["item"]
            it.update({"id": uuid.uuid4().hex[:10], "ts": m["ts"], "channel": m["channel"],
                       "url": m.get("url", ""), "status": "breaking", "srcCount": 1,
                       "srcType": m.get("srcType", "social"),   # press=정식보도(프론트 배지 구분)
                       "srcChannels": [m["origin"]], "urgency": "breaking"})
            by_id[it["id"]] = it
            changed.append(it)
            log(f"  ⚡ 신규: [{it.get('category')}] {it['title'][:60]} ({m['channel']})")
        elif r.get("action") == "merge" and r.get("matchId") in by_id:
            it = by_id[r["matchId"]]
            srcs = it.setdefault("srcChannels", [])
            if m["origin"] not in srcs:          # 같은 원출처 재보도는 교차확인 아님
                srcs.append(m["origin"])
                it["srcCount"] = len(srcs)
                changed.append(it)
                log(f"  🔗 교차확인 {it['srcCount']}개: {it['title'][:50]} (+{m['channel']})")
    if changed:
        save_store(list(by_id.values()))   # 상한 초과분은 save_store가 아카이브로 이동
    if do_post:
        flush_posts(changed)   # 실패해도 예외 안 던짐(보관 후 재시도) — 배치 유실 방지
    return changed

# ─── 텔레그램 ───
def make_client():
    cfg = load_env(Path.home() / ".telegram_api")
    from telethon import TelegramClient
    return TelegramClient(SESSION, int(cfg["API_ID"]), cfg["API_HASH"])

async def run_listener():
    from telethon import events
    client = make_client()
    await client.connect()
    if not await client.is_user_authorized():
        log("✖ 미인증 — 먼저 수동으로 실행: python3 breaking_listener.py --login")
        sys.exit(1)
    from telethon.tl.functions.channels import JoinChannelRequest
    chans = json.loads(CHANNELS_FILE.read_text())["channels"]
    entities, names, unames = [], {}, {}
    for c in chans:
        try:
            e = await client.get_entity(c["username"])
            # 핵심: 공개채널도 실시간 업데이트는 '가입된 채널'만 옴 — join 필수(이미 가입돼 있으면 무해)
            try:
                await client(JoinChannelRequest(e))
            except Exception as jex:
                log(f"  (join 생략: @{c['username']} — {str(jex)[:60]})")
            entities.append(e)
            names[e.id] = c["name"]
            unames[e.id] = c["username"]
            log(f"✓ 구독: {c['name']} (@{c['username']})")
            await asyncio.sleep(2)   # 연속 join 플러드 방지
        except Exception as ex:
            log(f"⚠ 채널 못 찾음: @{c['username']} — {ex}")
    if not entities:
        log("✖ 구독 가능한 채널 0개 — breaking_channels.json 확인")
        sys.exit(1)

    queue, seen = [], set()   # seen=(채널id,msg id) — 푸시·폴링 중복 방지
    _restored = load_pending_queue()   # 지난 세션에서 심사 못한 백로그 이어받기(크래시·재부팅 유실 방지)
    if _restored:
        queue.extend(_restored)
        log(f"↩ 이전 미처리 백로그 {len(_restored)}건 복원 — 이어서 심사")

    def enqueue(eid, msg):
        if (eid, msg.id) in seen:
            return
        seen.add((eid, msg.id))
        text = (msg.message or "").strip()
        if len(text) < MIN_TEXT:
            return
        fwd = msg.fwd_from
        # 포워드면 원출처 채널 id를 소스로(퍼나르기를 교차확인으로 오인 방지)
        origin = str(getattr(getattr(fwd, "from_id", None), "channel_id", "") or eid)
        uname = unames.get(eid, "")
        queue.append({
            "channel": names.get(eid, str(eid)),
            "origin": origin,
            "text": text,
            "url": f"https://t.me/{uname}/{msg.id}" if uname else "",
            "ts": msg.date.strftime("%Y-%m-%dT%H:%M:%SZ"),
        })

    @client.on(events.NewMessage(chats=entities))
    async def handler(ev):
        eid = getattr(ev.chat, "id", None) or abs(ev.chat_id) % 10**10   # -100 프리픽스 제거
        enqueue(eid, ev.message)

    # 폴링 안전망 — 푸시 업데이트가 누락돼도 60초마다 각 채널 새 메시지를 직접 수거.
    #   (실측: join 후에도 푸시가 안 오는 경우가 있어 폴링이 사실상 주 경로. 푸시는 보너스)
    last_ids = {}
    for e in entities:   # 첫 폴링에서 과거분 쏟아지지 않게 현재 최신 id로 초기화
        try:
            m = await client.get_messages(e, limit=1)
            last_ids[e.id] = m[0].id if m else 0
        except Exception:
            last_ids[e.id] = 0

    async def poll_loop():
        while True:
            await asyncio.sleep(POLL_SEC)
            for e in entities:
                try:
                    msgs = await client.get_messages(e, min_id=last_ids.get(e.id, 0), limit=15)
                    for m in reversed(msgs):   # 오래된 것부터
                        enqueue(e.id, m)
                        last_ids[e.id] = max(last_ids.get(e.id, 0), m.id)
                except Exception as ex:
                    log(f"⚠ 폴링 실패 @{unames.get(e.id,'?')}: {str(ex)[:60]}")

    # ── 국내언론 RSS 트랙(정식 보도, srcType=press) — 텔레그램과 같은 큐로 합류 ──
    feeds = json.loads(CHANNELS_FILE.read_text()).get("rss", [])

    async def rss_loop():
        import xml.etree.ElementTree as ET
        from email.utils import parsedate_to_datetime
        try:
            rss_seen = set(json.loads(RSS_SEEN.read_text()))
        except Exception:
            rss_seen = set()
        first = not bool(rss_seen)   # 최초 가동 시에만 백로그 스킵(재시작 시엔 seen 파일이 이어받음)
        while True:
            for f in feeds:
                try:
                    req = urlreq.Request(f["url"], headers={"user-agent": "Mozilla/5.0 (worldinfo-rss)"})
                    raw = await asyncio.to_thread(lambda: urlreq.urlopen(req, timeout=12).read())
                    for item in ET.fromstring(raw).iter("item"):
                        link = (item.findtext("link") or "").strip()
                        title = re.sub(r"<[^>]+>", "", item.findtext("title") or "").strip()
                        if not link or link in rss_seen or len(title) < MIN_TEXT:
                            continue
                        rss_seen.add(link)
                        if RSS_BLOCK.match(title):
                            continue   # 정형 잡물 — Haiku 호출 없이 즉시 폐기(seen에는 기록)
                        if first:
                            continue   # 기존 기사 백로그는 '본 것'만 기록하고 표시 안 함
                        desc = re.sub(r"<[^>]+>", "", item.findtext("description") or "").strip()[:300]
                        try:
                            ts = parsedate_to_datetime(item.findtext("pubDate")).astimezone(timezone.utc)
                        except Exception:
                            ts = datetime.now(timezone.utc)
                        queue.append({"channel": f["name"], "origin": "rss:" + f["id"],
                                      "srcType": "press",
                                      "text": title + (" — " + desc if desc else ""),
                                      "url": link,
                                      "ts": ts.strftime("%Y-%m-%dT%H:%M:%SZ")})
                except Exception as ex:
                    log(f"⚠ RSS 실패 {f['id']}: {str(ex)[:60]}")
            first = False
            try:
                # 상한 8000 — 피드 6개 체제에서 2000은 며칠이면 넘쳐 옛 링크가 밀려나고
                #   재수집→Haiku 재심사(호출 낭비)가 생긴다. 여유 있게.
                RSS_SEEN.write_text(json.dumps(sorted(rss_seen)[-8000:]))
            except Exception:
                pass
            await asyncio.sleep(RSS_SEC)

    asyncio.ensure_future(poll_loop())
    if feeds:
        asyncio.ensure_future(rss_loop())
    log(f"⚡ 리스너 가동 — TG {len(entities)}개 + RSS {len(feeds)}개, 폴링 {POLL_SEC}s/{RSS_SEC}s, 배치 {BATCH_SEC}s")
    while True:
        await asyncio.sleep(BATCH_SEC)
        if not queue:
            flush_posts()   # 새 메시지 없어도 밀린 POST는 재시도
            continue
        # 최신부터 처리(newest-first) — '실시간 속보'라 최근 메시지가 우선. 틱당 최대 BATCH_MAX 건.
        #   대형 백로그(장애 복구) 시 낡은 앞부분은 REQUEUE_MAX 상한으로 자연 폐기되고, 신선한 속보가
        #   먼저 반영돼 실시간성이 유지된다. (평시엔 큐가 작아 순서 무관하게 전량 처리)
        batch = queue[-BATCH_MAX:]
        del queue[-len(batch):]
        if len(seen) > 5000:   # seen 무한 증식 방지
            seen.clear()
        try:
            n = process_batch(batch)
            log(f"배치 {len(batch)}건 → 반영 {len(n)}건")
        except Exception as ex:
            # 심사(AI)/네트워크 실패 시 배치를 버리지 않고 큐로 복원 → 다음 틱 재시도(유실 방지).
            # newest-first 와 일관: 실패한 batch(방금 처리하려던 최신분)를 뒤(최신 위치)로 되돌려
            # 다음 틱에 우선 재시도. 상한 초과 시 앞(가장 오래된)부터 폐기해 최신 속보를 보존.
            merged = queue + batch
            queue[:] = merged[-REQUEUE_MAX:]
            dropped = len(merged) - len(queue)
            msg = f"⚠ 배치 심사 실패({len(batch)}건) — 큐 복원({len(queue)}건) 후 재시도: {str(ex)[:80]}"
            if dropped:
                msg += f" · 상한초과 최고령 {dropped}건 폐기"
            log(msg)
        # 큐 상한 — 성공 경로에서도 신규 유입이 처리 속도를 앞지르면 백로그가 무한 증식하므로
        #   REQUEUE_MAX 로 묶는다(newest-first 라 앞쪽=최고령부터 폐기 → 최신 속보 우선 보존).
        if len(queue) > REQUEUE_MAX:
            _drop = len(queue) - REQUEUE_MAX
            del queue[:_drop]
            log(f"⚠ 큐 상한({REQUEUE_MAX}) 초과 — 최고령 {_drop}건 폐기(백로그 {len(queue)})")
        # 백로그를 디스크에 동기화: 성공 시 queue 비어 파일 제거, 실패 시 백로그 저장.
        # (정상 상태에선 queue 비고 파일도 없어 no-op — 불필요한 쓰기 없음)
        if queue or PENDING_FILE.exists():
            save_pending_queue(queue)

async def do_login():
    client = make_client()
    await client.start()          # 대화식: 전화번호+인증코드 입력
    me = await client.get_me()
    log(f"✓ 로그인 완료: {me.first_name} — 세션 저장됨({SESSION}.session)")
    await client.disconnect()

async def do_check():
    client = make_client()
    await client.connect()
    if not await client.is_user_authorized():
        print("✖ 미인증 — 먼저: python3 breaking_listener.py --login")
        return
    for c in json.loads(CHANNELS_FILE.read_text())["channels"]:
        try:
            e = await client.get_entity(c["username"])
            cnt = getattr(e, "participants_count", "?")
            print(f"  ✓ @{c['username']:16s} {c['name']} (구독자 {cnt})")
        except Exception as ex:
            print(f"  ✖ @{c['username']:16s} 못 찾음 — {str(ex)[:60]}")
    await client.disconnect()

def do_selftest():
    fake = [{"channel": "SelfTest", "origin": "selftest",
             "text": "BREAKING: Explosions reported near Bushehr port, southern Iran. "
                     "Videos circulating on social media show smoke rising. No official confirmation yet.",
             "url": "https://t.me/selftest/1",
             "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}]
    print("Haiku 처리 테스트(POST 안 함)…")
    store_backup = load_store()
    try:
        out = process_batch(fake, do_post=False)
        print(json.dumps(out, ensure_ascii=False, indent=2))
    finally:
        save_store(store_backup)   # 셀프테스트 흔적 제거
    print("✓ selftest 완료")

if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg == "--login":
        asyncio.run(do_login())
    elif arg == "--check":
        asyncio.run(do_check())
    elif arg == "--selftest":
        do_selftest()
    else:
        asyncio.run(run_listener())
