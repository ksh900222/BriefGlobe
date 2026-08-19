# stock-news — 종목 뉴스·SNS → `stocks-news.js`

> 🕐 **갱신 주기: 매시간.** 뉴스·SNS는 빠르게 바뀌므로 매 사이클 갱신. (재무는 stock-fin 소관, 하루 1회)

stock-fin와 같은 **30개 티커**(미국 19 + 한국 11)의 최신 뉴스·SNS를 조사해 `stocks-news.js` 를 만든다.
**한국 종목(`.KS`)은 `news` 만 채우고 `sns` 는 항상 `[]`**(공식 X 계정 표에 미포함 → SNS 인용 안 함).

**⭐ 먼저 이미 수집·번역된 뉴스(`news-data.js`)에서 종목 관련 기사를 재사용한다 — 낭비 없이.** 아래로 추출(그대로 실행):
```bash
python3 -c "
import json
d=open('news-data.js',encoding='utf-8').read()
j=json.loads(d[d.index('['):d.rindex(']')+1])
KW={'AAPL':['애플','apple'],'MSFT':['마이크로소프트','microsoft'],'GOOGL':['구글','알파벳','google','alphabet'],'AMZN':['아마존','amazon'],'NVDA':['엔비디아','nvidia'],'META':['메타','meta','페이스북'],'TSLA':['테슬라','tesla'],'SPCX':['스페이스x','spacex','스타링크','starlink'],'PLTR':['팔란티어','palantir'],'SMR':['뉴스케일','nuscale'],'LCID':['루시드','lucid'],'PSNY':['폴스타','polestar'],'BRK-A':['버크셔','berkshire','버핏','buffett'],'BRK-B':['버크셔','berkshire','버핏','buffett'],'XE':['엑스에너지','x-energy','x energy'],'OKLO':['오클로','oklo'],'PFE':['화이자','pfizer'],'MRNA':['모더나','moderna'],'BNTX':['바이오엔테크','biontech'],'005930.KS':['삼성전자','samsung'],'000660.KS':['sk하이닉스','하이닉스','hynix'],'034020.KS':['두산에너빌리티','두산','doosan'],'011070.KS':['lg이노텍','이노텍','innotek'],'003550.KS':['(주)lg','엘지','lg corp'],'373220.KS':['lg에너지솔루션','엔솔','energy solution'],'035420.KS':['네이버','naver'],'035720.KS':['카카오','kakao'],'000720.KS':['현대건설','hyundai e&c'],'034730.KS':['sk(주)','sk이노','sk그룹'],'096770.KS':['sk이노베이션','sk innovation']}
days=sorted({x['date'] for x in j})[-3:]
for tk,kws in KW.items():
    hits=[x for x in j if x['date'] in days and any(k in (x['title']+x.get('summary','')).lower() for k in kws)]
    print(f'== {tk} ({len(hits)}) ==')
    for x in hits[:6]: print(f\"  {x['date']} {x['title']} | {x.get('url','')}\")
"
```
- 위 결과는 **이미 한국어 번역·URL이 있으니 그대로 해당 종목 `news` 에 재사용**(중복은 하나만).
- 재사용분으로 6~10개가 안 차는 종목만 **부족분을 실시간 검색으로 보충**한다. (SNS 는 아래 규칙대로 별도)

**뉴스와 SNS는 분리**한다. 형식(티커당 `news`·`sns` 두 배열):
```js
const STOCKS_NEWS = {
  "AAPL": {
    "news": [ { "date": "...", "title": "...", "source": "매체명 | https://원문" }, ... ],
    "sns":  [ { "date": "...", "title": "...", "source": "X·@tim_cook(공식) | https://게시물" }, ... ]
  },
  "MSFT": { "news": [...], "sns": [...] }, ...
};
```

**`news` (일반 뉴스) — 티커당 6~10개**, 최근 **7일 이내**:
- **주가 변동 사유·기업 이슈** 우선, 최근순. **공식 SNS는 여기 넣지 말 것**(→ `sns`).
- **`source` 에 반드시 원문 URL 포함** — `"매체명 | https://원문링크"`.

