/* ============================================================
   Cloudflare Pages Function · /api/quotes
   ------------------------------------------------------------
   KIS(한국투자증권) 실시간 현재가 프록시 — 주식 27종목의 "현재가"만 반환.
   (1년 히스토리·금리·원자재는 정적 market-data.js / 시간당 파이프라인 담당)

   · 국내 11종목: 시장구분 UN(통합=KRX+NXT) → 정규+NXT 프리/애프터 자동 반영
   · 미국 14종목: 해외 현재가 last → 프리/애프터 자동 반영
   · 엣지 캐시 10초 → 보는 사람이 몇이든 KIS 원천 호출은 10초당 1회로 고정(한도 방어)
   · 조회(quotations) 전용 — 주문/거래 엔드포인트 없음(read-only)

   필요 secret(Cloudflare Pages 환경변수):
     KIS_APPKEY, KIS_APPSECRET
   ============================================================ */

const BASE = "https://openapi.koreainvestment.com:9443";

// 국내: [seriesId, 6자리코드]
const KR = [
  ["005930.KS", "005930"], ["000660.KS", "000660"], ["034020.KS", "034020"],
  ["011070.KS", "011070"], ["003550.KS", "003550"], ["373220.KS", "373220"],
  ["035420.KS", "035420"], ["035720.KS", "035720"], ["000720.KS", "000720"],
  ["034730.KS", "034730"], ["096770.KS", "096770"],
];
// 미국: [seriesId, 거래소코드, KIS심볼]  (BRK-A/B 는 KIS 심볼이 BRK/A · BRK/B)
const US = [
  ["AAPL", "NAS", "AAPL"], ["MSFT", "NAS", "MSFT"], ["GOOGL", "NAS", "GOOGL"],
  ["AMZN", "NAS", "AMZN"], ["NVDA", "NAS", "NVDA"], ["META", "NAS", "META"],
  ["TSLA", "NAS", "TSLA"], ["PLTR", "NAS", "PLTR"], ["LCID", "NAS", "LCID"],
  ["PSNY", "NAS", "PSNY"], ["SMR", "NYS", "SMR"], ["OKLO", "NYS", "OKLO"],
  ["BRK-A", "NYS", "BRK/A"], ["BRK-B", "NYS", "BRK/B"],
  ["SPCX", "NAS", "SPCX"], ["XE", "NAS", "XE"],   // 스페이스X·엑스에너지 나스닥 상장(2026)
];
// 암호화폐 — 24시간 실시간(무료·키 불필요, KIS 무관).
//   CF는 Binance/CoinGecko 를 IP 차단당함 → Upbit 한 곳으로: KRW 마켓(원) + USDT 마켓(≈달러).
//   USDT≈$1 페그라 달러 근사. BNB 는 Upbit 미상장 → CF 폴백엔 BNB-USD 없음(Mac은 Binance로 있음).
const UPBIT_MAP = {
  "KRW-BTC": "UPBIT-KRW-BTC", "KRW-ETH": "UPBIT-KRW-ETH", "KRW-SOL": "UPBIT-KRW-SOL", "KRW-XRP": "UPBIT-KRW-XRP", "KRW-DOGE": "UPBIT-KRW-DOGE",
  "USDT-BTC": "BTC-USD", "USDT-ETH": "ETH-USD", "USDT-SOL": "SOL-USD", "USDT-XRP": "XRP-USD", "USDT-DOGE": "DOGE-USD",
};

async function fetchCrypto() {
  const out = {};
  try {
    const r = await fetch("https://api.upbit.com/v1/ticker?markets=" + Object.keys(UPBIT_MAP).join(","));
    if (r.ok) {
      for (const d of await r.json()) {
        const id = UPBIT_MAP[d.market];
        if (id) out[id] = { price: d.trade_price, chg: d.signed_change_rate * 100 };
      }
    }
  } catch (e) { /* skip */ }
  return out;
}

function kisHeaders(env, tok, trId) {
  return {
    "content-type": "application/json; charset=utf-8",
    "authorization": "Bearer " + tok,
    "appkey": env.KIS_APPKEY,
    "appsecret": env.KIS_APPSECRET,
    "tr_id": trId,
    "custtype": "P",
  };
}

// 접근토큰(24h) — 엣지 캐시에 보관(재발급은 하루 몇 번 수준, KIS 발급빈도 제한 방어)
async function getToken(env) {
  const cache = caches.default;
  const key = new Request("https://kis-token-cache/v1");
  const hit = await cache.match(key);
  if (hit) {
    const j = await hit.json();
    if (j.token && j.exp > Date.now() / 1000 + 60) return j.token;
  }
  const r = await fetch(BASE + "/oauth2/tokenP", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({
      grant_type: "client_credentials",
      appkey: env.KIS_APPKEY,
      appsecret: env.KIS_APPSECRET,
    }),
  });
  const d = await r.json();
  if (!d.access_token) throw new Error("token: " + JSON.stringify(d).slice(0, 140));
  const exp = Math.floor(Date.now() / 1000) + (d.expires_in || 86400) - 600;
  const store = new Response(JSON.stringify({ token: d.access_token, exp }),
    { headers: { "cache-control": "max-age=82800" } });   // ~23h
  await cache.put(key, store);
  return d.access_token;
}

