/* ============================================================
   Cloudflare Pages Function · /api/geo
   ------------------------------------------------------------
   방문자 IP 기반 대략 위치(Cloudflare 엣지 지오)를 반환.
   브라우저 GPS 권한 팝업 없이 도시 수준 근사치.
   지도 초기 회전(방문자 지역이 지구본 정면)에 사용.
   ※ 방문자마다 달라야 하므로 캐시 금지(no-store).
   ============================================================ */
export function onRequest(context) {
  const cf = (context.request && context.request.cf) || {};
  const num = (v) => {
    const n = parseFloat(v);
    return Number.isFinite(n) ? n : null;
  };
  const body = {
    lat: num(cf.latitude),
    lng: num(cf.longitude),
    city: cf.city || null,
    region: cf.region || null,
    country: cf.country || null,
    tz: cf.timezone || null,
  };
  return new Response(JSON.stringify(body), {
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store",
    },
  });
}
