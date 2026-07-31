/* ============================================================
   Cloudflare Pages Function · /api/markets
   ------------------------------------------------------------
   야후(spark 배치)·업비트에서 최근 1년 일봉을 수집해 JSON 반환.
   엣지 캐시 15분 — 아무리 많은 사용자가 접속해도 원천 호출은
   15분에 1번. (fetch_markets.py 의 JS 이식판 — 목록 동기화 유지)
   ============================================================ */

const SERIES = [
  // [야후심볼, 이름, 그룹, 단위]
  ["^GSPC","S&P 500","지수",""], ["^IXIC","나스닥 종합","지수",""],
  ["^DJI","다우존스","지수",""], ["^KS11","코스피","지수",""],
  ["^KQ11","코스닥","지수",""], ["^N225","닛케이 225","지수",""],
  ["^HSI","항셍 (홍콩)","지수",""], ["^GDAXI","독일 DAX","지수",""],
  ["^SOX","필라델피아 반도체","기술",""], ["^NDX","나스닥 100 (빅테크)","기술",""],
  // 주식 - 미국 (매그니피센트 7 + 2026.6 상장한 스페이스X)
  ["AAPL","애플 (Apple)","주식 - 미국","$"], ["MSFT","마이크로소프트 (Microsoft)","주식 - 미국","$"],
  ["GOOGL","알파벳·구글 (Alphabet)","주식 - 미국","$"], ["AMZN","아마존 (Amazon)","주식 - 미국","$"],
  ["NVDA","엔비디아 (Nvidia)","주식 - 미국","$"], ["META","메타 (Meta)","주식 - 미국","$"],
  ["TSLA","테슬라 (Tesla)","주식 - 미국","$"], ["SPCX","스페이스X (SpaceX)","주식 - 미국","$"],
  ["PLTR","팔란티어 (Palantir)","주식 - 미국","$"],
  ["SMR","뉴스케일파워 (NuScale)","주식 - 미국","$"],
  ["LCID","루시드 그룹 (Lucid)","주식 - 미국","$"], ["PSNY","폴스타 (Polestar)","주식 - 미국","$"],
  ["BRK-A","버크셔 해서웨이 A (Berkshire A)","주식 - 미국","$"],
  ["BRK-B","버크셔 해서웨이 B (Berkshire B)","주식 - 미국","$"],
  ["XE","엑스에너지 (X-Energy)","주식 - 미국","$"],
  ["OKLO","오클로 (Oklo)","주식 - 미국","$"],
  ["PFE","화이자 (Pfizer)","주식 - 미국","$"], ["MRNA","모더나 (Moderna)","주식 - 미국","$"],
  ["BNTX","바이오엔테크 (BioNTech)","주식 - 미국","$"],
  // 주식 - 한국 (원화 KRW · 야후 .KS)
  ["005930.KS","삼성전자 (Samsung Elec)","주식 - 한국","₩"],
  ["000660.KS","SK하이닉스 (SK hynix)","주식 - 한국","₩"],
  ["034020.KS","두산에너빌리티 (Doosan Enerbility)","주식 - 한국","₩"],
  ["011070.KS","LG이노텍 (LG Innotek)","주식 - 한국","₩"],
  ["003550.KS","LG (LG Corp.)","주식 - 한국","₩"],
  ["373220.KS","LG에너지솔루션 (LG Energy Solution)","주식 - 한국","₩"],
  ["035420.KS","NAVER (네이버)","주식 - 한국","₩"],
  ["035720.KS","카카오 (Kakao)","주식 - 한국","₩"],
  ["000720.KS","현대건설 (Hyundai E&C)","주식 - 한국","₩"],
  ["034730.KS","SK (SK Inc.)","주식 - 한국","₩"],
  ["096770.KS","SK이노베이션 (SK Innovation)","주식 - 한국","₩"],
  ["KRW=X","달러/원","환율(달러)","₩"], ["JPY=X","달러/엔","환율(달러)","¥"],
  ["EURUSD=X","유로/달러","환율(달러)","$"], ["GBPUSD=X","파운드/달러","환율(달러)","$"],
  ["CHF=X","달러/스위스프랑","환율(달러)","Fr"], ["CNY=X","달러/위안","환율(달러)","元"],
  ["TWD=X","달러/대만달러","환율(달러)","NT$"], ["INR=X","달러/인도루피","환율(달러)","₹"],
  ["CZK=X","달러/체코코루나","환율(달러)","Kč"], ["VND=X","달러/베트남동","환율(달러)","₫"],
  ["^IRX","미국 3개월물","미국 채권","%"], ["2YY=F","미국 2년물","미국 채권","%"],
  ["^FVX","미국 5년물","미국 채권","%"], ["^TNX","미국 10년물","미국 채권","%"],
  ["^TYX","미국 30년물","미국 채권","%"],
  ["114260.KS","국고채 3년 ETF (KODEX)","채권(한·일)","₩"],
  ["148070.KS","국고채 10년 ETF (KOSEF)","채권(한·일)","₩"],
  ["2561.T","일본국채 ETF (iShares)","채권(한·일)","¥"],
  ["CL=F","WTI 원유","원자재·에너지","$"], ["BZ=F","브렌트유","원자재·에너지","$"],
  ["NG=F","천연가스","원자재·에너지","$"], ["SRUUF","우라늄 (실물신탁)","원자재·에너지","$"],
  ["GC=F","금","원자재·금속","$"], ["SI=F","은","원자재·금속","$"],
  ["HG=F","구리","원자재·금속","$"], ["PL=F","백금","원자재·금속","$"],
  ["PA=F","팔라듐","원자재·금속","$"], ["TIO=F","철광석 (62% Fe)","원자재·금속","$"],
  ["ZC=F","옥수수","원자재·식품","$"], ["ZW=F","밀","원자재·식품","$"],
  ["ZS=F","대두","원자재·식품","$"], ["SB=F","설탕","원자재·식품","$"],
  ["KC=F","커피","원자재·식품","$"], ["CC=F","코코아","원자재·식품","$"],
  ["CT=F","면화","원자재·의류","$"],
  ["BTC-USD","비트코인","암호화폐(달러)","$"], ["ETH-USD","이더리움","암호화폐(달러)","$"],
  ["SOL-USD","솔라나","암호화폐(달러)","$"], ["XRP-USD","리플","암호화폐(달러)","$"],
  ["BNB-USD","바이낸스코인","암호화폐(달러)","$"], ["DOGE-USD","도지코인","암호화폐(달러)","$"],
];

