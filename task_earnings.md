# earnings — 실적 컨센서스·실제 분기 추세 누적 → delta JSON (`earnings-series.js`)

**▶ 큐 기반 절차:** ① `pipeline-todo.json` 의 **`earnings_todo`**(미등록 실적종목 — 예 SPCX)와 **`earnings_stale`**(신규 분기 의심 종목), 그리고 **`balance_backfill`**(자산·부채 시계열이 없는 종목 → 아래 재무상태표 5년치 백필 대상)을 읽는다.
② `earnings_todo` 종목은 신규로(각 종목 metrics 기준 분기 매출·EPS 등), `earnings_stale` 종목은 **새로 발표된 분기**의 act(+발표 전이면 다음 분기 cons)를 조사한다.
③ 결과를 **`series-delta.json` 의 `earnings` 섹션**에 담아 낸다(파일 직접 편집 금지). 저장은 `merge_series.py`.
- delta 형식: `{"earnings": {"<TICKER>": {"name","metrics":[...], "quarters":[{"period","revenue":{"act","cons"},"eps":{"act","cons"},...,"source"}]}}}` — 기존 종목이면 새 분기만 내도 됨(merge 가 과거·메타 보존).
- **⭐ act(실제)를 채우는 분기는 cons(컨센서스)도 반드시 같은 metric 객체에 함께 기록한다** — 그 분기의 시장 컨센서스(캘린더 `forecast`에서 수치 추출, 예 EPS·매출)를 `cons`에. **`act`만 넣고 `cons`를 null로 두지 마라**(그래프에 컨센서스 점이 안 보임). **컨센서스와 실제가 같아도 둘 다 기록**(그래프는 겹쳐도 둘 다 표시). 컨센서스를 정말 못 구하면만 `cons:null`.

> 🕐 **갱신 주기: 하루 1회(stock-fin·E와 함께).** 캘린더 '실적' 항목 클릭 시 뜨는 **"컨센서스 vs 실제" 분기 추세 차트**의 데이터다.
> ♻️ **누적 파일** — 과거 엔트리를 **절대 지우지 말고 보존**하며, 새 분기·새 실제값·새 컨센서스만 추가/갱신한다.

**⭐ 분기 재무상태표(자산·부채) 추이도 같은 quarters 에 함께 채운다 — 증시 상세 '자산·부채 추이' 그래프용:**
- 각 분기 객체에 다음 metric 을 **cons 없이**(`{"act": 값, "cons": null}`) 추가한다. 실적(매출·EPS)과 **같은 quarters 배열의 같은 period** 에 얹으면 된다.
  - **미국($B)**: `totalAssets`·`currentAssets`·`totalLiab`·`currentLiab`·`equity` (재무상태표 총자산/유동자산/부채총계/유동부채/자기자본, 단위 $B). 해당 종목 `metrics` 배열에 이 키들도 추가.
  - **한국(조원)**: `totalAssetsKRW`·`currentAssetsKRW`·`totalLiabKRW`·`currentLiabKRW`·`equityKRW` (조원). 달러 키와 섞지 말 것. 출처=DART.
- **최초엔 최근 5년치(약 20분기)를 백필**하고, 이후엔 새 분기만 추가(merge 가 과거 보존·누적). 재무상태표는 컨센서스가 없으므로 `cons` 는 항상 `null`.
- 스케일 오류 금지: 재무상태표는 **분기말 잔액(스톡)** 값 그대로(누적/연환산 아님). 억원→조원 ÷10000.

**대상: 주식-미국 16 + 주식-한국 11 전 종목** (market-data.js `주식 - 미국`·`주식 - 한국` 그룹의 모든 티커).
- 종목 수를 **하드코딩하지 말고**, `earnings-series.js`의 기존 키 + market-data.js 두 그룹 티커 + `econ-calendar` 실적 티커를 기준으로 삼는다.
- **미국(19, 달러)**: AAPL·MSFT·GOOGL·AMZN·NVDA·META·TSLA·SPCX·PLTR·SMR·LCID·PSNY·BRK-A·BRK-B·XE·OKLO·PFE·MRNA·BNTX.
  metric = `revenue`($B)·`eps`($)·`netIncome`($B)·`opMargin`(%)·`fcf`($B) + 종목별 KPI. (BRK는 규모 커도 $B 그대로; 프리레비뉴 종목은 확인된 분기만, 없으면 null.)
