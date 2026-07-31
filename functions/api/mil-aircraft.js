/* ============================================================
   Cloudflare Pages Function · /api/mil-aircraft
   ------------------------------------------------------------
   여러 커뮤니티 ADS-B 관측망(airplanes.live·adsb.lol·adsb.fi)의
   군용기 피드(/v2/mil)를 서버에서 받아 hex 기준으로 병합·중복제거해
   하나의 {ac:[...]} 로 반환. 관측망이 서로 달라 합치면 포착률↑.
   브라우저 CORS 문제(adsb.lol·adsb.fi는 CORS 미허용)도 여기서 해소.
   엣지 15초 캐시 — 다수 접속해도 원천 호출은 15초에 1번.
   ============================================================ */

const SOURCES = [
  ["airplanes.live", "https://api.airplanes.live/v2/mil"],
  ["adsb.lol", "https://api.adsb.lol/v2/mil"],
  ["adsb.fi", "https://opendata.adsb.fi/api/v2/mil"],
];

// 중복 기체 병합 시 비어있으면 채워넣을 필드
const FILL = ["t", "desc", "r", "ownOp", "flight", "category", "gs", "track",
  "true_heading", "alt_baro", "lat", "lon", "squawk"];

async function fetchSource(url) {
  const ctl = new AbortController();
  const to = setTimeout(() => ctl.abort(), 8000);
  try {
    const res = await fetch(url, {
      signal: ctl.signal,
      cf: { cacheTtl: 4 },
      headers: {
        "User-Agent": "Mozilla/5.0 (compatible; world-info-map/1.0; +https://world-info.pages.dev)",
        "Accept": "application/json",
      },
    });
    if (!res.ok) return { list: [], diag: "http " + res.status };
    const data = await res.json();
    const list = (data && Array.isArray(data.ac)) ? data.ac : [];
    return { list, diag: "ok " + list.length };
  } catch (e) {
    return { list: [], diag: "err " + (e && e.name) + ":" + (e && e.message || "").slice(0, 60) };
  } finally {
    clearTimeout(to);
  }
}

async function buildMerged() {
  const results = await Promise.all(SOURCES.map(([, url]) => fetchSource(url)));
  const byHex = {};
  const sources = {};
  const diag = {};
  SOURCES.forEach(([name], i) => {
    const r = results[i] || { list: [], diag: "none" };
    const list = r.list || [];
    diag[name] = r.diag;
    sources[name] = list.length;
    list.forEach((a) => {
      if (!a || !a.hex) return;
      const key = a.hex;
      if (!byHex[key]) {
        byHex[key] = Object.assign({}, a, { _srcs: [name] });
      } else {
        const cur = byHex[key];
        cur._srcs.push(name);
        for (const f of FILL) {
          const empty = cur[f] === undefined || cur[f] === null || cur[f] === "";
          const has = a[f] !== undefined && a[f] !== null && a[f] !== "";
          if (empty && has) cur[f] = a[f];
        }
      }
    });
  });
  const ac = Object.values(byHex);
  return { ac, total: ac.length, sources, diag, now: Date.now() };
}

export async function onRequest(context) {
  const cache = caches.default;
  const cacheKey = new Request("https://world-info-cache/api/mil-aircraft?v=3");
  const hit = await cache.match(cacheKey);
  if (hit) return hit;

  try {
    const body = JSON.stringify(await buildMerged());
    const res = new Response(body, { headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "public, max-age=5",        // 엣지 5초 캐시(빠른 갱신)
      "access-control-allow-origin": "*",
    }});
    context.waitUntil(cache.put(cacheKey, res.clone()));
    return res;
  } catch (e) {
    return new Response(JSON.stringify({ error: String(e), ac: [] }),
      { status: 502, headers: { "content-type": "application/json", "access-control-allow-origin": "*" } });
  }
}
