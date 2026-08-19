# stock-fin — 종목 재무·밸류에이션 상세 → `stocks-info.js`

**▶ 큐 기반 절차(공통 계약 준수):** ① `pipeline-todo.json` 의 **`stocks_info_todo`**(미등록 종목 — 사용자가 새로 넣은 종목 포함, 예 삼성전기)를 읽는다.
② 그 종목들 + 기존 종목의 재무·부채·자산·밸류에이션·투자자·발표일정을 조사해 `stocks-info.js` 를 갱신한다(신규 종목은 아래 스키마대로 엔트리 추가, **과거 종목 보존**).
③ 큐의 **모든** todo 를 처리하고 못 채운 값은 `null`/`"확인 필요"`. (stocks-info 는 series 파일 아님 → delta 아니라 이 파일을 직접 갱신.)

> 🕐 **갱신 주기: 하루 1회(또는 실적 발표일 기준).** 재무제표는 분기 실적 때만 바뀌므로 매시간 조사할 필요 없다.
> **뉴스·SNS는 여기서 다루지 않는다 → stock-news 소관.** (이 작업은 `news` 를 쓰지 않는다.)

시장 페이지 '주식 - 미국'·'주식 - 한국' 그룹의 각 종목을 클릭하면 상세 정보가 뜬다.
그 데이터를 검증 가능한 공개자료(회사 IR·SEC 10-K/10-Q·8-K·금감원 DART, stockanalysis/MacroTrends 등)로
조사해 `stocks-info.js` 의 `STOCKS_INFO` 객체를 갱신한다. **`news` 필드는 만들지 않는다**(stock-news가 `stocks-news.js`에 별도 관리).

**대상 티커 — 미국(19):** AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA, SPCX(스페이스X, 2026.6 상장·xAI 합병), PLTR(팔란티어), SMR(뉴스케일파워·소형모듈원자로), LCID(루시드·전기차), PSNY(폴스타·전기차), BRK-A·BRK-B(버크셔 해서웨이 A/B — 각각 별도 엔트리), XE(엑스에너지·SMR 원자력, 2026 상장), OKLO(오클로·SMR 원자력), PFE(화이자·제약), MRNA(모더나·mRNA), BNTX(바이오엔테크·mRNA, 나스닥 ADR)

**대상 티커 — 한국(11, 키=야후 `.KS`):** `005930.KS`(삼성전자), `000660.KS`(SK하이닉스), `034020.KS`(두산에너빌리티), `011070.KS`(LG이노텍), `003550.KS`(LG), `373220.KS`(LG에너지솔루션), `035420.KS`(NAVER), `035720.KS`(카카오), `000720.KS`(현대건설), `034730.KS`(SK), `096770.KS`(SK이노베이션)

> ⚠️ **한국 종목(`.KS`)은 원화(₩) 네이티브**: `financials`(revenue·opIncome·cfInvesting·cfFinancing)와 `debtAmt`(totalAssets·cash·totalLiab·equity 등) 금액은 **조원(조 KRW) 숫자**로 넣는다(미국의 $B 자리에 조원). 화면은 한국종목에 환율변환·통화토글을 적용하지 않고 원화로 그대로 표시한다. `shares`=발행주식수(십억 주), `per`·`debtRatio`·`opMargin`은 미국과 동일. **한국종목은 SNS 없음**(stock-news에서 `sns:[]`). 미확인 값은 `"확인 필요"`/`null`.
> SK ON(SK온)은 **미상장(IPO 미완, SK이노베이션 자회사)** → 대상 아님.
> 📏 **한국 종목도 미국과 동일하게 `financials.annual` 6개(FY2020~)·`quarterly` 8개를 채운다** — 과거는 DART 공시·사업보고서에서 확보(조원 네이티브). 재확보 어려운 회차는 **기존 `stocks-info.js` 값을 보존하고 배열을 축소하지 마라**(짧아지면 안 됨). LG에너지솔루션 등 상장 전 미존재 연도는 `null`.

**티커별 수집 항목:**
- `ceo` : CEO 이름(한글·영문)
- `investors` : 주요 기관투자자 3~5곳(가능하면 지분%). 문자열 배열 권장(예 `"뱅가드 ~9%"`)
- `per` : 최근 PER(배). 적자면 `"적자/미확인"`
- `shares` : **총 발행주식수(십억 주)** 숫자 — 시가총액(주가×shares)을 라이브로 계산하는 데 쓴다.
  알파벳·메타는 전 클래스 합계, 엔비디아는 액면분할 반영. (참고용 `mktCapRef` 문자열도 가능)
  ⚠️ **`shares`는 최신으로 유지·갱신하라 — 주식 카드 시가총액 내림차순 정렬의 입력이다**(정렬은 결정론 코드가 담당, AI는 shares 신선도만 책임). 자사주 매입·증자·분할 시 갱신.
- `debt` : `{ "shortTerm": "...", "longTerm": "..." }` — 단기·장기 부채 규모(값+기준, 참고용)
- `debtRatio` : `{ "totalRatio": 숫자(%), "shortRatio": 숫자(%), "longRatio": 숫자(%), "basis": "..." }`
  — **부채비율(부채/자기자본 %)**. total=부채총계, short=유동부채, long=비유동부채 각각 ÷ 자기자본 × 100.
  basis에 기준시점 명시. 자기자본 음수면 basis에 표기.
- `debtAmt` : `{ "totalAssets": $B, "currentAssets": $B, "nonCurrentAssets": $B, "cash": $B, "totalLiab": $B, "currentLiab": $B, "nonCurrentLiab": $B, "equity": $B, "basis": "..." }`
  — **자산·부채 금액**(십억 달러 숫자). 화면에서 원/달러 변환해 표시하므로 반드시 숫자로.
  `cash`=현금및현금성자산(+단기투자 포함 가능, basis에 명시), `currentAssets`=유동자산, `nonCurrentAssets`=비유동자산.
- `financials.annual` : 최근 **6개 회계연도** 각각(과거→최근 오름차순)
  `{ period, revenue, opIncome, opMargin, cfInvesting, cfFinancing }`
- `financials.quarterly` : 최근 **8개 분기** 같은 필드
  - 단위 통일: 매출·영업이익·현금흐름 = **$B(십억 달러) 숫자**, 영업이익률·부채비율 = **%**. 유출 현금흐름은 음수.
- `events` : 다가오는 실적발표·주요 발표 2~4개 `{ date(YYYY-MM-DD), title, detail }`
  ※ **`news` 는 만들지 않는다 → stock-news 소관.** (events=실적발표 일정은 여기 포함)

**규칙:** 추측·창작 금지. 확인 안 되는 값은 `"확인 필요"` 또는 `null`(빈칸 금지).
회계연도 마감월이 다른 회사(MS 6월, 엔비디아 1월 등)는 FY 라벨을 실제 분기말과 대조해 정확히.
저장 형식은 기존 `stocks-info.js` 를 그대로 따른다(키=티커, **`news` 제외**). 조사·검토가 끝나면 파일을 덮어쓰면 된다.

---