- **한국(11, ₩)**: 005930.KS(삼성전자)·000660.KS(SK하이닉스)·034020.KS(두산에너빌리티)·011070.KS(LG이노텍)·003550.KS(LG)·373220.KS(LG에너지솔루션)·035420.KS(NAVER)·035720.KS(카카오)·000720.KS(현대건설)·034730.KS(SK)·096770.KS(SK이노베이션).
  - **한국은 전용 metric 키를 쓴다**(달러 지표와 섞지 말 것): `revenueKRW`(매출 **조원**)·`opIncomeKRW`(영업이익 **조원**)·`netIncomeKRW`(순이익 **조원**)·`epsKRW`(EPS **원**). 예: 삼성전자 분기 매출 `"revenueKRW":{"act":79.1,"cons":78.0}`.
  - 티커 key 는 **`.KS` 포함**한 정확한 값(예 `"005930.KS"`). `name` 은 표시명(예 `"삼성전자 (Samsung Elec)"`).
  - 출처: **DART(금융감독원 전자공시)**·네이버금융·회사 IR. 조원 네이티브(억원이면 ÷10000해 조원). 컨센서스는 증권사/에프앤가이드·네이버 컨센서스.
  - ⛔ **단위·기간 스케일 오류 절대 금지 — 반드시 '단일 분기(3개월)' 값**(누적/반기/연간 아님). 억원↔조원(÷10000)·백만원 혼동 주의.
  - 📏 **정합성 자가검증(분기 매출 앵커 범위, 이 밖이면 스케일 오류이니 재확인):** 삼성전자 **70~85조**, SK하이닉스 **12~22조**, SK이노베이션 **15~22조**, SK(지주) **28~40조**, LG에너지솔루션 **5~8조**, 현대건설 **7~9조**, LG이노텍 **4~6조**, 두산에너빌리티 **4~5조**, NAVER **2.5~3조**, 카카오 **1.8~2.3조**, LG(지주) **1.8~2.3조**. **영업이익률은 업종·사이클마다 크게 다르다** — LG이노텍 3~5%, 삼성전자·SK하이닉스는 메모리 슈퍼사이클에서 **50~76%** 까지 간다(2026Q2 공시). **마진이 높다고 임의로 낮추지 마라.** 다만 **영업이익·순이익이 매출보다 큰 것은 불가능**하니 그건 오류다.
- **⭐ 신규 종목은 최근 8~12분기**를 우선 채워라(차트 기본 창이 최근 8분기). 확인 안 되는 과거·metric 은 넣지 말 것(억지 채움 금지, 불확실=null).

**구조 (JS 객체 리터럴 — `JSON.parse` 안 됨, `stocks-info.js`처럼 eval 파싱):**
```js
const EARNINGS_SERIES = {
  "TICKER": {
    "name": "표시명",
    "metrics": ["revenue","eps","netIncome","opMargin","fcf", /* +종목별 KPI */],
    "quarters": [
      { "period": "Q3 2025 (2025-09)",
        "revenue":{"act":28.1,"cons":null}, "eps":{"act":0.39,"cons":null},
        "netIncome":{"act":1.37,"cons":null}, "opMargin":{"act":5.78,"cons":null}, "fcf":{"act":3.99,"cons":null},
        "source": "https://stockanalysis.com/stocks/TSLA/financials/?p=quarterly" },
      { "period": "Q2 2026 (2026-06)",   // 다가오는 분기 = cons만(act 전부 null)
        "revenue":{"act":null,"cons":25.5}, "eps":{"act":null,"cons":0.48},
        "netIncome":{"act":null,"cons":null}, "opMargin":{"act":null,"cons":null}, "fcf":{"act":null,"cons":null},
        "source": "컨센서스 ... | https://..." }
    ]
  }
};
```
- **`metrics` 배열이 그 종목에 적용할 지표·순서를 정한다**(데이터 확보한 지표만 넣음). 각 분기 엔트리는 그 지표들을 `{act,cons}`로 가진다.
  UI 지표 라벨·단위는 `index.html`의 `EARN_METRICS` 레지스트리에 있으니 **키만 맞으면 자동 렌더**된다.