const UPBIT = [
  ["KRW-BTC","비트코인 (업비트)"], ["KRW-ETH","이더리움 (업비트)"],
  ["KRW-SOL","솔라나 (업비트)"], ["KRW-XRP","리플 (업비트)"],
  ["KRW-DOGE","도지코인 (업비트)"],
];

// 원화 크로스: [이름, 분모심볼, 배수, 곱셈여부(달러표시 통화)]
const KRW_CROSSES = [
  ["엔(100)/원","JPY=X",100,false], ["유로/원","EURUSD=X",1,true],
  ["파운드/원","GBPUSD=X",1,true], ["위안/원","CNY=X",1,false],
  ["스위스프랑/원","CHF=X",1,false], ["대만달러/원","TWD=X",1,false],
  ["동(100)/원","VND=X",100,false],
];

const UA = { "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)" };

function tsToPoints(ts, closes) {
  const out = {};
  (ts || []).forEach((t, i) => {
    const c = (closes || [])[i];
    if (c == null) return;
    out[new Date(t * 1000).toISOString().slice(0, 10)] = Math.round(c * 1e6) / 1e6;
  });
  return out;
}

async function fetchSpark(symbols) {
  const q = encodeURIComponent(symbols.join(","));
  const r = await fetch(
    `https://query1.finance.yahoo.com/v7/finance/spark?symbols=${q}&range=1y&interval=1d`,
    { headers: UA });
  if (!r.ok) throw new Error("yahoo " + r.status);
  const d = await r.json();
  const results = (d.spark && d.spark.result) || d.result || [];
  const out = {};
  for (const item of results) {
    try {
      const resp = item.response[0];
      out[item.symbol] = tsToPoints(resp.timestamp, resp.indicators.quote[0].close);
    } catch (e) { /* skip */ }
  }
  return out;
}

async function fetchUpbit(market) {
  const r = await fetch(
    `https://api.upbit.com/v1/candles/days?market=${market}&count=200`,
    { headers: { ...UA, Accept: "application/json" } });
  if (!r.ok) throw new Error("upbit " + r.status);
  const d = await r.json();
  const out = {};
  for (const c of d) out[c.candle_date_time_utc.slice(0, 10)] = c.trade_price;
  return Object.fromEntries(Object.entries(out).sort());
}

async function buildMarketData() {
  const raw = {};
  const syms = SERIES.map(s => s[0]);
  const chunks = [];
  for (let i = 0; i < syms.length; i += 20) chunks.push(syms.slice(i, i + 20));
  const sparkResults = await Promise.all(chunks.map(fetchSpark));
  sparkResults.forEach(r => Object.assign(raw, r));

  const data = [];
  for (const [sym, name, group, unit] of SERIES) {
    const pts = raw[sym];
    if (!pts || Object.keys(pts).length < 10) continue;
    const entries = Object.entries(pts).sort();
    data.push({ id: sym, name, group, unit,
      dates: entries.map(e => e[0]), closes: entries.map(e => e[1]) });
  }

  // 원화 크로스 (달러 페어에서 계산)
  const krw = raw["KRW=X"] || {};
  for (const [name, den, mul, isUsdQuoted] of KRW_CROSSES) {
    const d = raw[den] || {};
    const common = Object.keys(krw).filter(k => d[k] != null).sort();
    if (common.length < 10) continue;
    data.push({ id: "KRWX-" + den, name, group: "환율(원)", unit: "₩",
      dates: common,
      closes: common.map(k => Math.round(
        (isUsdQuoted ? krw[k] * d[k] : krw[k] / d[k]) * mul * 1e4) / 1e4) });
  }

  // 업비트 (실제 한국 시세)
  const upbitResults = await Promise.all(UPBIT.map(async ([mkt, name]) => {
    try {
      const pts = await fetchUpbit(mkt);
      if (Object.keys(pts).length < 10) return null;
      const entries = Object.entries(pts);
      return { id: "UPBIT-" + mkt, name, group: "암호화폐(원)", unit: "₩",
        dates: entries.map(e => e[0]), closes: entries.map(e => e[1]) };
    } catch (e) { return null; }
  }));
  upbitResults.filter(Boolean).forEach(s => data.push(s));

  // (주식 - 미국 그룹은 M7 + 스페이스X(SPCX) 모두 상장 종목 실시간 수집. xAI는 스페이스X에 병합.)

  return { updated: new Date().toISOString(), data };
}

export async function onRequest(context) {
  const cache = caches.default;
  const cacheKey = new Request("https://world-info-cache/api/markets?v=8-pharma");
  const hit = await cache.match(cacheKey);
  if (hit) return hit;

  try {
    const body = JSON.stringify(await buildMarketData());
    const res = new Response(body, { headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "public, max-age=900",     // 엣지 15분 캐시
    }});
    context.waitUntil(cache.put(cacheKey, res.clone()));
    return res;
  } catch (e) {
    return new Response(JSON.stringify({ error: String(e) }),
      { status: 502, headers: { "content-type": "application/json" } });
  }
}
