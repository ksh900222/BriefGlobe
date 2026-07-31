/* ============================================================
   국가 프로필 (경제력 Top50 대응)
   ------------------------------------------------------------
   항목: 주요 인종·비율, 통화, 문화, 언어, 기후, 교육수준,
         주요 수출품, 주요 수입품, 산업 취업 비중(1·2·3차)
   프로세스:
     1) 조사 에이전트 A (1–25위) / B (26–50위) 독립 조사
     2) 적대적 검수 에이전트 A′ / B′ 가 상호 반박·수정
   출처 계열: CIA World Factbook, World Bank/ILO, OECD, 각국 센서스 근사
   ⚠️ 교육·비교용 큐레이션. 연도·정의(거주인구/국민, 문해율·고등교육 지표) 편차.
      인종·민족 분류는 국가마다 달라 직접 비교에 주의.
   감사 로그: _adversarial_1_25.json, _adversarial_26_50.json
   ============================================================ */

const COUNTRY_PROFILES = [
  {
    "id": "usa",
    "country": "미국",
    "ethnicity": [
      {
        "name": "비히스패닉 백인",
        "pct": 58
      },
      {
        "name": "히스패닉",
        "pct": 19
      },
      {
        "name": "흑인",
        "pct": 13
      },
      {
        "name": "아시아계",
        "pct": 6
      },
      {
        "name": "기타·혼혈 등",
        "pct": 4
      }
    ],
    "currency": {
      "code": "USD",
      "name": "미국 달러"
    },
    "culture": "기독교(개신교·가톨릭) 전통이 강하고 세속·다문화 사회가 공존한다. 이민 국가로서 개인주의·자유시장·법치 가치가 사회 규범의 중심이며, 건국 이후 연방제와 수정헌법이 정치·문화 정체성을 형성했다. 대중문화·기술·고등교육이 세계적으로 영향력이 크다.",
    "languages": [
      {
        "name": "영어",
        "official": true,
        "note": "사실상 공용어·연방 업무 언어"
      },
      {
        "name": "스페인어",
        "official": false,
        "note": "최대 소수 언어"
      }
    ],
    "climate": "대륙이 넓어 쾨펜 기후가 다양하다. 동부·중부는 습윤 대륙성·아열대기후, 서부 내륙은 건조·반건조, 서해안은 지중해성·해양성 기후가 혼재한다.",
    "education": {
      "literacy": 99,
      "tertiary": 50,
      "note": "성인 문해율 사실상 보편. 25–64세 고등교육 이수 약 50%(OECD 근사)."
    },
    "exports": [
      "석유제품",
      "항공기·우주",
      "자동차·부품",
      "반도체·전자",
      "의약품",
      "기계"
    ],
    "imports": [
      "전자제품",
      "자동차",
      "원유",
      "의약품",
      "기계",
      "통신기기"
    ],
    "sectors": {
      "primary": 1.4,
      "secondary": 19.5,
      "tertiary": 79.1,
      "note": "취업 비중% 근사(ILO/World Bank 2022–23). 서비스 중심."
    },
    "sources": [
      "CIA World Factbook",
      "US Census Bureau",
      "World Bank/ILO",
      "OECD"
    ],
    "confidence": "high"
  },
  {
    "id": "china",
    "country": "중국",
    "ethnicity": [
      {
        "name": "한족",
        "pct": 91
      },
      {
        "name": "소수민족 합계",
        "pct": 9
      }
    ],
    "currency": {
      "code": "CNY",
      "name": "중국 위안(런민비)"
    },
    "culture": "유교·도교·불교 전통이 세속 사회주의 체제와 공존한다. 한족 중심의 단일 문명 정체성이 강하고, 55개 공식 소수민족이 인정된다. 개혁개방 이후 도시화·교육 확대로 사회 구조가 급변했다.",
    "languages": [
      {
        "name": "표준 중국어(보통화)",
        "official": true,
        "note": "국가 공용어"
      },
      {
        "name": "광둥어·우어·민어 등",
        "official": false,
        "note": "지역 방언·언어군"
      }
    ],
    "climate": "광활한 영토로 기후 유형이 다양하다. 동부는 온대·아열대 몬순, 북부는 건조·대륙성, 서부 고원·사막은 한랭·건조 기후가 우세하다.",
    "education": {
      "literacy": 97,
      "tertiary": 19,
      "note": "성인 문해율 약 97%. 25–64세 고등교육 이수 약 18–20%(OECD/UNESCO 근사)."
    },
    "exports": [
      "전자기기",
      "기계",
      "가구·소비재",
      "섬유·의류",
      "플라스틱",
      "자동차·부품"
    ],
    "imports": [
      "원유·가스",
      "반도체·칩",
      "철광·원자재",
      "대두 등 농산물",
      "기계",
      "자동차"
    ],
    "sectors": {
      "primary": 22,
      "secondary": 28,
      "tertiary": 50,
      "note": "취업 비중% 근사(ILO 2023 농업 약 22%). 제조 비중 여전히 큼."
    },
    "sources": [
      "CIA World Factbook",
      "World Bank/ILO",
      "중국 통계 공표 요약"
    ],
    "confidence": "high"
  },
  {
    "id": "germany",
    "country": "독일",
    "ethnicity": [
      {
        "name": "이민 배경 없음(독일계 등)",
        "pct": 74
      },
      {
        "name": "이민 배경(터키·동유럽·중동·아프리카 등)",
        "pct": 26
      }
    ],
    "currency": {
      "code": "EUR",
      "name": "유로"
    },
    "culture": "개신교·가톨릭 전통과 강한 세속화가 공존하는 복지국가다. 전후 재건·EU 통합 속에서 법치·산업 기술·직업교육(듀얼 시스템)이 사회 기반을 이룬다. 최근 이민으로 다문화화가 진행 중이다.",
    "languages": [
      {
        "name": "독일어",
        "official": true,
        "note": "공용어"
      }
    ],
    "climate": "대부분 온대 해양성~습윤 대륙성 기후(Cfb/Dfb). 서부는 온화·다습, 동부는 대륙성 특성이 강해 겨울이 더 춥다.",
    "education": {
      "literacy": 99,
      "tertiary": 33,
      "note": "문해율 사실상 보편. 고등교육 이수 약 30%대이나 직업교육 비중이 높음(OECD)."
    },
    "exports": [
      "자동차·부품",
      "기계",
      "화학·의약품",
      "전기기기",
      "항공기 부품"
    ],
    "imports": [
      "기계·전자기기",
      "자동차·부품",
      "원유·가스",
      "화학제품",
      "의약품"
    ],
    "sectors": {
      "primary": 1.2,
      "secondary": 27,
      "tertiary": 71.8,
      "note": "취업 비중% 근사(2022–23). 제조업 취업 비중이 선진국 중 높은 편."
    },
    "sources": [
      "CIA World Factbook",
      "Destatis",
      "World Bank/ILO",
      "OECD"
    ],
    "confidence": "high"
  },
  {
    "id": "india",
    "country": "인도",
    "ethnicity": [
      {
        "name": "인도아리아계",
        "pct": 72
      },
      {
        "name": "드라비다계",
        "pct": 25
      },
      {
        "name": "기타(몽골계·부족 등)",
        "pct": 3
      }
    ],
    "currency": {
      "code": "INR",
      "name": "인도 루피"
    },
    "culture": "힌두교가 다수이며 이슬람·기독교·시크교 등 다종교 사회다. 카스트·지역·언어 다양성이 일상과 정치에 깊게 남아 있고, 독립 이후 세속 민주주의 헌법 체제를 유지한다. IT·영화·요가가 현대 소프트파워를 상징한다.",
    "languages": [
      {
        "name": "힌디어",
        "official": true,
        "note": "연방 공용어"
      },
      {
        "name": "영어",
        "official": true,
        "note": "부공용어·행정·비즈니스"
      },
      {
        "name": "벵골어·텔루구어 등",
        "official": false,
        "note": "헌법 지정 22개 언어 등 다수"
      }
    ],
    "climate": "대부분 열대 몬순 기후. 북부 히말라야 산지는 한랭, 서북 타르는 건조, 남부는 열대 습윤 기후가 우세하다.",
    "education": {
      "literacy": 77,
      "tertiary": 13,
      "note": "성인 문해율 약 74–78%(성별 격차). 고등교육 이수 약 13%(OECD 2022 근사)."
    },
    "exports": [
      "석유제품",
      "의약품·화학",
      "보석·귀금속",
      "기계·자동차",
      "섬유·의류",
      "IT 서비스(상품 외)"
    ],
    "imports": [
      "원유",
      "금·귀금속",
      "전자기기",
      "기계",
      "석탄",
      "화학제품"
    ],
    "sectors": {
      "primary": 43.5,
      "secondary": 25.5,
      "tertiary": 31,
      "note": "취업 비중% 근사(ILO 2023). 농업 취업 비중이 여전히 매우 높음."
    },
    "sources": [
      "CIA World Factbook",
      "World Bank/ILO",
      "인도 인구조사 요약"
    ],
    "confidence": "medium"
  },
  {
    "id": "japan",
    "country": "일본",
    "ethnicity": [
      {
        "name": "야마토(일본인)",
        "pct": 97
      },
      {
        "name": "외국인 거주자·재일 한국·중국계 등",
        "pct": 2.5
      },
      {
        "name": "아이누·기타",
        "pct": 0.5
      }
    ],
    "currency": {
      "code": "JPY",
      "name": "일본 엔"
    },
    "culture": "신도·불교가 생활 의례에 깊게 녹아 있고 세속화가 진행된 고동질 사회다. 전후 평화헌법·집단 조화·장인 정신이 사회 규범을 이루며, 고령화·저출산이 문화·복지 의제를 지배한다.",
    "languages": [
      {
        "name": "일본어",
        "official": true,
        "note": "사실상 공용어(헌법·법률상 명시 없음)"
      }
    ],
    "climate": "대부분 온대 습윤 기후. 태평양 측은 여름 고온다습·겨울 건조, 동해 측은 겨울 강설이 많다. 북부(홋카이도)는 냉대, 남부 난세이는 아열대성이다.",
    "education": {
      "literacy": 99,
      "tertiary": 56,
      "note": "문해율 사실상 보편. 청년층 고등교육 이수 비율이 OECD 상위권."
    },
    "exports": [
      "자동차",
      "반도체·전자부품",
      "기계",
      "철강",
      "화학제품",
      "광학기기"
    ],
    "imports": [
      "원유·LNG",
      "석탄",
      "전자기기",
      "의약품",
      "의류",
      "식료품"
    ],
    "sectors": {
      "primary": 3,
      "secondary": 24,
      "tertiary": 73,
      "note": "취업 비중% 근사(ILO 2023). 서비스·제조 중심."
    },
    "sources": [
      "CIA World Factbook",
      "총무성 통계",
      "World Bank/ILO",
      "OECD"
    ],
    "confidence": "high"
  },
  {
    "id": "uk",
    "country": "영국",
    "ethnicity": [
      {
        "name": "백인(영국·아일랜드 등)",
        "pct": 82
      },
      {
        "name": "아시아계",
        "pct": 9
      },
      {
        "name": "흑인",
        "pct": 4
      },
      {
        "name": "혼혈·기타",
        "pct": 5
      }
    ],
    "currency": {
      "code": "GBP",
      "name": "영국 파운드"
    },
    "culture": "성공회·기독교 전통과 강한 세속·다문화 사회가 공존한다. 의회 민주주의·보통법·산업혁명의 유산이 정체성 핵심이며, 브렉시트 이후 유럽과의 관계가 재편되고 있다. 영연방·영어 문화권의 중심이다.",
    "languages": [
      {
        "name": "영어",
        "official": true,
        "note": "사실상 공용어"
      },
      {
        "name": "웨일스어 등",
        "official": true,
        "note": "웨일스 공용어 등 지역 공인 언어"
      }
    ],
    "climate": "온대 해양성 기후(Cfb). 연중 온화하고 강수가 비교적 고르며, 스코틀랜드 고지·북부는 더 서늘하고 습하다.",
    "education": {
      "literacy": 99,
      "tertiary": 51,
      "note": "문해율 사실상 보편. 성인 고등교육 이수 약 50%대(OECD)."
    },
    "exports": [
      "기계·자동차",
      "의약품",
      "석유·가스",
      "항공기 부품",
      "금융·서비스(상품 외)",
      "귀금속"
    ],
    "imports": [
      "기계·자동차",
      "전자기기",
      "의약품",
      "식료품",
      "의류",
      "원유"
    ],
    "sectors": {
      "primary": 1,
      "secondary": 18,
      "tertiary": 81,
      "note": "취업 비중% 근사(2022–23). 서비스·금융 비중 극대."
    },
    "sources": [
      "CIA World Factbook",
      "ONS",
      "World Bank/ILO",
      "OECD"
    ],
    "confidence": "high"
  },
  {
    "id": "france",
    "country": "프랑스",
    "ethnicity": [
      {
        "name": "프랑스계 유럽인",
        "pct": 85
      },
      {
        "name": "북아프리카·아프리카계 등",
        "pct": 10
      },
      {
        "name": "기타",
        "pct": 5
      }
    ],
    "currency": {
      "code": "EUR",
      "name": "유로"
    },
    "culture": "가톨릭 전통과 라이시테(정교분리) 세속주의가 공존하는 공화국이다. 혁명 이후 자유·평등·박애와 중앙집권 국가 모델이 정체성 핵심이며, 문화·미식·패션·원자력 산업이 소프트파워를 이룬다. 공식 인종 통계를 수집하지 않아 민족 구성은 추정치다.",
    "languages": [
      {
        "name": "프랑스어",
        "official": true,
        "note": "공용어"
      }
    ],
    "climate": "서부는 온대 해양성, 남부는 지중해성(Csa/Csb), 중동부 내륙은 대륙성 특성이 나타난다. 알프스·피레네는 산지 기후다.",
    "education": {
      "literacy": 99,
      "tertiary": 42,
      "note": "문해율 사실상 보편. 고등교육 이수 OECD 평균 이상."
    },
    "exports": [
      "항공기",
      "의약품·화학",
      "자동차",
      "와인·농식품",
      "향수·럭셔리",
      "기계"
    ],
    "imports": [
      "기계·자동차",
      "원유·가스",
      "전자기기",
      "화학제품",
      "의류"
    ],
    "sectors": {
      "primary": 2.5,
      "secondary": 20,
      "tertiary": 77.5,
      "note": "취업 비중% 근사(ILO 2023). 서비스 중심·농업 GDP 비중은 작으나 수출 강점."
    },
    "sources": [
      "CIA World Factbook",
      "INSEE",
      "World Bank/ILO",
      "OECD"
    ],
    "confidence": "medium"
  },
  {
    "id": "italy",
    "country": "이탈리아",
    "ethnicity": [
      {
        "name": "이탈리아인",
        "pct": 92
      },
      {
        "name": "기타 유럽·이민",
        "pct": 8
      }
    ],
    "currency": {
      "code": "EUR",
      "name": "유로"
    },
    "culture": "가톨릭 전통이 깊고 지역(북·남) 정체성이 강하다. 로마 제국·르네상스·도시국가 유산이 예술·패션·미식 문화의 뿌리이며, 가족 중심 사회와 중소 제조 클러스터가 특징이다.",
    "languages": [
      {
        "name": "이탈리아어",
        "official": true,
        "note": "공용어"
      },
      {
        "name": "독일어·프랑스어 등",
        "official": false,
        "note": "일부 자치지역 공인"
      }
    ],
    "climate": "대부분 지중해성 기후. 북부 포 평원은 습윤 아열대·대륙성, 알프스는 산지 기후, 남부·섬은 전형적인 건조 여름 지중해성이다.",
    "education": {
      "literacy": 99,
      "tertiary": 20,
      "note": "문해율 보편. 고등교육 이수는 OECD 하위권(약 20%)."
    },
    "exports": [
      "기계",
      "자동차·부품",
      "패션·의류·가죽",
      "의약품",
      "식품·와인",
      "가구"
    ],
    "imports": [
      "원유·가스",
      "자동차",
      "화학제품",
      "전자기기",
      "금속",
      "의약품"
    ],
    "sectors": {
      "primary": 3.6,
      "secondary": 26,
      "tertiary": 70.4,
      "note": "취업 비중% 근사(2022–23). 제조·관광 강점."
    },
    "sources": [
      "CIA World Factbook",
      "Istat",
      "World Bank/ILO",
      "OECD"
    ],
    "confidence": "high"
  },
  {
    "id": "brazil",
    "country": "브라질",
    "ethnicity": [
      {
        "name": "백인",
        "pct": 43
      },
      {
        "name": "파르두(혼혈)",
        "pct": 45
      },
      {
        "name": "흑인",
        "pct": 10
      },
      {
        "name": "아시아·원주민 등",
        "pct": 2
      }
    ],
    "currency": {
      "code": "BRL",
      "name": "브라질 헤알"
    },
    "culture": "포르투갈 식민·가톨릭 전통과 아프리카·원주민 문화가 혼합된 다인종 사회다. 삼바·축구·카니발이 국가 상징이며, 포르투갈어권 최대 국가로서 남미 지역 영향력이 크다. 빈부 격차와 지역 불균형이 사회 이슈다.",
    "languages": [
      {
        "name": "포르투갈어",
        "official": true,
        "note": "공용어"
      }
    ],
    "climate": "대부분 열대 기후. 아마존은 열대 우림, 중부는 사바나(세라도), 남부는 아열대·온대 습윤 기후가 나타난다.",
    "education": {
      "literacy": 94,
      "tertiary": 21,
      "note": "성인 문해율 약 93–95%. 고등교육 이수 약 20%대."
    },
    "exports": [
      "대두",
      "철광석",
      "원유",
      "육류",
      "사탕수수·설탕",
      "커피"
    ],
    "imports": [
      "기계",
      "전자기기",
      "화학·비료",
      "석유제품",
      "자동차 부품"
    ],
    "sectors": {
      "primary": 8.2,
      "secondary": 20,
      "tertiary": 71.8,
      "note": "취업 비중% 근사(ILO 2023). 1차 산업 수출 비중이 GDP 기여보다 큼."
    },
    "sources": [
      "CIA World Factbook",
      "IBGE",
      "World Bank/ILO",
      "OEC"
    ],
    "confidence": "high"
  },
  {
    "id": "canada",
    "country": "캐나다",
    "ethnicity": [
      {
        "name": "유럽계(영국·프랑스 등)",
        "pct": 70
      },
      {
        "name": "아시아계",
        "pct": 18
      },
      {
        "name": "원주민",
        "pct": 5
      },
      {
        "name": "흑인·기타",
        "pct": 7
      }
    ],
    "currency": {
      "code": "CAD",
      "name": "캐나다 달러"
    },
    "culture": "영국·프랑스 이중 식민 유산과 다문화 정책이 공존한다. 세속 복지국가이며 영어·불어 이중 언어 체제가 정체성 핵심이다. 원주민 권리·이민 통합이 사회 의제이며 미국과 밀접한 경제·문화 관계를 유지한다.",
    "languages": [
      {
        "name": "영어",
        "official": true,
        "note": "연방 공용어"
      },
      {
        "name": "프랑스어",
        "official": true,
        "note": "연방 공용어·퀘벡 주 중심"
      }
    ],
    "climate": "대부분 냉대·아한대 기후. 남부 인구 벨트는 습윤 대륙성, 서해안(밴쿠버)은 온대 해양성, 북극 지역은 툰드라·극지 기후다.",
    "education": {
      "literacy": 99,
      "tertiary": 63,
      "note": "문해율 보편. 고등교육 이수 OECD 최상위권(약 60%+)."
    },
    "exports": [
      "원유·에너지",
      "자동차·부품",
      "목재·임산물",
      "광물·금속",
      "기계",
      "농산물"
    ],
    "imports": [
      "자동차·부품",
      "기계",
      "전자기기",
      "석유제품",
      "의약품",
      "플라스틱"
    ],
    "sectors": {
      "primary": 1.5,
      "secondary": 19.5,
      "tertiary": 79,
      "note": "취업 비중% 근사(2022–23). 자원 수출 강국이나 취업은 서비스 중심."
    },
    "sources": [
      "CIA World Factbook",
      "Statistics Canada",
      "World Bank/ILO",
      "OECD"
    ],
    "confidence": "high"
  },
  {
    "id": "russia",
    "country": "러시아",
    "ethnicity": [
      {
        "name": "러시아인",
        "pct": 72
      },
      {
        "name": "타타르",
        "pct": 3
      },
      {
        "name": "우크라이나계 등",
        "pct": 2
      },
      {
        "name": "기타 민족·미상",
        "pct": 23
      }
    ],
    "currency": {
      "code": "RUB",
      "name": "러시아 루블"
    },
    "culture": "동방 정교회 전통과 소비에트 유산이 공존하는 다민족 연방이다. 슬라브 문화·문학·과학 전통이 강하고, 국가 중심 정치 문화가 사회에 깊게 스며 있다. 2021 인구센서스 응답 공백으로 민족 비율 해석에 주의가 필요하다.",
    "languages": [
      {
        "name": "러시아어",
        "official": true,
        "note": "연방 공용어"
      },
      {
        "name": "타타르어 등 지역 언어",
        "official": false,
        "note": "공화국별 공인 언어 다수"
      }
    ],
    "climate": "대부분 냉대 대륙성·아한대 기후. 시베리아는 극심한 겨울 한랭, 흑해 연안 일부는 아열대성, 극동은 몬순 영향이 있다.",
    "education": {
      "literacy": 100,
      "tertiary": 57,
      "note": "문해율 사실상 100%. 고등교육 이수 비율 높은 편(구소련 유산)."
    },
    "exports": [
      "원유",
      "천연가스",
      "석탄",
      "금속·철강",
      "곡물",
      "무기·기계"
    ],
    "imports": [
      "기계",
      "의약품",
      "자동차",
      "전자기기",
      "소비재",
      "화학제품"
    ],
    "sectors": {
      "primary": 5.7,
      "secondary": 26.5,
      "tertiary": 67.8,
      "note": "취업 비중% 근사(ILO 2023). 에너지 수출 의존·전시경제로 통계 불확실성."
    },
    "sources": [
      "CIA World Factbook",
      "Rosstat 요약",
      "World Bank/ILO"
    ],
    "confidence": "medium"
  },
  {
    "id": "mexico",
    "country": "멕시코",
    "ethnicity": [
      {
        "name": "메스티소",
        "pct": 62
      },
      {
        "name": "원주민",
        "pct": 21
      },
      {
        "name": "백인",
        "pct": 10
      },
      {
        "name": "기타",
        "pct": 7
      }
    ],
    "currency": {
      "code": "MXN",
      "name": "멕시코 페소"
    },
    "culture": "가톨릭과 원주민·스페인 식민 유산이 융합된 메스티소 문화가 중심이다. 독립·혁명 역사가 국가 신화에 자리하며, 미국과의 국경 경제·이주가 현대 사회를 규정한다. 민족 분류는 자가식별·언어 기준에 따라 편차가 크다.",
    "languages": [
      {
        "name": "스페인어",
        "official": true,
        "note": "사실상 공용어"
      },
      {
        "name": "나와틀어 등 원주민 언어",
        "official": true,
        "note": "헌법상 국어(국가언어)로 인정·다수 원주민 언어"
      }
    ],
    "climate": "대부분 아열대~열대. 중앙 고원은 온화, 북부는 건조·사막, 남동 유카탄·연안은 열대 습윤·우기가 뚜렷하다.",
    "education": {
      "literacy": 95,
      "tertiary": 21,
      "note": "성인 문해율 약 95%. 고등교육 이수 약 20–23%(OECD)."
    },
    "exports": [
      "자동차·부품",
      "전자기기",
      "기계",
      "의료기기",
      "원유",
      "농산물"
    ],
    "imports": [
      "전자기기·부품",
      "기계",
      "자동차 부품",
      "플라스틱",
      "석유제품",
      "곡물"
    ],
    "sectors": {
      "primary": 12,
      "secondary": 25,
      "tertiary": 63,
      "note": "취업 비중% 근사(ILO 2023). 제조(마킬라도라)·서비스 확대."
    },
    "sources": [
      "CIA World Factbook",
      "INEGI",
      "World Bank/ILO",
      "OECD"
    ],
    "confidence": "medium"
  },
  {
    "id": "skorea",
    "country": "대한민국",
    "ethnicity": [
      {
        "name": "한민족(한국인)",
        "pct": 95
      },
      {
        "name": "외국인·기타",
        "pct": 5
      }
    ],
    "currency": {
      "code": "KRW",
      "name": "대한민국 원"
    },
    "culture": "유교 전통과 급속 근대화가 공존하는 고동질 사회다. 불교·개신교·가톨릭이 주요 종교이며 세속화도 진행 중이다. 교육열·압축 성장·한류(K-pop·드라마)가 현대 정체성의 상징이다.",
    "languages": [
      {
        "name": "한국어",
        "official": true,
        "note": "공용어"
      }
    ],
    "climate": "온대 몬순 기후. 여름 고온다습·장마, 겨울 한랭건조가 뚜렷하며 남해안·제주는 상대적으로 온난하다.",
    "education": {
      "literacy": 99,
      "tertiary": 70,
      "note": "문해율 보편. 청년 고등교육 이수 세계 최상위권(OECD)."
    },
    "exports": [
      "반도체",
      "자동차",
      "석유화학",
      "선박",
      "디스플레이·전자기기",
      "배터리"
    ],
    "imports": [
      "원유·가스",
      "반도체 장비·소재",
      "기계",
      "석탄",
      "전자기기",
      "식료품"
    ],
    "sectors": {
      "primary": 5.3,
      "secondary": 24.5,
      "tertiary": 70.2,
      "note": "취업 비중% 근사(ILO 2023). 제조 수출 강국·서비스 취업 비중 확대."
    },
    "sources": [
      "CIA World Factbook",
      "통계청",
      "World Bank/ILO",
      "OECD"
    ],
    "confidence": "high"
  },
  {
    "id": "australia",
    "country": "호주",
    "ethnicity": [
      {
        "name": "유럽계(영·아일 등)",
        "pct": 57
      },
      {
        "name": "아시아계",
        "pct": 18
      },
      {
        "name": "기타·복합 출신 등",
        "pct": 22
      },
      {
        "name": "원주민(애보리진·토레스)",
        "pct": 3
      }
    ],
    "currency": {
      "code": "AUD",
      "name": "호주 달러"
    },
    "culture": "영국 식민 유산의 세속 민주주의·다문화 이민 사회다. 원주민 문화 인정과 화해가 국가 의제이며, 스포츠·야외 생활·자원 경제가 라이프스타일을 규정한다. 아시아·태평양 지향이 강화되고 있다.",
    "languages": [
      {
        "name": "영어",
        "official": true,
        "note": "사실상 공용어"
      }
    ],
    "climate": "대륙 대부분이 건조·반건조. 북부는 열대 몬순, 동남·서남 인구 밀집 지역은 온대 해양성·지중해성 기후가 우세하다.",
    "education": {
      "literacy": 99,
      "tertiary": 51,
      "note": "문해율 보편. 고등교육 이수 OECD 상위권."
    },
    "exports": [
      "철광석",
      "석탄",
      "천연가스(LNG)",
      "금",
      "육류·밀",
      "교육 서비스(상품 외)"
    ],
    "imports": [
      "자동차",
      "전자기기",
      "원유·석유제품",
      "기계",
      "의약품",
      "의류"
    ],
    "sectors": {
      "primary": 2.5,
      "secondary": 19,
      "tertiary": 78.5,
      "note": "취업 비중% 근사(2022–23). 광업 GDP 기여 크나 취업은 서비스 중심."
    },
    "sources": [
      "CIA World Factbook",
      "ABS",
      "World Bank/ILO",
      "OECD"
    ],
    "confidence": "high"
  },
  {
    "id": "spain",
    "country": "스페인",
    "ethnicity": [
      {
        "name": "스페인(카스티야 등)",
        "pct": 85
      },
      {
        "name": "기타 유럽·라틴아메리카 이민",
        "pct": 12
      },
      {
        "name": "북아프리카·기타",
        "pct": 3
      }
    ],
    "currency": {
      "code": "EUR",
      "name": "유로"
    },
    "culture": "가톨릭 전통과 지역 자치(카탈루냐·바스크 등) 정체성이 강하다. 이베리아 이슬람·레콩키스타·제국 유산이 문화에 남아 있고, 민주화 이후 EU 통합·관광·미식이 현대 이미지를 형성한다.",
    "languages": [
      {
        "name": "스페인어(카스티야어)",
        "official": true,
        "note": "국가 공용어"
      },
      {
        "name": "카탈루냐어·갈리시아어·바스크어",
        "official": true,
        "note": "자치지역 공동 공용어(카탈루냐·갈리시아·바스크)"
      }
    ],
    "climate": "대부분 지중해성 기후. 북부 대서양 연안은 해양성, 중부 메세타는 대륙성·건조, 남동은 반건조 특성이 나타난다.",
    "education": {
      "literacy": 99,
      "tertiary": 41,
      "note": "문해율 보편. 고등교육 이수 OECD 평균 수준."
    },
    "exports": [
      "자동차",
      "기계",
      "의약품",
      "농식품(과일·올리브유)",
      "의류",
      "석유제품"
    ],
    "imports": [
      "원유·가스",
      "자동차·부품",
      "의약품",
      "전자기기",
      "화학제품"
    ],
    "sectors": {
      "primary": 3.6,
      "secondary": 20,
      "tertiary": 76.4,
      "note": "취업 비중% 근사(ILO 2023). 관광·서비스 비중 큼."
    },
    "sources": [
      "CIA World Factbook",
      "INE",
      "World Bank/ILO",
      "OECD"
    ],
    "confidence": "high"
  },
  {
    "id": "indonesia",
    "country": "인도네시아",
    "ethnicity": [
      {
        "name": "자바족",
        "pct": 40
      },
      {
        "name": "순다족",
        "pct": 16
      },
      {
        "name": "말레이·바탁·마두라 등",
        "pct": 30
      },
      {
        "name": "기타 다수 민족",
        "pct": 14
      }
    ],
    "currency": {
      "code": "IDR",
      "name": "인도네시아 루피아"
    },
    "culture": "세계 최대 이슬람 인구 국가이나 공식 이념 판차실라로 다종교를 포용한다. 수백 민족·섬으로 이뤄진 군도 국가로 자바 중심성이 강하며, 힌두·불교 역사 유산(보로부두르 등)과 현대 민주주의가 공존한다.",
    "languages": [
      {
        "name": "인도네시아어",
        "official": true,
        "note": "공용어(바하사 인도네시아)"
      },
      {
        "name": "자바어 등",
        "official": false,
        "note": "지역 모어 다수"
      }
    ],
    "climate": "거의 전역이 열대 우림·열대 몬순 기후. 적도 부근으로 연중 고온다습하며 우기·건기 구분이 지역에 따라 뚜렷하다.",
    "education": {
      "literacy": 96,
      "tertiary": 13,
      "note": "성인 문해율 약 96%. 고등교육 이수 약 13%(OECD 파트너 근사)."
    },
    "exports": [
      "석탄",
      "팜유",
      "니켈·광물",
      "철강",
      "의류·신발",
      "전자기기"
    ],
    "imports": [
      "원유·석유제품",
      "기계",
      "전자기기",
      "플라스틱",
      "철강",
      "식료품"
    ],
    "sectors": {
      "primary": 28.8,
      "secondary": 22,
      "tertiary": 49.2,
      "note": "취업 비중% 근사(ILO 2023). 농업·비공식 취업 비중 높음."
    },
    "sources": [
      "CIA World Factbook",
      "BPS",
      "World Bank/ILO"
    ],
    "confidence": "high"
  },
  {
    "id": "netherlands",
    "country": "네덜란드",
    "ethnicity": [
      {
        "name": "네덜란드인",
        "pct": 75
      },
      {
        "name": "기타 유럽",
        "pct": 10
      },
      {
        "name": "터키·모로코·수리남 등",
        "pct": 10
      },
      {
        "name": "기타",
        "pct": 5
      }
    ],
    "currency": {
      "code": "EUR",
      "name": "유로"
    },
    "culture": "개신교·가톨릭 전통과 강한 세속·자유주의 사회다. 무역·항만·관용·합의 정치(폴더 모델)가 역사적 정체성이며, EU·국제법·물 관리 기술로 영향력을 유지한다.",
    "languages": [
      {
        "name": "네덜란드어",
        "official": true,
        "note": "공용어"
      },
      {
        "name": "프리지아어",
        "official": true,
        "note": "프리스란트 주 공용어(지역)"
      }
    ],
    "climate": "온대 해양성 기후(Cfb). 연중 온화·습윤하고 바람·강수가 비교적 고르며 극단 기온은 드물다.",
    "education": {
      "literacy": 99,
      "tertiary": 44,
      "note": "문해율 보편. 고등교육 이수·영어 구사율 높음(OECD)."
    },
    "exports": [
      "기계·전자기기",
      "석유제품",
      "화학·의약품",
      "농식품(화훼·낙농)",
      "반도체 장비"
    ],
    "imports": [
      "원유",
      "전자기기",
      "기계",
      "화학제품",
      "자동차",
      "의약품"
    ],
    "sectors": {
      "primary": 2,
      "secondary": 16.5,
      "tertiary": 81.5,
      "note": "취업 비중% 근사(2022–23). 로테르담 중계무역·서비스 중심."
    },
    "sources": [
      "CIA World Factbook",
      "CBS",
      "World Bank/ILO",
      "OECD"
    ],
    "confidence": "high"
  },
  {
    "id": "turkey",
    "country": "튀르키예",
    "ethnicity": [
      {
        "name": "터키인",
        "pct": 70
      },
      {
        "name": "쿠르드",
        "pct": 19
      },
      {
        "name": "기타(아랍·체르케스 등)",
        "pct": 11
      }
    ],
    "currency": {
      "code": "TRY",
      "name": "터키 리라"
    },
    "culture": "세속 공화국 전통 위에 이슬람 사회 규범이 강하게 남아 있는 국가다. 오스만 제국 유산과 유럽·중동을 잇는 지정학이 정체성을 규정하며, 쿠르드 문제·이민이 사회 의제다. 민족 통계는 공식 상세 인구조사가 제한적이다.",
    "languages": [
      {
        "name": "터키어",
        "official": true,
        "note": "공용어"
      },
      {
        "name": "쿠르드어",
        "official": false,
        "note": "주요 소수 언어"
      }
    ],
    "climate": "서·남은 지중해성, 내륙 아나톨리아는 대륙성·반건조, 북부 흑해 연안은 온대 해양성·다우 기후가 나타난다.",
    "education": {
      "literacy": 97,
      "tertiary": 25,
      "note": "성인 문해율 약 96–97%. 고등교육 이수 약 20%대 후반."
    },
    "exports": [
      "자동차·부품",
      "기계",
      "의류·섬유",
      "철강",
      "보석·귀금속",
      "농식품"
    ],
    "imports": [
      "원유·가스",
      "기계",
      "전자기기",
      "철강·금속",
      "화학제품",
      "금"
    ],
    "sectors": {
      "primary": 14.6,
      "secondary": 27,
      "tertiary": 58.4,
      "note": "취업 비중% 근사(ILO 2023). 농업 취업 비중이 유럽 대비 높음."
    },
    "sources": [
      "CIA World Factbook",
      "TurkStat",
      "World Bank/ILO"
    ],
    "confidence": "medium"
  },
  {
    "id": "saudi",
    "country": "사우디아라비아",
    "ethnicity": [
      {
        "name": "사우디 국민(아랍)",
        "pct": 58
      },
      {
        "name": "외국인 거주자",
        "pct": 42
      }
    ],
    "currency": {
      "code": "SAR",
      "name": "사우디 리얄"
    },
    "culture": "수니 이슬람(와하브 전통)과 왕정이 사회·법의 중심이다. 메카·메디나 성지 수호국으로서 이슬람권 위상이 크며, 비전 2030으로 경제 다각화·사회 개방이 추진 중이다. 인구의 약 42%가 외국인 거주자(대부분 이주노동자와 그 가족)다.",
    "languages": [
      {
        "name": "아랍어",
        "official": true,
        "note": "공용어"
      },
      {
        "name": "영어",
        "official": false,
        "note": "비즈니스·외국인 사회에서 널리 사용"
      }
    ],
    "climate": "대부분 열대·아열대 사막 기후(BWh). 내륙은 극심한 고온·건조, 홍해·페르시아만 연안은 습도가 높고, 남서 아시르는 산지로 상대적으로 선선하다.",
    "education": {
      "literacy": 98,
      "tertiary": 30,
      "note": "성인 문해율 급상승(약 97–98%). 고등교육 확대 중."
    },
    "exports": [
      "원유",
      "석유제품",
      "석유화학",
      "플라스틱",
      "천연가스 관련"
    ],
    "imports": [
      "기계",
      "자동차",
      "전자기기",
      "식료품",
      "의약품",
      "군수·장비"
    ],
    "sectors": {
      "primary": 2.8,
      "secondary": 24.5,
      "tertiary": 72.7,
      "note": "취업 비중% 근사(ILO 2023). 석유 GDP 비중과 취업 구조는 괴리. 외국인 노동 의존."
    },
    "sources": [
      "CIA World Factbook",
      "GAStat 2022 센서스",
      "World Bank/ILO"
    ],
    "confidence": "medium"
  },
  {
    "id": "switzerland",
    "country": "스위스",
    "ethnicity": [
      {
        "name": "스위스인(독일·프랑스·이탈리아계)",
        "pct": 70
      },
      {
        "name": "기타 유럽 이민",
        "pct": 22
      },
      {
        "name": "기타",
        "pct": 8
      }
    ],
    "currency": {
      "code": "CHF",
      "name": "스위스 프랑"
    },
    "culture": "연방·직접민주주의·영세 중립이 국가 정체성이다. 개신교·가톨릭 전통과 강한 세속·다언어 사회이며, 금융·정밀 제조·국제기구 유치로 알려져 있다. 칸톤 자치가 문화 다양성을 뒷받침한다.",
    "languages": [
      {
        "name": "독일어",
        "official": true,
        "note": "연방 공용어(다수)"
      },
      {
        "name": "프랑스어",
        "official": true,
        "note": "연방 공용어"
      },
      {
        "name": "이탈리아어",
        "official": true,
        "note": "연방 공용어"
      },
      {
        "name": "로만슈어",
        "official": true,
        "note": "연방 공용어(제한적)"
      }
    ],
    "climate": "온대·산지 기후. 고도에 따라 다양하며 알프스는 한랭 산지, 중부 고원은 온대 해양성~대륙성 혼합이다.",
    "education": {
      "literacy": 99,
      "tertiary": 44,
      "note": "문해율 보편. 이원 직업교육·고등교육 병행(OECD 상위)."
    },
    "exports": [
      "의약품·화학",
      "시계",
      "기계",
      "귀금속",
      "정밀기기",
      "초콜릿·치즈"
    ],
    "imports": [
      "의약품",
      "기계",
      "귀금속",
      "자동차",
      "화학제품",
      "전자기기"
    ],
    "sectors": {
      "primary": 2.5,
      "secondary": 20.5,
      "tertiary": 77,
      "note": "취업 비중% 근사(2022–23). 고부가 제조·금융 서비스."
    },
    "sources": [
      "CIA World Factbook",
      "BFS",
      "World Bank/ILO",
      "OECD"
    ],
    "confidence": "high"
  },
  {
    "id": "poland",
    "country": "폴란드",
    "ethnicity": [
      {
        "name": "폴란드인",
        "pct": 97
      },
      {
        "name": "실롱스크·독일·우크라이나 등",
        "pct": 3
      }
    ],
    "currency": {
      "code": "PLN",
      "name": "폴란드 즈워티"
    },
    "culture": "가톨릭이 사회·정체성에 깊게 뿌리내린 중동부 유럽 국가다. 분할·점령·공산 체제 이후 1989년 체제 전환과 EU 가입이 현대사의 전환점이며, 민족적 동질성이 높은 편이다.",
    "languages": [
      {
        "name": "폴란드어",
        "official": true,
        "note": "공용어"
      }
    ],
    "climate": "온대 습윤·대륙성 전이 기후. 겨울은 한랭, 여름은 온난하며 동쪽으로 갈수록 대륙성이 강해진다.",
    "education": {
      "literacy": 99,
      "tertiary": 33,
      "note": "문해율 보편. 고등교육 이수 OECD 중위권."
    },
    "exports": [
      "기계·가전",
      "자동차·부품",
      "가구",
      "전자기기",
      "식료품",
      "금속"
    ],
    "imports": [
      "기계",
      "화학제품",
      "자동차",
      "원유·가스",
      "전자기기",
      "플라스틱"
    ],
    "sectors": {
      "primary": 7.6,
      "secondary": 30.5,
      "tertiary": 61.9,
      "note": "취업 비중% 근사(ILO 2023). 제조업 취업 비중이 EU 내 높은 편."
    },
    "sources": [
      "CIA World Factbook",
      "GUS",
      "World Bank/ILO",
      "OECD"
    ],
    "confidence": "high"
  },
  {
    "id": "taiwan",
    "country": "대만",
    "ethnicity": [
      {
        "name": "한족(민난·하카·외성인 등)",
        "pct": 95
      },
      {
        "name": "원주민",
        "pct": 2.5
      },
      {
        "name": "신이민·기타",
        "pct": 2.5
      }
    ],
    "currency": {
      "code": "TWD",
      "name": "신 대만 달러"
    },
    "culture": "한족 이민·일본 통치·전후 중화민국 정체성이 층위를 이룬다. 불교·도교·민간 신앙이 생활 문화에 깊고, 민주화 이후 대만 정체성·다원주의가 강화되었다. 반도체 산업이 현대 경제 정체성의 핵심이다.",
    "languages": [
      {
        "name": "중국어(국어/보통화)",
        "official": true,
        "note": "사실상 행정·교육 공용어(국어)"
      },
      {
        "name": "대만어(민난어)",
        "official": true,
        "note": "국가언어법상 국가언어·일상 광범위"
      },
      {
        "name": "하카어·원주민 언어",
        "official": true,
        "note": "국가언어법상 국가언어(소수·지역)"
      }
    ],
    "climate": "북부는 온대 습윤, 중·남은 아열대~열대 몬순 기후. 여름 태풍·고온다습, 산지는 고도별 기후 변화가 크다.",
    "education": {
      "literacy": 99,
      "tertiary": 50,
      "note": "문해율 보편. 고등교육 진학·이수 비율 높음."
    },
    "exports": [
      "반도체·집적회로",
      "전자기기",
      "기계",
      "플라스틱",
      "광학기기",
      "석유화학"
    ],
    "imports": [
      "반도체 장비·소재",
      "원유",
      "전자기기 부품",
      "기계",
      "석탄",
      "화학제품"
    ],
    "sectors": {
      "primary": 4.5,
      "secondary": 35.5,
      "tertiary": 60,
      "note": "취업 비중% 근사(2020년대). 제조·첨단 산업 취업 비중 높음. 국제기구 통계 공백 있음."
    },
    "sources": [
      "CIA World Factbook",
      "대만 주계총처",
      "WTO/무역 통계"
    ],
    "confidence": "medium"
  },
  {
    "id": "belgium",
    "country": "벨기에",
    "ethnicity": [
      {
        "name": "플라망(네덜란드계)",
        "pct": 58
      },
      {
        "name": "왈롱(프랑스계)",
        "pct": 31
      },
      {
        "name": "기타·이민",
        "pct": 11
      }
    ],
    "currency": {
      "code": "EUR",
      "name": "유로"
    },
    "culture": "플라망·왈롱 언어 공동체가 연방 체제를 이루는 다언어 국가다. 가톨릭 전통과 세속 복지국가가 공존하며, EU·NATO 본부가 있는 유럽 행정 중심지다. 공동체 간 정치 타협이 일상적이다.",
    "languages": [
      {
        "name": "네덜란드어",
        "official": true,
        "note": "플라망 지역·연방"
      },
      {
        "name": "프랑스어",
        "official": true,
        "note": "왈롱·브뤼셀"
      },
      {
        "name": "독일어",
        "official": true,
        "note": "동부 소지역"
      }
    ],
    "climate": "온대 해양성 기후(Cfb). 연중 온화·습윤하고 구름 낀 날이 많으며 기온 진폭이 작다.",
    "education": {
      "literacy": 99,
      "tertiary": 45,
      "note": "문해율 보편. 고등교육 이수 OECD 중상위."
    },
    "exports": [
      "화학·의약품",
      "자동차·부품",
      "기계",
      "플라스틱",
      "다이아몬드·귀금속",
      "식료품"
    ],
    "imports": [
      "기계",
      "화학제품",
      "자동차",
      "원유·가스",
      "의약품",
      "전자기기"
    ],
    "sectors": {
      "primary": 1,
      "secondary": 18.5,
      "tertiary": 80.5,
      "note": "취업 비중% 근사(2022–23). 서비스·물류·행정 중심."
    },
    "sources": [
      "CIA World Factbook",
      "Statbel",
      "World Bank/ILO",
      "OECD"
    ],
    "confidence": "high"
  },
  {
    "id": "argentina",
    "country": "아르헨티나",
    "ethnicity": [
      {
        "name": "유럽계(이탈리아·스페인 등)",
        "pct": 85
      },
      {
        "name": "메스티소·기타",
        "pct": 12
      },
      {
        "name": "원주민",
        "pct": 3
      }
    ],
    "currency": {
      "code": "ARS",
      "name": "아르헨티나 페소"
    },
    "culture": "스페인 식민·대규모 유럽 이민으로 라틴아메리카에서 유럽적 경관이 두드러진다. 가톨릭 전통과 세속 도시 문화, 탱고·축구·쇠고기 문화가 상징이다. 반복된 경제 위기와 페론주의 정치 전통이 사회를 규정한다. 자가 유럽계 정체성과 유전적 혼혈 비율은 차이가 있다.",
    "languages": [
      {
        "name": "스페인어",
        "official": true,
        "note": "공용어"
      }
    ],
    "climate": "대부분 온대. 팜파스는 습윤 아열대·온대, 남부 파타고니아는 한랭·건조, 북서는 고산·아열대, 북동은 아열대 습윤이다.",
    "education": {
      "literacy": 99,
      "tertiary": 25,
      "note": "문해율 매우 높음. 고등교육 진학률은 높으나 이수율은 중남미 중위권."
    },
    "exports": [
      "대두·유지박",
      "옥수수",
      "자동차",
      "육류",
      "석유·가스",
      "밀"
    ],
    "imports": [
      "기계",
      "자동차·부품",
      "화학제품",
      "전자기기",
      "천연가스",
      "플라스틱"
    ],
    "sectors": {
      "primary": 7,
      "secondary": 22,
      "tertiary": 71,
      "note": "취업 비중% 근사(2020년대). 농축산 수출 강국이나 취업은 서비스 중심. 공식 시계열 편차 있음."
    },
    "sources": [
      "CIA World Factbook",
      "INDEC",
      "World Bank/ILO"
    ],
    "confidence": "medium"
  },
  {
    "id": "sweden",
    "country": "스웨덴",
    "ethnicity": [
      {
        "name": "스웨덴인",
        "pct": 80
      },
      {
        "name": "기타 유럽",
        "pct": 10
      },
      {
        "name": "중동·아프리카 등 이민",
        "pct": 10
      }
    ],
    "currency": {
      "code": "SEK",
      "name": "스웨덴 크로나"
    },
    "culture": "루터교 전통과 강한 세속·복지국가(노르딕 모델)가 공존한다. 합의·평등·고신뢰 사회로 알려졌으며, 최근 이민 증가로 다문화 전환이 진행 중이다. 혁신·환경·디자인 문화가 국가 브랜드다.",
    "languages": [
      {
        "name": "스웨덴어",
        "official": true,
        "note": "공용어"
      },
      {
        "name": "핀란드어·사미어 등",
        "official": false,
        "note": "소수 공인 언어"
      }
    ],
    "climate": "대부분 냉대 습윤 기후. 남부는 온대 해양성 전이, 북부 라플란드는 아한대·툰드라성이다. 겨울이 길고 일조 계절 차가 크다.",
    "education": {
      "literacy": 99,
      "tertiary": 48,
      "note": "문해율 보편. 고등교육 이수 OECD 상위."
    },
    "exports": [
      "기계",
      "자동차·트럭",
      "의약품",
      "전자·통신",
      "철강·종이",
      "석유제품"
    ],
    "imports": [
      "기계",
      "전자기기",
      "자동차",
      "원유·석유제품",
      "화학제품",
      "식료품"
    ],
    "sectors": {
      "primary": 1.5,
      "secondary": 18,
      "tertiary": 80.5,
      "note": "취업 비중% 근사(2022–23). 서비스·첨단 제조 중심."
    },
    "sources": [
      "CIA World Factbook",
      "SCB",
      "World Bank/ILO",
      "OECD"
    ],
    "confidence": "high"
  },
  {
    "id": "ireland",
    "country": "아일랜드",
    "ethnicity": [
      {
        "name": "아일랜드인(화이트 아이리시)",
        "pct": 77
      },
      {
        "name": "기타 백인",
        "pct": 11
      },
      {
        "name": "아시아계",
        "pct": 4
      },
      {
        "name": "흑인",
        "pct": 2
      },
      {
        "name": "기타·미상",
        "pct": 6
      }
    ],
    "currency": {
      "code": "EUR",
      "name": "유로"
    },
    "culture": "영어권 켈트 문화권으로 가톨릭 전통과 문학·음악 유산이 강하다. EU·미국 다국적 기업의 유럽 허브로 제약·IT·금융 서비스가 발달했다. 브렉시트 이후 영국과의 북아일랜드 국경·무역 이슈가 부각된다. 아일랜드어(게일어)는 공식어이지만 일상은 영어 중심이다.",
    "languages": [
      {
        "name": "영어",
        "official": true
      },
      {
        "name": "아일랜드어",
        "official": true
      }
    ],
    "climate": "북대서양 난류의 영향을 받는 온난 해양성 기후로 겨울이 온화하고 여름이 서늘하며 연중 습하고 구름이 많다.",
    "education": {
      "literacy": 99,
      "tertiary": 63,
      "note": "문해율 사실상 보편. 25–34세 고등교육 이수율 OECD 최상위권(~60%대). 다국적 기업 수요에 맞춘 STEM·제약 인재 배출. 의약품·의료·유기화학이 상품수출 핵심(약 절반 전후)."
    },
    "exports": [
      "의약품",
      "유기화학",
      "컴퓨터·전자",
      "의료기기",
      "항공서비스"
    ],
    "imports": [
      "항공기",
      "기계",
      "원유·연료",
      "자동차",
      "화학제품"
    ],
    "sectors": {
      "primary": 5,
      "secondary": 17,
      "tertiary": 78,
      "note": "취업 비중 근사(World Bank/ILO 2023: 농업~5%, 산업~17%, 서비스~78). GDP는 제약·IT 수출로 2차 비중이 더 커 보이나 고용은 서비스 중심."
    },
    "sources": [
      "CIA Factbook",
      "World Bank",
      "CSO Ireland"
    ],
    "confidence": "high"
  },
  {
    "id": "uae",
    "country": "아랍에미리트",
    "ethnicity": [
      {
        "name": "인도계 거주자",
        "pct": 38
      },
      {
        "name": "파키스탄계 거주자",
        "pct": 17
      },
      {
        "name": "에미리트 국민",
        "pct": 11
      },
      {
        "name": "방글라데시·필리핀 등 아시아계",
        "pct": 20
      },
      {
        "name": "기타(아랍·유럽·이란 등)",
        "pct": 14
      }
    ],
    "currency": {
      "code": "AED",
      "name": "아랍에미리트 디르함"
    },
    "culture": "7개 토후국 연방으로 아부다비·두바이가 정치·경제 중심이다. 전체 인구의 약 88–89%가 외국인 거주자이며 국민(에미리트인)은 약 11% 전후 소수다. 이슬람 문화와 관용·다국적 비즈니스 환경이 공존하며, 비석유 부문(관광·물류·금융·부동산)이 GDP의 약 70% 수준까지 확대됐다. 에미라티제이션(자국민 고용 확대) 정책이 진행 중이다. 통화는 아랍에미리트 디르함(AED).",
    "languages": [
      {
        "name": "아랍어",
        "official": true
      },
      {
        "name": "영어",
        "official": false
      }
    ],
    "climate": "대부분 사막성 기후로 여름이 매우 덥고 건조하며, 해안은 습도가 높다. 연 강수량이 적고 내륙은 고온 건조하다.",
    "education": {
      "literacy": 98,
      "tertiary": 61,
      "note": "성인 문해율 ~98%. 고등교육 GER~60%대(World Bank). 거주 인구 통계는 국적·체류 자격에 따라 편차 큼. 민간 노동력은 외국인 중심."
    },
    "exports": [
      "원유·석유제품",
      "금·귀금속",
      "알루미늄",
      "재수출 상품",
      "플라스틱"
    ],
    "imports": [
      "기계·전자",
      "금",
      "자동차",
      "항공기",
      "식료품"
    ],
    "sectors": {
      "primary": 2,
      "secondary": 31,
      "tertiary": 67,
      "note": "취업 비중 근사(World Bank/ILO 2023: 농업~1.5%, 산업~31%, 서비스~68). 석유는 GDP·재정 비중은 크나 고용은 건설·서비스·무역 중심. 국민은 공공부문 선호."
    },
    "sources": [
      "CIA Factbook",
      "World Bank",
      "UAE FCSA/GMI",
      "BTI"
    ],
    "confidence": "medium"
  },
  {
    "id": "singapore",
    "country": "싱가포르",
    "ethnicity": [
      {
        "name": "중국계(거주자)",
        "pct": 74
      },
      {
        "name": "말레이계(거주자)",
        "pct": 14
      },
      {
        "name": "인도계(거주자)",
        "pct": 9
      },
      {
        "name": "기타(거주자)",
        "pct": 3
      }
    ],
    "currency": {
      "code": "SGD",
      "name": "싱가포르 달러"
    },
    "culture": "도시국가·자유항으로 동남아 금융·물류·반도체 허브다. 공식 통계의 인종 구성(CMIO: 중국·말레이·인도·기타)은 시민·영주권자(거주자) 기준이며, 전체 인구의 약 30%는 비거주 외국인 노동자다. 영어 중심의 다언어·다종교 사회로 공공주택 인종 할당 등 통합 정책이 있다.",
    "languages": [
      {
        "name": "영어",
        "official": true
      },
      {
        "name": "중국어(표준)",
        "official": true
      },
      {
        "name": "말레이어",
        "official": true
      },
      {
        "name": "타밀어",
        "official": true
      }
    ],
    "climate": "적도 근처 열대 우림 기후로 연중 고온다습하며 우기와 소나기가 잦다.",
    "education": {
      "literacy": 97,
      "tertiary": 55,
      "note": "거주자 문해율 높음(~98%). tertiary 수치는 성인 고등교육 이수·인력 수준 근사(거주자 기준); 총진학률(GER)은 90%대. CMIO 그룹 간 대학 진학률 격차 존재."
    },
    "exports": [
      "집적회로·전자",
      "정제석유",
      "화학제품",
      "기계",
      "의약품"
    ],
    "imports": [
      "집적회로",
      "원유",
      "기계",
      "전자부품",
      "금"
    ],
    "sectors": {
      "primary": 0,
      "secondary": 14,
      "tertiary": 86,
      "note": "취업 비중 근사. 제조(반도체·바이오) GDP 비중은 상당하나 고용은 금융·무역·전문서비스 중심."
    },
    "sources": [
      "CIA Factbook",
      "World Bank",
      "Singapore DOS",
      "Population in Brief"
    ],
    "confidence": "high"
  },
  {
    "id": "israel",
    "country": "이스라엘",
    "ethnicity": [
      {
        "name": "유대인",
        "pct": 73
      },
      {
        "name": "아랍인(무슬림·드루즈·기독교 등)",
        "pct": 21
      },
      {
        "name": "기타",
        "pct": 6
      }
    ],
    "currency": {
      "code": "ILS",
      "name": "이스라엘 신 셰켈"
    },
    "culture": "중동의 고기술·스타트업 중심국으로 방산·사이버·바이오·소프트웨어가 강하다. 유대인 다수(약 73%)와 아랍 소수(약 21%)가 공존하며 사회·경제적 격차가 있다. 2018 민족국가기본법 이후 히브리어가 국가어이고 아랍어는 특별 지위를 가진다. 안보 환경이 경제·관광에 큰 영향을 준다.",
    "languages": [
      {
        "name": "히브리어",
        "official": true
      },
      {
        "name": "아랍어(특별 지위)",
        "official": false
      }
    ],
    "climate": "지중해성 기후가 해안·북부에 지배적이며, 남부 네게브는 건조·사막성이다. 여름 건조·더위, 겨울 온화·강수가 특징이다.",
    "education": {
      "literacy": 98,
      "tertiary": 50,
      "note": "전체 문해율 높음. 고등교육·연구개발 집약. 하레디·아랍 인구 집단 간 노동·교육 참여 격차 존재."
    },
    "exports": [
      "첨단기술·전자",
      "연마 다이아몬드",
      "의약품",
      "화학제품",
      "방산·항공"
    ],
    "imports": [
      "원유·연료",
      "원자재 다이아몬드",
      "자동차",
      "기계",
      "전자부품"
    ],
    "sectors": {
      "primary": 1,
      "secondary": 15,
      "tertiary": 84,
      "note": "취업 비중 근사(World Bank/ILO 2023: 농업~1%, 산업~15%, 서비스~84). 하이테크가 수출의 절반 전후를 차지하나 고용 비중은 그보다 작음."
    },
    "sources": [
      "CIA Factbook",
      "World Bank",
      "CBS Israel",
      "Innovation Authority"
    ],
    "confidence": "high"
  },
  {
    "id": "austria",
    "country": "오스트리아",
    "ethnicity": [
      {
        "name": "오스트리아인(독일어권)",
        "pct": 81
      },
      {
        "name": "구유고·터키·동유럽 이민 등",
        "pct": 15
      },
      {
        "name": "기타",
        "pct": 4
      }
    ],
    "currency": {
      "code": "EUR",
      "name": "유로"
    },
    "culture": "알프스 중심의 고소득 사회민주주의형 복지국가로 기계·자동차 부품·관광이 강하다. 빈은 국제기구·문화 도시로 유명하다. 독일어 사용 다수이며 역사적으로 합스부르크·중부유럽 문화권에 속한다.",
    "languages": [
      {
        "name": "독일어",
        "official": true
      },
      {
        "name": "슬로베니아어·크로아티아어·헝가리어(지역)",
        "official": false
      }
    ],
    "climate": "온대 대륙성·알프스 기후로 산지는 한랭하고 강설이 많으며, 동부 평야는 여름이 따뜻하고 겨울이 다소 춥다.",
    "education": {
      "literacy": 99,
      "tertiary": 45,
      "note": "이중교육(도제) 시스템 강점. 문해율 보편, 직업교육과 대학 병행."
    },
    "exports": [
      "기계",
      "차량·부품",
      "철강·금속",
      "의약품",
      "전자"
    ],
    "imports": [
      "기계",
      "차량",
      "화학제품",
      "원유·가스",
      "전자"
    ],
    "sectors": {
      "primary": 3,
      "secondary": 26,
      "tertiary": 71,
      "note": "취업 비중 근사. 제조업 고용 비중이 서유럽 평균보다 다소 높음."
    },
    "sources": [
      "CIA Factbook",
      "World Bank",
      "Statistik Austria"
    ],
    "confidence": "high"
  },
  {
    "id": "thailand",
    "country": "태국",
    "ethnicity": [
      {
        "name": "타이족",
        "pct": 75
      },
      {
        "name": "중국계 타이",
        "pct": 14
      },
      {
        "name": "말레이계 등 기타",
        "pct": 11
      }
    ],
    "currency": {
      "code": "THB",
      "name": "태국 바트"
    },
    "culture": "입헌군주제 국가로 불교(테라바다) 문화가 일상과 정치에 깊이 자리한다. 방콕은 동남아 관광·제조·물류 거점이며 자동차·전자·식품 수출이 강하다. 왕실 존중과 쿠데타·정치 갈등이 반복된 역사를 가진다.",
    "languages": [
      {
        "name": "태국어",
        "official": true
      }
    ],
    "climate": "열대 몬순 기후로 건기·우기가 뚜렷하다. 중·남은 고온다습, 북부는 산악으로 상대적으로 선선하다.",
    "education": {
      "literacy": 94,
      "tertiary": 45,
      "note": "기초 문해율 양호. 고등교육 확대 중이나 숙련 인력·지역 격차 과제."
    },
    "exports": [
      "자동차·부품",
      "전자·컴퓨터",
      "고무·플라스틱",
      "농수산물",
      "보석·귀금속"
    ],
    "imports": [
      "원유·연료",
      "전자부품",
      "기계",
      "철강",
      "화학제품"
    ],
    "sectors": {
      "primary": 30,
      "secondary": 22,
      "tertiary": 48,
      "note": "취업 비중 근사. 농업 고용 비중은 높으나 GDP 기여는 낮고, 제조·관광이 성장 동력."
    },
    "sources": [
      "CIA Factbook",
      "World Bank",
      "NESDC Thailand"
    ],
    "confidence": "high"
  },
  {
    "id": "norway",
    "country": "노르웨이",
    "ethnicity": [
      {
        "name": "노르웨이인",
        "pct": 82
      },
      {
        "name": "기타 유럽계·이민",
        "pct": 15
      },
      {
        "name": "사미 등 원주민·기타",
        "pct": 3
      }
    ],
    "currency": {
      "code": "NOK",
      "name": "노르웨이 크로네"
    },
    "culture": "북유럽 복지국가로 석유·가스 수익을 국부펀드에 축적해 고복지·고임금을 유지한다. 평등·아웃도어·해양 문화가 강하며 EU 비회원(EEA)이다. 원유 수출국이지만 국내 전력은 수력 비중이 매우 높다.",
    "languages": [
      {
        "name": "노르웨이어",
        "official": true
      },
      {
        "name": "사미어(지역)",
        "official": false
      }
    ],
    "climate": "해안은 난류 영향으로 위도에 비해 온화한 해양성, 내륙·북부는 한랭 대륙성·극지성이다. 긴 겨울과 짧은 여름이 특징이다.",
    "education": {
      "literacy": 99,
      "tertiary": 48,
      "note": "무상에 가까운 고등교육. 성인 고등교육 이수율 OECD 상위(25–34세 ~45–50%대). 문해·인적자본 최상위권."
    },
    "exports": [
      "원유·천연가스",
      "수산물",
      "금속",
      "기계",
      "화학"
    ],
    "imports": [
      "기계",
      "자동차",
      "전자",
      "식료품",
      "화학제품"
    ],
    "sectors": {
      "primary": 2,
      "secondary": 19,
      "tertiary": 79,
      "note": "취업 비중 근사(World Bank/ILO 2023: 농업~2%, 산업~19%, 서비스~79). 석유·가스는 GDP·수출 핵심이나 고용 비중은 서비스가 압도적."
    },
    "sources": [
      "CIA Factbook",
      "World Bank",
      "Statistics Norway"
    ],
    "confidence": "high"
  },
  {
    "id": "vietnam",
    "country": "베트남",
    "ethnicity": [
      {
        "name": "킨족(비엣)",
        "pct": 85
      },
      {
        "name": "따이·타이·무옹·크메르 등 소수민족",
        "pct": 14
      },
      {
        "name": "화교 등 기타",
        "pct": 1
      }
    ],
    "currency": {
      "code": "VND",
      "name": "베트남 동"
    },
    "culture": "사회주의 일당 체제 아래 도이머이 이후 수출주도 제조업이 급성장했다. 유교·불교·민간신앙이 혼재하며 가족·교육 중시 문화가 강하다. 전자·의류·신발의 글로벌 공급망 거점으로 부상했다.",
    "languages": [
      {
        "name": "베트남어",
        "official": true
      }
    ],
    "climate": "북부는 아열대 몬순(사계절), 남부는 열대 몬순(건기·우기). 중부 해안은 태풍·홍수 피해가 잦다.",
    "education": {
      "literacy": 96,
      "tertiary": 35,
      "note": "기초 문해율 높음. 고등교육 확대 중이나 숙련·연구 인력은 제조 수요 대비 과제."
    },
    "exports": [
      "전자·휴대폰",
      "의류·섬유",
      "신발",
      "기계",
      "농수산물·커피·쌀"
    ],
    "imports": [
      "전자부품",
      "기계",
      "원유·연료",
      "철강",
      "플라스틱"
    ],
    "sectors": {
      "primary": 27,
      "secondary": 34,
      "tertiary": 39,
      "note": "취업 비중 근사(World Bank/ILO 2023: 농업~27%, 산업~34%, 서비스~40). 제조업 고용·수출 비중이 빠르게 확대, 농업 고용은 감소 추세."
    },
    "sources": [
      "CIA Factbook",
      "World Bank",
      "GSO Vietnam"
    ],
    "confidence": "high"
  },
  {
    "id": "philippines",
    "country": "필리핀",
    "ethnicity": [
      {
        "name": "타갈로그·비사야 등 말레이계 필리핀인",
        "pct": 95
      },
      {
        "name": "중국계·기타",
        "pct": 5
      }
    ],
    "currency": {
      "code": "PHP",
      "name": "필리핀 페소"
    },
    "culture": "스페인·미국 식민 유산으로 가톨릭과 영어 사용이 널리 퍼져 있다. 해외 송금(OFW)과 BPO(비즈니스 프로세스 아웃소싱)·전자 수출이 경제 버팀목이다. 7,000여 섬의 다민족·다언어 사회로 지역 정체성이 강하다.",
    "languages": [
      {
        "name": "필리핀어(타갈로그 기반)",
        "official": true
      },
      {
        "name": "영어",
        "official": true
      }
    ],
    "climate": "열대 해양·몬순 기후로 고온다습하며 태풍(슈퍼 타이푼) 위험이 높다. 건기·우기가 뚜렷하다.",
    "education": {
      "literacy": 98,
      "tertiary": 44,
      "note": "성인 문해율 매우 높음(~98%, World Bank 2020). 영어 능숙 인력으로 BPO 경쟁력. 고등교육 GER~44%(2023). 교육 질·지역 격차는 과제."
    },
    "exports": [
      "전자·반도체",
      "기계",
      "농산물(코코넛·바나나)",
      "광물",
      "의류"
    ],
    "imports": [
      "원유·연료",
      "전자부품",
      "기계",
      "수송장비",
      "철강"
    ],
    "sectors": {
      "primary": 22,
      "secondary": 19,
      "tertiary": 59,
      "note": "취업 비중 근사. 서비스(소매·BPO)·해외취업 의존도가 높음."
    },
    "sources": [
      "CIA Factbook",
      "World Bank",
      "PSA Philippines"
    ],
    "confidence": "high"
  },
  {
    "id": "bangladesh",
    "country": "방글라데시",
    "ethnicity": [
      {
        "name": "벵골인",
        "pct": 98
      },
      {
        "name": "소수민족·기타",
        "pct": 2
      }
    ],
    "currency": {
      "code": "BDT",
      "name": "방글라데시 타카"
    },
    "culture": "벵골 이슬람 문화권의 인구 대국으로 의류(RMG) 수출이 외화 수입의 핵심이다. 저임금 제조와 해외 송금이 성장을 이끌었으며 기후 취약성(홍수·사이클론)이 크다. 벵골어와 이슬람이 사회 정체성의 중심이다.",
    "languages": [
      {
        "name": "벵골어",
        "official": true
      },
      {
        "name": "영어",
        "official": false
      }
    ],
    "climate": "열대 몬순 기후로 우기 호우·홍수가 잦고, 벵골만 연안은 사이클론 위험이 높다. 연중 고온다습하다.",
    "education": {
      "literacy": 79,
      "tertiary": 25,
      "note": "성인 문해율 약 79%(World Bank/UNESCO 2022). 지속 상승 중. 여성 교육·의류 산업 인력 확대가 특징."
    },
    "exports": [
      "의류·니트",
      "황마 제품",
      "가죽",
      "수산물",
      "가정용 섬유"
    ],
    "imports": [
      "면화·섬유원료",
      "기계",
      "원유·연료",
      "식량·식용유",
      "철강"
    ],
    "sectors": {
      "primary": 45,
      "secondary": 18,
      "tertiary": 37,
      "note": "취업 비중 근사(World Bank/ILO 2023: 농업~45%, 산업~18%, 서비스~37). 농업 고용 비중 여전히 높고, 제조는 의류(RMG) 중심. RMG는 상품수출의 약 80%+."
    },
    "sources": [
      "CIA Factbook",
      "World Bank",
      "BBS Bangladesh"
    ],
    "confidence": "high"
  },
  {
    "id": "malaysia",
    "country": "말레이시아",
    "ethnicity": [
      {
        "name": "부미푸트라(말레이·토착민)",
        "pct": 70
      },
      {
        "name": "중국계",
        "pct": 23
      },
      {
        "name": "인도계",
        "pct": 6
      },
      {
        "name": "기타",
        "pct": 1
      }
    ],
    "currency": {
      "code": "MYR",
      "name": "말레이시아 링깃"
    },
    "culture": "다민족·다종교 연방국가로 말레이 무슬림 다수와 중국·인도계가 공존한다. 부미푸트라 우대(NEP 계승) 정책이 교육·사업·공공부문에 영향을 준다. 반도체·석유·팜유·관광이 경제 축이며 이슬람 금융도 발달했다. 통계는 시민 기준이 주이며 외국인 노동자 비중이 상당하다.",
    "languages": [
      {
        "name": "말레이어",
        "official": true
      },
      {
        "name": "영어",
        "official": false
      },
      {
        "name": "중국어·타밀어 등",
        "official": false
      }
    ],
    "climate": "적도 근처 열대 우림 기후로 연중 고온다습하고 몬순 강수가 많다.",
    "education": {
      "literacy": 95,
      "tertiary": 37,
      "note": "문해율 높음(~96%). 고등교육 총진학률(GER)~37%(World Bank 2023). 공공대학 부미푸트라 할당 등 민족별 교육 경로 차이 존재."
    },
    "exports": [
      "집적회로·전자",
      "석유·LNG",
      "팜유",
      "화학",
      "기계"
    ],
    "imports": [
      "전자부품",
      "원유·연료",
      "기계",
      "플라스틱",
      "철강"
    ],
    "sectors": {
      "primary": 10,
      "secondary": 26,
      "tertiary": 64,
      "note": "취업 비중 근사(World Bank/ILO 2023: 농업~10%, 산업~26%, 서비스~64). 제조(전자)와 서비스가 고용·수출 핵심."
    },
    "sources": [
      "CIA Factbook",
      "World Bank",
      "DOSM Malaysia"
    ],
    "confidence": "high"
  },
  {
    "id": "denmark",
    "country": "덴마크",
    "ethnicity": [
      {
        "name": "덴마크인",
        "pct": 86
      },
      {
        "name": "기타 유럽·이민",
        "pct": 14
      }
    ],
    "currency": {
      "code": "DKK",
      "name": "덴마크 크로네"
    },
    "culture": "고복지·고신뢰의 북유럽 모델로 ‘휘게’ 문화와 평등주의가 특징이다. 제약(노보 등)·해운·재생에너지·농식품 수출이 강하다. EU 회원이지만 유로 미도입이다.",
    "languages": [
      {
        "name": "덴마크어",
        "official": true
      }
    ],
    "climate": "온난 해양성 기후로 겨울은 온화·습하고 여름은 선선하다. 바람이 강해 풍력 발전에 유리하다.",
    "education": {
      "literacy": 99,
      "tertiary": 49,
      "note": "무상 교육·직업훈련 체계 우수. 성인 고등교육 이수율 OECD 상위(25–34세 약 45–50%대). 인적자본·혁신 지표 세계 상위."
    },
    "exports": [
      "의약품",
      "기계",
      "농식품",
      "석유·에너지 관련",
      "전자"
    ],
    "imports": [
      "기계",
      "화학제품",
      "자동차",
      "전자",
      "원유·연료"
    ],
    "sectors": {
      "primary": 2,
      "secondary": 19,
      "tertiary": 79,
      "note": "취업 비중 근사(World Bank/ILO 2023: 농업~2%, 산업~19%, 서비스~79)."
    },
    "sources": [
      "CIA Factbook",
      "World Bank",
      "Statistics Denmark"
    ],
    "confidence": "high"
  },
  {
    "id": "hongkong",
    "country": "홍콩",
    "ethnicity": [
      {
        "name": "중국계",
        "pct": 92
      },
      {
        "name": "기타(남아시아·서양계 등)",
        "pct": 8
      }
    ],
    "currency": {
      "code": "HKD",
      "name": "홍콩 달러"
    },
    "culture": "중국 특별행정구로 ‘일국양제’ 아래 금융·무역·물류 국제 허브 역할을 한다. 광둥어·영어가 상용되며 대륙과의 경제 통합이 심화됐다. 서비스 경제 비중이 극히 높고 제조는 거의 없다.",
    "languages": [
      {
        "name": "중국어(광둥어 상용)",
        "official": true
      },
      {
        "name": "영어",
        "official": true
      }
    ],
    "climate": "아열대 몬순 기후로 여름 고온다습·태풍 영향이 있고, 겨울은 온화 건조한 편이다.",
    "education": {
      "literacy": 96,
      "tertiary": 50,
      "note": "문해율 높고 대학 진학·국제학교 비중 큼. 영어·중국어 이중언어 교육."
    },
    "exports": [
      "전자·통신장비",
      "귀금속·보석",
      "사무기기",
      "의류",
      "재수출 상품"
    ],
    "imports": [
      "전자부품",
      "통신장비",
      "귀금속",
      "식료품",
      "연료"
    ],
    "sectors": {
      "primary": 0,
      "secondary": 14,
      "tertiary": 86,
      "note": "취업 비중 근사(World Bank/ILO 2023: 산업~14%는 건설 포함, 제조 자체는 ~2%). 금융·무역·전문서비스·관광이 고용 대부분."
    },
    "sources": [
      "CIA Factbook",
      "World Bank",
      "C&SD Hong Kong"
    ],
    "confidence": "high"
  },
  {
    "id": "southafrica",
    "country": "남아프리카공화국",
    "ethnicity": [
      {
        "name": "흑인(아프리카계)",
        "pct": 82
      },
      {
        "name": "컬러드(혼혈)",
        "pct": 9
      },
      {
        "name": "백인",
        "pct": 7
      },
      {
        "name": "인도·아시아계",
        "pct": 2
      }
    ],
    "currency": {
      "code": "ZAR",
      "name": "남아프리카 랜드"
    },
    "culture": "아프리카 최대급 산업경제로 광업(금·백금·석탄)·금융·제조가 발달했다. 아파르트헤이트 종식 후에도 인종·소득 격차와 높은 실업이 구조적 과제다. 12개 공용어, 다양한 문화가 공존하는 ‘무지개 국가’로 불린다.",
    "languages": [
      {
        "name": "줄루어·코사어·아프리칸스어·영어 등 12개(2023년 남아공 수어 추가)",
        "official": true
      }
    ],
    "climate": "대체로 온대~아열대. 내륙 고원은 건조·일교차 크고, 남서부(케이프)는 지중해성, 동해안은 습윤하다.",
    "education": {
      "literacy": 95,
      "tertiary": 25,
      "note": "문해율은 양호하나 교육 질·인종·지역 격차가 큼. 고등교육 접근성 불균등."
    },
    "exports": [
      "백금·금 등 광물",
      "석탄",
      "자동차",
      "철강·금속",
      "농산물"
    ],
    "imports": [
      "원유·연료",
      "기계",
      "전자",
      "화학",
      "자동차 부품"
    ],
    "sectors": {
      "primary": 6,
      "secondary": 21,
      "tertiary": 73,
      "note": "취업 비중 근사(World Bank/ILO 2023: 농림어업~5.5%, 산업~21%, 서비스~74%). 공식 실업률이 매우 높아 비공식·미취업 비중 해석 주의."
    },
    "sources": [
      "CIA Factbook",
      "World Bank",
      "Stats SA"
    ],
    "confidence": "high"
  },
  {
    "id": "iran",
    "country": "이란",
    "ethnicity": [
      {
        "name": "페르시아인",
        "pct": 61
      },
      {
        "name": "아제르바이잔인",
        "pct": 16
      },
      {
        "name": "쿠르드",
        "pct": 10
      },
      {
        "name": "루르",
        "pct": 6
      },
      {
        "name": "아랍·발루치·투르크멘 등",
        "pct": 7
      }
    ],
    "currency": {
      "code": "IRR",
      "name": "이란 리알"
    },
    "culture": "시아파 이슬람 공화국으로 페르시아 문명 유산이 깊다. 세계 유수의 원유·가스 매장국이며 제재 하에서도 원유·석유화학 수출(주로 중국 등, 비공식·우회 경로 포함)이 재정 핵심이다. 국영·준국영(본야드·IRGC 계열) 비중이 크고 리알(IRR) 가치 하락·고인플레이션이 반복된다.",
    "languages": [
      {
        "name": "페르시아어(파르시)",
        "official": true
      },
      {
        "name": "아제르바이잔어·쿠르드어 등",
        "official": false
      }
    ],
    "climate": "대부분 건조·반건조. 북부 카스피해 연안은 습윤, 중부 고원·남부는 사막성, 서부 산지는 한랭하다.",
    "education": {
      "literacy": 89,
      "tertiary": 59,
      "note": "성인 문해율 ~89%. tertiary는 총진학률(GER)~59%(World Bank 2022)이며 성인 이수율(attainment)과는 다름. 제재·경기 침체로 숙련 인력 유출·실업 문제."
    },
    "exports": [
      "원유·콘덴세이트",
      "석유화학",
      "가스",
      "금속·광물",
      "농산물·카펫"
    ],
    "imports": [
      "기계·산업설비",
      "곡물·식량",
      "의약품",
      "전자",
      "중간재"
    ],
    "sectors": {
      "primary": 14,
      "secondary": 35,
      "tertiary": 51,
      "note": "취업 비중 근사. 석유는 재정·수출 핵심이나 고용은 서비스·제조·비공식 부문 중심. 제재로 통계 신뢰도 제한."
    },
    "sources": [
      "CIA Factbook",
      "World Bank",
      "BTI",
      "secondary estimates"
    ],
    "confidence": "low"
  },
  {
    "id": "colombia",
    "country": "콜롬비아",
    "ethnicity": [
      {
        "name": "메스티소·백인",
        "pct": 87
      },
      {
        "name": "아프리카계",
        "pct": 7
      },
      {
        "name": "원주민",
        "pct": 4
      },
      {
        "name": "기타",
        "pct": 2
      }
    ],
    "currency": {
      "code": "COP",
      "name": "콜롬비아 페소"
    },
    "culture": "안데스·카리브·아마존이 공존하는 다문화 국가로 커피·음악·문학 문화가 유명하다. 석유·석탄·커피·절화가 주요 수출품이며, 과거 분쟁 이후 치안·투자는 개선 추세이나 지역 격차가 크다.",
    "languages": [
      {
        "name": "스페인어",
        "official": true
      }
    ],
    "climate": "적도 근처이나 고도에 따라 열대~한대까지 다양하다. 해안·저지 고온다습, 보고타 등 고원은 선선하다.",
    "education": {
      "literacy": 95,
      "tertiary": 55,
      "note": "문해율 양호. 고등교육 확대 중이나 질·지역 격차 존재."
    },
    "exports": [
      "원유·석탄",
      "커피",
      "금",
      "절화",
      "플라스틱·화학"
    ],
    "imports": [
      "기계",
      "전자",
      "화학제품",
      "자동차",
      "연료·중간재"
    ],
    "sectors": {
      "primary": 14,
      "secondary": 20,
      "tertiary": 66,
      "note": "취업 비중 근사. 서비스·비공식 고용 비중이 큼."
    },
    "sources": [
      "CIA Factbook",
      "World Bank",
      "DANE Colombia"
    ],
    "confidence": "high"
  },
  {
    "id": "pakistan",
    "country": "파키스탄",
    "ethnicity": [
      {
        "name": "펀자브인",
        "pct": 45
      },
      {
        "name": "파슈툰",
        "pct": 15
      },
      {
        "name": "신드인",
        "pct": 14
      },
      {
        "name": "사라이키 등",
        "pct": 8
      },
      {
        "name": "무하지르·발루치·기타",
        "pct": 18
      }
    ],
    "currency": {
      "code": "PKR",
      "name": "파키스탄 루피"
    },
    "culture": "이슬람 공화국으로 펀자브·신드·카이베르파크툰크와·발루치스탄 등 지역·종족 정체성이 강하다. 섬유·의류 수출과 해외 송금이 외화 핵심이며 재정·에너지 위기가 반복된다. 우르두가 국어·공용어이나 모어 화자는 약 9%에 불과하고, 펀자브어(모어 ~37%)·파슈토·신드·사라이키 등 지역어 화자가 다수다. 영어는 엘리트·공적 언어로 쓰인다.",
    "languages": [
      {
        "name": "우르두어",
        "official": true
      },
      {
        "name": "영어",
        "official": true
      },
      {
        "name": "펀자브어(최다 모어)",
        "official": false
      },
      {
        "name": "파슈토어·신드어·사라이키 등",
        "official": false
      }
    ],
    "climate": "대부분 건조·반건조. 인더스 유역은 농업 중심, 북부 산지는 한랭, 남부는 고온이다. 몬순 홍수·폭염이 잦다.",
    "education": {
      "literacy": 61,
      "tertiary": 11,
      "note": "문해율 약 61%(센서스 2023 ~60.7%; 10세+ 기준 출처별 편차). 여아 교육 격차 큼. 고등교육 GER~10–11%."
    },
    "exports": [
      "섬유·의류",
      "쌀",
      "가죽",
      "스포츠용품",
      "시멘트·화학"
    ],
    "imports": [
      "원유·연료",
      "기계",
      "전자",
      "식용유·식량",
      "철강·화학"
    ],
    "sectors": {
      "primary": 37,
      "secondary": 25,
      "tertiary": 38,
      "note": "취업 비중 근사(World Bank/ILO 2023: 농업~37%, 산업~25%, 서비스~38). 농업 고용 비중 높고 제조는 섬유 중심."
    },
    "sources": [
      "CIA Factbook",
      "World Bank",
      "PBS Pakistan"
    ],
    "confidence": "medium"
  },
  {
    "id": "romania",
    "country": "루마니아",
    "ethnicity": [
      {
        "name": "루마니아인",
        "pct": 89
      },
      {
        "name": "헝가리인",
        "pct": 6
      },
      {
        "name": "로마(집시) 등 기타",
        "pct": 5
      }
    ],
    "currency": {
      "code": "RON",
      "name": "루마니아 레우"
    },
    "culture": "동유럽 EU·NATO 회원국으로 라틴계 언어·문화권을 이룬다. 자동차·전선·IT 아웃소싱·농산물이 경제에 중요하며 서유럽으로의 인력 유출이 크다. 정교회 전통이 강하다.",
    "languages": [
      {
        "name": "루마니아어",
        "official": true
      },
      {
        "name": "헝가리어(지역)",
        "official": false
      }
    ],
    "climate": "온대 대륙성 기후로 여름은 덥고 겨울은 춥다. 카르파티아 산지와 흑해 연안의 지역 차가 있다.",
    "education": {
      "literacy": 99,
      "tertiary": 35,
      "note": "문해율 높음. STEM·IT 인력 강점이나 두뇌 유출 지속."
    },
    "exports": [
      "자동차·부품",
      "전선·전기기기",
      "기계",
      "농산물",
      "의류"
    ],
    "imports": [
      "기계",
      "화학·의약품",
      "연료",
      "자동차 부품",
      "전자"
    ],
    "sectors": {
      "primary": 12,
      "secondary": 33,
      "tertiary": 55,
      "note": "취업 비중 근사(World Bank/ILO 2023: 농업~12%, 산업~33%, 서비스~55). 농업 고용 비중은 과거보다 줄었으나 EU 평균보다 여전히 높음."
    },
    "sources": [
      "CIA Factbook",
      "World Bank",
      "INS Romania"
    ],
    "confidence": "high"
  },
  {
    "id": "egypt",
    "country": "이집트",
    "ethnicity": [
      {
        "name": "이집트 아랍인",
        "pct": 99
      },
      {
        "name": "누비아·베두인·기타",
        "pct": 1
      }
    ],
    "currency": {
      "code": "EGP",
      "name": "이집트 파운드"
    },
    "culture": "나일강 문명의 후예로 아랍·이슬람 세계의 인구·문화 중심국 중 하나다. 수에즈 운하 통행료, 관광, 해외 송금, 천연가스·석유가 외화 원천이다. 카이로 대도시권과 농촌 격차가 크고 최근 통화 평가절하·인플레 압력이 있었다.",
    "languages": [
      {
        "name": "아랍어",
        "official": true
      }
    ],
    "climate": "대부분 사막성 기후로 극히 건조하다. 나일 계곡·삼각주와 지중해·홍해 연안에 인구가 집중된다. 여름 고온, 겨울 온화하다.",
    "education": {
      "literacy": 79,
      "tertiary": 38,
      "note": "성인 문해율 약 79%(World Bank 2022; 여성 더 낮음). 고등교육 총진학률(GER)~38% 규모는 크나 질·노동시장 연계 과제."
    },
    "exports": [
      "천연가스·석유",
      "금",
      "비료·화학",
      "과일·채소",
      "섬유·의류"
    ],
    "imports": [
      "밀·식량",
      "기계",
      "차량",
      "전자",
      "중간재·연료"
    ],
    "sectors": {
      "primary": 18,
      "secondary": 29,
      "tertiary": 53,
      "note": "취업 비중 근사(World Bank/ILO 2023: 농업~18%, 산업~29%, 서비스~53). 공공·비공식 서비스 비중 큼."
    },
    "sources": [
      "CIA Factbook",
      "World Bank",
      "CAPMAS Egypt"
    ],
    "confidence": "medium"
  },
  {
    "id": "czechia",
    "country": "체코",
    "ethnicity": [
      {
        "name": "체코인",
        "pct": 89
      },
      {
        "name": "모라비아인·슬로바키아인 등",
        "pct": 5
      },
      {
        "name": "기타(우크라이나·베트남 등)",
        "pct": 6
      }
    ],
    "currency": {
      "code": "CZK",
      "name": "체코 코루나"
    },
    "culture": "중부유럽의 제조 강국으로 자동차·기계·전자 공급망이 독일 경제와 긴밀하다. 프라하는 관광·IT 허브이며, 맥주·고전 음악 문화가 유명하다. EU·NATO 회원, 유로 미도입(통화 CZK 체코 코루나).",
    "languages": [
      {
        "name": "체코어",
        "official": true
      }
    ],
    "climate": "온대 대륙성 기후로 사계절이 뚜렷하고 겨울 추위·여름 온난이 특징이다.",
    "education": {
      "literacy": 99,
      "tertiary": 40,
      "note": "문해율 보편. 기술·공학 교육 전통이 강함."
    },
    "exports": [
      "자동차·부품",
      "기계",
      "전자·전기",
      "철강·금속",
      "플라스틱"
    ],
    "imports": [
      "기계·부품",
      "전자",
      "화학",
      "연료",
      "자동차 부품"
    ],
    "sectors": {
      "primary": 3,
      "secondary": 36,
      "tertiary": 61,
      "note": "취업 비중 근사. 제조업 고용 비중이 EU 내 최상위권."
    },
    "sources": [
      "CIA Factbook",
      "World Bank",
      "CZSO"
    ],
    "confidence": "high"
  },
  {
    "id": "chile",
    "country": "칠레",
    "ethnicity": [
      {
        "name": "백인·메스티소",
        "pct": 89
      },
      {
        "name": "마푸체 등 원주민",
        "pct": 10
      },
      {
        "name": "기타",
        "pct": 1
      }
    ],
    "currency": {
      "code": "CLP",
      "name": "칠레 페소"
    },
    "culture": "남미에서 상대적으로 안정된 시장경제·제도를 가진 국가로 세계 최대 구리 생산·수출국이다(구리·관련 광물이 상품수출의 약 절반 전후). 안데스와 긴 해안선, 와인·연어·과일 수출도 중요하다. 스페인어권이며 소득 불평등과 사회 시위 경험이 있다.",
    "languages": [
      {
        "name": "스페인어",
        "official": true
      }
    ],
    "climate": "남북으로 길어 기후 다양. 북부 아타카마 극건조, 중부 지중해성, 남부 서안 해양성·한랭 습윤이다.",
    "education": {
      "literacy": 97,
      "tertiary": 50,
      "note": "문해율 높음. 고등교육 진학률 높으나 비용·격차 이슈."
    },
    "exports": [
      "구리·광물",
      "리튬",
      "과일",
      "와인",
      "연어·수산물"
    ],
    "imports": [
      "원유·연료",
      "기계",
      "자동차",
      "전자",
      "화학"
    ],
    "sectors": {
      "primary": 6,
      "secondary": 22,
      "tertiary": 72,
      "note": "취업 비중 근사. 광업은 수출·GDP 핵심이나 고용 비중은 제한적."
    },
    "sources": [
      "CIA Factbook",
      "World Bank",
      "INE Chile"
    ],
    "confidence": "high"
  },
  {
    "id": "finland",
    "country": "핀란드",
    "ethnicity": [
      {
        "name": "핀란드인",
        "pct": 91
      },
      {
        "name": "스웨덴계 핀란드인",
        "pct": 5
      },
      {
        "name": "기타(러시아·이민 등)",
        "pct": 4
      }
    ],
    "currency": {
      "code": "EUR",
      "name": "유로"
    },
    "culture": "북유럽 복지·교육 강국으로 숲·호수 문화와 사우나, 디자인·게임이 유명하다. 기계·임산물·통신·청정기술 수출이 중요하며 NATO 가입(2023)으로 안보 지형이 바뀌었다. 스웨덴어도 공용어다.",
    "languages": [
      {
        "name": "핀란드어",
        "official": true
      },
      {
        "name": "스웨덴어",
        "official": true
      }
    ],
    "climate": "한랭 온대·아극 기후로 긴 겨울과 짧은 여름이 특징이다. 남부 해안은 상대적으로 온화하다.",
    "education": {
      "literacy": 99,
      "tertiary": 40,
      "note": "PISA 등으로 알려진 공교육 강국. 25–34세 고등교육 이수율은 OECD 평균 이하(~40% 전후, EAG). 문해·형평성 세계 상위. GER는 100% 상회(중복·성인학습 포함)."
    },
    "exports": [
      "기계·전기기기",
      "종이·펄프",
      "철강",
      "화학",
      "목재"
    ],
    "imports": [
      "원유·연료",
      "기계",
      "화학",
      "자동차",
      "전자"
    ],
    "sectors": {
      "primary": 4,
      "secondary": 21,
      "tertiary": 75,
      "note": "취업 비중 근사(World Bank/ILO 2023: 농업~4%, 산업~21%, 서비스~75)."
    },
    "sources": [
      "CIA Factbook",
      "World Bank",
      "Statistics Finland"
    ],
    "confidence": "high"
  },
  {
    "id": "portugal",
    "country": "포르투갈",
    "ethnicity": [
      {
        "name": "포르투갈인",
        "pct": 95
      },
      {
        "name": "기타(브라질·아프리카·유럽 이민 등)",
        "pct": 5
      }
    ],
    "currency": {
      "code": "EUR",
      "name": "유로"
    },
    "culture": "대항해 시대 유산을 가진 남유럽 국가로 가톨릭·해양 문화가 깊다. 관광, 포르투와인, 코르크, 신발·섬유, 재생에너지가 경제에 기여한다. 최근 디지털 노마드·부동산 유입과 주택 가격 이슈가 있다.",
    "languages": [
      {
        "name": "포르투갈어",
        "official": true
      }
    ],
    "climate": "지중해성·해양성 혼합. 남부 여름 건조·고온, 북부·대서양 연안은 더 습하고 온화하다.",
    "education": {
      "literacy": 96,
      "tertiary": 45,
      "note": "문해율 높음. 고등교육 확대, EU 평균 수준 접근."
    },
    "exports": [
      "차량·부품",
      "기계",
      "농식품·와인",
      "의류·신발",
      "석유제품"
    ],
    "imports": [
      "기계",
      "차량",
      "원유·연료",
      "전자",
      "화학"
    ],
    "sectors": {
      "primary": 3,
      "secondary": 25,
      "tertiary": 72,
      "note": "취업 비중 근사. 관광·서비스 고용 비중이 큼."
    },
    "sources": [
      "CIA Factbook",
      "World Bank",
      "INE Portugal"
    ],
    "confidence": "high"
  },
  {
    "id": "kazakhstan",
    "country": "카자흐스탄",
    "ethnicity": [
      {
        "name": "카자흐인",
        "pct": 71
      },
      {
        "name": "러시아인",
        "pct": 15
      },
      {
        "name": "우즈베크·우크라이나·위구르 등",
        "pct": 14
      }
    ],
    "currency": {
      "code": "KZT",
      "name": "카자흐스탄 텡게"
    },
    "culture": "중앙아시아 최대 영토 국가로 유목 전통·이슬람·소련 유산이 공존한다. 원유·가스·우라늄·금속 수출이 경제를 좌우하며 중국·러시아·유럽을 잇는 물류 요충이다. 카자흐어가 국가어(state language)이고, 러시아어는 국가기관에서 카자흐어와 함께 공식적으로 사용된다(헌법상 동등 사용).",
    "languages": [
      {
        "name": "카자흐어",
        "official": true
      },
      {
        "name": "러시아어",
        "official": true
      }
    ],
    "climate": "대륙성·건조 기후로 여름 고온, 겨울 한파가 심하다. 스텝·반사막이 넓다.",
    "education": {
      "literacy": 100,
      "tertiary": 55,
      "note": "소련 유산으로 문해율 사실상 보편. 고등교육 비중 높으나 질·기술 다양화 과제."
    },
    "exports": [
      "원유·가스",
      "구리·금속",
      "우라늄",
      "곡물",
      "화학"
    ],
    "imports": [
      "기계",
      "전자",
      "차량",
      "의약품",
      "소비재"
    ],
    "sectors": {
      "primary": 12,
      "secondary": 20,
      "tertiary": 68,
      "note": "취업 비중 근사(World Bank/ILO 2023: 농업~12%, 산업~20%, 서비스~68). 자원 수출 의존, 고용은 서비스·공공 비중 확대."
    },
    "sources": [
      "CIA Factbook",
      "World Bank",
      "Bureau of National Statistics KZ"
    ],
    "confidence": "high"
  },
  {
    "id": "peru",
    "country": "페루",
    "ethnicity": [
      {
        "name": "메스티소",
        "pct": 60
      },
      {
        "name": "원주민(케추아·아이마라 등)",
        "pct": 26
      },
      {
        "name": "백인",
        "pct": 6
      },
      {
        "name": "아프리카계·아시아계·기타",
        "pct": 8
      }
    ],
    "currency": {
      "code": "PEN",
      "name": "페루 솔"
    },
    "culture": "잉카 유산과 스페인 식민, 안데스·아마존·태평양 문화가 혼합된 국가다. 구리·금·아연 등 광업 수출이 총수출의 약 60% 전후를 차지하나 직접 고용 비중은 작다. 미식(세비체 등)으로 국제적 인지도가 높다. 스페인어와 케추아어 등이 공용어다.",
    "languages": [
      {
        "name": "스페인어",
        "official": true
      },
      {
        "name": "케추아어",
        "official": true
      },
      {
        "name": "아이마라어",
        "official": true
      }
    ],
    "climate": "태평양 연안은 사막·온난 건조, 안데스는 고산 한랭, 동부 아마존은 열대 우림으로 지형에 따른 기후 차가 극심하다.",
    "education": {
      "literacy": 94,
      "tertiary": 35,
      "note": "문해율 양호. 농촌·원주민 지역 교육 격차 존재."
    },
    "exports": [
      "구리",
      "금",
      "아연·납",
      "수산물·어분",
      "농산물(아보카도·커피)"
    ],
    "imports": [
      "원유·연료",
      "기계",
      "전자",
      "차량",
      "철강·화학"
    ],
    "sectors": {
      "primary": 24,
      "secondary": 16,
      "tertiary": 60,
      "note": "취업 비중 근사. 광업 수출 비중 크나 고용은 농업·서비스·비공식 부문 중심."
    },
    "sources": [
      "CIA Factbook",
      "World Bank",
      "INEI Peru"
    ],
    "confidence": "high"
  }
];

const COUNTRY_PROFILE_BY_ID = Object.fromEntries(
  (typeof COUNTRY_PROFILES !== "undefined" ? COUNTRY_PROFILES : []).map(p => [p.id, p])
);