- **한국 종목(₩) 구조 예 — 전용 조원/원 키 사용:**
```js
  "005930.KS": { "name": "삼성전자 (Samsung Elec)",
    "metrics": ["revenueKRW","opIncomeKRW","netIncomeKRW","epsKRW"],
    "quarters": [
      { "period": "Q1 2026 (2026-03)",
        "revenueKRW":{"act":79.1,"cons":78.0}, "opIncomeKRW":{"act":6.7,"cons":6.5},
        "netIncomeKRW":{"act":6.9,"cons":6.6}, "epsKRW":{"act":1010,"cons":970},
        "source": "DART 분기보고서 | https://dart.fss.or.kr ..." } ] }
```
- **지표 키·단위**:
  - 공통(미국, 전 종목): `revenue`·`netIncome`·`fcf` = **$B**, `opMargin` = **%**, `eps` = **$**.
  - **한국(₩) 전용**: `revenueKRW`·`opIncomeKRW`·`netIncomeKRW` = **조원**, `epsKRW` = **원**. (달러 지표와 섞지 말 것)
  - 마진류: `grossMargin`·`autoGrossMargin`·`azureGrowth` = **%**.
  - 세그먼트 매출: `iphoneRev`·`servicesRev`·`adRev`·`cloudRev`·`awsRev`·`awsOpIncome`·`dcRev`·`commercialRev`·`govRev` = **$B**.
  - 기타: `deliveries`·`production` = **대**, `energyStorage` = **GWh**, `dau` = **억명**, `adArpu` = **$**.
- **종목별 목표 KPI(데이터 신뢰될 때 `metrics`에 추가):** TSLA `production`·`energyStorage`·`autoGrossMargin` /
  AAPL `iphoneRev`·`servicesRev` / GOOGL `adRev`·`cloudRev` / AMZN `awsRev`·`awsOpIncome` / NVDA `dcRev`·`grossMargin` /
  META `dau`·`adArpu` / MSFT `azureGrowth`·`cloudRev` / PLTR `commercialRev`·`govRev`.
  ⚠️ **세그먼트/KPI는 분기 실제값이 확인될 때만**(공식 실적·10-Q). stockanalysis '세그먼트' 페이지는 TTM(누적)이라 분기값으로 쓰지 말 것. 미확보 = 해당 키를 넣지 않거나 `act:null`.
- **컨센서스(`cons`)**: 과거 분기는 **지어내지 말고 그대로 둔다(대개 null)**. 매 주기 **다가오는 분기**의 `cons`를 기록한다 —
  **컨센서스가 공표되는 지표만**(매출·EPS·순이익·세그먼트 등, calendar 값 재활용). 컨센서스 없는 지표(생산량·DAU·마진 등)는 `cons` 계속 `null`.
- **실제값(`act`)**: 분기 실적이 **발표되면** 그 분기 각 지표의 `act`를 채운다. 이전 `cons`는 **그대로 보존**(대비 유지). 출처는 **stockanalysis.com 분기 재무** 등 검증 가능한 것만.
- `source`: 분기별 `"매체 | https://원문"`. 다가오는 분기는 컨센서스 출처.

**누적 규칙 (반드시):**
1. 기존 `earnings-series.js`를 읽어 파싱한다(과거 엔트리 **유지**).
2. 각 대상 티커에 대해:
   - **다가오는 실적 분기 엔트리가 없으면** 추가하고 `cons`를 채운다(`act`=null).
   - **직전에 '다가오는'이던 분기가 이제 발표됐으면** 그 엔트리의 `act`를 실제값으로 채운다(`cons`는 보존). 그리고 그다음 분기의 cons 엔트리를 새로 추가.
3. `period` 문자열은 **그 종목 기존 표기 규칙**을 따른다 — 현재 형식 `"Q{분기} {회계연도} ({기말 YYYY-MM})"` (예: 애플 `"Q3 2026 (2026-06)"`, 엔비디아 `"Q2 2027 (2026-07)"`). 기말월(괄호)로 분기를 앵커링한다. **중복 period 금지.**
4. **지어내기 금지.** 확인 안 되면 해당 값 `null`. 범위 컨센서스(예 `$1.89–1.93`)는 중간값으로 하고 `source`에 원 범위 표기.
5. **지표별 채움 우선순위**: 공통 3종(netIncome·opMargin·fcf)을 먼저, 그다음 종목별 KPI. 무리한 전량 채움보다 **검증 가능한 값 우선**.

**저장:** `earnings-series.js` 를 위 구조로 **전체 티커·전체 분기 포함** 덮어쓴다. (다른 파일 건드리지 않음)

---

## ✅ 완료 판정
- `series-delta.json` 에 `earnings` 섹션을 쓰고 **`python3 merge_series.py --delta series-delta.json`** 실행.
- 출력에 `🛡️` 줄이 있으면 **네가 낸 값이 차단·교정된 것**이다. 원인을 고쳐 다시 내라
  (유니버스 밖 티커 / 종목명 오기 / 다른 회사 출처 / 공시와 다른 값 / 중복 분기).
- ⛔ 이 파일은 **실적 시계열 전용**이다. 뉴스·번역(`to_translate.json`·`merge_news.py`)은 여기서 하지 마라.