async function krQuote(env, tok, id, code) {
  const u = new URL(BASE + "/uapi/domestic-stock/v1/quotations/inquire-price");
  u.searchParams.set("FID_COND_MRKT_DIV_CODE", "UN");   // 통합(KRX+NXT)
  u.searchParams.set("FID_INPUT_ISCD", code);
  const r = await fetch(u, { headers: kisHeaders(env, tok, "FHKST01010100") });
  const d = await r.json();
  const o = d.output || {};
  const p = parseFloat(o.stck_prpr || 0);
  if (!p) throw new Error("HTTP" + r.status + " " + (d.msg_cd || "") + " " + (d.msg1 || "no price"));
  return { id, price: p, chg: parseFloat(o.prdy_ctrt || 0) };
}

async function usQuote(env, tok, id, excd, symb) {
  const u = new URL(BASE + "/uapi/overseas-price/v1/quotations/price");
  u.searchParams.set("AUTH", "");
  u.searchParams.set("EXCD", excd);
  u.searchParams.set("SYMB", symb);
  const r = await fetch(u, { headers: kisHeaders(env, tok, "HHDFS00000300") });
  const d = await r.json();
  const o = d.output || {};
  const p = parseFloat(o.last || 0);
  if (!p) throw new Error("HTTP" + r.status + " " + (d.msg_cd || "") + " " + (d.msg1 || "no price"));
  return { id, price: p, chg: parseFloat(o.rate || 0) };
}

// 25종목을 완전 순차(동시성 0)·호출간 250ms — 로컬 파이프라인과 동일 패턴(EGW00201 회피).
//   CF는 동시요청 버스트가 KIS 초당한도를 건드려서, 순차가 유일하게 안정적. 재시도 없음(버스트 유발).
//   총 소요 ~14초지만 stale-while-revalidate 로 클라이언트 지연과 분리됨. 실패 종목은 다음 갱신에 반영.
async function fetchAll(env, tok) {
  const tasks = [
    ...KR.map(([id, code]) => () => krQuote(env, tok, id, code)),
    ...US.map(([id, excd, symb]) => () => usQuote(env, tok, id, excd, symb)),
  ];
  const out = {};
  const errs = [];
  for (let i = 0; i < tasks.length; i++) {
    try {
      const v = await tasks[i]();
      if (v) out[v.id] = { price: v.price, chg: v.chg };
    } catch (e) {
      errs.push(String(e && e.message || e).slice(0, 80));
    }
    if (i < tasks.length - 1) await new Promise(rs => setTimeout(rs, 500));
  }
  return { out, errs };
}

function json(obj, status, cc) {
  const h = { "content-type": "application/json; charset=utf-8" };
  if (cc) h["cache-control"] = cc;
  return new Response(JSON.stringify(obj), { status: status || 200, headers: h });
}

const FRESH_MS = 8000;   // 캐시가 이보다 오래되면 백그라운드 갱신 트리거

export async function onRequest(context) {
  const { env } = context;
  if (!env.KIS_APPKEY || !env.KIS_APPSECRET) {
    return json({ error: "KIS secret 미설정" }, 503);
  }
  const debug = new URL(context.request.url).searchParams.has("debug");
  const cache = caches.default;
  const cacheKey = new Request("https://world-info-cache/api/quotes?v=2");

  // KIS 를 안전 페이스로 조회 → 이전 캐시에 병합(실패 종목은 직전 값 유지) → 저장.
  //   CF 공유 IP가 KIS 유량제한을 받아 회차당 일부 실패하지만, 병합으로 25종목이 항상 채워지고
  //   각 종목은 몇 회차 안에 최신화된다.
  const refresh = async () => {
    const prev = await cache.match(cacheKey);
    const prevQ = prev ? ((await prev.json()).quotes || {}) : {};
    const cryptoP = fetchCrypto();                 // KIS 토큰과 무관하게 병렬
    let out = {}, errs = [];
    try {
      const tok = await getToken(env);
      const r = await fetchAll(env, tok);
      out = r.out; errs = r.errs;
    } catch (e) { errs.push("stocks: " + String(e).slice(0, 60)); }
    Object.assign(out, await cryptoP);             // 크립토 병합(주식 실패해도 크립토는 나옴)
    const cnt = Object.keys(out).length;
    const merged = { ...prevQ, ...out };
    const body = { updated: new Date().toISOString(), quotes: merged, _ts: Date.now(), _fresh: cnt };
    if (cnt || prev) await cache.put(cacheKey, json(body, 200, "public, max-age=60"));
    return { body: (cnt || prev) ? body : null, errs, cnt };
  };

  if (debug) {                                   // 진단: 동기 조회 + 실패 이유
    const { body, errs, cnt } = await refresh();
    return json({ count: cnt, errs, sample: body ? Object.entries(body.quotes).slice(0, 3) : [] }, 200);
  }

  const cached = await cache.match(cacheKey);
  const body = cached ? await cached.json() : null;
  const age = (body && body._ts) ? Date.now() - body._ts : Infinity;

  if (body && age < FRESH_MS) return json(body, 200);        // 신선 → 즉시
  if (body) {                                                 // 만료 → stale 즉시 + 백그라운드 갱신
    context.waitUntil(refresh().catch(() => {}));
    return json(body, 200);
  }
  try {                                                       // 최초 1회만 갱신 완료까지 대기
    const { body: nb } = await refresh();
    return json(nb || { updated: new Date().toISOString(), quotes: {} }, 200);
  } catch (e) {
    return json({ error: String(e) }, 502);
  }
}