**`sns` (공식 X 게시물) — 티커당 0~4개**, 최근 **2일(48시간) 이내**만:
- 아래 표의 **공식 계정** 최근 게시물 중 시장·사업 관련만. **없으면 빈 배열 `[]`** (억지로 넣지 말 것).
- `source` = `"X·@handle(공식) | https://게시물링크"`, `title`=발언 요지(중립), `date`=게시일.
- 2일보다 오래된 게시물은 제외.

**✅ 종목별 공식 X 계정 (2026-07 검증 — 매 회차 이 계정들의 최근 2일 게시물을 확인):**

| 티커 | 회사 계정 | CEO 개인 계정 |
|---|---|---|
| AAPL | @Apple | @tim_cook (활발) |
| MSFT | @Microsoft | @satyanadella (활발) |
| GOOGL | @Google | @sundarpichai (활발) |
| AMZN | @amazon | @ajassy (활발) |
| NVDA | @nvidia + @nvidianewsroom(공식 뉴스룸) | **없음 → 회사계정만** (⚠️ @jensenhuang 은 사칭 가능, 금지) |
| META | @Meta | **회사계정 위주** (@finkd 는 저커버그 진짜지만 휴면. ⚠️ @marzuckerberg 는 패러디, 절대 금지) |
| TSLA | @Tesla 본계정 + 공식 제휴: @Tesla_AI(자율주행·FSD) · @Tesla_Optimus(로봇) · @TeslaCharging(슈퍼차저) · @teslaenergy(에너지) · @cybertruck · @tesla_na(북미) | @elonmusk (활발) |
| SPCX | @SpaceX 본계정 + 공식 제휴: @Starlink(위성인터넷) · @SpaceXAI(舊 @xai — 2026.7 xAI→SpaceXAI 리브랜딩) · @grok(SpaceXAI의 Grok AI, 공식 골드뱃지) | @elonmusk (활발) |
| PLTR | @PalantirTech | **없음 → 회사계정만** |
| SMR | @NuScale_Power | **없음 → 회사계정만** |
| PFE | @Pfizer (활발) | @AlbertBourla (CEO, 활발) |
| MRNA | @moderna_tx | **회사계정 위주** |
| BNTX | @BioNTech_Group | **회사계정 위주** |

- 매 회차 위 계정들의 **최근 게시물**을 확인해 시장·사업 관련 발언이 있으면 종목당 1~2개 포함. **없으면 억지로 넣지 말고 생략.**
- 위 표에 없는 개인계정을 CEO 계정이라 단정하지 말 것. 표의 **회사 계정은 항상 안전**, 개인 계정은 표에 명시된 것만.
- ⚠️ **PFE·MRNA·BNTX(2026-07-30 추가)**: 공식 X 핸들(@moderna_tx·@BioNTech_Group 등)은 **첫 사용 시 실제 인증 계정인지 확인**하고, 불확실하면 회사계정만 쓰거나 `sns:[]`로 둔다(사칭 주의).
- **TSLA·SPCX 제휴계정은 모두 해당사 공식**이므로 인용 가능. `source` 에 어느 계정인지 표기(예: `"X·@Starlink(SpaceX 공식) | https://..."`, `"X·@grok(SpaceXAI 공식) | https://..."`).
- ⚠️ **제외**: 팬·오너클럽(@teslaownersSV, Tesla Owners of ~ 등)과 **제3자 뉴스·논평 계정**(@Teslarati 등)은 비공식 → 넣지 마라.
- ✅ **단, 회사가 직접 운영하는 공식 뉴스룸 계정은 포함 가능**(예: NVDA @nvidianewsroom, 그 외 회사 공식 newsroom). 회사 운영이 **확실할 때만**.

**⚠️ CEO·임원 SNS 인용 규칙 (오정보 방지 — 반드시 지킬 것):**
- **인증된 공식 계정만.** 사칭·패러디·익명·미인증 계정 절대 금지. 불확실하면 **넣지 마라.**
- **원문 URL + 게시 날짜** 필수. 확인 안 되면 제외.
- 삭제·수정·반어·농담 가능성 — **맥락 왜곡 금지**, 요지는 중립적으로.
- SNS는 소문·시세조작(pump-and-dump)의 통로 — IR·공시로 **교차확인 안 된 시세성 주장은 '사실'로 쓰지 마라.**
- 실존 인물이 **실제로 한 발언만.** 하지 않은 말 금지. 공식 IR이 있으면 우선.

---
