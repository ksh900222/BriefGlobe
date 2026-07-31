/* ============================================================
   Cloudflare Pages Function · /api/breaking
   ------------------------------------------------------------
   속보 트랙: Mac의 breaking_listener.py(텔레그램 수신)가 POST로
   항목을 밀어 넣고, 프론트가 60초 폴링으로 GET.
   저장은 KV(BREAKING_KV) 단일 키 — 쓰기 주체가 리스너 하나뿐이라
   read-modify-write로 충분. 화면 노출은 48h까지(전체 이력은
   리스너가 로컬 breaking-store.json에 별도 보관).
   GET  공개 · 엣지 캐시 20초 (다수 접속해도 KV 읽기는 20초에 1번)
   POST Authorization: Bearer <BREAKING_TOKEN> (Pages secret)
   ============================================================ */

const KEY = "items";
const KEEP_MS = 48 * 3600 * 1000;   // 화면 노출 최대 48시간
const MAX_ITEMS = 800;              // KV 항목 상한(안전판)

async function readItems(env) {
  try { return JSON.parse((await env.BREAKING_KV.get(KEY)) || "[]"); }
  catch (e) { return []; }
}

export async function onRequestGet({ env }) {
  const now = Date.now();
  const items = (await readItems(env)).filter(it => now - Date.parse(it.ts) < KEEP_MS);
  return new Response(JSON.stringify({ items, t: now }), {
    headers: {
      "content-type": "application/json; charset=utf-8",
      "access-control-allow-origin": "*",
      "cache-control": "public, max-age=15, s-maxage=20",
    },
  });
}

export async function onRequestPost({ request, env }) {
  const auth = request.headers.get("authorization") || "";
  if (!env.BREAKING_TOKEN || auth !== `Bearer ${env.BREAKING_TOKEN}`)
    return new Response("unauthorized", { status: 401 });

  let body;
  try { body = await request.json(); }
  catch (e) { return new Response("bad json", { status: 400 }); }
  const incoming = Array.isArray(body) ? body : [body];

  // id 기준 upsert — 리스너가 같은 사건에 소스 추가·상태 승격(confirmed)을 재전송할 수 있음
  const byId = new Map((await readItems(env)).map(it => [it.id, it]));
  for (const it of incoming) {
    if (!it || !it.id || !it.ts || !it.title) continue;
    byId.set(it.id, { ...(byId.get(it.id) || {}), ...it });
  }
  const now = Date.now();
  const items = [...byId.values()]
    .filter(it => now - Date.parse(it.ts) < KEEP_MS)
    .sort((a, b) => Date.parse(b.ts) - Date.parse(a.ts))
    .slice(0, MAX_ITEMS);
  await env.BREAKING_KV.put(KEY, JSON.stringify(items));
  return new Response(JSON.stringify({ ok: true, count: items.length }), {
    headers: { "content-type": "application/json" },
  });
}
