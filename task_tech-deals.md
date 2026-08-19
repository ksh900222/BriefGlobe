# tech-deals — 글로벌 테크 딜 실검색 → `grok-tech-news.json`

> 🕐 **갱신 주기: 하루 2회.** 🎯 목적: GDELT DOC(어그리게이터 편중)이 **구조적으로 못 보는**
>   전문 매체·1차/공식 소스·아시아 언론의 테크 뉴스를 Grok 웹 실검색으로 직접 수집.

실시간 검색(웹 + X)으로 **AI·반도체·양자·우주·자율주행·데이터센터·국방테크·로보틱스** 8개 섹터의
**"딜·발표" 성격 뉴스**(계약·투자·수주·출시·실적·규제·인수합병)를 찾아 `grok-tech-news.json` 에 저장.

**⭐ 핵심 — 소스를 넓혀라(이게 이 작업의 존재 이유):**
GDELT엔 안 잡히는 아래 **전문·1차·다국어 매체**를 우선 겨냥한다:
- **AI**: The Information, TechCrunch, The Decoder, Axios, VentureBeat + OpenAI/Anthropic 릴리즈노트
- **반도체**: DIGITIMES, TrendForce, 전자신문, Nikkei Asia + TSMC/ASML 공시(SEC)
- **양자**: The Quantum Insider, Quantum Computing Report
- **우주**: SpaceNews, Space.com + NASA/FAA/SpaceX 공식
- **자율주행**: Electrek, Not a Tesla App, Teslarati + **NHTSA 공시**
- **데이터센터**: DataCenterDynamics(DCD) + AWS/Meta 뉴스룸
- **국방테크**: Defense News, Aviation Week, Militarnyi
- **1차/공식**: SEC·NHTSA·NASA·FAA·DoD·EU집행위 + 기업 공식 블로그
- **아시아**: 뉴스핌·디지털타임스(한) / 36Kr·SCMP·Caixin(중) / Nikkei Asia(일)

**수집 대상 (총 30~50건 목표, 섹터별 3~8건):**
- 최근 오늘~3일. **딜·발표 중심** — 분석·전망·논평·루머는 제외(구체적 사건만).
- 실재·검증 가능한 것만. 추측·창작 금지. **출처 URL 필수**(위 매체 원문 직접 링크).
- 같은 딜 중복 금지. **제목은 한국어로 작성**(번역 불필요하게).

**⭐ `theme`(섹터)를 반드시 아래 6종 중 하나로 태깅** — 프론트 "기업·테크" 칩 드릴다운에 쓰인다:
`자율주행·로보틱스` / `AI·연산·전력` / `우주·발사` / `반도체·전기차·배터리` / `양자컴퓨터` / `국방·방산테크`
(데이터센터→`AI·연산·전력`, 로보틱스→`자율주행·로보틱스`로 접어 넣는다)

**출력 — `grok-tech-news.json` 에만 저장** (asia-news의 `grok-news.json` 과 별개 파일 — 서로 안 건드린다). JSON 배열:
```json
[
  {
    "title": "한국어 제목 (한 줄, 딜 내용 구체적으로)",
    "summary": "한국어 요약 2줄 정도(2문장, 약 40~80자) — 금액·당사자·시점 등 구체 수치 포함",
    "category": "기술",
    "theme": "위 6종 섹터 중 하나",
    "source": "출처 매체명 (예: Electrek, DIGITIMES, NHTSA)",
    "city": "본사/발표 도시 (한국어)",
    "country": "나라 (한국어)",
    "lat": 37.5665,
    "lng": 126.9780,
    "date": "YYYY-MM-DD (발표일)",
    "url": "https://실제-원문-링크",
    "importance": 7
  }
]
```
- `category`는 **항상 `"기술"`**. `theme`·`source`·`url` **필수**.
- `lat`/`lng`는 본사나 발표 장소(예: 엔비디아→산타클라라, TSMC→신주). 모르면 도시명으로 자동 보정되니 `city`/`country`만이라도 정확히.
- `importance`(0~10): 딜 규모·파급력 기준 — **상단 "공통 — 중요도 채점 기준" 표를 따를 것.** (대형 계약·수십억달러 투자·핵심 규제 ≈ 7~8, 일반 출시·소규모 ≈ 5 이하)

---
