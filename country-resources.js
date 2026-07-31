/* ============================================================
   국가별 주요 원자재·자원 (경제력 Top50 대응)
   ------------------------------------------------------------
   항목: 자원명, 생산량·매장량(근사), 담당 회사, 본사 국가, 지분구조
   프로세스: 조사 에이전트 2팀 + 적대적 검수 에이전트 2팀
   출처 계열: USGS MCS, EIA, 각국 국영·상장사 공개자료, commodities.js 교차
   ⚠️ 교육·비교용 큐레이션. 연도·정의(확인매장 vs 자원량, 액체 vs 원유) 편차.
      회사 지분은 변동 가능. 제재국(이란 등) 수치는 불투명.
   감사: _adversarial_resources_1_25.json, _adversarial_resources_26_50.json
   ============================================================ */

const COUNTRY_RESOURCES = [
  {
    "id": "usa",
    "country": "미국",
    "resources": [
      {
        "name": "원유",
        "category": "에너지",
        "trade": ["생산","수출"],
        "production": {
          "text": "원유 약 1,300만 b/d·전체 액체 2,200만 b/d 규모 (세계 1위)",
          "rank": 1
        },
        "reserve": {
          "text": "확인매장 약 450–460억 bbl (세계 10위권)",
          "rank": 10
        },
        "note": "셰일·퍼미언 분지 중심. 스윙 생산국 역할.",
        "companies": [
          {
            "name": "ExxonMobil",
            "hqCountry": "미국",
            "role": "탐사·생산·정제·LNG",
            "ownership": "미국 상장 분산소유 (기관·연기금 중심)",
            "majorHolders": [
              {
                "holder": "Vanguard 등 기관",
                "country": "미국",
                "pct": null
              }
            ]
          },
          {
            "name": "Chevron",
            "hqCountry": "미국",
            "role": "탐사·생산·정제",
            "ownership": "미국 상장 분산소유",
            "majorHolders": [
              {
                "holder": "Vanguard·BlackRock 등",
                "country": "미국",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "천연가스",
        "category": "에너지",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 생산 약 1/4 수준 (세계 1위)",
          "rank": 1
        },
        "reserve": {
          "text": "확인매장 세계 상위권 (EIA 기준 수백 Tcf 규모)",
          "rank": 4
        },
        "note": "마셀러스·퍼미언 셰일. LNG 수출 확대.",
        "companies": [
          {
            "name": "EQT",
            "hqCountry": "미국",
            "role": "애팔래치아 가스 생산",
            "ownership": "미국 상장 분산소유",
            "majorHolders": []
          },
          {
            "name": "ExxonMobil·Chevron 등",
            "hqCountry": "미국",
            "role": "관련 분지 가스·NGL",
            "ownership": "민간 메이저·독립계 분산",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "석탄",
        "category": "에너지",
        "trade": ["생산","수출"],
        "production": {
          "text": "약 4.5–5억 t 규모 (세계 6위권, 2024년 러시아·호주에 근소하게 뒤짐)",
          "rank": 6
        },
        "reserve": {
          "text": "세계 최대급 확인매장 (파우더리버 등)",
          "rank": 1
        },
        "note": "발전·수출. 장기 수요 둔화 추세.",
        "companies": [
          {
            "name": "Peabody Energy",
            "hqCountry": "미국",
            "role": "노천·갱내 채탄",
            "ownership": "미국 상장 분산소유",
            "majorHolders": []
          },
          {
            "name": "Core Natural Resources (구 Arch Resources, 2025년 1월 CONSOL Energy와 합병)",
            "hqCountry": "미국",
            "role": "야금탄·발전탄",
            "ownership": "미국 상장 분산소유",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "구리",
        "category": "광물",
        "trade": ["생산"],
        "production": {
          "text": "약 110–120만 t (세계 5위권)",
          "rank": 5
        },
        "reserve": {
          "text": "애리조나·유타 등 대규모 매장 (세계 상위)",
          "rank": 5
        },
        "note": "모렌시 등 남서부 벨트. 전력·EV 수요 핵심.",
        "companies": [
          {
            "name": "Freeport-McMoRan",
            "hqCountry": "미국",
            "role": "모렌시 등 채광·선광",
            "ownership": "미국 상장. 모렌시 JV에 Sumitomo 지분",
            "majorHolders": [
              {
                "holder": "Freeport (모렌시)",
                "country": "미국",
                "pct": 72
              },
              {
                "holder": "Sumitomo",
                "country": "일본",
                "pct": 28
              }
            ]
          }
        ]
      },
      {
        "name": "희토류",
        "category": "광물",
        "trade": ["생산"],
        "production": {
          "text": "마운틴패스 중심, 중국 외 주요 생산 (세계 2위권)",
          "rank": 2
        },
        "reserve": {
          "text": "마운틴패스 등 확인매장 (세계 6–7위권; 중국·브라질·인도·호주 등이 상위)",
          "rank": 7
        },
        "note": "분리·정련은 아직 중국 의존 비중 큼. 내재화 추진.",
        "companies": [
          {
            "name": "MP Materials",
            "hqCountry": "미국",
            "role": "채광·농축·분리 확대",
            "ownership": "미국 상장 분산소유",
            "majorHolders": [
              {
                "holder": "기관 투자자",
                "country": "미국",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "옥수수",
        "category": "농산물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 생산 약 30% 전후 (세계 1위)",
          "rank": 1
        },
        "reserve": {
          "text": "농지·재고 기반 (매장 개념 N/A)",
          "rank": null
        },
        "note": "콘벨트. 사료·에탄올·수출 핵심.",
        "companies": [
          {
            "name": "Cargill·ADM 등 곡물메이저",
            "hqCountry": "미국",
            "role": "유통·가공·수출",
            "ownership": "민간 (Cargill 비상장 가족기업 등)",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "대두",
        "category": "농산물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 2위 (브라질과 양강)",
          "rank": 2
        },
        "reserve": {
          "text": "농지·재고 기반 (매장 개념 N/A)",
          "rank": null
        },
        "note": "중국 등 수출 의존 구조. 중서부 주산지.",
        "companies": [
          {
            "name": "가족농·영농기업 + 곡물메이저",
            "hqCountry": "미국",
            "role": "생산·유통",
            "ownership": "민간 농가 + 다국적 트레이더",
            "majorHolders": []
          }
        ]
      }
    ],
    "confidence": "high",
    "sources": [
      "EIA",
      "USGS MCS",
      "BP/EI Statistical Review",
      "회사 IR"
    ]
  },
  {
    "id": "china",
    "country": "중국",
    "resources": [
      {
        "name": "희토류",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 채광·분리 과반 이상 (세계 1위)",
          "rank": 1
        },
        "reserve": {
          "text": "세계 최대 매장권 (내몽골 바얀오보 등)",
          "rank": 1
        },
        "note": "중·경희토 쿼터·수출통제로 전략 무기화.",
        "companies": [
          {
            "name": "China Northern Rare Earth",
            "hqCountry": "중국",
            "role": "바얀오보 채광·분리",
            "ownership": "국유 지배",
            "majorHolders": [
              {
                "holder": "국유자본·지방국자",
                "country": "중국",
                "pct": null
              }
            ]
          },
          {
            "name": "China Rare Earth Group 등",
            "hqCountry": "중국",
            "role": "남부 이온흡착형·통합",
            "ownership": "국유 통합 그룹",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "석탄",
        "category": "에너지",
        "trade": ["생산","수입"],
        "production": {
          "text": "약 40억 t 이상 (세계 1위, 글로벌 과반 근접)",
          "rank": 1
        },
        "reserve": {
          "text": "세계 상위 매장 (산시·네이멍구 등)",
          "rank": 3
        },
        "note": "발전·제철 연료. 세계 최대 소비·생산국.",
        "companies": [
          {
            "name": "China Energy (Shenhua)",
            "hqCountry": "중국",
            "role": "채탄·발전 통합",
            "ownership": "국유 중앙기업",
            "majorHolders": [
              {
                "holder": "국무원 국자위",
                "country": "중국",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "금",
        "category": "광물",
        "trade": ["생산"],
        "production": {
          "text": "세계 1위 생산",
          "rank": 1
        },
        "reserve": {
          "text": "산둥 자오둥 등 대규모 (세계 상위)",
          "rank": 5
        },
        "note": "자오둥 금광대· Zijin 해외 자산 병행.",
        "companies": [
          {
            "name": "Shandong Gold",
            "hqCountry": "중국",
            "role": "산둥 채광",
            "ownership": "국유·지방국자 중심",
            "majorHolders": []
          },
          {
            "name": "Zijin Mining",
            "hqCountry": "중국",
            "role": "국내·해외 금·구리",
            "ownership": "민간 성격 강하나 정책 연계",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "리튬",
        "category": "광물",
        "trade": ["생산","수입"],
        "production": {
          "text": "경암·염호 합산 세계 3위권 (정련은 1위권)",
          "rank": 3
        },
        "reserve": {
          "text": "칭하이·장시 등 + 해외 자산",
          "rank": 5
        },
        "note": "배터리 정련·양극재 세계 지배. 원광 수입 병행.",
        "companies": [
          {
            "name": "Ganfeng Lithium",
            "hqCountry": "중국",
            "role": "채광·정련·배터리 소재",
            "ownership": "중국 상장 (민간 중심)",
            "majorHolders": []
          },
          {
            "name": "Tianqi Lithium",
            "hqCountry": "중국",
            "role": "호주 Greenbushes 지분 등",
            "ownership": "중국 상장",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "원유",
        "category": "에너지",
        "trade": ["생산","수입"],
        "production": {
          "text": "약 400만 b/d 전후 (세계 5–6위권)",
          "rank": 6
        },
        "reserve": {
          "text": "다칭·창칭 등 (세계 중상위, 수입 의존 큼)",
          "rank": 13
        },
        "note": "세계 최대 원유 수입국. 해외 NOC 자산 확대.",
        "companies": [
          {
            "name": "PetroChina (CNPC)",
            "hqCountry": "중국",
            "role": "육상 생산·파이프",
            "ownership": "국유 지배 상장",
            "majorHolders": [
              {
                "holder": "CNPC (국유)",
                "country": "중국",
                "pct": null
              }
            ]
          },
          {
            "name": "Sinopec·CNOOC",
            "hqCountry": "중국",
            "role": "정제·해상 생산",
            "ownership": "국유 지배",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "철광석",
        "category": "광물",
        "trade": ["생산","수입"],
        "production": {
          "text": "국내 생산 세계 3위권이나 저품위·수입 의존",
          "rank": 3
        },
        "reserve": {
          "text": "안산 등 대규모 저품위 매장",
          "rank": 4
        },
        "note": "호주·브라질 고품위 수입 필수. 제철 세계 1위.",
        "companies": [
          {
            "name": "Ansteel·Baowu 계열",
            "hqCountry": "중국",
            "role": "국내 광산·제철 통합",
            "ownership": "국유",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "흑연·텅스텐 등 전략광물",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "천연흑연·텅스텐·안티몬 등 다수 세계 1위",
          "rank": 1
        },
        "reserve": {
          "text": "다수 품목 세계 최대 매장권",
          "rank": 1
        },
        "note": "정련·중간재 수출 통제 가능. 공급망 레버리지.",
        "companies": [
          {
            "name": "국유·지방 광산 SOE 다수",
            "hqCountry": "중국",
            "role": "채광·정련",
            "ownership": "국유 중심",
            "majorHolders": []
          }
        ]
      }
    ],
    "confidence": "high",
    "sources": [
      "USGS MCS",
      "EIA",
      "중국 통계·SOE IR",
      "IEA"
    ]
  },
  {
    "id": "germany",
    "country": "독일",
    "resources": [
      {
        "name": "갈탄(리그나이트)",
        "category": "에너지",
        "trade": ["생산"],
        "production": {
          "text": "갈탄(리그나이트) 세계 1–2위권·EU 최대",
          "rank": 1
        },
        "reserve": {
          "text": "라인란트·루사티아 등 대규모",
          "rank": 5
        },
        "note": "2030년대 탈석탄 목표로 단계 축소. 에너지 안보 쟁점.",
        "companies": [
          {
            "name": "RWE",
            "hqCountry": "독일",
            "role": "갈탄 채광·발전",
            "ownership": "독일 상장 분산소유",
            "majorHolders": [
              {
                "holder": "기관 투자자",
                "country": "독일·해외",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "칼륨(포타시)",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "유럽 주요 생산 (세계 중상위)",
          "rank": 5
        },
        "reserve": {
          "text": "중부·북부 암염·칼리 층",
          "rank": 5
        },
        "note": "비료 원료. 에너지·화학 연계.",
        "companies": [
          {
            "name": "K+S",
            "hqCountry": "독일",
            "role": "칼리·마그네슘염 채광",
            "ownership": "독일 상장 분산소유",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "암염·산업용 광물",
        "category": "광물",
        "trade": ["생산"],
        "production": {
          "text": "암염·석고 등 유럽 유력 생산",
          "rank": null
        },
        "reserve": {
          "text": "북독 암염층 풍부",
          "rank": null
        },
        "note": "화학산업 원료. 전략 광물 자체는 수입 의존.",
        "companies": [
          {
            "name": "K+S·화학 계열",
            "hqCountry": "독일",
            "role": "채광·가공",
            "ownership": "민간 상장",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "전략 원자재 (수입 의존)",
        "category": "전략의존",
        "trade": ["수입"],
        "production": {
          "text": "국내 채광 미미 (원유·가스·희토·구리 등 거의 전량 수입)",
          "rank": null
        },
        "reserve": {
          "text": "본토 매장 제한적",
          "rank": null
        },
        "note": "제조·자동차·화학 강국이나 에너지·핵심광물 대외 의존. 노르트스트림 이후 LNG·재생 전환.",
        "companies": [
          {
            "name": "BASF",
            "hqCountry": "독일",
            "role": "화학·중간재 (원료 수입 가공)",
            "ownership": "독일 상장 분산소유",
            "majorHolders": []
          },
          {
            "name": "Thyssenkrupp",
            "hqCountry": "독일",
            "role": "철강·엔지니어링 (철광·석탄 수입)",
            "ownership": "상장 (일부 공적 지분 논의 이력)",
            "majorHolders": []
          }
        ]
      }
    ],
    "confidence": "medium",
    "sources": [
      "BGR Germany",
      "USGS",
      "RWE/K+S IR",
      "IEA"
    ]
  },
  {
    "id": "india",
    "country": "인도",
    "resources": [
      {
        "name": "석탄",
        "category": "에너지",
        "trade": ["생산","수입"],
        "production": {
          "text": "약 9–10억 t 규모 (세계 2위)",
          "rank": 2
        },
        "reserve": {
          "text": "자리아·탈처 등 대규모 (세계 상위)",
          "rank": 5
        },
        "note": "발전 연료 핵심. 수입 발전탄도 병행.",
        "companies": [
          {
            "name": "Coal India",
            "hqCountry": "인도",
            "role": "채탄 (세계 최대 석탄기업급)",
            "ownership": "인도 정부 과반 국영",
            "majorHolders": [
              {
                "holder": "인도 중앙정부",
                "country": "인도",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "철광석",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "약 2.5–2.8억 t (세계 4위권)",
          "rank": 4
        },
        "reserve": {
          "text": "오디샤·차티스가르·고아 등",
          "rank": 5
        },
        "note": "국내 제철 + 수출. 바일라딜라 고품위.",
        "companies": [
          {
            "name": "NMDC",
            "hqCountry": "인도",
            "role": "국영 철광 채광",
            "ownership": "인도 정부 지배",
            "majorHolders": [
              {
                "holder": "인도 정부",
                "country": "인도",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "보크사이트",
        "category": "광물",
        "trade": ["생산"],
        "production": {
          "text": "세계 5위권",
          "rank": 5
        },
        "reserve": {
          "text": "오디샤 등 대규모",
          "rank": 5
        },
        "note": "알루미나·알루미늄 산업 연계.",
        "companies": [
          {
            "name": "NALCO",
            "hqCountry": "인도",
            "role": "보크사이트·알루미나·알루미늄",
            "ownership": "국영",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "밀",
        "category": "농산물",
        "trade": ["생산"],
        "production": {
          "text": "세계 2위권",
          "rank": 2
        },
        "reserve": {
          "text": "농지·공공 비축 (매장 N/A)",
          "rank": null
        },
        "note": "펀자브·하리아나. 식량안보 조달.",
        "companies": [
          {
            "name": "소농 + FCI 조달",
            "hqCountry": "인도",
            "role": "생산·수매·비축",
            "ownership": "소농 분산 + 국영 유통",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "우라늄",
        "category": "에너지",
        "trade": ["생산"],
        "production": {
          "text": "소규모 (세계 10위권)",
          "rank": 9
        },
        "reserve": {
          "text": "자두구다 등 제한적",
          "rank": null
        },
        "note": "전량 자국 원전용. 수입·국제협력 병행.",
        "companies": [
          {
            "name": "UCIL",
            "hqCountry": "인도",
            "role": "채광·정련",
            "ownership": "국영 100%",
            "majorHolders": [
              {
                "holder": "인도 정부",
                "country": "인도",
                "pct": 100
              }
            ]
          }
        ]
      },
      {
        "name": "원유·가스 (수입 의존)",
        "category": "에너지",
        "trade": ["수입"],
        "production": {
          "text": "국내 생산 제한, 수요의 80%+ 원유 수입",
          "rank": null
        },
        "reserve": {
          "text": "뭄바이 하이 등 소규모",
          "rank": null
        },
        "note": "에너지 안보 취약. ONGC·해외 자산 확보 추진.",
        "companies": [
          {
            "name": "ONGC",
            "hqCountry": "인도",
            "role": "국내·해외 탐사생산",
            "ownership": "국영 지배",
            "majorHolders": [
              {
                "holder": "인도 정부",
                "country": "인도",
                "pct": null
              }
            ]
          },
          {
            "name": "Reliance Industries",
            "hqCountry": "인도",
            "role": "KG-D6 가스·정제",
            "ownership": "암바니 일가 지배 상장",
            "majorHolders": [
              {
                "holder": "Mukesh Ambani 일가",
                "country": "인도",
                "pct": null
              }
            ]
          }
        ]
      }
    ],
    "confidence": "high",
    "sources": [
      "USGS",
      "Coal India",
      "IEA",
      "인도 광업부"
    ]
  },
  {
    "id": "japan",
    "country": "일본",
    "resources": [
      {
        "name": "전략 원자재 (거의 전량 수입)",
        "category": "전략의존",
        "trade": ["수입"],
        "production": {
          "text": "원유·LNG·철광·구리·희토 등 국내 채광 미미",
          "rank": null
        },
        "reserve": {
          "text": "본토 상업 매장 극소",
          "rank": null
        },
        "note": "자원 빈국. 종합상사·JOGMEC·비축으로 공급망 관리. 2010 희토 쇼크 이후 다변화.",
        "companies": [
          {
            "name": "JOGMEC",
            "hqCountry": "일본",
            "role": "자원 탐사 지원·비축·지분 참여",
            "ownership": "일본 정부 산하 독립행정법인",
            "majorHolders": [
              {
                "holder": "일본 정부",
                "country": "일본",
                "pct": 100
              }
            ]
          },
          {
            "name": "Mitsubishi Corp·Mitsui&Co 등",
            "hqCountry": "일본",
            "role": "해외 광산·LNG 지분·트레이딩",
            "ownership": "일본 상장 분산소유",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "원유·LNG (해외 자산)",
        "category": "에너지",
        "trade": ["수입"],
        "production": {
          "text": "국내 생산 무시 가능 수준. 해외 지분 생산 보유",
          "rank": null
        },
        "reserve": {
          "text": "국내 매장 미미",
          "rank": null
        },
        "note": "LNG 세계 주요 수입국. 호주·중동·미국 공급.",
        "companies": [
          {
            "name": "INPEX",
            "hqCountry": "일본",
            "role": "이치스 LNG 등 해외 E&P",
            "ownership": "상장, 정부·JOGMEC 영향력",
            "majorHolders": [
              {
                "holder": "일본 정부 관련",
                "country": "일본",
                "pct": null
              }
            ]
          },
          {
            "name": "JX (Eneos)",
            "hqCountry": "일본",
            "role": "정제·석유제품·일부 E&P",
            "ownership": "일본 상장",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "석탄 (잔존·수입)",
        "category": "에너지",
        "trade": ["수입"],
        "production": {
          "text": "국내 채탄 사실상 종료, 전량 수입",
          "rank": null
        },
        "reserve": {
          "text": "상업 채굴 종료",
          "rank": null
        },
        "note": "제철·발전용 석탄 호주 등 수입.",
        "companies": [
          {
            "name": "JFE·일본제철 등",
            "hqCountry": "일본",
            "role": "야금탄 장기 계약·해외 지분",
            "ownership": "상장",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "비철 정련·소재",
        "category": "광물",
        "trade": ["생산","수입"],
        "production": {
          "text": "원광 수입 후 구리·니켈·희토 정련·자석 소재 강점",
          "rank": null
        },
        "reserve": {
          "text": "원광 매장 N/A (가공 허브)",
          "rank": null
        },
        "note": "산업 사슬 하류. 전략은 '보유'보다 '가공·비축'.",
        "companies": [
          {
            "name": "Sumitomo Metal Mining",
            "hqCountry": "일본",
            "role": "니켈·구리 정련, 해외 광산 지분",
            "ownership": "스미토모 계열 상장",
            "majorHolders": []
          },
          {
            "name": "JX·DOWA 등",
            "hqCountry": "일본",
            "role": "비철 제련·재활용",
            "ownership": "상장",
            "majorHolders": []
          }
        ]
      }
    ],
    "confidence": "high",
    "sources": [
      "JOGMEC",
      "METI",
      "USGS",
      "회사 IR"
    ]
  },
  {
    "id": "uk",
    "country": "영국",
    "resources": [
      {
        "name": "원유 (북해)",
        "category": "에너지",
        "trade": ["생산","수입"],
        "production": {
          "text": "북해 감산 추세, 순수입 전환 (세계 20위권)",
          "rank": null
        },
        "reserve": {
          "text": "북해 잔존 매장 제한·성숙 유전",
          "rank": null
        },
        "note": "1970–90년대 대비 생산 크게 감소. 에너지 안보 이슈.",
        "companies": [
          {
            "name": "bp",
            "hqCountry": "영국",
            "role": "북해·글로벌 E&P",
            "ownership": "영국 상장 분산소유",
            "majorHolders": [
              {
                "holder": "기관 투자자",
                "country": "영국·미국 등",
                "pct": null
              }
            ]
          },
          {
            "name": "Shell",
            "hqCountry": "영국",
            "role": "북해·LNG·글로벌 통합",
            "ownership": "영국 본사 상장 (구 영·네 이원)",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "천연가스 (북해)",
        "category": "에너지",
        "trade": ["생산","수입"],
        "production": {
          "text": "국내 생산 감소, 수입·LNG 비중 확대",
          "rank": null
        },
        "reserve": {
          "text": "성숙 가스전",
          "rank": null
        },
        "note": "대륙붕 잔존 + 노르웨이 파이프·LNG.",
        "companies": [
          {
            "name": "Shell·bp·Centrica 등",
            "hqCountry": "영국",
            "role": "생산·공급",
            "ownership": "상장·민간",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "석탄 (역사·잔존)",
        "category": "에너지",
        "trade": ["수입"],
        "production": {
          "text": "사실상 상업 채탄 종료",
          "rank": null
        },
        "reserve": {
          "text": "역사적 대규모, 현재 미가동",
          "rank": null
        },
        "note": "산업혁명 기반 자원. 현재는 전량 수입 대체.",
        "companies": [
          {
            "name": "역사 국유화 탄광 (현재 사실상 종료)",
            "hqCountry": "영국",
            "role": "과거 국내 채탄 — 현재 미미",
            "ownership": "민간 소규모·수입 의존",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "글로벌 광업 본사·금융",
        "category": "전략의존",
        "trade": ["수입"],
        "production": {
          "text": "국내 채광 미미. 해외 자산 지배력은 큼",
          "rank": null
        },
        "reserve": {
          "text": "본토 전략광물 제한",
          "rank": null
        },
        "note": "런던 상장·본사로 글로벌 자원 현금흐름 유치.",
        "companies": [
          {
            "name": "Rio Tinto",
            "hqCountry": "영국·호주",
            "role": "철광·알루미늄·구리 글로벌",
            "ownership": "이원 상장 분산소유",
            "majorHolders": [
              {
                "holder": "기관 투자자",
                "country": "다국적",
                "pct": null
              }
            ]
          },
          {
            "name": "Anglo American",
            "hqCountry": "영국",
            "role": "구리·프리미엄 철광석·작물영양 (백금 부문은 2025년 5월 Valterra Platinum으로 분사·잔여 지분 매각, Teck Resources와의 합병으로 Anglo Teck 출범 절차 진행 중)",
            "ownership": "런던 상장",
            "majorHolders": []
          },
          {
            "name": "Glencore (상장 런던)",
            "hqCountry": "스위스·저지",
            "role": "광업·트레이딩",
            "ownership": "런던 상장, 스위스 영업 본거",
            "majorHolders": []
          }
        ]
      }
    ],
    "confidence": "medium",
    "sources": [
      "NSTA UK",
      "EIA",
      "bp/Shell IR",
      "USGS"
    ]
  },
  {
    "id": "france",
    "country": "프랑스",
    "resources": [
      {
        "name": "우라늄 (해외·정련)",
        "category": "에너지",
        "trade": ["수입"],
        "production": {
          "text": "본토 채광 종료. 니제르 등 해외 + 정련·연료 강점",
          "rank": null
        },
        "reserve": {
          "text": "본토 잔존 제한, 해외 자산 중심",
          "rank": null
        },
        "note": "원전 전력 비중 세계 최고 수준. 핵연료 사이클 전략 자산.",
        "companies": [
          {
            "name": "Orano",
            "hqCountry": "프랑스",
            "role": "우라늄 채광·전환·재처리",
            "ownership": "프랑스 정부 지배 국영 (지분 약 90%)",
            "majorHolders": [
              {
                "holder": "프랑스 정부",
                "country": "프랑스",
                "pct": 90.3
              },
              {
                "holder": "JNFL·MHI 등",
                "country": "일본",
                "pct": 9.7
              }
            ]
          },
          {
            "name": "EDF",
            "hqCountry": "프랑스",
            "role": "원전 운영·연료 수요",
            "ownership": "사실상 국유",
            "majorHolders": [
              {
                "holder": "프랑스 정부",
                "country": "프랑스",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "원유·가스 (해외 메이저)",
        "category": "에너지",
        "trade": ["수입"],
        "production": {
          "text": "본토 생산 미미. TotalEnergies 글로벌 생산 대규모",
          "rank": null
        },
        "reserve": {
          "text": "본토 매장 미미",
          "rank": null
        },
        "note": "아프리카·중동·미주 자산. LNG·재생 전환 병행.",
        "companies": [
          {
            "name": "TotalEnergies",
            "hqCountry": "프랑스",
            "role": "통합 에너지 메이저",
            "ownership": "프랑스 상장 분산소유",
            "majorHolders": [
              {
                "holder": "기관 투자자",
                "country": "프랑스·해외",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "밀",
        "category": "농산물",
        "trade": ["생산","수출"],
        "production": {
          "text": "EU 최대 밀 생산국 (세계 5–6위권)",
          "rank": 6
        },
        "reserve": {
          "text": "농지 기반 (매장 N/A)",
          "rank": null
        },
        "note": "보스 평원 등. 수출 농산물 강국.",
        "companies": [
          {
            "name": "협동조합·영농기업",
            "hqCountry": "프랑스",
            "role": "생산·수집",
            "ownership": "농가·협동조합",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "보크사이트 (역사)·알루미늄",
        "category": "광물",
        "trade": ["수입"],
        "production": {
          "text": "본토 보크사이트 잔존 미미, 알루미늄 산업·재활용",
          "rank": null
        },
        "reserve": {
          "text": "역사 산지, 현재 수입 원료",
          "rank": null
        },
        "note": "보크사이트 어원(Les Baux). 현재 전략은 재활용·해외.",
        "companies": [
          {
            "name": "Rio Tinto Aluminium (유럽 사업)",
            "hqCountry": "영국·호주",
            "role": "제련·가공",
            "ownership": "다국적",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "전략광물 수입 의존",
        "category": "전략의존",
        "trade": ["수입"],
        "production": {
          "text": "희토·리튬·구리 등 국내 채광 제한",
          "rank": null
        },
        "reserve": {
          "text": "일부 탐사 프로젝트 진행",
          "rank": null
        },
        "note": "EU 핵심원자재법 대응. 국내 광산 재개 논쟁.",
        "companies": [
          {
            "name": "Eramet",
            "hqCountry": "프랑스",
            "role": "망간·니켈 등 해외 광업",
            "ownership": "상장, 정부 지분 보유",
            "majorHolders": [
              {
                "holder": "프랑스 정부 관련",
                "country": "프랑스",
                "pct": null
              }
            ]
          }
        ]
      }
    ],
    "confidence": "medium",
    "sources": [
      "Orano",
      "TotalEnergies IR",
      "USGS",
      "IEA"
    ]
  },
  {
    "id": "italy",
    "country": "이탈리아",
    "resources": [
      {
        "name": "천연가스",
        "category": "에너지",
        "trade": ["생산","수입"],
        "production": {
          "text": "국내 소규모, 수요 대부분 수입 (알제리·아제르·LNG)",
          "rank": null
        },
        "reserve": {
          "text": "아드리아·포 평야 잔존 제한",
          "rank": null
        },
        "note": "러시아 의존 축소 후 다변화. Eni 핵심.",
        "companies": [
          {
            "name": "Eni",
            "hqCountry": "이탈리아",
            "role": "국내·아프리카·글로벌 E&P",
            "ownership": "이탈리아 정부 유의미 지분 상장",
            "majorHolders": [
              {
                "holder": "이탈리아 정부(MEF/Cassa)",
                "country": "이탈리아",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "원유",
        "category": "에너지",
        "trade": ["생산","수입"],
        "production": {
          "text": "국내 소량, 대부분 수입·Eni 해외 생산",
          "rank": null
        },
        "reserve": {
          "text": "본토·시칠리아 소규모",
          "rank": null
        },
        "note": "정제 허브(사로므 등) 역할.",
        "companies": [
          {
            "name": "Eni",
            "hqCountry": "이탈리아",
            "role": "탐사생산·정제",
            "ownership": "정부 지분 + 시장",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "대리석·산업용 광물",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "카라라 대리석 세계 유명 산지",
          "rank": null
        },
        "reserve": {
          "text": "토스카나 등",
          "rank": null
        },
        "note": "전략광물보다 건축·문화 수출 품목.",
        "companies": [
          {
            "name": "현지 채석 기업 다수",
            "hqCountry": "이탈리아",
            "role": "채석·가공",
            "ownership": "민간 중소",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "전략 원자재 의존",
        "category": "전략의존",
        "trade": ["수입"],
        "production": {
          "text": "핵심광물·에너지 대외 의존 높음",
          "rank": null
        },
        "reserve": {
          "text": "본토 제한",
          "rank": null
        },
        "note": "제조·기계 강국이나 1차 자원 빈약.",
        "companies": [
          {
            "name": "Eni·Edison 등",
            "hqCountry": "이탈리아",
            "role": "에너지 조달",
            "ownership": "상장·혼합",
            "majorHolders": []
          }
        ]
      }
    ],
    "confidence": "medium",
    "sources": [
      "Eni IR",
      "IEA",
      "USGS"
    ]
  },
  {
    "id": "russia",
    "country": "러시아",
    "resources": [
      {
        "name": "천연가스",
        "category": "에너지",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 2위 생산 (약 600–700 Bcm대)",
          "rank": 2
        },
        "reserve": {
          "text": "확인매장 세계 1위 (약 1,600–1,700 Tcf 규모)",
          "rank": 1
        },
        "note": "야말·우렌고이. 유럽 파이프 축소 후 아시아·LNG 전환.",
        "companies": [
          {
            "name": "Gazprom",
            "hqCountry": "러시아",
            "role": "생산·파이프 수출",
            "ownership": "러시아 정부 지배 국영",
            "majorHolders": [
              {
                "holder": "러시아 연방 정부",
                "country": "러시아",
                "pct": null
              }
            ]
          },
          {
            "name": "Novatek",
            "hqCountry": "러시아",
            "role": "LNG (야말·아크틱)",
            "ownership": "민간 과두 + 정부 연계",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "원유",
        "category": "에너지",
        "trade": ["생산","수출"],
        "production": {
          "text": "약 1,000–1,050만 b/d 규모 (세계 2–3위권)",
          "rank": 3
        },
        "reserve": {
          "text": "서시베리아 등 세계 상위 매장",
          "rank": 8
        },
        "note": "제재 하 할인 수출·그림자 선단. 중국·인도 판로.",
        "companies": [
          {
            "name": "Rosneft",
            "hqCountry": "러시아",
            "role": "최대 국영 석유",
            "ownership": "국영 지배",
            "majorHolders": [
              {
                "holder": "Rosneftegaz/정부",
                "country": "러시아",
                "pct": null
              }
            ]
          },
          {
            "name": "Lukoil",
            "hqCountry": "러시아",
            "role": "민간 대형 석유",
            "ownership": "민간 (제재 영향)",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "니켈·팔라듐(PGM)",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "팔라듐 세계 1위권·니켈 세계 상위(3–5위권, 노릴스크)",
          "rank": 2
        },
        "reserve": {
          "text": "노릴스크-탈나흐 초대규모",
          "rank": 2
        },
        "note": "촉매·배터리·반도체 소재 공급 레버리지.",
        "companies": [
          {
            "name": "Nornickel",
            "hqCountry": "러시아",
            "role": "니켈·구리·PGM·코발트",
            "ownership": "과두 자본 지배",
            "majorHolders": [
              {
                "holder": "Vladimir Potanin 등",
                "country": "러시아",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "금",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 2위 (호주와 경합)",
          "rank": 2
        },
        "reserve": {
          "text": "시베리아·극동 대규모",
          "rank": 3
        },
        "note": "중앙은행 매입·수출. Polyus 등.",
        "companies": [
          {
            "name": "Polyus",
            "hqCountry": "러시아",
            "role": "금 채광",
            "ownership": "러시아 자본",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "석탄",
        "category": "에너지",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 4위 (2024년 476Mt, 호주·미국과 근소한 차), 수출 강국",
          "rank": 4
        },
        "reserve": {
          "text": "쿠즈바스 등 대규모",
          "rank": 2
        },
        "note": "아시아 수출. 물류·제재 제약.",
        "companies": [
          {
            "name": "SUEK",
            "hqCountry": "러시아",
            "role": "채탄·수출",
            "ownership": "민간 과두",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "밀",
        "category": "농산물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 최대 밀 수출국 중 하나 (생산 3위권)",
          "rank": 3
        },
        "reserve": {
          "text": "흑토 지대 농지 (매장 N/A)",
          "rank": null
        },
        "note": "수출 쿼터·관세. 중동·아프리카·아시아 식량 영향.",
        "companies": [
          {
            "name": "대형 아그로홀딩",
            "hqCountry": "러시아",
            "role": "생산·수출",
            "ownership": "민간 + 국가 통제",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "우라늄·원자력 연료",
        "category": "에너지",
        "trade": ["생산","수출"],
        "production": {
          "text": "채광 중상위, 농축·수출 세계 유력",
          "rank": 6
        },
        "reserve": {
          "text": "중상위 매장",
          "rank": 5
        },
        "note": "Rosatom 연료 사이클·원전 수출.",
        "companies": [
          {
            "name": "Rosatom (ARMZ)",
            "hqCountry": "러시아",
            "role": "우라늄·농축·원전",
            "ownership": "국영 100%",
            "majorHolders": [
              {
                "holder": "러시아 정부",
                "country": "러시아",
                "pct": 100
              }
            ]
          }
        ]
      }
    ],
    "confidence": "high",
    "sources": [
      "EIA",
      "USGS",
      "BP/EI Review",
      "회사·국영 발표"
    ]
  },
  {
    "id": "brazil",
    "country": "브라질",
    "resources": [
      {
        "name": "철광석",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "약 4억 t 전후 (세계 2위)",
          "rank": 2
        },
        "reserve": {
          "text": "카라자스 등 세계 상위 고품위",
          "rank": 2
        },
        "note": "중국 수출 핵심. Vale 중심.",
        "companies": [
          {
            "name": "Vale",
            "hqCountry": "브라질",
            "role": "철광·니켈 채광·수출",
            "ownership": "브라질 상장 분산소유 (정부 황금주 이력)",
            "majorHolders": [
              {
                "holder": "기관·연금 분산",
                "country": "브라질·해외",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "대두",
        "category": "농산물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 1위",
          "rank": 1
        },
        "reserve": {
          "text": "세라두·마투그로수 농지",
          "rank": null
        },
        "note": "중국 최대 공급원. 삼림·토지 이슈.",
        "companies": [
          {
            "name": "대규모 영농 + Cargill·ADM·COFCO",
            "hqCountry": "브라질",
            "role": "생산·수출 유통",
            "ownership": "현지 농기업 + 다국적 트레이더",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "원유",
        "category": "에너지",
        "trade": ["생산","수출"],
        "production": {
          "text": "약 350–400만 b/d (세계 8–9위권, 심해 프리솔트)",
          "rank": 8
        },
        "reserve": {
          "text": "투피 등 프리솔트 대규모",
          "rank": 15
        },
        "note": "자급+수출 확대. Petrobras.",
        "companies": [
          {
            "name": "Petrobras",
            "hqCountry": "브라질",
            "role": "심해 생산·정제",
            "ownership": "연방 정부 지배 상장",
            "majorHolders": [
              {
                "holder": "브라질 연방정부",
                "country": "브라질",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "보크사이트",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 4위권",
          "rank": 4
        },
        "reserve": {
          "text": "파라 트롬베타스 등",
          "rank": 3
        },
        "note": "알루미나·알루미늄 연계.",
        "companies": [
          {
            "name": "MRN (Mineração Rio do Norte)",
            "hqCountry": "브라질",
            "role": "보크사이트 채광",
            "ownership": "현지·다국적 합작",
            "majorHolders": [
              {
                "holder": "Glencore",
                "country": "스위스",
                "pct": 45
              },
              {
                "holder": "South32",
                "country": "호주",
                "pct": 33
              },
              {
                "holder": "Rio Tinto",
                "country": "영국·호주",
                "pct": 12
              },
              {
                "holder": "CBA",
                "country": "브라질",
                "pct": 10
              }
            ]
          }
        ]
      },
      {
        "name": "니오븀",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 생산 약 90% 수준 (사실상 독점)",
          "rank": 1
        },
        "reserve": {
          "text": "아라샤 등 세계 최대",
          "rank": 1
        },
        "note": "고강도 강·초전도. 전략 광물.",
        "companies": [
          {
            "name": "CBMM",
            "hqCountry": "브라질",
            "role": "니오븀 채광·가공",
            "ownership": "Moreira Salles 가문 중심 + 중국·일본 소수지분 이력",
            "majorHolders": [
              {
                "holder": "Moreira Salles 계열",
                "country": "브라질",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "리튬",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "미나스 경암 리튬 급성장 (세계 6위, USGS 2024년 약 1만t)",
          "rank": 6
        },
        "reserve": {
          "text": "미나스제라이스 벨트",
          "rank": 8
        },
        "note": "배터리 공급망 신규 축.",
        "companies": [
          {
            "name": "Sigma Lithium 등",
            "hqCountry": "캐나다·브라질",
            "role": "경암 리튬 개발",
            "ownership": "외국·현지 자본",
            "majorHolders": []
          }
        ]
      }
    ],
    "confidence": "high",
    "sources": [
      "USGS",
      "Vale/Petrobras IR",
      "CONAB",
      "EIA"
    ]
  },
  {
    "id": "canada",
    "country": "캐나다",
    "resources": [
      {
        "name": "원유 (오일샌드)",
        "category": "에너지",
        "trade": ["생산","수출"],
        "production": {
          "text": "약 500–600만 b/d (세계 4위)",
          "rank": 4
        },
        "reserve": {
          "text": "오일샌드 포함 세계 3위권 매장",
          "rank": 3
        },
        "note": "애서배스카. 파이프·해안 수출 병목 이슈.",
        "companies": [
          {
            "name": "Suncor",
            "hqCountry": "캐나다",
            "role": "오일샌드·정제",
            "ownership": "캐나다 상장 분산소유",
            "majorHolders": []
          },
          {
            "name": "Canadian Natural Resources (CNRL)",
            "hqCountry": "캐나다",
            "role": "오일샌드·재래",
            "ownership": "상장 분산소유",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "우라늄",
        "category": "에너지",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 2위권 (카자흐 다음)",
          "rank": 2
        },
        "reserve": {
          "text": "애서배스카 분지 고품위 세계 최상",
          "rank": 3
        },
        "note": "시가 레이크·맥아더리버.",
        "companies": [
          {
            "name": "Cameco",
            "hqCountry": "캐나다",
            "role": "채광·연료 서비스",
            "ownership": "캐나다 상장",
            "majorHolders": [
              {
                "holder": "기관 투자자",
                "country": "캐나다·미국",
                "pct": null
              }
            ]
          },
          {
            "name": "Orano (합작)",
            "hqCountry": "프랑스",
            "role": "시가 레이크 등 지분",
            "ownership": "프랑스 국영",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "칼리(포타시)",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 최대 수출·생산 강국 (세계 1–2위)",
          "rank": 1
        },
        "reserve": {
          "text": "서스캐처원 세계 최대 매장",
          "rank": 1
        },
        "note": "세계 비료 안보 핵심.",
        "companies": [
          {
            "name": "Nutrien",
            "hqCountry": "캐나다",
            "role": "칼리·질소 비료",
            "ownership": "상장 분산소유",
            "majorHolders": []
          },
          {
            "name": "Mosaic (일부 캐나다 자산)",
            "hqCountry": "미국",
            "role": "칼리 채광",
            "ownership": "미국 상장",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "니켈",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 5–6위권 (서드베리·래브라도)",
          "rank": 6
        },
        "reserve": {
          "text": "세계 상위",
          "rank": 5
        },
        "note": "배터리·스테인리스. 부산물 코발트·PGM.",
        "companies": [
          {
            "name": "Vale Canada",
            "hqCountry": "브라질",
            "role": "서드베리 니켈",
            "ownership": "Vale 자회사",
            "majorHolders": []
          },
          {
            "name": "Glencore",
            "hqCountry": "스위스",
            "role": "래글랜·캐나다 니켈",
            "ownership": "다국적 광업·트레이딩",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "금",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 4–5위권",
          "rank": 4
        },
        "reserve": {
          "text": "온타리오·퀘벡·북부",
          "rank": 5
        },
        "note": "글로벌 금광 메이저 HQ 다수 (토론토 금융).",
        "companies": [
          {
            "name": "Agnico Eagle",
            "hqCountry": "캐나다",
            "role": "금 채광",
            "ownership": "캐나다 상장",
            "majorHolders": []
          },
          {
            "name": "Barrick Mining Corporation (구 Barrick Gold)",
            "hqCountry": "캐나다",
            "role": "글로벌 금·구리",
            "ownership": "캐나다 상장",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "천연가스",
        "category": "에너지",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 5위권",
          "rank": 5
        },
        "reserve": {
          "text": "서부 몬트니 등",
          "rank": 15
        },
        "note": "미국 수출·LNG 캐나다 프로젝트.",
        "companies": [
          {
            "name": "Tourmaline·CNRL 등",
            "hqCountry": "캐나다",
            "role": "셰일·재래 가스",
            "ownership": "상장 분산",
            "majorHolders": []
          }
        ]
      }
    ],
    "confidence": "high",
    "sources": [
      "NRCan",
      "USGS",
      "EIA",
      "Cameco/Nutrien IR"
    ]
  },
  {
    "id": "mexico",
    "country": "멕시코",
    "resources": [
      {
        "name": "은",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 1위",
          "rank": 1
        },
        "reserve": {
          "text": "확인매장 세계 5–6위권 (페루·호주 등이 더 큼). 생산 1위와 괴리",
          "rank": 6
        },
        "note": "사카테카스·두랑고 벨트.",
        "companies": [
          {
            "name": "Fresnillo plc",
            "hqCountry": "멕시코·영국",
            "role": "은·금 채광",
            "ownership": "멕시코 자본, 런던 상장",
            "majorHolders": [
              {
                "holder": "Peñoles/Bal 가문 계열",
                "country": "멕시코",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "원유",
        "category": "에너지",
        "trade": ["생산","수출"],
        "production": {
          "text": "약 165–175만 b/d (Pemex 장기 감산 지속, 2025년 46년래 최저권 — 2026년 초 국가 전체 약 174만 b/d)",
          "rank": 12
        },
        "reserve": {
          "text": "멕시코만·육상 잔존",
          "rank": 17
        },
        "note": "Pemex 독점 구조 잔존. 재정적 부담.",
        "companies": [
          {
            "name": "Pemex",
            "hqCountry": "멕시코",
            "role": "탐사·생산·정제",
            "ownership": "멕시코 연방 국영 100%",
            "majorHolders": [
              {
                "holder": "멕시코 정부",
                "country": "멕시코",
                "pct": 100
              }
            ]
          }
        ]
      },
      {
        "name": "구리",
        "category": "광물",
        "trade": ["생산"],
        "production": {
          "text": "세계 10위권 (소노라 벨트)",
          "rank": 10
        },
        "reserve": {
          "text": "북부 대규모",
          "rank": 8
        },
        "note": "북미 공급망·EV 수요.",
        "companies": [
          {
            "name": "Grupo México (Southern Copper)",
            "hqCountry": "멕시코",
            "role": "부에나비스타 등 구리",
            "ownership": "멕시코 재벌 (Larrea)",
            "majorHolders": [
              {
                "holder": "Larrea 가문",
                "country": "멕시코",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "금",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 7–8위권",
          "rank": 7
        },
        "reserve": {
          "text": "북·중부 다수",
          "rank": 10
        },
        "note": "외국 메이저 운영 비중.",
        "companies": [
          {
            "name": "Newmont (Peñasquito)",
            "hqCountry": "미국",
            "role": "금·은 다금속",
            "ownership": "미국 상장",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "천연가스",
        "category": "에너지",
        "trade": ["수입"],
        "production": {
          "text": "국내 부족, 미국 파이프 수입 의존",
          "rank": null
        },
        "reserve": {
          "text": "제한적",
          "rank": null
        },
        "note": "산업·전력용 가스 대미 의존.",
        "companies": [
          {
            "name": "Pemex·CFE",
            "hqCountry": "멕시코",
            "role": "생산·조달·발전",
            "ownership": "국영",
            "majorHolders": []
          }
        ]
      }
    ],
    "confidence": "high",
    "sources": [
      "USGS",
      "Pemex",
      "EIA",
      "Fresnillo IR"
    ]
  },
  {
    "id": "skorea",
    "country": "대한민국",
    "resources": [
      {
        "name": "전략 원자재 (고도 수입 의존)",
        "category": "전략의존",
        "trade": ["수입"],
        "production": {
          "text": "원유·가스·철광·구리·리튬 원광 등 거의 전량 수입",
          "rank": null
        },
        "reserve": {
          "text": "본토 상업 매장 극소",
          "rank": null
        },
        "note": "제조·반도체·배터리 강국. 자원 빈국. 비축·장기계약·해외 지분 확보가 안보 핵심.",
        "companies": [
          {
            "name": "한국광해광업공단(KOMIR)",
            "hqCountry": "대한민국",
            "role": "해외 자원 투자·비축 지원",
            "ownership": "대한민국 정부",
            "majorHolders": [
              {
                "holder": "대한민국 정부",
                "country": "대한민국",
                "pct": 100
              }
            ]
          },
          {
            "name": "포스코홀딩스",
            "hqCountry": "대한민국",
            "role": "철강원료 조달·리튬·니켈 투자",
            "ownership": "상장 분산소유 (국민연금 등)",
            "majorHolders": [
              {
                "holder": "국민연금 등 기관",
                "country": "대한민국",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "석탄 (잔존)",
        "category": "에너지",
        "trade": ["수입"],
        "production": {
          "text": "국내 무연탄 잔존 소량, 상용 석탄 거의 전량 수입",
          "rank": null
        },
        "reserve": {
          "text": "강원 등 잔존 제한",
          "rank": null
        },
        "note": "역사적 에너지원. 현재 발전·제철 수입탄.",
        "companies": [
          {
            "name": "대한석탄공사 등",
            "hqCountry": "대한민국",
            "role": "잔존 광산·관리",
            "ownership": "공기업",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "텅스텐 (역사·재개발)",
        "category": "광물",
        "trade": ["생산"],
        "production": {
          "text": "과거 세계적 산지, 현재 재개발·소량",
          "rank": null
        },
        "reserve": {
          "text": "상동 광산 등 유의미 잔존",
          "rank": null
        },
        "note": "상동 텅스텐 재가동 추진. 전략광물 상징.",
        "companies": [
          {
            "name": "알몬티(상동) 관련·국내 파트너",
            "hqCountry": "캐나다·대한민국",
            "role": "상동 재개발",
            "ownership": "외국·국내 합작 구조",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "아연·비철 제련",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "원광 수입 후 아연 정련 세계 유력",
          "rank": null
        },
        "reserve": {
          "text": "원광 매장 미미",
          "rank": null
        },
        "note": "고려아연 온산. 가공 허브형 자원 안보.",
        "companies": [
          {
            "name": "고려아연(Korea Zinc)",
            "hqCountry": "대한민국",
            "role": "아연·연·귀금속 제련",
            "ownership": "영풍·MBK 등 지배구조 쟁점 이력 있는 상장사",
            "majorHolders": [
              {
                "holder": "영풍 계열 등",
                "country": "대한민국",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "리튬 가공·이차전지 소재",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "국내 원광 거의 없음. 수산화리튬·양극재 가공 세계 상위",
          "rank": null
        },
        "reserve": {
          "text": "원광 N/A",
          "rank": null
        },
        "note": "포스코·LG·삼성SDI 등. 호주·아르헨 원료 의존.",
        "companies": [
          {
            "name": "포스코퓨처엠·포스코홀딩스",
            "hqCountry": "대한민국",
            "role": "리튬·양극재",
            "ownership": "포스코 그룹 상장",
            "majorHolders": []
          },
          {
            "name": "LG에너지솔루션·에코프로",
            "hqCountry": "대한민국",
            "role": "배터리·전구체·양극재",
            "ownership": "상장 (LG 오너일가·기관)",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "원유·LNG (전량 수입)",
        "category": "에너지",
        "trade": ["수입"],
        "production": {
          "text": "국내 생산 없음",
          "rank": null
        },
        "reserve": {
          "text": "없음",
          "rank": null
        },
        "note": "중동 원유·호주·카타르 LNG. 해상로 안보 직결.",
        "companies": [
          {
            "name": "한국석유공사·가스공사",
            "hqCountry": "대한민국",
            "role": "비축·도입·해외 광구",
            "ownership": "공기업",
            "majorHolders": [
              {
                "holder": "대한민국 정부",
                "country": "대한민국",
                "pct": null
              }
            ]
          },
          {
            "name": "SK이노베이션·S-Oil·GS칼텍스",
            "hqCountry": "대한민국",
            "role": "정제·석유화학",
            "ownership": "민간 재벌·합작 (S-Oil은 아람코 지분)",
            "majorHolders": [
              {
                "holder": "Saudi Aramco (S-Oil)",
                "country": "사우디아라비아",
                "pct": null
              }
            ]
          }
        ]
      }
    ],
    "confidence": "high",
    "sources": [
      "산업부",
      "KOMIR",
      "USGS",
      "회사 IR"
    ]
  },
  {
    "id": "australia",
    "country": "호주",
    "resources": [
      {
        "name": "철광석",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "약 9억 t 규모 (세계 1위 수출·생산 강국)",
          "rank": 1
        },
        "reserve": {
          "text": "필바라 세계 최대급",
          "rank": 1
        },
        "note": "중국 철강 원료 생명선. BHP·Rio·FMG 과점.",
        "companies": [
          {
            "name": "BHP",
            "hqCountry": "호주",
            "role": "필바라 철광·구리 등",
            "ownership": "호주 상장 분산소유",
            "majorHolders": [
              {
                "holder": "기관 투자자",
                "country": "호주·해외",
                "pct": null
              }
            ]
          },
          {
            "name": "Rio Tinto",
            "hqCountry": "영국·호주",
            "role": "필바라 철광",
            "ownership": "이원 상장 분산소유",
            "majorHolders": []
          },
          {
            "name": "Fortescue (FMG)",
            "hqCountry": "호주",
            "role": "필바라 철광",
            "ownership": "Andrew Forrest 유력 지분 + 시장",
            "majorHolders": [
              {
                "holder": "Andrew Forrest 관련",
                "country": "호주",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "리튬",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "경암 리튬 세계 1위권",
          "rank": 1
        },
        "reserve": {
          "text": "그린부시스 등 세계 최상",
          "rank": 2
        },
        "note": "배터리 원료. 중국 정련 연계 강함.",
        "companies": [
          {
            "name": "Greenbushes JV (Albemarle·Tianqi·IGO)",
            "hqCountry": "미국·중국·호주",
            "role": "세계 최대 경암 리튬",
            "ownership": "다국적 합작",
            "majorHolders": [
              {
                "holder": "Albemarle",
                "country": "미국",
                "pct": 49
              },
              {
                "holder": "Tianqi",
                "country": "중국",
                "pct": 26
              },
              {
                "holder": "IGO",
                "country": "호주",
                "pct": 25
              }
            ]
          },
          {
            "name": "Pilbara Minerals 등",
            "hqCountry": "호주",
            "role": "필바라 경암 리튬",
            "ownership": "호주 상장",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "석탄",
        "category": "에너지",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 5위권, 수출 세계 정상급",
          "rank": 5
        },
        "reserve": {
          "text": "퀸즐랜드·NSW 대규모",
          "rank": 4
        },
        "note": "야금탄·발전탄. 아시아 수출.",
        "companies": [
          {
            "name": "BHP·Glencore 등",
            "hqCountry": "호주·스위스",
            "role": "보웬 분지 등",
            "ownership": "다국적",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "천연가스(LNG)",
        "category": "에너지",
        "trade": ["생산","수출"],
        "production": {
          "text": "LNG 수출 세계 1–2위권",
          "rank": 7
        },
        "reserve": {
          "text": "북서 셸프 등 대규모",
          "rank": 12
        },
        "note": "동아시아 장기계약.",
        "companies": [
          {
            "name": "Woodside Energy",
            "hqCountry": "호주",
            "role": "LNG 생산",
            "ownership": "호주 상장",
            "majorHolders": []
          },
          {
            "name": "Chevron (Gorgon 등)",
            "hqCountry": "미국",
            "role": "북서 셸프 LNG",
            "ownership": "미국 메이저",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "금",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 3위권 (중국·러시아 다음)",
          "rank": 3
        },
        "reserve": {
          "text": "서호주 골든마일 등",
          "rank": 3
        },
        "note": "뉴몬트·현지 생산자.",
        "companies": [
          {
            "name": "Newmont·Northern Star 등",
            "hqCountry": "미국·호주",
            "role": "금 채광",
            "ownership": "다국적·호주 상장",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "희토류",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "마운트웰드 등 중국 외 주요 (세계 4위권)",
          "rank": 4
        },
        "reserve": {
          "text": "서호주 등 확인매장 (세계 4–6위권)",
          "rank": 5
        },
        "note": "Lynas 말레이 분리 연계. 대중국 대안.",
        "companies": [
          {
            "name": "Lynas Rare Earths",
            "hqCountry": "호주",
            "role": "채광·해외 분리",
            "ownership": "호주 상장 분산소유",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "보크사이트",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 1위권",
          "rank": 1
        },
        "reserve": {
          "text": "웨이파 등 대규모",
          "rank": 2
        },
        "note": "알루미나 수출.",
        "companies": [
          {
            "name": "Rio Tinto",
            "hqCountry": "영국·호주",
            "role": "보크사이트·알루미나",
            "ownership": "이원 상장",
            "majorHolders": []
          }
        ]
      }
    ],
    "confidence": "high",
    "sources": [
      "USGS",
      "Geoscience Australia",
      "BHP/Rio/Woodside IR",
      "EIA"
    ]
  },
  {
    "id": "spain",
    "country": "스페인",
    "resources": [
      {
        "name": "구리·다금속 (이베리아)",
        "category": "광물",
        "trade": ["생산"],
        "production": {
          "text": "리오틴토 벨트 등 유럽 유력 구리 생산",
          "rank": null
        },
        "reserve": {
          "text": "이베리아 황철광 벨트",
          "rank": null
        },
        "note": "역사적 광산 재개발. EU 구리 공급 일원.",
        "companies": [
          {
            "name": "Atalaya Mining 등",
            "hqCountry": "스페인·키프로스 상장",
            "role": "리오틴토 구리",
            "ownership": "상장 분산",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "원유·가스 (제한·수입)",
        "category": "에너지",
        "trade": ["수입"],
        "production": {
          "text": "국내 미미, 대부분 수입",
          "rank": null
        },
        "reserve": {
          "text": "극소",
          "rank": null
        },
        "note": "LNG 터미널 유럽 허브 역할. Repsol 글로벌 자산.",
        "companies": [
          {
            "name": "Repsol",
            "hqCountry": "스페인",
            "role": "통합 에너지·해외 E&P",
            "ownership": "스페인 상장 분산소유",
            "majorHolders": [
              {
                "holder": "기관 투자자",
                "country": "스페인·해외",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "올리브유·농산물",
        "category": "농산물",
        "trade": ["생산","수출"],
        "production": {
          "text": "올리브유 세계 1위",
          "rank": 1
        },
        "reserve": {
          "text": "안달루시아 농지",
          "rank": null
        },
        "note": "세계 식품 자원으로서 중요.",
        "companies": [
          {
            "name": "협동조합·민간 수출사",
            "hqCountry": "스페인",
            "role": "생산·수출",
            "ownership": "농가·민간",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "리튬·전략광물 탐사",
        "category": "광물",
        "trade": ["생산"],
        "production": {
          "text": "상업 생산 초기·프로젝트 단계",
          "rank": null
        },
        "reserve": {
          "text": "이베리아 리튬 벨트 잠재",
          "rank": null
        },
        "note": "환경·지역 반대로 개발 불확실. EU 핵심원자재 관심.",
        "companies": [
          {
            "name": "탐사 기업 다수",
            "hqCountry": "스페인·캐나다 등",
            "role": "리튬·텅스텐 탐사",
            "ownership": "소형 상장·민간",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "전략 의존",
        "category": "전략의존",
        "trade": ["수입"],
        "production": {
          "text": "에너지·핵심광물 수입 비중 높음",
          "rank": null
        },
        "reserve": {
          "text": "본토 제한",
          "rank": null
        },
        "note": "재생에너지 확대·북아프리카 연계 가스.",
        "companies": [
          {
            "name": "Iberdrola·Naturgy",
            "hqCountry": "스페인",
            "role": "전력·가스 조달",
            "ownership": "상장",
            "majorHolders": []
          }
        ]
      }
    ],
    "confidence": "low",
    "sources": [
      "USGS",
      "Repsol IR",
      "EU CRM",
      "스페인 광업통계"
    ]
  },
  {
    "id": "indonesia",
    "country": "인도네시아",
    "resources": [
      {
        "name": "니켈",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 1위 (글로벌 약 60% 점유)",
          "rank": 1
        },
        "reserve": {
          "text": "술라웨시·말루쿠 라테라이트 세계 최대권",
          "rank": 1
        },
        "note": "원광 수출금지·국내 제련. 중국 자본 HPAL 깊음. 배터리 핵심.",
        "companies": [
          {
            "name": "PT Vale Indonesia",
            "hqCountry": "브라질·인도네시아",
            "role": "소로아코 니켈",
            "ownership": "Vale·MIND ID 등 합작",
            "majorHolders": []
          },
          {
            "name": "중국계 제련·HPAL 합작",
            "hqCountry": "중국·인도네시아",
            "role": "니켈선철·MHP",
            "ownership": "중국 민간·국유 + 현지",
            "majorHolders": [
              {
                "holder": "중국 자본 컨소시엄",
                "country": "중국",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "석탄",
        "category": "에너지",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 3위권, 수출 강국",
          "rank": 3
        },
        "reserve": {
          "text": "칼리만탄 등 대규모",
          "rank": 7
        },
        "note": "발전·아시아 수출. 구 Adaro Energy의 석탄 사업은 2024년 12월 PT Adaro Andalan Indonesia(AADI)로 분사·IDX 상장, 모회사는 Alamtri Resources Indonesia로 개명.",
        "companies": [
          {
            "name": "Adaro Andalan(AADI)·Bumi Resources",
            "hqCountry": "인도네시아",
            "role": "채탄·수출",
            "ownership": "현지 대기업",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "팜유",
        "category": "농산물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 1위",
          "rank": 1
        },
        "reserve": {
          "text": "수마트라·칼리만탄 플랜테이션",
          "rank": null
        },
        "note": "식용유·바이오연료. 산림 이슈.",
        "companies": [
          {
            "name": "대형 플랜테이션 그룹",
            "hqCountry": "인도네시아",
            "role": "재배·압착·수출",
            "ownership": "현지 대기업 + 소농",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "구리·금 (그라스버그)",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "구리 세계 7위권, 금 부산물 대규모",
          "rank": 7
        },
        "reserve": {
          "text": "그라스버그 세계 최대급 구리·금",
          "rank": 5
        },
        "note": "국영 지분 과반 + Freeport 운영.",
        "companies": [
          {
            "name": "PT Freeport Indonesia",
            "hqCountry": "미국·인도네시아",
            "role": "그라스버그 채광",
            "ownership": "MIND ID 51% + Freeport 49%",
            "majorHolders": [
              {
                "holder": "Inalum/MIND ID",
                "country": "인도네시아",
                "pct": 51
              },
              {
                "holder": "Freeport-McMoRan",
                "country": "미국",
                "pct": 49
              }
            ]
          }
        ]
      },
      {
        "name": "주석",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 2위권 (방카·빌리톤)",
          "rank": 2
        },
        "reserve": {
          "text": "세계 상위",
          "rank": 2
        },
        "note": "전자 솔더. 불법 채광 이슈 병존.",
        "companies": [
          {
            "name": "PT Timah",
            "hqCountry": "인도네시아",
            "role": "주석 채광·제련",
            "ownership": "국영 계열",
            "majorHolders": [
              {
                "holder": "MIND ID/정부",
                "country": "인도네시아",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "보크사이트·코발트",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "보크사이트 세계 상위, 코발트는 니켈 부산물 세계 2위권",
          "rank": 2
        },
        "reserve": {
          "text": "빈탄 보크사이트·라테라이트 Co",
          "rank": 5
        },
        "note": "다운스트림 정책으로 국내 가공 유도.",
        "companies": [
          {
            "name": "Antam (MIND ID)",
            "hqCountry": "인도네시아",
            "role": "보크사이트·니켈 등",
            "ownership": "국영",
            "majorHolders": []
          }
        ]
      }
    ],
    "confidence": "high",
    "sources": [
      "USGS",
      "MEMR Indonesia",
      "Freeport IR",
      "IEA"
    ]
  },
  {
    "id": "netherlands",
    "country": "네덜란드",
    "resources": [
      {
        "name": "천연가스 (흐로닝언)",
        "category": "에너지",
        "trade": ["생산","수입"],
        "production": {
          "text": "흐로닝언 단계적 폐쇄, 잔여 소량·소규모 가스전",
          "rank": null
        },
        "reserve": {
          "text": "과거 유럽 최대급, 현재 생산 중단·잔존",
          "rank": null
        },
        "note": "지진 이슈로 생산 종료 수순. 순수입 전환.",
        "companies": [
          {
            "name": "NAM (Shell·Exxon JV)",
            "hqCountry": "네덜란드·미국",
            "role": "과거 흐로닝언 운영",
            "ownership": "Shell·ExxonMobil 합작",
            "majorHolders": [
              {
                "holder": "Shell",
                "country": "영국",
                "pct": 50
              },
              {
                "holder": "ExxonMobil",
                "country": "미국",
                "pct": 50
              }
            ]
          },
          {
            "name": "Gasunie",
            "hqCountry": "네덜란드",
            "role": "가스 인프라",
            "ownership": "네덜란드 정부",
            "majorHolders": [
              {
                "holder": "네덜란드 정부",
                "country": "네덜란드",
                "pct": 100
              }
            ]
          }
        ]
      },
      {
        "name": "원유·에너지 트레이딩 허브",
        "category": "에너지",
        "trade": ["수입"],
        "production": {
          "text": "본토 생산 미미. 로테르담 정제·트레이딩 핵심",
          "rank": null
        },
        "reserve": {
          "text": "미미",
          "rank": null
        },
        "note": "유럽 에너지·석유제품 물류 허브.",
        "companies": [
          {
            "name": "Shell",
            "hqCountry": "영국",
            "role": "글로벌 통합·역사적 네 거점",
            "ownership": "영국 본사 상장",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "농산물·원예 (집약)",
        "category": "농산물",
        "trade": ["생산","수출"],
        "production": {
          "text": "국토 대비 농식품 수출 세계 2위권",
          "rank": null
        },
        "reserve": {
          "text": "집약 농지·온실",
          "rank": null
        },
        "note": "천연자원 '매장'보다 고부가 농업 시스템.",
        "companies": [
          {
            "name": "협동조합·트레이더 (FrieslandCampina 등)",
            "hqCountry": "네덜란드",
            "role": "유제품·농식품",
            "ownership": "협동조합·민간",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "전략 의존·가공",
        "category": "전략의존",
        "trade": ["수입"],
        "production": {
          "text": "금속·에너지 원료 수입 후 재수출",
          "rank": null
        },
        "reserve": {
          "text": "본토 광물 빈약",
          "rank": null
        },
        "note": "항만·화학 클러스터. 자원 보유국 아님.",
        "companies": [
          {
            "name": "Vitol 등 트레이더 (제네바·로테르담 연계)",
            "hqCountry": "스위스·네덜란드",
            "role": "에너지 트레이딩",
            "ownership": "비상장",
            "majorHolders": []
          }
        ]
      }
    ],
    "confidence": "medium",
    "sources": [
      "EIA",
      "Gasunie",
      "Shell 역사",
      "CBS Netherlands"
    ]
  },
  {
    "id": "turkey",
    "country": "튀르키예",
    "resources": [
      {
        "name": "붕소(보론)",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 생산 과반 이상 (사실상 지배)",
          "rank": 1
        },
        "reserve": {
          "text": "세계 매장 약 70%+ 수준",
          "rank": 1
        },
        "note": "유리·반도체·전기차 등. 국영 독점.",
        "companies": [
          {
            "name": "Eti Maden",
            "hqCountry": "튀르키예",
            "role": "붕소 채광·가공·수출",
            "ownership": "튀르키예 국영 100%",
            "majorHolders": [
              {
                "holder": "튀르키예 정부",
                "country": "튀르키예",
                "pct": 100
              }
            ]
          }
        ]
      },
      {
        "name": "석탄",
        "category": "에너지",
        "trade": ["생산"],
        "production": {
          "text": "갈탄 중심 국내 생산, 발전 연료",
          "rank": null
        },
        "reserve": {
          "text": "국내 갈탄 상당",
          "rank": null
        },
        "note": "에너지 자급 보조. 수입 석탄·가스도 큼.",
        "companies": [
          {
            "name": "TKİ 등 공기업·민간",
            "hqCountry": "튀르키예",
            "role": "채탄",
            "ownership": "국영·민간 혼재",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "크롬",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 2위 생산국 (남아공 다음, 2024년 약 800만 t)",
          "rank": 2
        },
        "reserve": {
          "text": "세계 상위",
          "rank": 5
        },
        "note": "스테인리스·합금철.",
        "companies": [
          {
            "name": "현지 광산·제련사",
            "hqCountry": "튀르키예",
            "role": "채광·페로크롬",
            "ownership": "민간 중심",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "원유·가스 (수입 의존)",
        "category": "에너지",
        "trade": ["수입"],
        "production": {
          "text": "국내 소량, 대부분 수입·파이프 통과국",
          "rank": null
        },
        "reserve": {
          "text": "남동부·흑해 탐사 중 (사카리야 가스 등)",
          "rank": null
        },
        "note": "에너지 허브 지향. TPAO 흑해 가스 개발.",
        "companies": [
          {
            "name": "TPAO",
            "hqCountry": "튀르키예",
            "role": "국영 석유·가스",
            "ownership": "국영",
            "majorHolders": [
              {
                "holder": "튀르키예 정부",
                "country": "튀르키예",
                "pct": 100
              }
            ]
          }
        ]
      },
      {
        "name": "밀·농산물",
        "category": "농산물",
        "trade": ["생산","수출"],
        "production": {
          "text": "중상위 생산, 세계 1위권 밀가루 수출",
          "rank": 10
        },
        "reserve": {
          "text": "아나톨리아 농지",
          "rank": null
        },
        "note": "러·우 밀 재가공 수출 모델.",
        "companies": [
          {
            "name": "TMO (곡물청)",
            "hqCountry": "튀르키예",
            "role": "수매·비축",
            "ownership": "국영",
            "majorHolders": []
          }
        ]
      }
    ],
    "confidence": "medium",
    "sources": [
      "Eti Maden",
      "USGS",
      "TPAO",
      "IEA"
    ]
  },
  {
    "id": "saudi",
    "country": "사우디아라비아",
    "resources": [
      {
        "name": "원유",
        "category": "에너지",
        "trade": ["생산","수출"],
        "production": {
          "text": "약 900–1,100만 b/d (세계 2–3위, OPEC+ 쿼터 변동)",
          "rank": 2
        },
        "reserve": {
          "text": "약 2,600억 bbl 전후 (세계 2위권)",
          "rank": 2
        },
        "note": "가와르·사파니야. 스윙 프로듀서.",
        "companies": [
          {
            "name": "Saudi Aramco",
            "hqCountry": "사우디아라비아",
            "role": "탐사·생산·정제·화학",
            "ownership": "사우디 정부 직접 + PIF 계열 절대 지배 상장",
            "majorHolders": [
              {
                "holder": "사우디 정부 (직접)",
                "country": "사우디아라비아",
                "pct": 81.5
              },
              {
                "holder": "PIF 및 완전출자 자회사",
                "country": "사우디아라비아",
                "pct": 16
              },
              {
                "holder": "일반 상장 유통·기타",
                "country": "다국적",
                "pct": 2.5
              }
            ]
          }
        ]
      },
      {
        "name": "천연가스",
        "category": "에너지",
        "trade": ["생산"],
        "production": {
          "text": "세계 8–10위권, 자푸라 비전통 확대",
          "rank": 9
        },
        "reserve": {
          "text": "세계 5–6위권",
          "rank": 5
        },
        "note": "국내 발전·석유화학 전환 연료. 원유 수출 여유 확보.",
        "companies": [
          {
            "name": "Saudi Aramco",
            "hqCountry": "사우디아라비아",
            "role": "가스 개발 단독 중심",
            "ownership": "사우디 정부 직접 + PIF 계열 절대 지배 상장",
            "majorHolders": [
              {
                "holder": "사우디 정부 (직접)",
                "country": "사우디아라비아",
                "pct": 81.5
              },
              {
                "holder": "PIF 및 완전출자 자회사",
                "country": "사우디아라비아",
                "pct": 16
              },
              {
                "holder": "일반 상장 유통·기타",
                "country": "다국적",
                "pct": 2.5
              }
            ]
          }
        ]
      },
      {
        "name": "인광석·광업 (Ma'aden)",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "인광 세계 6위 (2024년 약 950만 t), 보크사이트·금 확대",
          "rank": 6
        },
        "reserve": {
          "text": "북부 인광·알바이타 보크사이트",
          "rank": 8
        },
        "note": "Vision 2030 비석유 다각화.",
        "companies": [
          {
            "name": "Ma'aden",
            "hqCountry": "사우디아라비아",
            "role": "인광·알루미늄·금·베이스메탈",
            "ownership": "PIF·정부 지배 상장",
            "majorHolders": [
              {
                "holder": "PIF/정부",
                "country": "사우디아라비아",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "헬륨 등 특수가스",
        "category": "에너지",
        "trade": ["계획"],
        "production": {
          "text": "Jafurah 가스전 연계 헬륨 회수 계획 중 (현재 상업 생산 없음)",
          "rank": null
        },
        "reserve": {
          "text": "가스전 수반",
          "rank": null
        },
        "note": "반도체·의료용. 전략 소재.",
        "companies": [
          {
            "name": "Aramco 연계 헬륨",
            "hqCountry": "사우디아라비아",
            "role": "수반가스 헬륨 회수 계획",
            "ownership": "국영 구조",
            "majorHolders": []
          }
        ]
      }
    ],
    "confidence": "high",
    "sources": [
      "EIA",
      "Aramco 연차",
      "OPEC",
      "Ma'aden IR"
    ]
  },
  {
    "id": "switzerland",
    "country": "스위스",
    "resources": [
      {
        "name": "수력",
        "category": "에너지",
        "trade": ["생산"],
        "production": {
          "text": "전력의 상당 비중 수력 (알프스)",
          "rank": null
        },
        "reserve": {
          "text": "수자원·고도차 (매장 개념 상이)",
          "rank": null
        },
        "note": "본토 유일 대규모 '자원'. 원전·수입도 병행.",
        "companies": [
          {
            "name": "Axpo·Alpiq 등",
            "hqCountry": "스위스",
            "role": "수력·전력",
            "ownership": "칸톤·민간 혼합",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "암염·소규모 광물",
        "category": "광물",
        "trade": ["생산"],
        "production": {
          "text": "암염 등 소규모",
          "rank": null
        },
        "reserve": {
          "text": "제한",
          "rank": null
        },
        "note": "전략광물 생산국 아님.",
        "companies": [
          {
            "name": "Schweizer Salinen 등",
            "hqCountry": "스위스",
            "role": "암염",
            "ownership": "칸톤 소유 성격",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "원자재 트레이딩 허브",
        "category": "전략의존",
        "trade": ["수입","수출"],
        "production": {
          "text": "국내 채광 미미. 세계 원자재 무역·금융 중심",
          "rank": null
        },
        "reserve": {
          "text": "본토 N/A",
          "rank": null
        },
        "note": "본사·트레이딩으로 글로벌 자원 흐름 통제력.",
        "companies": [
          {
            "name": "Glencore",
            "hqCountry": "스위스 (Baar 영업, 저지 설립)",
            "role": "광업·상품 트레이딩",
            "ownership": "런던 상장, 경영진·기관",
            "majorHolders": [
              {
                "holder": "기관·내부자",
                "country": "다국적",
                "pct": null
              }
            ]
          },
          {
            "name": "Trafigura·Gunvor 등",
            "hqCountry": "싱가포르·스위스",
            "role": "석유·금속 트레이딩",
            "ownership": "비상장",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "금 정제",
        "category": "광물",
        "trade": ["수입","수출"],
        "production": {
          "text": "원광 없음. 세계 금 정제·중개 허브",
          "rank": null
        },
        "reserve": {
          "text": "N/A",
          "rank": null
        },
        "note": "귀금속 정제 세계 비중 큼.",
        "companies": [
          {
            "name": "Valcambi·PAMP·Argor 등",
            "hqCountry": "스위스",
            "role": "금·귀금속 정제",
            "ownership": "민간·외국 소유 혼재",
            "majorHolders": []
          }
        ]
      }
    ],
    "confidence": "medium",
    "sources": [
      "SFOE",
      "Glencore IR",
      "LBMA",
      "USGS"
    ]
  },
  {
    "id": "poland",
    "country": "폴란드",
    "resources": [
      {
        "name": "석탄",
        "category": "에너지",
        "trade": ["생산","수입"],
        "production": {
          "text": "EU 최대 경석탄 생산국",
          "rank": 10
        },
        "reserve": {
          "text": "실롱스크 등 대규모",
          "rank": 8
        },
        "note": "발전 의존 잔존. EU 탄소정책과 긴장.",
        "companies": [
          {
            "name": "PGE·PGG 등",
            "hqCountry": "폴란드",
            "role": "채탄·발전",
            "ownership": "국영·준국영",
            "majorHolders": [
              {
                "holder": "폴란드 국고",
                "country": "폴란드",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "구리·은",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "은 세계 4–5위; 구리는 유럽 최대급·세계 10위권(루빈)",
          "rank": 4
        },
        "reserve": {
          "text": "은 매장 세계 상위(폴란드 ~5위권); 구리 루빈 벨트 대규모",
          "rank": 5
        },
        "note": "KGHM 중심. 유럽 전략 금속.",
        "companies": [
          {
            "name": "KGHM Polska Miedź",
            "hqCountry": "폴란드",
            "role": "구리·은·부산물",
            "ownership": "국고 유의미 지분 상장",
            "majorHolders": [
              {
                "holder": "폴란드 국고",
                "country": "폴란드",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "원유·가스 (수입 의존)",
        "category": "에너지",
        "trade": ["수입"],
        "production": {
          "text": "국내 소량, 대부분 수입",
          "rank": null
        },
        "reserve": {
          "text": "제한",
          "rank": null
        },
        "note": "러시아 의존 축소 후 노르웨이·LNG·발틱 파이프.",
        "companies": [
          {
            "name": "Orlen (구 PGNiG 통합)",
            "hqCountry": "폴란드",
            "role": "석유·가스·정제",
            "ownership": "국고 지배 상장",
            "majorHolders": [
              {
                "holder": "폴란드 국고",
                "country": "폴란드",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "갈탄·산업광물",
        "category": "에너지",
        "trade": ["생산"],
        "production": {
          "text": "갈탄 발전용 생산",
          "rank": null
        },
        "reserve": {
          "text": "중부·서부",
          "rank": null
        },
        "note": "전력 믹스 전환 과제.",
        "companies": [
          {
            "name": "PGE 등",
            "hqCountry": "폴란드",
            "role": "갈탄·전력",
            "ownership": "국영",
            "majorHolders": []
          }
        ]
      }
    ],
    "confidence": "medium",
    "sources": [
      "USGS",
      "KGHM IR",
      "IEA",
      "폴란드 통계"
    ]
  },
  {
    "id": "taiwan",
    "country": "대만",
    "resources": [
      {
        "name": "전략 원자재 (전면 수입 의존)",
        "category": "전략의존",
        "trade": ["수입"],
        "production": {
          "text": "원유·가스·금속 원광 거의 전량 수입",
          "rank": null
        },
        "reserve": {
          "text": "본토 상업 매장 극소",
          "rank": null
        },
        "note": "반도체 초강국이나 1차 자원 빈국. 해상 봉쇄 시 에너지·소재 취약.",
        "companies": [
          {
            "name": "CPC Corporation (대만중유)",
            "hqCountry": "대만",
            "role": "원유·가스 도입·정제",
            "ownership": "대만 행정원 국영",
            "majorHolders": [
              {
                "holder": "대만 정부",
                "country": "대만",
                "pct": 100
              }
            ]
          }
        ]
      },
      {
        "name": "석탄 (수입)",
        "category": "에너지",
        "trade": ["수입"],
        "production": {
          "text": "국내 채탄 종료, 전량 수입",
          "rank": null
        },
        "reserve": {
          "text": "잔존 비경제",
          "rank": null
        },
        "note": "발전 연료. 호주 등 수입.",
        "companies": [
          {
            "name": "Taipower 등",
            "hqCountry": "대만",
            "role": "발전·연료 조달",
            "ownership": "국영",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "천연가스(LNG)",
        "category": "에너지",
        "trade": ["수입"],
        "production": {
          "text": "국내 미미, LNG 수입 의존",
          "rank": null
        },
        "reserve": {
          "text": "미미",
          "rank": null
        },
        "note": "전력 전환 핵심. 터미널·저장 확충.",
        "companies": [
          {
            "name": "CPC·Taipower",
            "hqCountry": "대만",
            "role": "LNG 도입",
            "ownership": "국영",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "반도체 소재·용수 (산업 자원)",
        "category": "전략의존",
        "trade": ["수입"],
        "production": {
          "text": "고순도 화학·가스는 수입·일부 현지 생산",
          "rank": null
        },
        "reserve": {
          "text": "수자원 제약 (가뭄 리스크)",
          "rank": null
        },
        "note": "TSMC 생태계. 천연자원보다 공업용수·전력이 병목.",
        "companies": [
          {
            "name": "TSMC 공급망 소재사",
            "hqCountry": "대만·일본·미국",
            "role": "특수가스·케미컬",
            "ownership": "다국적",
            "majorHolders": []
          }
        ]
      }
    ],
    "confidence": "medium",
    "sources": [
      "CPC",
      "IEA",
      "USGS",
      "대만 경제부"
    ]
  },
  {
    "id": "belgium",
    "country": "벨기에",
    "resources": [
      {
        "name": "석탄 (역사)",
        "category": "에너지",
        "trade": ["수입"],
        "production": {
          "text": "상업 채탄 종료",
          "rank": null
        },
        "reserve": {
          "text": "역사 탄전, 현재 미가동",
          "rank": null
        },
        "note": "산업혁명기 자원. 현재 전량 수입 에너지.",
        "companies": [
          {
            "name": "역사 탄전 (폐쇄)",
            "hqCountry": "벨기에",
            "role": "과거 채탄 — 현재 수입·전환",
            "ownership": "해당 없음 (산업 전환)",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "귀금속·배터리 소재 정제 (Umicore)",
        "category": "광물",
        "trade": ["수입","수출"],
        "production": {
          "text": "원광 없음. 세계적 재활용·정련 허브",
          "rank": null
        },
        "reserve": {
          "text": "도시광산(스크랩) 모델",
          "rank": null
        },
        "note": "PGM·코발트·리튬 순환. '보유' 대신 '순환·정제'.",
        "companies": [
          {
            "name": "Umicore",
            "hqCountry": "벨기에",
            "role": "귀금속 정제·배터리 소재·재활용",
            "ownership": "벨기에 상장 분산소유",
            "majorHolders": [
              {
                "holder": "기관 투자자",
                "country": "벨기에·해외",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "에너지 수입·항만 허브",
        "category": "에너지",
        "trade": ["수입"],
        "production": {
          "text": "국내 화석 생산 미미",
          "rank": null
        },
        "reserve": {
          "text": "미미",
          "rank": null
        },
        "note": "앤트워프 항 석유화학·LNG. 유럽 물류.",
        "companies": [
          {
            "name": "TotalEnergies·Exxon 정유 (앤트워프)",
            "hqCountry": "프랑스·미국",
            "role": "정제·석유화학",
            "ownership": "외국 메이저",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "전략 의존",
        "category": "전략의존",
        "trade": ["수입"],
        "production": {
          "text": "핵심광물·에너지 전면 수입",
          "rank": null
        },
        "reserve": {
          "text": "본토 빈약",
          "rank": null
        },
        "note": "고부가 정제·물류로 공급망 위치 확보.",
        "companies": [
          {
            "name": "Solvay",
            "hqCountry": "벨기에",
            "role": "화학·특수소재",
            "ownership": "상장",
            "majorHolders": []
          }
        ]
      }
    ],
    "confidence": "low",
    "sources": [
      "Umicore IR",
      "USGS",
      "IEA",
      "벨기에 통계"
    ]
  },
  {
    "id": "argentina",
    "country": "아르헨티나",
    "resources": [
      {
        "name": "리튬",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 3–4위권 (염호)",
          "rank": 4
        },
        "reserve": {
          "text": "리튬 삼각 확인매장 세계 3위권 (칠레·호주 다음; 자원량 기준은 더 상위 가능)",
          "rank": 3
        },
        "note": "옴브레 무에르토 등. 외국 자본 주도.",
        "companies": [
          {
            "name": "Rio Tinto Lithium (구 Arcadium; Livent+Allkem 합병사, 2025년 3월 Rio Tinto가 인수)",
            "hqCountry": "영국·호주",
            "role": "염호 리튬 (옴브레 무에르토/페닉스, 올라로스 등)",
            "ownership": "외국 기업 자회사 (Rio Tinto 100%)",
            "majorHolders": []
          },
          {
            "name": "POSCO 등 한국·중국 투자",
            "hqCountry": "대한민국·중국",
            "role": "염호·가공 프로젝트",
            "ownership": "외국 투자",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "대두",
        "category": "농산물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 3위권",
          "rank": 3
        },
        "reserve": {
          "text": "팜파스 농지",
          "rank": null
        },
        "note": "수출·대두박·오일. 외화 핵심.",
        "companies": [
          {
            "name": "영농기업 + Cargill·ADM·COFCO",
            "hqCountry": "아르헨티나",
            "role": "생산·수출",
            "ownership": "현지 + 다국적",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "천연가스·셰일 (바카 무에르타)",
        "category": "에너지",
        "trade": ["생산","수출"],
        "production": {
          "text": "셰일 가스·오일 급성장 중 (세계 유망)",
          "rank": null
        },
        "reserve": {
          "text": "바카 무에르타 셰일 기술회수 가능 자원 세계 정상급 (가스 자원량 기준 상위; 확인매장 순위와 다름)",
          "rank": 2
        },
        "note": "YPF·외국 파트너. 인프라·거시경제가 병목.",
        "companies": [
          {
            "name": "YPF",
            "hqCountry": "아르헨티나",
            "role": "셰일·재래 석유가스",
            "ownership": "아르헨티나 정부 지배 상장",
            "majorHolders": [
              {
                "holder": "아르헨티나 정부",
                "country": "아르헨티나",
                "pct": null
              }
            ]
          },
          {
            "name": "Techint/Tecpetrol·Vista 등",
            "hqCountry": "아르헨티나·이탈리아 계열",
            "role": "바카 무에르타 개발",
            "ownership": "민간",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "옥수수",
        "category": "농산물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 4위권",
          "rank": 4
        },
        "reserve": {
          "text": "팜파스",
          "rank": null
        },
        "note": "수출 곡물.",
        "companies": [
          {
            "name": "영농·곡물메이저",
            "hqCountry": "아르헨티나",
            "role": "생산·유통",
            "ownership": "민간",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "구리 (개발 중)",
        "category": "광물",
        "trade": ["생산"],
        "production": {
          "text": "현재 소량, 대형 프로젝트 대기",
          "rank": null
        },
        "reserve": {
          "text": "안데스 구리 유망",
          "rank": null
        },
        "note": "Josemaría 등. 투자·인허가 변수.",
        "companies": [
          {
            "name": "외국 메이저·중형 광업",
            "hqCountry": "캐나다·호주 등",
            "role": "탐사·개발",
            "ownership": "외국 자본",
            "majorHolders": []
          }
        ]
      }
    ],
    "confidence": "high",
    "sources": [
      "USGS",
      "YPF",
      "US EIA",
      "아르헨 광업부"
    ]
  },
  {
    "id": "sweden",
    "country": "스웨덴",
    "resources": [
      {
        "name": "철광석",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "EU 최대 철광 생산 (세계 12위권)",
          "rank": 12
        },
        "reserve": {
          "text": "키루나·말름베리 고품위",
          "rank": 10
        },
        "note": "LKAB. 유럽 녹색철강 원료 축.",
        "companies": [
          {
            "name": "LKAB",
            "hqCountry": "스웨덴",
            "role": "철광 채광·펠릿",
            "ownership": "스웨덴 정부 100% 국영",
            "majorHolders": [
              {
                "holder": "스웨덴 정부",
                "country": "스웨덴",
                "pct": 100
              }
            ]
          }
        ]
      },
      {
        "name": "구리·아연·납 (볼리덴)",
        "category": "광물",
        "trade": ["생산"],
        "production": {
          "text": "유럽 주요 베이스메탈 생산",
          "rank": null
        },
        "reserve": {
          "text": "스켈레프테 벨트 등",
          "rank": null
        },
        "note": "북유럽 광업 클러스터.",
        "companies": [
          {
            "name": "Boliden",
            "hqCountry": "스웨덴",
            "role": "구리·아연·금 채광·제련",
            "ownership": "스웨덴 상장 분산소유",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "희토류·인회석 (개발)",
        "category": "광물",
        "trade": ["생산"],
        "production": {
          "text": "상업 생산 준비 (Per Geijer 등 발견)",
          "rank": null
        },
        "reserve": {
          "text": "유럽 최대급 희토 매장 발표 (키루나 인근)",
          "rank": null
        },
        "note": "LKAB 희토·인 부산물 전략. EU 대중 의존 완화 기대.",
        "companies": [
          {
            "name": "LKAB",
            "hqCountry": "스웨덴",
            "role": "희토·인 프로젝트",
            "ownership": "국영",
            "majorHolders": [
              {
                "holder": "스웨덴 정부",
                "country": "스웨덴",
                "pct": 100
              }
            ]
          }
        ]
      },
      {
        "name": "수력·임업",
        "category": "에너지",
        "trade": ["생산","수출"],
        "production": {
          "text": "수력·바이오 전력 비중 높음, 임산물 수출 강국",
          "rank": null
        },
        "reserve": {
          "text": "삼림·수자원 풍부",
          "rank": null
        },
        "note": "재생·바이오 자원 강점.",
        "companies": [
          {
            "name": "Vattenfall",
            "hqCountry": "스웨덴",
            "role": "수력·전력",
            "ownership": "스웨덴 정부",
            "majorHolders": [
              {
                "holder": "스웨덴 정부",
                "country": "스웨덴",
                "pct": 100
              }
            ]
          },
          {
            "name": "SCA 등 임업",
            "hqCountry": "스웨덴",
            "role": "임산·바이오",
            "ownership": "상장",
            "majorHolders": []
          }
        ]
      },
      {
        "name": "원유·가스 의존",
        "category": "전략의존",
        "trade": ["수입"],
        "production": {
          "text": "화석 생산 없음 (수입)",
          "rank": null
        },
        "reserve": {
          "text": "없음",
          "rank": null
        },
        "note": "광물·임산 강점, 석유가스는 전면 수입.",
        "companies": [
          {
            "name": "Preem 등 정제",
            "hqCountry": "스웨덴",
            "role": "원유 수입 정제",
            "ownership": "민간",
            "majorHolders": []
          }
        ]
      }
    ],
    "confidence": "medium",
    "sources": [
      "LKAB",
      "USGS",
      "SGU Sweden",
      "Boliden IR"
    ]
  },
  {
    "id": "ireland",
    "country": "아일랜드",
    "resources": [
      {
        "name": "아연·납",
        "category": "광물",
        "trade": ["생산"],
        "production": {
          "text": "타라(Tara) 광산 등에서 과거 EU 유수 아연 생산, 최근 운영 중단·재가동 변동으로 생산량 소규모",
          "rank": null
        },
        "reserve": {
          "text": "매장 규모 세계 비중 미미, 탐·개발 잠재는 제한적",
          "rank": null
        },
        "note": "자원 빈국. 역사적으로 유럽 내 유의미한 아연 생산지였으나 현재는 산업·서비스 중심.",
        "companies": [
          {
            "name": "Boliden Tara Mines",
            "hqCountry": "스웨덴",
            "role": "타라 아연·납 광산 운영(변동)",
            "ownership": "Boliden 100%",
            "majorHolders": [
              {
                "holder": "Boliden",
                "country": "스웨덴",
                "pct": 100
              }
            ]
          }
        ]
      },
      {
        "name": "이탄(토탄)",
        "category": "에너지",
        "trade": ["생산"],
        "production": {
          "text": "역사적으로 가정·발전용 이탄 채취, 기후정책으로 단계적 축소",
          "rank": null
        },
        "reserve": {
          "text": "중부 보그랜드 이탄층 광범위하나 상업 채굴은 축소 중",
          "rank": null
        },
        "note": "전통 에너지 자원. 재생에너지 전환으로 전략적 중요도 하락.",
        "companies": [
          {
            "name": "Bord na Móna",
            "hqCountry": "아일랜드",
            "role": "이탄·재생에너지·바이오 전환",
            "ownership": "아일랜드 정부 100%",
            "majorHolders": [
              {
                "holder": "아일랜드 정부",
                "country": "아일랜드",
                "pct": 100
              }
            ]
          }
        ]
      },
      {
        "name": "낙농·축산",
        "category": "농산물",
        "trade": ["생산","수출"],
        "production": {
          "text": "버터·분유·치즈 등 유제품 수출 강국, EU 내 고부가 낙농 허브",
          "rank": null
        },
        "reserve": {
          "text": "해당 없음(농산물)",
          "rank": null
        },
        "note": "천연자원보다 농업·식품 가공이 실질 자원 기반. 제약·IT와 함께 수출 핵심.",
        "companies": [
          {
            "name": "Ornua",
            "hqCountry": "아일랜드",
            "role": "유제품 수출·브랜드(Kerrygold 등)",
            "ownership": "낙농 협동조합 소유",
            "majorHolders": [
              {
                "holder": "아일랜드 낙농 협동조합",
                "country": "아일랜드",
                "pct": null
              }
            ]
          },
          {
            "name": "Glanbia",
            "hqCountry": "아일랜드",
            "role": "낙농·영양 소재",
            "ownership": "상장 + 협동조합 지분",
            "majorHolders": [
              {
                "holder": "기관·일반 주주",
                "country": "아일랜드 등",
                "pct": null
              },
              {
                "holder": "Glanbia Co-operative Society",
                "country": "아일랜드",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "제약·바이오 가공",
        "category": "가공·무역",
        "trade": ["생산","수출"],
        "production": {
          "text": "다국적 제약사 제조·수출 허브로 의약품이 상품 수출의 큰 비중",
          "rank": null
        },
        "reserve": {
          "text": "해당 없음",
          "rank": null
        },
        "note": "광물 자원은 빈약하나 고부가 가공·IP 기반 수출 구조. '자원'보다 산업 인프라 성격.",
        "companies": [
          {
            "name": "Pfizer Ireland 등 다국적 제약 클러스터",
            "hqCountry": "미국 등",
            "role": "원료·완제 의약품 제조·수출",
            "ownership": "다국적 민간",
            "majorHolders": [
              {
                "holder": "다국적 제약사",
                "country": "미국·유럽",
                "pct": null
              }
            ]
          }
        ]
      }
    ],
    "confidence": "medium",
    "sources": [
      "USGS",
      "Bord na Móna",
      "Boliden",
      "CSO Ireland"
    ]
  },
  {
    "id": "uae",
    "country": "아랍에미리트",
    "resources": [
      {
        "name": "원유",
        "category": "에너지",
        "trade": ["생산","수출"],
        "production": {
          "text": "일산 약 300–400만 배럴대, 세계 상위권(원유·석유액체 합산 약 7위권)",
          "rank": 7
        },
        "reserve": {
          "text": "확인매장 약 970–1,130억 배럴대, 세계 약 6위·비중 약 6%",
          "rank": 6
        },
        "note": "아부다비 중심. ADNOC가 상류·중류 지배. 생산능력 확대(5백만 bpd 목표) 추진.",
        "companies": [
          {
            "name": "ADNOC",
            "hqCountry": "아랍에미리트",
            "role": "국영 원유·가스 전 밸류체인",
            "ownership": "아부다비 정부 100%",
            "majorHolders": [
              {
                "holder": "아부다비 정부",
                "country": "아랍에미리트",
                "pct": 100
              }
            ]
          }
        ]
      },
      {
        "name": "천연가스",
        "category": "에너지",
        "trade": ["생산"],
        "production": {
          "text": "해상 가스·콘덴세이트 중심, 국내 수요·LNG·석유화학 원료",
          "rank": null
        },
        "reserve": {
          "text": "확인매장 세계 상위권(약 7–8위대, 수 조 m³)",
          "rank": 7
        },
        "note": "원유 대비 가스 자급·수입 병행 구조. ADNOC Gas 등 분리 상장 자회사 운영.",
        "companies": [
          {
            "name": "ADNOC Gas",
            "hqCountry": "아랍에미리트",
            "role": "가스 처리·판매",
            "ownership": "ADNOC 지배",
            "majorHolders": [
              {
                "holder": "ADNOC",
                "country": "아랍에미리트",
                "pct": null
              },
              {
                "holder": "일반 주주",
                "country": "다국적",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "알루미늄(제련)",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 유수 1차 알루미늄 생산국(저가 에너지 기반 제련)",
          "rank": null
        },
        "reserve": {
          "text": "보크사이트 원광 자체 매장 미미, 수입 원료 가공",
          "rank": null
        },
        "note": "자원 채굴보다 에너지 집약 가공 허브. 걸프 산업다각화 대표 사례.",
        "companies": [
          {
            "name": "Emirates Global Aluminium (EGA)",
            "hqCountry": "아랍에미리트",
            "role": "1차 알루미늄 생산",
            "ownership": "Mubadala·ICD 공동",
            "majorHolders": [
              {
                "holder": "Mubadala",
                "country": "아랍에미리트",
                "pct": 50
              },
              {
                "holder": "Investment Corporation of Dubai",
                "country": "아랍에미리트",
                "pct": 50
              }
            ]
          }
        ]
      },
      {
        "name": "석유화학·정유",
        "category": "가공·무역",
        "trade": ["생산","수출"],
        "production": {
          "text": "루웨이스 등 대형 정유·석유화학 단지, 수출 지향",
          "rank": null
        },
        "reserve": {
          "text": "해당 없음",
          "rank": null
        },
        "note": "원유 부가가치 제고 및 다운스트림 다각화.",
        "companies": [
          {
            "name": "ADNOC Refining / ADNOC",
            "hqCountry": "아랍에미리트",
            "role": "정유·석유화학",
            "ownership": "ADNOC 중심(합작 포함)",
            "majorHolders": [
              {
                "holder": "ADNOC",
                "country": "아랍에미리트",
                "pct": null
              }
            ]
          }
        ]
      }
    ],
    "confidence": "high",
    "sources": [
      "EIA",
      "OPEC",
      "ADNOC",
      "BP Statistical Review/EI"
    ]
  },
  {
    "id": "singapore",
    "country": "싱가포르",
    "resources": [
      {
        "name": "원유 정제·석유제품",
        "category": "가공·무역",
        "trade": ["수입","수출"],
        "production": {
          "text": "동남아 핵심 정유 허브, 일 정제능력 백만 배럴대·석유제품 대규모 재수출",
          "rank": null
        },
        "reserve": {
          "text": "원유 매장 사실상 없음",
          "rank": null
        },
        "note": "천연자원 제로에 가깝고 수입→정제→무역 모델. 전략 허브 성격.",
        "companies": [
          {
            "name": "ExxonMobil Singapore",
            "hqCountry": "미국",
            "role": "정유·석유화학",
            "ownership": "ExxonMobil 100%",
            "majorHolders": [
              {
                "holder": "ExxonMobil",
                "country": "미국",
                "pct": 100
              }
            ]
          },
          {
            "name": "Shell Singapore",
            "hqCountry": "영국",
            "role": "정유·윤활·화학",
            "ownership": "Shell 계열",
            "majorHolders": [
              {
                "holder": "Shell",
                "country": "영국",
                "pct": 100
              }
            ]
          }
        ]
      },
      {
        "name": "원유·상품 트레이딩",
        "category": "가공·무역",
        "trade": ["수입","수출"],
        "production": {
          "text": "아시아 원유·LNG·금속·농산물 트레이딩 중심지",
          "rank": null
        },
        "reserve": {
          "text": "해당 없음",
          "rank": null
        },
        "note": "물리적 매장 없이 금융·물류·창구 역할로 원자재 시장 영향력 보유.",
        "companies": [
          {
            "name": "Trafigura",
            "hqCountry": "싱가포르",
            "role": "원자재 트레이딩",
            "ownership": "직원 소유 민간",
            "majorHolders": [
              {
                "holder": "직원 주주",
                "country": "다국적",
                "pct": null
              }
            ]
          },
          {
            "name": "Vitol Asia 등",
            "hqCountry": "네덜란드·스위스",
            "role": "원유 트레이딩 아시아 거점",
            "ownership": "민간 트레이더",
            "majorHolders": [
              {
                "holder": "민간 파트너",
                "country": "다국적",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "석유화학",
        "category": "가공·무역",
        "trade": ["수입","수출"],
        "production": {
          "text": "주롱섬 석유화학 단지, 아시아 중간재 공급",
          "rank": null
        },
        "reserve": {
          "text": "해당 없음",
          "rank": null
        },
        "note": "나프타·올레핀 등 중간재 허브.",
        "companies": [
          {
            "name": "PCS / ExxonMobil Chemical 등",
            "hqCountry": "싱가포르·미국",
            "role": "석유화학 생산",
            "ownership": "다국적 합작·자회사",
            "majorHolders": [
              {
                "holder": "다국적 화학사",
                "country": "미국·유럽·아시아",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "항만·벙커링",
        "category": "가공·무역",
        "trade": ["수입","수출"],
        "production": {
          "text": "세계 최대급 벙커링·컨테이너 환적항",
          "rank": null
        },
        "reserve": {
          "text": "해당 없음",
          "rank": null
        },
        "note": "에너지·물류 '허브 자원'. 해협 통과 무역의 결절점.",
        "companies": [
          {
            "name": "PSA International",
            "hqCountry": "싱가포르",
            "role": "항만 터미널 운영",
            "ownership": "Temasek 계열 사실상 국부 지배",
            "majorHolders": [
              {
                "holder": "Temasek",
                "country": "싱가포르",
                "pct": null
              }
            ]
          }
        ]
      }
    ],
    "confidence": "high",
    "sources": [
      "EIA",
      "IEA",
      "MPA Singapore",
      "company filings"
    ]
  },
  {
    "id": "israel",
    "country": "이스라엘",
    "resources": [
      {
        "name": "천연가스",
        "category": "에너지",
        "trade": ["생산","수출"],
        "production": {
          "text": "동지중해 해상(타마르·리바이어선·카리시) 중심, 연간 약 20 bcm대·역내 2위권",
          "rank": null
        },
        "reserve": {
          "text": "해상 가스전 수십 Tcf, 세계 순위는 중하위이나 역내 전략 자산",
          "rank": null
        },
        "note": "국내 전력 가스화 + 이집트·요르단 수출. 안보 리스크에 생산 중단 이력.",
        "companies": [
          {
            "name": "Chevron (Noble Energy 인수)",
            "hqCountry": "미국",
            "role": "리바이어선·타마르 운영 파트너",
            "ownership": "상장 메이저",
            "majorHolders": [
              {
                "holder": "기관 주주",
                "country": "미국 등",
                "pct": null
              }
            ]
          },
          {
            "name": "NewMed Energy",
            "hqCountry": "이스라엘",
            "role": "리바이어선 최대 지분 파트너",
            "ownership": "상장(구 Delek Drilling)",
            "majorHolders": [
              {
                "holder": "기관·창업 계열",
                "country": "이스라엘",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "칼륨(포타시)·브롬",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "사해 증발·화학 추출, 브롬 세계 상위 생산",
          "rank": null
        },
        "reserve": {
          "text": "사해 염수 사실상 무한 공급원 성격(환경 제약)",
          "rank": null
        },
        "note": "비료·난연·특수화학 원료. 요르단 측 Arab Potash와 대칭.",
        "companies": [
          {
            "name": "ICL Group",
            "hqCountry": "이스라엘",
            "role": "사해 칼륨·브롬·인산 제품",
            "ownership": "상장, 이스라엘 기관 지분 유의미",
            "majorHolders": [
              {
                "holder": "Israel Corp 등 기관",
                "country": "이스라엘",
                "pct": null
              },
              {
                "holder": "일반 주주",
                "country": "다국적",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "인광석·인산",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "네게브 인광 채굴·가공, 비료 수출",
          "rank": null
        },
        "reserve": {
          "text": "중동 인광 벨트 일부, 세계 비중 중소",
          "rank": null
        },
        "note": "ICL·로템 단지 중심.",
        "companies": [
          {
            "name": "ICL / Rotem",
            "hqCountry": "이스라엘",
            "role": "인광·인산 비료",
            "ownership": "ICL 계열",
            "majorHolders": [
              {
                "holder": "ICL Group",
                "country": "이스라엘",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "담수·수자원 기술",
        "category": "기타",
        "trade": ["생산"],
        "production": {
          "text": "대규모 해수담수화로 생활·농업용수 공급",
          "rank": null
        },
        "reserve": {
          "text": "담수 자연 부존 빈약",
          "rank": null
        },
        "note": "천연 수자원 부족을 기술·인프라로 보완. 전략적 '대체 자원'.",
        "companies": [
          {
            "name": "IDE Technologies 등",
            "hqCountry": "이스라엘",
            "role": "담수화 플랜트 기술·운영",
            "ownership": "민간",
            "majorHolders": [
              {
                "holder": "민간 주주",
                "country": "이스라엘",
                "pct": null
              }
            ]
          }
        ]
      }
    ],
    "confidence": "medium",
    "sources": [
      "EIA",
      "MEES",
      "ICL",
      "Israel Ministry of Energy"
    ]
  },
  {
    "id": "austria",
    "country": "오스트리아",
    "resources": [
      {
        "name": "원유·천연가스",
        "category": "에너지",
        "trade": ["생산","수입"],
        "production": {
          "text": "국내 생산 소규모, 수입 의존. 비엔나 분지 등 전통 유전",
          "rank": null
        },
        "reserve": {
          "text": "매장 미미, 유럽 중계·저장 허브 성격 강함",
          "rank": null
        },
        "note": "자원 빈국에 가깝고 OMV의 해외 자산·중동부유럽 다운스트림이 핵심.",
        "companies": [
          {
            "name": "OMV",
            "hqCountry": "오스트리아",
            "role": "상류·정유·화학·가스",
            "ownership": "상장, 국가·UAE 지분 유의미",
            "majorHolders": [
              {
                "holder": "ÖBAG(오스트리아 국가)",
                "country": "오스트리아",
                "pct": 31.5
              },
              {
                "holder": "Abu Dhabi (Mubadala 등)",
                "country": "아랍에미리트",
                "pct": 24.9
              },
              {
                "holder": "일반 주주",
                "country": "다국적",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "목재·임산물",
        "category": "농산물",
        "trade": ["생산","수출"],
        "production": {
          "text": "알프스 임업, 제재·펄프·바이오매스 공급",
          "rank": null
        },
        "reserve": {
          "text": "산림 면적 국토 대비 높음",
          "rank": null
        },
        "note": "전통 재생 자원. EU 지속가능 임업 프레임.",
        "companies": [
          {
            "name": "Mayr-Melnhof / 임업 협동·민간",
            "hqCountry": "오스트리아",
            "role": "제지·목재 가공",
            "ownership": "민간·상장",
            "majorHolders": [
              {
                "holder": "민간 주주",
                "country": "오스트리아",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "수력",
        "category": "에너지",
        "trade": ["생산"],
        "production": {
          "text": "알프스 수력이 전력의 큰 비중, 재생 비중 높음",
          "rank": null
        },
        "reserve": {
          "text": "수력 잠재 개발 성숙 단계",
          "rank": null
        },
        "note": "광물·화석보다 수력이 실질 에너지 기반.",
        "companies": [
          {
            "name": "Verbund",
            "hqCountry": "오스트리아",
            "role": "수력·전력 생산·판매",
            "ownership": "오스트리아 공화국 과반",
            "majorHolders": [
              {
                "holder": "오스트리아 공화국",
                "country": "오스트리아",
                "pct": 51
              },
              {
                "holder": "일반 주주",
                "country": "다국적",
                "pct": 49
              }
            ]
          }
        ]
      },
      {
        "name": "철강·금속 가공",
        "category": "가공·무역",
        "trade": ["생산","수입"],
        "production": {
          "text": "고로·특수강 가공, 원광은 수입 의존",
          "rank": null
        },
        "reserve": {
          "text": "철광 자체 매장 미미",
          "rank": null
        },
        "note": "가공 산업 강점. 원자재 채굴국 아님.",
        "companies": [
          {
            "name": "voestalpine",
            "hqCountry": "오스트리아",
            "role": "특수강·철강 제품",
            "ownership": "상장",
            "majorHolders": [
              {
                "holder": "voestalpine Mitarbeiterbeteiligung 등",
                "country": "오스트리아",
                "pct": null
              },
              {
                "holder": "기관 주주",
                "country": "유럽",
                "pct": null
              }
            ]
          }
        ]
      }
    ],
    "confidence": "medium",
    "sources": [
      "OMV",
      "Verbund",
      "USGS",
      "Statistics Austria"
    ]
  },
  {
    "id": "thailand",
    "country": "태국",
    "resources": [
      {
        "name": "천연가스",
        "category": "에너지",
        "trade": ["생산","수입"],
        "production": {
          "text": "타이만 해상 가스전 중심, 국내 발전·산업용. 생산 정체·수입 LNG 확대",
          "rank": null
        },
        "reserve": {
          "text": "확인매장 중소 규모, 고갈 압력",
          "rank": null
        },
        "note": "PTTEP·합작이 상류 담당. 에너지 안보 핵심.",
        "companies": [
          {
            "name": "PTT / PTTEP",
            "hqCountry": "태국",
            "role": "국영 에너지·상류 가스·원유",
            "ownership": "태국 재무부 최대주주(PTT)",
            "majorHolders": [
              {
                "holder": "태국 정부(재무부)",
                "country": "태국",
                "pct": null
              },
              {
                "holder": "일반 주주",
                "country": "태국 등",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "쌀",
        "category": "농산물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 주요 쌀 수출국, 자스민·백미 브랜드",
          "rank": null
        },
        "reserve": {
          "text": "해당 없음",
          "rank": null
        },
        "note": "차오프라야 평야 관개 농업. 수출 쿼터·기후 변수.",
        "companies": [
          {
            "name": "민간 미곡상·CP 그룹 등",
            "hqCountry": "태국",
            "role": "수매·가공·수출",
            "ownership": "민간 재벌·중개상",
            "majorHolders": [
              {
                "holder": "민간 자본",
                "country": "태국",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "천연고무",
        "category": "농산물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 상위 고무 생산·수출국",
          "rank": null
        },
        "reserve": {
          "text": "해당 없음(농산물)",
          "rank": null
        },
        "note": "남부 플랜테이션. 타이어 원료 공급.",
        "companies": [
          {
            "name": "Sri Trang / 소농 네트워크",
            "hqCountry": "태국",
            "role": "고무 가공·수출",
            "ownership": "상장·소농 혼합",
            "majorHolders": [
              {
                "holder": "민간·소농",
                "country": "태국",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "팜유",
        "category": "농산물",
        "trade": ["생산"],
        "production": {
          "text": "세계 3위권 팜유 생산(비중 약 4%)",
          "rank": 3
        },
        "reserve": {
          "text": "해당 없음",
          "rank": null
        },
        "note": "남부 수랏타니 등. 인니·말련 대비 규모 작음.",
        "companies": [
          {
            "name": "소농·가공 기업",
            "hqCountry": "태국",
            "role": "재배·압착",
            "ownership": "소농+현지 기업",
            "majorHolders": [
              {
                "holder": "소농·현지 기업",
                "country": "태국",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "희토류",
        "category": "광물",
        "trade": ["생산"],
        "production": {
          "text": "중간 가공·소규모 채굴 포함, 세계 약 6위권(비중 약 3%, 통계는 중국 수입 기반 추정치 포함)",
          "rank": 6
        },
        "reserve": {
          "text": "확인 매장 미미(수천 t 수준), 생산 통계는 가공·환적 성격 혼재 가능",
          "rank": null
        },
        "note": "중국 공급망 주변 국가로 관심. 매장국이라기보다 가공·무역 허브 성격 강함. 데이터·환경 규제 불투명.",
        "companies": [
          {
            "name": "현지 광산·가공 기업",
            "hqCountry": "태국",
            "role": "채굴·중간재",
            "ownership": "현지 자본",
            "majorHolders": [
              {
                "holder": "현지 광산기업",
                "country": "태국",
                "pct": null
              }
            ]
          }
        ]
      }
    ],
    "confidence": "medium",
    "sources": [
      "USGS",
      "PTT",
      "FAO",
      "EIA"
    ]
  },
  {
    "id": "norway",
    "country": "노르웨이",
    "resources": [
      {
        "name": "원유",
        "category": "에너지",
        "trade": ["생산","수출"],
        "production": {
          "text": "북해·노르웨이해 상류, 유럽 유수 비OPEC 산유국·순수출국",
          "rank": null
        },
        "reserve": {
          "text": "확인매장 세계 중상위, 신규 발견·연장 개발 지속",
          "rank": null
        },
        "note": "국부펀드(GPFG) 재원. Equinor·국가지분 SDFI(Petoro) 구조.",
        "companies": [
          {
            "name": "Equinor",
            "hqCountry": "노르웨이",
            "role": "북해 원유·가스 최대 운영사",
            "ownership": "노르웨이 국가 과반 지배",
            "majorHolders": [
              {
                "holder": "노르웨이 정부",
                "country": "노르웨이",
                "pct": 67
              },
              {
                "holder": "일반 주주",
                "country": "다국적",
                "pct": 33
              }
            ]
          },
          {
            "name": "Petoro (SDFI)",
            "hqCountry": "노르웨이",
            "role": "국가 직접 지분(SDFI) 관리",
            "ownership": "노르웨이 정부 100%",
            "majorHolders": [
              {
                "holder": "노르웨이 정부",
                "country": "노르웨이",
                "pct": 100
              }
            ]
          }
        ]
      },
      {
        "name": "천연가스",
        "category": "에너지",
        "trade": ["생산","수출"],
        "production": {
          "text": "트롤 등 대형 가스전, 유럽 파이프라인 공급 핵심(세계 생산 약 8위권·비중 약 3%)",
          "rank": 8
        },
        "reserve": {
          "text": "유럽 내 최대급 가스 매장·생산국",
          "rank": null
        },
        "note": "러시아 가스 대체 공급원으로 전략 위상 상승.",
        "companies": [
          {
            "name": "Equinor",
            "hqCountry": "노르웨이",
            "role": "가스 생산·수송 지분",
            "ownership": "국가 67%",
            "majorHolders": [
              {
                "holder": "노르웨이 정부",
                "country": "노르웨이",
                "pct": 67
              },
              {
                "holder": "일반 주주",
                "country": "다국적",
                "pct": 33
              }
            ]
          }
        ]
      },
      {
        "name": "수력",
        "category": "에너지",
        "trade": ["생산"],
        "production": {
          "text": "전력의 대부분 수력, 유럽 최대급 수력 생산",
          "rank": null
        },
        "reserve": {
          "text": "피오르·고지 수력 잠재 활용도 높음",
          "rank": null
        },
        "note": "전력 집약 산업(알루미늄·데이터) 기반.",
        "companies": [
          {
            "name": "Statkraft",
            "hqCountry": "노르웨이",
            "role": "수력·재생 발전",
            "ownership": "노르웨이 정부 100%",
            "majorHolders": [
              {
                "holder": "노르웨이 정부",
                "country": "노르웨이",
                "pct": 100
              }
            ]
          }
        ]
      },
      {
        "name": "알루미늄",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "저가 수력 기반 1차 알루미늄 수출",
          "rank": null
        },
        "reserve": {
          "text": "보크사이트 자체 매장 없음(수입 원료)",
          "rank": null
        },
        "note": "채굴보다 제련 가공. Norsk Hydro 중심.",
        "companies": [
          {
            "name": "Norsk Hydro",
            "hqCountry": "노르웨이",
            "role": "알루미늄 전 밸류체인",
            "ownership": "상장, 국가 최대주주",
            "majorHolders": [
              {
                "holder": "노르웨이 정부",
                "country": "노르웨이",
                "pct": 34
              },
              {
                "holder": "일반 주주",
                "country": "다국적",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "수산물(연어 등)",
        "category": "농산물",
        "trade": ["생산","수출"],
        "production": {
          "text": "양식 연어 세계 최대 수출국",
          "rank": 1
        },
        "reserve": {
          "text": "해당 없음(양식·어업)",
          "rank": null
        },
        "note": "해양 생물자원·양식 산업. 식량·수출 핵심.",
        "companies": [
          {
            "name": "Mowi",
            "hqCountry": "노르웨이",
            "role": "양식 연어 세계 최대급",
            "ownership": "상장",
            "majorHolders": [
              {
                "holder": "기관 주주",
                "country": "노르웨이·유럽",
                "pct": null
              }
            ]
          }
        ]
      }
    ],
    "confidence": "high",
    "sources": [
      "NPD/Norwegian Offshore Directorate",
      "Equinor",
      "EIA",
      "Statistics Norway"
    ]
  },
  {
    "id": "vietnam",
    "country": "베트남",
    "resources": [
      {
        "name": "희토류",
        "category": "광물",
        "trade": ["생산"],
        "production": {
          "text": "생산은 극소(연 수백 t REO, 세계 비중 0.1%대), 개발·인허가 지연",
          "rank": null
        },
        "reserve": {
          "text": "확인매장 세계 약 6위권(REO 약 350만 t, USGS MCS 2025 개정; 과거 2,200만 t 통계는 상향 과대)",
          "rank": 6
        },
        "note": "매장 잠재는 유의미하나 USGS가 매장 규모를 대폭 하향 개정. 라이쩌우 등 개발은 미·일 협력 논의 수준, 실제 생산은 미미.",
        "companies": [
          {
            "name": "국영·합작 광산",
            "hqCountry": "베트남",
            "role": "희토류 탐·개발",
            "ownership": "국영 주도+외국 합작",
            "majorHolders": [
              {
                "holder": "베트남 국영·합작",
                "country": "베트남",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "보크사이트",
        "category": "광물",
        "trade": ["생산"],
        "production": {
          "text": "생산 제한적, 알루미나 프로젝트 단계",
          "rank": null
        },
        "reserve": {
          "text": "중부 고원 매장 세계 상위(약 3위권·비중 약 12%)",
          "rank": 3
        },
        "note": "매장 풍부·생산 미흡. 환경·인프라 제약.",
        "companies": [
          {
            "name": "Vinacomin / 국영 합작",
            "hqCountry": "베트남",
            "role": "보크사이트·석탄 등 광업",
            "ownership": "국영",
            "majorHolders": [
              {
                "holder": "베트남 정부",
                "country": "베트남",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "원유·가스",
        "category": "에너지",
        "trade": ["생산","수입"],
        "production": {
          "text": "남중국해·대륙붕 유전, 순수입 전환 압력",
          "rank": null
        },
        "reserve": {
          "text": "중소 규모, 영유권 분쟁 구역 포함",
          "rank": null
        },
        "note": "PetroVietnam 독점적 상류. 남중국해 지정학 리스크.",
        "companies": [
          {
            "name": "PetroVietnam (PVN)",
            "hqCountry": "베트남",
            "role": "국영 석유·가스",
            "ownership": "베트남 정부 100%",
            "majorHolders": [
              {
                "holder": "베트남 정부",
                "country": "베트남",
                "pct": 100
              }
            ]
          }
        ]
      },
      {
        "name": "쌀",
        "category": "농산물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 주요 쌀 수출국(메콩 삼각주)",
          "rank": null
        },
        "reserve": {
          "text": "해당 없음",
          "rank": null
        },
        "note": "식량 안보·수출 환수 동시. 기후·염해 리스크.",
        "companies": [
          {
            "name": "Vinafood 등 국영·민간 수출",
            "hqCountry": "베트남",
            "role": "미곡 수매·수출",
            "ownership": "국영+민간",
            "majorHolders": [
              {
                "holder": "국영·민간 트레이더",
                "country": "베트남",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "커피",
        "category": "농산물",
        "trade": ["생산","수출"],
        "production": {
          "text": "로부스타 중심 세계 2위권 생산·수출",
          "rank": 2
        },
        "reserve": {
          "text": "해당 없음",
          "rank": null
        },
        "note": "중부 고원 재배. 소농 중심.",
        "companies": [
          {
            "name": "소농·수출 가공업체",
            "hqCountry": "베트남",
            "role": "재배·생두 수출",
            "ownership": "소농+민간 수출상",
            "majorHolders": [
              {
                "holder": "소농·민간",
                "country": "베트남",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "석탄",
        "category": "에너지",
        "trade": ["생산","수입"],
        "production": {
          "text": "북부 무연탄 등 국내 발전용, 수입 병행",
          "rank": null
        },
        "reserve": {
          "text": "국내 매장 보유, 품질·채산성 편차",
          "rank": null
        },
        "note": "전력 석탄 의존 잔존. Vinacomin.",
        "companies": [
          {
            "name": "Vinacomin",
            "hqCountry": "베트남",
            "role": "석탄 채굴",
            "ownership": "국영",
            "majorHolders": [
              {
                "holder": "베트남 정부",
                "country": "베트남",
                "pct": null
              }
            ]
          }
        ]
      }
    ],
    "confidence": "medium",
    "sources": [
      "USGS",
      "PetroVietnam",
      "FAO",
      "IEA"
    ]
  },
  {
    "id": "philippines",
    "country": "필리핀",
    "resources": [
      {
        "name": "니켈",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 2위권 니켈 광석 생산(비중 약 8–10%), 중국 공급 핵심",
          "rank": 2
        },
        "reserve": {
          "text": "라테라이트 매장 세계 상위(약 6위권·비중 약 5%)",
          "rank": 6
        },
        "note": "수리가오·팔라완 등. 원광 수출→중간 가공 확대 정책 변동.",
        "companies": [
          {
            "name": "Nickel Asia Corporation",
            "hqCountry": "필리핀",
            "role": "니켈 광산 운영",
            "ownership": "상장, 현지+일본 투자",
            "majorHolders": [
              {
                "holder": "현지 대주주",
                "country": "필리핀",
                "pct": null
              },
              {
                "holder": "Sumitomo Metal Mining 등",
                "country": "일본",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "코발트",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "니켈 라테라이트 부산물·수반, 세계 약 6위권(비중 약 2%)",
          "rank": 6
        },
        "reserve": {
          "text": "니켈 벨트 수반 매장(비중 약 3%)",
          "rank": 5
        },
        "note": "배터리 공급망 연관. 생산 통계 니켈과 연동.",
        "companies": [
          {
            "name": "Nickel Asia 등 니켈 광산",
            "hqCountry": "필리핀",
            "role": "니켈·코발트 수반 생산",
            "ownership": "현지+일본",
            "majorHolders": [
              {
                "holder": "Nickel Asia 등",
                "country": "필리핀",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "금",
        "category": "광물",
        "trade": ["생산"],
        "production": {
          "text": "소규모·중견 금광, 동남아시아 내 유의미",
          "rank": null
        },
        "reserve": {
          "text": "다금속·에피서멀 금 매장 산재",
          "rank": null
        },
        "note": "비공식 채굴·환경 이슈 병존.",
        "companies": [
          {
            "name": "Philex / 기타 광산",
            "hqCountry": "필리핀",
            "role": "금·구리 채굴",
            "ownership": "현지 상장·민간",
            "majorHolders": [
              {
                "holder": "현지 자본",
                "country": "필리핀",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "구리",
        "category": "광물",
        "trade": ["생산"],
        "production": {
          "text": "역사적 산지, 현재 생산 변동·프로젝트 재개 시도",
          "rank": null
        },
        "reserve": {
          "text": "유망 매장 보유, 개발 지연 사례 다수",
          "rank": null
        },
        "note": "대형 프로젝트 인허가·사회 갈등 리스크.",
        "companies": [
          {
            "name": "현지·외국 합작 광산",
            "hqCountry": "필리핀",
            "role": "구리 탐·개발",
            "ownership": "합작",
            "majorHolders": [
              {
                "holder": "현지·외국 자본",
                "country": "필리핀 등",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "지열",
        "category": "에너지",
        "trade": ["생산"],
        "production": {
          "text": "세계 상위 지열 발전 용량·생산",
          "rank": null
        },
        "reserve": {
          "text": "환태평양 화산대 지열 잠재 풍부",
          "rank": null
        },
        "note": "전력 믹스 핵심 재생원. 에너지 안보 기여.",
        "companies": [
          {
            "name": "Energy Development Corporation (EDC)",
            "hqCountry": "필리핀",
            "role": "지열 발전",
            "ownership": "민간(Lopez 등 계열 변동)",
            "majorHolders": [
              {
                "holder": "민간 주주",
                "country": "필리핀",
                "pct": null
              }
            ]
          }
        ]
      }
    ],
    "confidence": "high",
    "sources": [
      "USGS",
      "MGB Philippines",
      "Nickel Asia",
      "IEA"
    ]
  },
  {
    "id": "bangladesh",
    "country": "방글라데시",
    "resources": [
      {
        "name": "천연가스",
        "category": "에너지",
        "trade": ["생산","수입"],
        "production": {
          "text": "국내 주력 1차 에너지, 생산 정체·고갈로 LNG 수입 확대",
          "rank": null
        },
        "reserve": {
          "text": "확인매장 감소 추세, 신규 발견 제한적",
          "rank": null
        },
        "note": "자원 기반은 가스에 편중. 전력·비료 원료.",
        "companies": [
          {
            "name": "Petrobangla",
            "hqCountry": "방글라데시",
            "role": "국영 석유·가스 홀딩",
            "ownership": "방글라데시 정부 100%",
            "majorHolders": [
              {
                "holder": "방글라데시 정부",
                "country": "방글라데시",
                "pct": 100
              }
            ]
          },
          {
            "name": "Chevron Bangladesh 등",
            "hqCountry": "미국",
            "role": "가스전 생산 파트너",
            "ownership": "IOC PSC",
            "majorHolders": [
              {
                "holder": "Chevron",
                "country": "미국",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "쌀",
        "category": "농산물",
        "trade": ["생산"],
        "production": {
          "text": "세계 상위 쌀 생산국, 자급 중심",
          "rank": null
        },
        "reserve": {
          "text": "해당 없음",
          "rank": null
        },
        "note": "고용·식량 안보 핵심. 홍수·기후 취약.",
        "companies": [
          {
            "name": "소농·정부 조달",
            "hqCountry": "방글라데시",
            "role": "생산·비축",
            "ownership": "소농 중심",
            "majorHolders": [
              {
                "holder": "소규모 농가",
                "country": "방글라데시",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "황마(저트)",
        "category": "농산물",
        "trade": ["생산","수출"],
        "production": {
          "text": "전통 황마 생산·가공, 세계 유수 산지",
          "rank": null
        },
        "reserve": {
          "text": "해당 없음",
          "rank": null
        },
        "note": "역사적 수출 작물. 플라스틱 대체 수요 관심.",
        "companies": [
          {
            "name": "국영·민간 황마 가공",
            "hqCountry": "방글라데시",
            "role": "방적·포장재",
            "ownership": "국영+민간",
            "majorHolders": [
              {
                "holder": "국영·민간",
                "country": "방글라데시",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "석탄",
        "category": "에너지",
        "trade": ["생산","수입"],
        "production": {
          "text": "바라푸쿠리아 등 제한 생산, 수입 석탄·LNG와 병행",
          "rank": null
        },
        "reserve": {
          "text": "북서부 유망 매장 논의, 개발 지연",
          "rank": null
        },
        "note": "대규모 광업국 아님. 에너지 믹스 다변화 시도.",
        "companies": [
          {
            "name": "BCMCL 등 국영",
            "hqCountry": "방글라데시",
            "role": "석탄 채굴",
            "ownership": "국영",
            "majorHolders": [
              {
                "holder": "방글라데시 정부",
                "country": "방글라데시",
                "pct": null
              }
            ]
          }
        ]
      }
    ],
    "confidence": "medium",
    "sources": [
      "Petrobangla",
      "EIA",
      "FAO",
      "USGS"
    ]
  },
  {
    "id": "malaysia",
    "country": "말레이시아",
    "resources": [
      {
        "name": "원유·천연가스",
        "category": "에너지",
        "trade": ["생산","수출"],
        "production": {
          "text": "남중국해·사라왁 해상, LNG 수출 강국. 원유 순수입 전환 압력",
          "rank": null
        },
        "reserve": {
          "text": "원유 약 수십억 배럴, 가스 매장 상대적 풍부",
          "rank": null
        },
        "note": "Petronas가 상류·LNG·석유화학 지배.",
        "companies": [
          {
            "name": "Petronas",
            "hqCountry": "말레이시아",
            "role": "국영 석유·가스 전 밸류체인",
            "ownership": "말레이시아 정부 100%",
            "majorHolders": [
              {
                "holder": "말레이시아 정부",
                "country": "말레이시아",
                "pct": 100
              }
            ]
          }
        ]
      },
      {
        "name": "팜유",
        "category": "농산물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 2위 생산·수출(비중 약 24%)",
          "rank": 2
        },
        "reserve": {
          "text": "해당 없음",
          "rank": null
        },
        "note": "사바·사라왁·반도 플랜테이션. ESG·EUDR 규제 리스크.",
        "companies": [
          {
            "name": "SD Guthrie (구 Sime Darby Plantation)",
            "hqCountry": "말레이시아",
            "role": "대규모 팜 플랜테이션",
            "ownership": "상장, 국부·기관 지분",
            "majorHolders": [
              {
                "holder": "PNB 등 말레이 기관",
                "country": "말레이시아",
                "pct": null
              },
              {
                "holder": "일반 주주",
                "country": "다국적",
                "pct": null
              }
            ]
          },
          {
            "name": "FGV Holdings (구 Felda Global Ventures)",
            "hqCountry": "말레이시아",
            "role": "팜유 생산·가공",
            "ownership": "국부·상장 혼합",
            "majorHolders": [
              {
                "holder": "FELDA 계열",
                "country": "말레이시아",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "천연고무",
        "category": "농산물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 상위 고무 산지(역사적 주산)",
          "rank": null
        },
        "reserve": {
          "text": "해당 없음",
          "rank": null
        },
        "note": "소농 비중 높음. 타이어 원료.",
        "companies": [
          {
            "name": "소농·가공 기업",
            "hqCountry": "말레이시아",
            "role": "재배·가공",
            "ownership": "소농+민간",
            "majorHolders": [
              {
                "holder": "소농·민간",
                "country": "말레이시아",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "주석",
        "category": "광물",
        "trade": ["생산"],
        "production": {
          "text": "역사적 세계 주산, 현재 생산 소규모",
          "rank": null
        },
        "reserve": {
          "text": "잔존 매장 제한적",
          "rank": null
        },
        "note": "산업사적 의미. 현재 전략 광물 위상은 낮음.",
        "companies": [
          {
            "name": "말레이시아 스멜팅(MSC) 등",
            "hqCountry": "말레이시아",
            "role": "주석 제련·무역",
            "ownership": "상장·민간",
            "majorHolders": [
              {
                "holder": "민간 주주",
                "country": "말레이시아 등",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "LNG",
        "category": "에너지",
        "trade": ["생산","수출"],
        "production": {
          "text": "블린툴루 등 세계 유수 LNG 수출 단지",
          "rank": null
        },
        "reserve": {
          "text": "해상 가스전 연계",
          "rank": null
        },
        "note": "동아시아 장기계약 공급. Petronas LNG.",
        "companies": [
          {
            "name": "Petronas LNG",
            "hqCountry": "말레이시아",
            "role": "LNG 액화·수출",
            "ownership": "Petronas 100%",
            "majorHolders": [
              {
                "holder": "Petronas",
                "country": "말레이시아",
                "pct": 100
              }
            ]
          }
        ]
      }
    ],
    "confidence": "high",
    "sources": [
      "Petronas",
      "USGS",
      "MPOB",
      "EIA"
    ]
  },
  {
    "id": "denmark",
    "country": "덴마크",
    "resources": [
      {
        "name": "북해 원유·가스",
        "category": "에너지",
        "trade": ["생산","수입"],
        "production": {
          "text": "북해 덴마크 구역 생산 감소 추세, 순수입 전환",
          "rank": null
        },
        "reserve": {
          "text": "잔존 매장 축소, 신규 탐사 정책 제약",
          "rank": null
        },
        "note": "과거 Maersk Oil 매각 후 TotalEnergies 등 운영. 화석 출구 정책.",
        "companies": [
          {
            "name": "TotalEnergies",
            "hqCountry": "프랑스",
            "role": "덴마크 북해 상류 주요 운영",
            "ownership": "상장 메이저",
            "majorHolders": [
              {
                "holder": "기관 주주",
                "country": "프랑스 등",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "해상풍력",
        "category": "에너지",
        "trade": ["생산"],
        "production": {
          "text": "해상풍력 기술·설치 세계 선도, 전력 수출입 연계",
          "rank": null
        },
        "reserve": {
          "text": "북해 풍력 자원 풍부(자연 에너지)",
          "rank": null
        },
        "note": "광물 자원 빈국이나 재생 '자원·기술' 강국.",
        "companies": [
          {
            "name": "Ørsted",
            "hqCountry": "덴마크",
            "role": "해상풍력 개발·운영",
            "ownership": "상장, 덴마크 국가 과반",
            "majorHolders": [
              {
                "holder": "덴마크 정부",
                "country": "덴마크",
                "pct": 50.1
              },
              {
                "holder": "일반 주주",
                "country": "다국적",
                "pct": 49.9
              }
            ]
          }
        ]
      },
      {
        "name": "돼지고기·낙농",
        "category": "농산물",
        "trade": ["생산","수출"],
        "production": {
          "text": "1인당·수출 기준 세계 유수 축산·낙농 수출국",
          "rank": null
        },
        "reserve": {
          "text": "해당 없음",
          "rank": null
        },
        "note": "협동조합 모델. 식량 자원 성격.",
        "companies": [
          {
            "name": "Danish Crown",
            "hqCountry": "덴마크",
            "role": "양돈·육가공",
            "ownership": "협동조합",
            "majorHolders": [
              {
                "holder": "덴마크 양돈 농가 협동",
                "country": "덴마크",
                "pct": null
              }
            ]
          },
          {
            "name": "Arla Foods",
            "hqCountry": "덴마크",
            "role": "낙농 협동조합(덴-스웨 등)",
            "ownership": "낙농 협동조합",
            "majorHolders": [
              {
                "holder": "북유럽 낙농 조합원",
                "country": "덴마크·스웨덴 등",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "해운·에너지 서비스",
        "category": "가공·무역",
        "trade": ["생산"],
        "production": {
          "text": "머스크 중심 컨테이너·물류, 에너지 서비스",
          "rank": null
        },
        "reserve": {
          "text": "해당 없음",
          "rank": null
        },
        "note": "물리적 채굴 자원 대신 무역·물류 허브 역량.",
        "companies": [
          {
            "name": "A.P. Moller-Maersk",
            "hqCountry": "덴마크",
            "role": "컨테이너 해운·물류",
            "ownership": "상장, 머스크 가문 지배",
            "majorHolders": [
              {
                "holder": "A.P. Moller Holding",
                "country": "덴마크",
                "pct": null
              },
              {
                "holder": "일반 주주",
                "country": "다국적",
                "pct": null
              }
            ]
          }
        ]
      }
    ],
    "confidence": "medium",
    "sources": [
      "DEA Denmark",
      "Ørsted",
      "TotalEnergies",
      "Statistics Denmark"
    ]
  },
  {
    "id": "hongkong",
    "country": "홍콩",
    "resources": [
      {
        "name": "항만·물류 허브",
        "category": "가공·무역",
        "trade": ["수입","수출"],
        "production": {
          "text": "남중국 관문 컨테이너·항공 화물 허브(경쟁 심화)",
          "rank": null
        },
        "reserve": {
          "text": "해당 없음",
          "rank": null
        },
        "note": "천연자원 전무. 중개·금융·물류가 사실상 '자원'.",
        "companies": [
          {
            "name": "Hutchison Ports / Modern Terminals 등",
            "hqCountry": "홍콩",
            "role": "컨테이너 터미널",
            "ownership": "민간 대기업",
            "majorHolders": [
              {
                "holder": "CK Hutchison 등",
                "country": "홍콩",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "금·원자재 금융·무역",
        "category": "가공·무역",
        "trade": ["수입","수출"],
        "production": {
          "text": "금·보석·원자재 무역·보관·금융 중개",
          "rank": null
        },
        "reserve": {
          "text": "자체 광산 없음",
          "rank": null
        },
        "note": "실물 채굴 없이 가격·유통 노드.",
        "companies": [
          {
            "name": "홍콩 거래소·금은 딜러 네트워크",
            "hqCountry": "홍콩",
            "role": "상품·금융 거래",
            "ownership": "상장·민간",
            "majorHolders": [
              {
                "holder": "HKEX 등",
                "country": "홍콩",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "전력·도시가스(수입 의존)",
        "category": "에너지",
        "trade": ["수입"],
        "production": {
          "text": "자체 화석 채굴 없음, 수입 LNG·전력 연계",
          "rank": null
        },
        "reserve": {
          "text": "없음",
          "rank": null
        },
        "note": "에너지 안보 전량 외부 의존.",
        "companies": [
          {
            "name": "CLP / HK Electric / Towngas",
            "hqCountry": "홍콩",
            "role": "전력·가스 유틸리티",
            "ownership": "민간 상장",
            "majorHolders": [
              {
                "holder": "기관·가문 주주",
                "country": "홍콩 등",
                "pct": null
              }
            ]
          }
        ]
      }
    ],
    "confidence": "high",
    "sources": [
      "Census and Statistics HK",
      "company reports"
    ]
  },
  {
    "id": "southafrica",
    "country": "남아프리카공화국",
    "resources": [
      {
        "name": "백금족(PGM)",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "백금(Pt) 세계 1위(비중 약 70%), 팔라듐은 러시아와 양분; PGM 합산 생산 비중 약 50–55%",
          "rank": 1
        },
        "reserve": {
          "text": "부시벨드 복합체 중심, 세계 PGM 확인매장 약 3/4 이상(비중 약 78%, USGS)",
          "rank": 1
        },
        "note": "자동차 촉매·수소 경제 핵심. 'PGM 70%'는 백금 단품에 가깝고 합산 비중은 더 낮음. 전력·노조·심부 채굴 리스크.",
        "companies": [
          {
            "name": "Valterra Platinum (구 Anglo American Platinum/Amplats)",
            "hqCountry": "남아프리카공화국",
            "role": "PGM 최대급 생산(남아공 상장, 2025 Anglo demerger)",
            "ownership": "상장(구 Anglo 계열, 2025 demerger 후 독립; Anglo 잔여 소수 지분)",
            "majorHolders": [
              {
                "holder": "기관·일반 주주(구 Anglo 주주 배분 포함)",
                "country": "남아공·영국 등",
                "pct": null
              },
              {
                "holder": "Anglo American (잔여 소수)",
                "country": "영국",
                "pct": null
              }
            ]
          },
          {
            "name": "Impala Platinum / Sibanye-Stillwater",
            "hqCountry": "남아프리카공화국",
            "role": "PGM·금 생산",
            "ownership": "상장",
            "majorHolders": [
              {
                "holder": "기관 주주",
                "country": "남아공·해외",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "금",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "역사적 1위에서 하락, 여전히 유의미 생산",
          "rank": null
        },
        "reserve": {
          "text": "비트바테르스란드 심부 매장 세계 상위(약 3위·비중 약 9%)",
          "rank": 3
        },
        "note": "심부·고비용. Sibanye·Harmony 등.",
        "companies": [
          {
            "name": "Sibanye-Stillwater",
            "hqCountry": "남아프리카공화국",
            "role": "금·PGM",
            "ownership": "상장",
            "majorHolders": [
              {
                "holder": "기관 주주",
                "country": "다국적",
                "pct": null
              }
            ]
          },
          {
            "name": "Harmony Gold",
            "hqCountry": "남아프리카공화국",
            "role": "금 생산",
            "ownership": "상장",
            "majorHolders": [
              {
                "holder": "기관 주주",
                "country": "남아공 등",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "석탄",
        "category": "에너지",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 상위 생산·수출(비중 약 3%, 약 7위권), 국내 발전 주연료",
          "rank": 7
        },
        "reserve": {
          "text": "하이벨드 탄전 대규모(세계 약 10위권)",
          "rank": 10
        },
        "note": "Eskom 전력 위기와 직결. 수출은 리처즈베이.",
        "companies": [
          {
            "name": "Exxaro / Thungela",
            "hqCountry": "남아프리카공화국",
            "role": "석탄 채굴·수출",
            "ownership": "상장 현지",
            "majorHolders": [
              {
                "holder": "현지·기관 주주",
                "country": "남아공",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "철광석",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "시셴 등 세계 약 9위권(비중 약 2.5%), 대중 수출",
          "rank": 9
        },
        "reserve": {
          "text": "노던케이프 고품위 매장",
          "rank": null
        },
        "note": "Kumba(Anglo) 중심.",
        "companies": [
          {
            "name": "Kumba Iron Ore",
            "hqCountry": "남아프리카공화국",
            "role": "철광석 생산",
            "ownership": "Anglo American 과반",
            "majorHolders": [
              {
                "holder": "Anglo American",
                "country": "영국",
                "pct": 70
              },
              {
                "holder": "일반·BEE 주주",
                "country": "남아공",
                "pct": 30
              }
            ]
          }
        ]
      },
      {
        "name": "망간·크롬",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "망간·크로마이트 세계 최상위권 생산",
          "rank": null
        },
        "reserve": {
          "text": "칼라하리 망간 필드(Kalahari Manganese Field) 등 세계 최대급 매장",
          "rank": null
        },
        "note": "철강·스테인리스 원료. 중국 수요 연동.",
        "companies": [
          {
            "name": "South32 / Assmang 등",
            "hqCountry": "호주·남아공",
            "role": "망간·합금철",
            "ownership": "상장·합작",
            "majorHolders": [
              {
                "holder": "South32·African Rainbow 등",
                "country": "호주·남아공",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "옥수수",
        "category": "농산물",
        "trade": ["생산","수출"],
        "production": {
          "text": "남부아프리카 곡창, 세계 비중 약 1–2%",
          "rank": 9
        },
        "reserve": {
          "text": "해당 없음",
          "rank": null
        },
        "note": "가뭄 시 역내 식량 수급 좌우. SAFEX 시장.",
        "companies": [
          {
            "name": "상업농·Senwes 등",
            "hqCountry": "남아프리카공화국",
            "role": "생산·유통",
            "ownership": "민간·협동",
            "majorHolders": [
              {
                "holder": "상업농·유통사",
                "country": "남아공",
                "pct": null
              }
            ]
          }
        ]
      }
    ],
    "confidence": "high",
    "sources": [
      "USGS",
      "DMRE South Africa",
      "Anglo American",
      "EIA"
    ]
  },
  {
    "id": "iran",
    "country": "이란",
    "resources": [
      {
        "name": "원유",
        "category": "에너지",
        "trade": ["생산","수출"],
        "production": {
          "text": "제재 하에서도 세계 상위 산유(약 9위권·비중 약 4%), 실제 통계 불투명",
          "rank": 9
        },
        "reserve": {
          "text": "확인매장 세계 3–4위권(약 1,500억 배럴대·비중 약 9%)",
          "rank": 3
        },
        "note": "NIOC 독점. 서방 제재로 공식 수출 제약, 중국 등 '그림자 함대' 수출. 데이터 신뢰도 낮음.",
        "companies": [
          {
            "name": "NIOC (National Iranian Oil Company)",
            "hqCountry": "이란",
            "role": "국영 원유 독점",
            "ownership": "이란 정부 100%",
            "majorHolders": [
              {
                "holder": "이란 정부",
                "country": "이란",
                "pct": 100
              }
            ]
          }
        ]
      },
      {
        "name": "천연가스",
        "category": "에너지",
        "trade": ["생산"],
        "production": {
          "text": "세계 3위권 생산(비중 약 6%), 대부분 내수·재주입",
          "rank": 3
        },
        "reserve": {
          "text": "세계 2위 매장(사우스파스 등, 비중 약 16%)",
          "rank": 2
        },
        "note": "수출 인프라·제재로 매장 대비 수출 미흡. NIGC/NIOC 계열.",
        "companies": [
          {
            "name": "NIOC / NIGC",
            "hqCountry": "이란",
            "role": "가스 상류·수송",
            "ownership": "국영 100%",
            "majorHolders": [
              {
                "holder": "이란 정부",
                "country": "이란",
                "pct": 100
              }
            ]
          }
        ]
      },
      {
        "name": "철광석",
        "category": "광물",
        "trade": ["생산"],
        "production": {
          "text": "세계 약 6위권(비중 약 3%), 국내 철강 원료",
          "rank": 6
        },
        "reserve": {
          "text": "케르만 등 대규모 매장(세계 약 9위권)",
          "rank": 9
        },
        "note": "국영·준국영 광산. 제재로 장비·투자 제약.",
        "companies": [
          {
            "name": "Golgohar / Chadormalu 등 국영계",
            "hqCountry": "이란",
            "role": "철광 채굴",
            "ownership": "국영·준국영",
            "majorHolders": [
              {
                "holder": "이란 국영 계열",
                "country": "이란",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "구리",
        "category": "광물",
        "trade": ["생산"],
        "production": {
          "text": "사르체슈메 등 중동 유수 구리 산지",
          "rank": null
        },
        "reserve": {
          "text": "포르피리 구리 매장 풍부",
          "rank": null
        },
        "note": "NICICO 국영 중심.",
        "companies": [
          {
            "name": "National Iranian Copper Industries (NICICO)",
            "hqCountry": "이란",
            "role": "구리 채굴·제련",
            "ownership": "국영·상장 혼재(국가 지배)",
            "majorHolders": [
              {
                "holder": "이란 정부·기관",
                "country": "이란",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "석유화학",
        "category": "가공·무역",
        "trade": ["생산","수출"],
        "production": {
          "text": "대규모 석유화학 단지, 제재 하 수출",
          "rank": null
        },
        "reserve": {
          "text": "해당 없음",
          "rank": null
        },
        "note": "가스 원료 기반 다운스트림. 통계·소유 불투명.",
        "companies": [
          {
            "name": "NPC / 민영화 석유화학 단지",
            "hqCountry": "이란",
            "role": "석유화학 생산",
            "ownership": "준국영·민간 혼재",
            "majorHolders": [
              {
                "holder": "이란 기관·민간",
                "country": "이란",
                "pct": null
              }
            ]
          }
        ]
      }
    ],
    "confidence": "low",
    "sources": [
      "EIA",
      "OPEC (opaque)",
      "USGS",
      "NIOC statements"
    ]
  },
  {
    "id": "colombia",
    "country": "콜롬비아",
    "resources": [
      {
        "name": "원유",
        "category": "에너지",
        "trade": ["생산","수출"],
        "production": {
          "text": "중남미 주요 산유국, 성숙 유전·신규 탐사 병행",
          "rank": null
        },
        "reserve": {
          "text": "확인매장 중소, 가채연수 짧아 탐사 중요",
          "rank": null
        },
        "note": "Ecopetrol 중심. 파이프라인 보안·시위 리스크.",
        "companies": [
          {
            "name": "Ecopetrol",
            "hqCountry": "콜롬비아",
            "role": "국영 석유·가스·일부 광업",
            "ownership": "콜롬비아 정부 과반",
            "majorHolders": [
              {
                "holder": "콜롬비아 정부",
                "country": "콜롬비아",
                "pct": 88.5
              },
              {
                "holder": "일반 주주",
                "country": "다국적",
                "pct": 11.5
              }
            ]
          }
        ]
      },
      {
        "name": "석탄",
        "category": "에너지",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 유수 열탄 수출국, 세레혼·북부 탄전",
          "rank": null
        },
        "reserve": {
          "text": "대규모 노천 열탄 매장",
          "rank": null
        },
        "note": "유럽·아시아 수출. 에너지전환·지역 갈등.",
        "companies": [
          {
            "name": "Cerrejón",
            "hqCountry": "콜롬비아",
            "role": "대형 노천 석탄",
            "ownership": "Glencore 100%(인수 후)",
            "majorHolders": [
              {
                "holder": "Glencore",
                "country": "스위스",
                "pct": 100
              }
            ]
          }
        ]
      },
      {
        "name": "커피",
        "category": "농산물",
        "trade": ["생산","수출"],
        "production": {
          "text": "아라비카 고품질, 세계 3위권 생산·수출",
          "rank": 3
        },
        "reserve": {
          "text": "해당 없음",
          "rank": null
        },
        "note": "커피 벨트 소농. 국가 브랜드.",
        "companies": [
          {
            "name": "FNC (콜롬비아 커피생산자연합)",
            "hqCountry": "콜롬비아",
            "role": "수매·품질·수출 조율",
            "ownership": "생산자 단체",
            "majorHolders": [
              {
                "holder": "커피 소농 조합",
                "country": "콜롬비아",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "니켈",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세로 마토소 페로니켈, 세계 약 9위권",
          "rank": 9
        },
        "reserve": {
          "text": "코르도바 라테라이트",
          "rank": null
        },
        "note": "남미 대표 페로니켈 단일 광산.",
        "companies": [
          {
            "name": "Cerro Matoso (South32)",
            "hqCountry": "호주",
            "role": "페로니켈 생산",
            "ownership": "South32 사실상 100%",
            "majorHolders": [
              {
                "holder": "South32",
                "country": "호주",
                "pct": 99.9
              }
            ]
          }
        ]
      },
      {
        "name": "금·에메랄드",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "금 생산 유의미, 에메랄드 세계 최상위 품질·점유",
          "rank": null
        },
        "reserve": {
          "text": "안데스 금·보이 등 에메랄드 벨트",
          "rank": null
        },
        "note": "비공식 채굴·불법 광업 이슈. 백금족 소량(초코).",
        "companies": [
          {
            "name": "Aris Mining (구 Gran Colombia Gold) 등 / 소규모 채굴",
            "hqCountry": "캐나다·콜롬비아",
            "role": "금 채굴",
            "ownership": "외국·현지 혼재",
            "majorHolders": [
              {
                "holder": "외국·현지 자본",
                "country": "캐나다·콜롬비아",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "팜유",
        "category": "농산물",
        "trade": ["생산"],
        "production": {
          "text": "세계 4위권(비중 약 2%)",
          "rank": 4
        },
        "reserve": {
          "text": "해당 없음",
          "rank": null
        },
        "note": "동부 평원 확장. 내수·바이오디젤.",
        "companies": [
          {
            "name": "플랜테이션 기업·농가",
            "hqCountry": "콜롬비아",
            "role": "재배·압착",
            "ownership": "현지 기업+농가",
            "majorHolders": [
              {
                "holder": "현지 자본",
                "country": "콜롬비아",
                "pct": null
              }
            ]
          }
        ]
      }
    ],
    "confidence": "high",
    "sources": [
      "Ecopetrol",
      "USGS",
      "UPME",
      "FNC"
    ]
  },
  {
    "id": "pakistan",
    "country": "파키스탄",
    "resources": [
      {
        "name": "천연가스",
        "category": "에너지",
        "trade": ["생산","수입"],
        "production": {
          "text": "국내 주력 화석, 생산 정체로 LNG·파이프 수입 확대",
          "rank": null
        },
        "reserve": {
          "text": "확인매장 감소, 신규 발견 제한",
          "rank": null
        },
        "note": "에너지 적자·순환정전 구조적 원인 중 하나.",
        "companies": [
          {
            "name": "OGDC / PPL",
            "hqCountry": "파키스탄",
            "role": "국영 상류 가스·원유",
            "ownership": "정부 지배 상장",
            "majorHolders": [
              {
                "holder": "파키스탄 정부",
                "country": "파키스탄",
                "pct": null
              },
              {
                "holder": "일반 주주",
                "country": "파키스탄",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "석탄",
        "category": "에너지",
        "trade": ["생산","수입"],
        "production": {
          "text": "타르 탄전 등 국내 개발 확대 중, 품질·인프라 제약",
          "rank": null
        },
        "reserve": {
          "text": "타르(신드) 갈탄 세계 유수 매장 규모",
          "rank": null
        },
        "note": "중국 협력 발전 프로젝트 연계. 환경 이슈.",
        "companies": [
          {
            "name": "Sindh Engro Coal Mining 등",
            "hqCountry": "파키스탄",
            "role": "타르 석탄 채굴",
            "ownership": "합작(현지+Engro 등)",
            "majorHolders": [
              {
                "holder": "Engro 등 현지",
                "country": "파키스탄",
                "pct": null
              },
              {
                "holder": "신드 정부 등",
                "country": "파키스탄",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "구리·금 (Reko Diq)",
        "category": "광물",
        "trade": ["생산"],
        "production": {
          "text": "대형 광산 개발 단계, 본격 생산 전·초기",
          "rank": null
        },
        "reserve": {
          "text": "발루치스탄 Reko Diq 세계급 구리·금 매장",
          "rank": null
        },
        "note": "Barrick·정부 합작. 안보·지방 정치 리스크. 미래 핵심 자원.",
        "companies": [
          {
            "name": "Reko Diq Mining Company",
            "hqCountry": "파키스탄",
            "role": "구리·금 개발",
            "ownership": "Barrick + 파키스탄 정부 기관 합작",
            "majorHolders": [
              {
                "holder": "Barrick Gold",
                "country": "캐나다",
                "pct": 50
              },
              {
                "holder": "파키스탄 연방·발루치스탄 기관",
                "country": "파키스탄",
                "pct": 50
              }
            ]
          }
        ]
      },
      {
        "name": "밀",
        "category": "농산물",
        "trade": ["생산"],
        "production": {
          "text": "세계 약 8위권(비중 약 3%), 펀자브 곡창",
          "rank": 8
        },
        "reserve": {
          "text": "해당 없음",
          "rank": null
        },
        "note": "식량 안보 핵심. 소농+국가 조달.",
        "companies": [
          {
            "name": "소규모 농가·정부 조달",
            "hqCountry": "파키스탄",
            "role": "생산·비축",
            "ownership": "소농 중심",
            "majorHolders": [
              {
                "holder": "소규모 농가",
                "country": "파키스탄",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "면화",
        "category": "농산물",
        "trade": ["생산"],
        "production": {
          "text": "세계 상위 면화 산지, 섬유 산업 원료",
          "rank": null
        },
        "reserve": {
          "text": "해당 없음",
          "rank": null
        },
        "note": "섬유 수출 경제와 직결. 단수·병해 변동.",
        "companies": [
          {
            "name": "소농·방적 산업",
            "hqCountry": "파키스탄",
            "role": "재배·방적",
            "ownership": "소농+민간 방적",
            "majorHolders": [
              {
                "holder": "소농·민간",
                "country": "파키스탄",
                "pct": null
              }
            ]
          }
        ]
      }
    ],
    "confidence": "medium",
    "sources": [
      "USGS",
      "OGRA/OGDC",
      "Barrick",
      "FAO"
    ]
  },
  {
    "id": "romania",
    "country": "루마니아",
    "resources": [
      {
        "name": "원유·천연가스",
        "category": "에너지",
        "trade": ["생산"],
        "production": {
          "text": "EU 내 상대적 산유·산가스국, 흑해 가스 개발 진행",
          "rank": null
        },
        "reserve": {
          "text": "육상 성숙+흑해 신규 가스 매장",
          "rank": null
        },
        "note": "OMV Petrom·Romgaz. 역내 에너지 안보 기여 잠재.",
        "companies": [
          {
            "name": "OMV Petrom",
            "hqCountry": "루마니아",
            "role": "상류·정유 통합",
            "ownership": "OMV 과반 + 루마니아 국가 지분",
            "majorHolders": [
              {
                "holder": "OMV",
                "country": "오스트리아",
                "pct": 51
              },
              {
                "holder": "루마니아 정부",
                "country": "루마니아",
                "pct": 20.6
              },
              {
                "holder": "일반 주주",
                "country": "다국적",
                "pct": null
              }
            ]
          },
          {
            "name": "Romgaz",
            "hqCountry": "루마니아",
            "role": "국영 가스 생산",
            "ownership": "루마니아 정부 과반",
            "majorHolders": [
              {
                "holder": "루마니아 정부",
                "country": "루마니아",
                "pct": 70
              },
              {
                "holder": "일반 주주",
                "country": "다국적",
                "pct": 30
              }
            ]
          }
        ]
      },
      {
        "name": "소금",
        "category": "광물",
        "trade": ["생산"],
        "production": {
          "text": "암염·소금 광산 전통 산지",
          "rank": null
        },
        "reserve": {
          "text": "트란실바니아 등 대규모 암염",
          "rank": null
        },
        "note": "산업·식용. 관광 광산 병행.",
        "companies": [
          {
            "name": "Salrom",
            "hqCountry": "루마니아",
            "role": "국영 소금 생산",
            "ownership": "국영",
            "majorHolders": [
              {
                "holder": "루마니아 정부",
                "country": "루마니아",
                "pct": 100
              }
            ]
          }
        ]
      },
      {
        "name": "목재",
        "category": "농산물",
        "trade": ["생산","수출"],
        "production": {
          "text": "카르파티아 임업·제재 수출",
          "rank": null
        },
        "reserve": {
          "text": "EU 내 유의미 산림 자원",
          "rank": null
        },
        "note": "불법 벌채 논란·EU 규제.",
        "companies": [
          {
            "name": "민간 임업·제재",
            "hqCountry": "루마니아",
            "role": "벌채·가공",
            "ownership": "민간",
            "majorHolders": [
              {
                "holder": "민간 자본",
                "country": "루마니아·EU",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "금·구리(잠재)",
        "category": "광물",
        "trade": ["생산"],
        "production": {
          "text": "현재 대규모 생산 제한, 프로젝트 논쟁",
          "rank": null
        },
        "reserve": {
          "text": "로시아 몬타나 등 유망·민감 매장",
          "rank": null
        },
        "note": "환경·유산 반대로 대형 개발 지연. 자원 잠재 vs 사회 갈등.",
        "companies": [
          {
            "name": "과거 RMGC 등 외국 개발사",
            "hqCountry": "캐나다 등",
            "role": "금 프로젝트(중단·분쟁)",
            "ownership": "외국 자본 시도",
            "majorHolders": [
              {
                "holder": "외국 광산 자본",
                "country": "캐나다 등",
                "pct": null
              }
            ]
          }
        ]
      }
    ],
    "confidence": "medium",
    "sources": [
      "OMV Petrom",
      "Romgaz",
      "USGS",
      "EU energy stats"
    ]
  },
  {
    "id": "egypt",
    "country": "이집트",
    "resources": [
      {
        "name": "천연가스",
        "category": "에너지",
        "trade": ["생산","수출"],
        "production": {
          "text": "동지중해 최대급(조르 등), 2020년대 중반 생산·수출 변동·내수 부족 압력",
          "rank": null
        },
        "reserve": {
          "text": "확인매장 아프리카·지중해 상위",
          "rank": null
        },
        "note": "ENI 조르 발견으로 자급·LNG 수출 후 재수입 압력. 이스라엘 가스 수입 연계.",
        "companies": [
          {
            "name": "EGAS / EGPC",
            "hqCountry": "이집트",
            "role": "국영 가스·석유",
            "ownership": "이집트 정부 100%",
            "majorHolders": [
              {
                "holder": "이집트 정부",
                "country": "이집트",
                "pct": 100
              }
            ]
          },
          {
            "name": "Eni",
            "hqCountry": "이탈리아",
            "role": "조르 등 상류 운영",
            "ownership": "상장, 이탈리아 국가 지분",
            "majorHolders": [
              {
                "holder": "이탈리아 정부(MEF/Cassa)",
                "country": "이탈리아",
                "pct": null
              },
              {
                "holder": "일반 주주",
                "country": "다국적",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "원유",
        "category": "에너지",
        "trade": ["생산","수입"],
        "production": {
          "text": "성숙 유전, 순수입 성향 강화",
          "rank": null
        },
        "reserve": {
          "text": "수에즈만·서부사막 매장 중소",
          "rank": null
        },
        "note": "수에즈 운하·SUMED는 통과 자원 아닌 전략 인프라.",
        "companies": [
          {
            "name": "EGPC 합작(IOC)",
            "hqCountry": "이집트",
            "role": "원유 생산",
            "ownership": "국영+IOC 합작",
            "majorHolders": [
              {
                "holder": "EGPC",
                "country": "이집트",
                "pct": null
              },
              {
                "holder": "IOC",
                "country": "다국적",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "인광석",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 상위 인광 생산·수출",
          "rank": null
        },
        "reserve": {
          "text": "홍해·나일 서부 인광 벨트 대규모",
          "rank": null
        },
        "note": "비료 산업 연계. 북아프리카 인광 공급축.",
        "companies": [
          {
            "name": "Misr Phosphate / 국영 광업",
            "hqCountry": "이집트",
            "role": "인광 채굴",
            "ownership": "국영·준국영",
            "majorHolders": [
              {
                "holder": "이집트 정부",
                "country": "이집트",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "금",
        "category": "광물",
        "trade": ["생산"],
        "production": {
          "text": "수카리 등 대형 금광 가동으로 생산 증가",
          "rank": null
        },
        "reserve": {
          "text": "동부사막 누비아 실드 금 벨트",
          "rank": null
        },
        "note": "외국 광산+이집트 지분.",
        "companies": [
          {
            "name": "Centamin (Sukari)",
            "hqCountry": "저지섬·영국",
            "role": "수카리 금광",
            "ownership": "AngloGold Ashanti 완전 자회사 (2024년 11월 인수, 상장폐지)",
            "majorHolders": [
              {
                "holder": "AngloGold Ashanti (남아공 계열, 뉴욕 상장)",
                "country": "남아프리카공화국",
                "pct": null
              },
              {
                "holder": "이집트 EMRA 생산공유",
                "country": "이집트",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "면화",
        "category": "농산물",
        "trade": ["생산","수출"],
        "production": {
          "text": "장섬유 이집트산 면 프리미엄, 생산량 세계 비중은 중소",
          "rank": null
        },
        "reserve": {
          "text": "해당 없음",
          "rank": null
        },
        "note": "나일 관개 농업. 품질 브랜드.",
        "companies": [
          {
            "name": "소농·방적 공사",
            "hqCountry": "이집트",
            "role": "재배·방적",
            "ownership": "소농+국영·민간",
            "majorHolders": [
              {
                "holder": "소농·국영",
                "country": "이집트",
                "pct": null
              }
            ]
          }
        ]
      }
    ],
    "confidence": "medium",
    "sources": [
      "EIA",
      "EGAS",
      "USGS",
      "Eni"
    ]
  },
  {
    "id": "czechia",
    "country": "체코",
    "resources": [
      {
        "name": "갈탄·석탄",
        "category": "에너지",
        "trade": ["생산"],
        "production": {
          "text": "북서부 갈탄 발전용 채굴, 단계적 감축 정책",
          "rank": null
        },
        "reserve": {
          "text": "북보헤미아 갈탄 분지 잔존 매장",
          "rank": null
        },
        "note": "전통 에너지 자원. EU 탈석탄 일정과 충돌.",
        "companies": [
          {
            "name": "Sev.en / ČEZ 연계 광산",
            "hqCountry": "체코",
            "role": "갈탄 채굴·발전 연료",
            "ownership": "민간·준국영 혼재",
            "majorHolders": [
              {
                "holder": "현지 자본·ČEZ",
                "country": "체코",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "우라늄(역사·잔존)",
        "category": "에너지",
        "trade": ["생산"],
        "production": {
          "text": "과거 유럽 유수 생산, 현재 잔여·환경복원 단계",
          "rank": null
        },
        "reserve": {
          "text": "잔존 매장 있으나 신규 채굴 제한적",
          "rank": null
        },
        "note": "냉전 시기 전략 광산. 현재 전략 위상 하락.",
        "companies": [
          {
            "name": "DIAMO (국영)",
            "hqCountry": "체코",
            "role": "우라늄 잔여·복원",
            "ownership": "체코 정부 100%",
            "majorHolders": [
              {
                "holder": "체코 정부",
                "country": "체코",
                "pct": 100
              }
            ]
          }
        ]
      },
      {
        "name": "리튬(잠재)",
        "category": "광물",
        "trade": ["생산"],
        "production": {
          "text": "상업 생산 전·파일럿, 치노베츠 등 개발 추진",
          "rank": null
        },
        "reserve": {
          "text": "유럽 내 유망 경암 리튬 매장",
          "rank": null
        },
        "note": "EU 배터리 공급망 관심. 인허가·지역 수용성 변수.",
        "companies": [
          {
            "name": "ČEZ / European Metals 등 합작 논의",
            "hqCountry": "체코·호주",
            "role": "리튬 프로젝트",
            "ownership": "국영전력+외국 탐광",
            "majorHolders": [
              {
                "holder": "ČEZ",
                "country": "체코",
                "pct": null
              },
              {
                "holder": "European Metals",
                "country": "호주",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "목재·카올린 등",
        "category": "광물",
        "trade": ["생산"],
        "production": {
          "text": "임산물·도자기용 카올린·건설광물",
          "rank": null
        },
        "reserve": {
          "text": "산업광물 자급 성격",
          "rank": null
        },
        "note": "세계적 전략 광물국은 아님. 제조업 원료 보조.",
        "companies": [
          {
            "name": "현지 산업광물·임업 기업",
            "hqCountry": "체코",
            "role": "채굴·가공",
            "ownership": "민간",
            "majorHolders": [
              {
                "holder": "현지 민간",
                "country": "체코",
                "pct": null
              }
            ]
          }
        ]
      }
    ],
    "confidence": "medium",
    "sources": [
      "Czech Geological Survey",
      "ČEZ",
      "USGS",
      "EU critical raw materials"
    ]
  },
  {
    "id": "chile",
    "country": "칠레",
    "resources": [
      {
        "name": "구리",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 1위(비중 약 24–27%), 에스콘디다·코델코 광산군",
          "rank": 1
        },
        "reserve": {
          "text": "세계 1위(약 1.9억 t·비중 약 20%)",
          "rank": 1
        },
        "note": "국가 재정·수출 핵심. 품위 하락·물·전력 제약.",
        "companies": [
          {
            "name": "Codelco",
            "hqCountry": "칠레",
            "role": "국영 구리 생산",
            "ownership": "칠레 정부 100%",
            "majorHolders": [
              {
                "holder": "칠레 정부",
                "country": "칠레",
                "pct": 100
              }
            ]
          },
          {
            "name": "BHP (Escondida)",
            "hqCountry": "호주",
            "role": "세계 최대급 구리 광산 운영",
            "ownership": "합작",
            "majorHolders": [
              {
                "holder": "BHP",
                "country": "호주",
                "pct": 57.5
              },
              {
                "holder": "Rio Tinto",
                "country": "영국·호주",
                "pct": 30
              },
              {
                "holder": "JECO 등",
                "country": "일본",
                "pct": 12.5
              }
            ]
          }
        ]
      },
      {
        "name": "리튬",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 2위권 염수 리튬(비중 약 25%)",
          "rank": 2
        },
        "reserve": {
          "text": "세계 1위 매장(아타카마, 비중 약 36%)",
          "rank": 1
        },
        "note": "SQM·Albemarle. Codelco-SQM 합작으로 국가 통제 강화(2030년대).",
        "companies": [
          {
            "name": "SQM",
            "hqCountry": "칠레",
            "role": "아타카마 염수 리튬·칼륨",
            "ownership": "상장, 중국·칠레 지분 혼재",
            "majorHolders": [
              {
                "holder": "Tianqi Lithium",
                "country": "중국",
                "pct": 22
              },
              {
                "holder": "Pampa Group 등",
                "country": "칠레",
                "pct": null
              },
              {
                "holder": "일반 주주",
                "country": "다국적",
                "pct": null
              }
            ]
          },
          {
            "name": "Albemarle",
            "hqCountry": "미국",
            "role": "아타카마 리튬 생산",
            "ownership": "상장",
            "majorHolders": [
              {
                "holder": "기관 주주",
                "country": "미국 등",
                "pct": null
              }
            ]
          },
          {
            "name": "Codelco (리튬 합작)",
            "hqCountry": "칠레",
            "role": "NovaAndino Litio 등 국가 리튬 파트너",
            "ownership": "칠레 정부 100%",
            "majorHolders": [
              {
                "holder": "칠레 정부",
                "country": "칠레",
                "pct": 100
              }
            ]
          }
        ]
      },
      {
        "name": "몰리브덴",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "구리 부산물 세계 최상위 생산",
          "rank": null
        },
        "reserve": {
          "text": "구리 광상 수반 매장",
          "rank": null
        },
        "note": "철강 합금 원료. Codelco·민간 구리광.",
        "companies": [
          {
            "name": "Codelco / 구리 광산 운영사",
            "hqCountry": "칠레",
            "role": "몰리브덴 부산물",
            "ownership": "국영+다국적",
            "majorHolders": [
              {
                "holder": "Codelco·BHP 등",
                "country": "칠레·호주",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "은",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "구리 부산물 은, 세계 약 4위권(비중 약 6%)",
          "rank": 4
        },
        "reserve": {
          "text": "북부 구리벨트 수반(약 7위·비중 5%)",
          "rank": 7
        },
        "note": "독립 은광보다 부산물 비중.",
        "companies": [
          {
            "name": "BHP·Codelco 등",
            "hqCountry": "호주·칠레",
            "role": "구리 부산물 은",
            "ownership": "다국적·국영",
            "majorHolders": [
              {
                "holder": "BHP·Codelco",
                "country": "호주·칠레",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "요오드·질산염",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "아타카마 칼레체 요오드 세계 최상위",
          "rank": null
        },
        "reserve": {
          "text": "북부 사막 특수 광상",
          "rank": null
        },
        "note": "SQM 등 특수화학.",
        "companies": [
          {
            "name": "SQM / Cosayach 등",
            "hqCountry": "칠레",
            "role": "요오드·질산염",
            "ownership": "상장·민간",
            "majorHolders": [
              {
                "holder": "SQM 등",
                "country": "칠레",
                "pct": null
              }
            ]
          }
        ]
      }
    ],
    "confidence": "high",
    "sources": [
      "USGS",
      "Cochilco",
      "Codelco",
      "SQM"
    ]
  },
  {
    "id": "finland",
    "country": "핀란드",
    "resources": [
      {
        "name": "니켈",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "테라파메 등 EU 내 핵심 니켈 산지(세계 약 10위·비중 약 1%)",
          "rank": 10
        },
        "reserve": {
          "text": "탈비바라 등 황화·흑색혈암형 매장",
          "rank": null
        },
        "note": "배터리 니켈·중간재. 국영 Finnish Minerals Group 주도.",
        "companies": [
          {
            "name": "Terrafame",
            "hqCountry": "핀란드",
            "role": "니켈·아연·코발트 바이오힐칭 생산",
            "ownership": "국영 지주 과반 + Trafigura(Galena) 계열",
            "majorHolders": [
              {
                "holder": "Finnish Minerals Group",
                "country": "핀란드",
                "pct": 56.1
              },
              {
                "holder": "Galena (Trafigura)",
                "country": "싱가포르",
                "pct": 39.4
              },
              {
                "holder": "Mandatum 등 기타",
                "country": "핀란드",
                "pct": 4.5
              }
            ]
          }
        ]
      },
      {
        "name": "임산물·목재",
        "category": "농산물",
        "trade": ["생산","수출"],
        "production": {
          "text": "펄프·제지·목재 세계 유수 수출, 바이오경제 기반",
          "rank": null
        },
        "reserve": {
          "text": "국토 대부분 산림, 지속가능 시업",
          "rank": null
        },
        "note": "전통 국가 기간 자원. EU 탄소·생물다양성 규제.",
        "companies": [
          {
            "name": "UPM / Stora Enso / Metsä",
            "hqCountry": "핀란드",
            "role": "임산·펄프·제지·바이오",
            "ownership": "상장·협동조합",
            "majorHolders": [
              {
                "holder": "기관·재단 주주",
                "country": "핀란드",
                "pct": null
              },
              {
                "holder": "Metsäliitto 협동",
                "country": "핀란드",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "코발트·배터리 원료",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "니켈 수반 코발트·정련 역량, EU 배터리 밸류체인",
          "rank": null
        },
        "reserve": {
          "text": "니켈 광상 수반",
          "rank": null
        },
        "note": "채굴+정련+전구물질 클러스터 지향.",
        "companies": [
          {
            "name": "Terrafame / Freeport Cobalt(역사) 등",
            "hqCountry": "핀란드",
            "role": "코발트 중간재",
            "ownership": "국영·다국적 혼재",
            "majorHolders": [
              {
                "holder": "Finnish Minerals Group 등",
                "country": "핀란드",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "백금족·구리-니켈",
        "category": "광물",
        "trade": ["생산"],
        "production": {
          "text": "케비차 등 PGM·니켈-구리(세계 PGM 소량·약 7위)",
          "rank": 7
        },
        "reserve": {
          "text": "라플란드 매그매틱 벨트",
          "rank": 6
        },
        "note": "Boliden 운영. EU 내 희소 1차 PGM.",
        "companies": [
          {
            "name": "Boliden Kevitsa",
            "hqCountry": "스웨덴",
            "role": "니켈·구리·PGM 광산",
            "ownership": "Boliden 100%",
            "majorHolders": [
              {
                "holder": "Boliden",
                "country": "스웨덴",
                "pct": 100
              }
            ]
          }
        ]
      },
      {
        "name": "토탄·바이오에너지",
        "category": "에너지",
        "trade": ["생산"],
        "production": {
          "text": "전통 토탄 축소, 바이오매스·열병합 확대",
          "rank": null
        },
        "reserve": {
          "text": "이탄지 광범위, 기후정책으로 채굴 축소",
          "rank": null
        },
        "note": "에너지 전환 중. 임산 바이오 비중 증가.",
        "companies": [
          {
            "name": "Neova 등",
            "hqCountry": "핀란드",
            "role": "토탄·원예·에너지",
            "ownership": "국영 지분 유의미",
            "majorHolders": [
              {
                "holder": "핀란드 국가·민간",
                "country": "핀란드",
                "pct": null
              }
            ]
          }
        ]
      }
    ],
    "confidence": "high",
    "sources": [
      "USGS",
      "GTK Finland",
      "Terrafame",
      "Finnish Minerals Group"
    ]
  },
  {
    "id": "portugal",
    "country": "포르투갈",
    "resources": [
      {
        "name": "리튬",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "현재 소량(세계 약 8위·비중 1% 미만, 연 ~380 t Li), 바로주 등 개발 추진",
          "rank": 8
        },
        "reserve": {
          "text": "유럽 내 경암 리튬 매장(약 9위권)",
          "rank": 9
        },
        "note": "EU 전략 원료. 주민 반대·인허가로 대형 생산 지연.",
        "companies": [
          {
            "name": "Savannah Resources",
            "hqCountry": "영국",
            "role": "바로주 리튬 프로젝트",
            "ownership": "상장 탐광",
            "majorHolders": [
              {
                "holder": "기관·일반 주주",
                "country": "영국 등",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "구리·아연",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "네베스코르부 등 이베리아 황화광상 생산",
          "rank": null
        },
        "reserve": {
          "text": "이베리아 파이라이트 벨트",
          "rank": null
        },
        "note": "중견 광업국 수준.",
        "companies": [
          {
            "name": "Lundin Mining (Neves-Corvo)",
            "hqCountry": "캐나다",
            "role": "구리·아연 광산",
            "ownership": "상장",
            "majorHolders": [
              {
                "holder": "Lundin 가문·기관",
                "country": "캐나다·스웨덴",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "텅스텐",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "유럽 내 희소 텅스텐 산지(판나스케이라 등)",
          "rank": null
        },
        "reserve": {
          "text": "중부 화강암 관련 매장",
          "rank": null
        },
        "note": "전략 금속. 중국 의존 완화 관심.",
        "companies": [
          {
            "name": "Almonty / 현지 광산",
            "hqCountry": "캐나다·포르투갈",
            "role": "텅스텐 채굴",
            "ownership": "외국·현지",
            "majorHolders": [
              {
                "holder": "외국 광산 자본",
                "country": "캐나다 등",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "코르크",
        "category": "농산물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 1위 코르크 생산·가공",
          "rank": 1
        },
        "reserve": {
          "text": "코르크참나무 숲(몬타도) 최대",
          "rank": null
        },
        "note": "와인 마개·건축·산업 소재. 독보적 비목재 임산물.",
        "companies": [
          {
            "name": "Amorim",
            "hqCountry": "포르투갈",
            "role": "코르크 가공 세계 최대",
            "ownership": "상장·가문",
            "majorHolders": [
              {
                "holder": "Amorim 가문",
                "country": "포르투갈",
                "pct": null
              },
              {
                "holder": "일반 주주",
                "country": "다국적",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "수산·해산물",
        "category": "농산물",
        "trade": ["생산"],
        "production": {
          "text": "대서양 어업·양식, 내수·EU 시장",
          "rank": null
        },
        "reserve": {
          "text": "EEZ 어업 자원",
          "rank": null
        },
        "note": "전통 식량 자원. 할당·지속가능 이슈.",
        "companies": [
          {
            "name": "어업 협동·가공 기업",
            "hqCountry": "포르투갈",
            "role": "어획·가공",
            "ownership": "민간·협동",
            "majorHolders": [
              {
                "holder": "현지 어업 자본",
                "country": "포르투갈",
                "pct": null
              }
            ]
          }
        ]
      }
    ],
    "confidence": "medium",
    "sources": [
      "USGS",
      "DGEG Portugal",
      "Savannah Resources",
      "FAO"
    ]
  },
  {
    "id": "kazakhstan",
    "country": "카자흐스탄",
    "resources": [
      {
        "name": "원유",
        "category": "에너지",
        "trade": ["생산","수출"],
        "production": {
          "text": "텐기즈·카샤간·카라차가낙 등 중견 산유·수출국",
          "rank": null
        },
        "reserve": {
          "text": "카스피해 연안 대규모 매장, 세계 상위권",
          "rank": null
        },
        "note": "CPC 파이프라인 수출. 다국적 컨소시엄+국영 KazMunayGas.",
        "companies": [
          {
            "name": "KazMunayGas",
            "hqCountry": "카자흐스탄",
            "role": "국영 석유 홀딩",
            "ownership": "Samruk-Kazyna 지배",
            "majorHolders": [
              {
                "holder": "Samruk-Kazyna",
                "country": "카자흐스탄",
                "pct": null
              }
            ]
          },
          {
            "name": "Tengizchevroil",
            "hqCountry": "카자흐스탄",
            "role": "텐기즈 유전 운영",
            "ownership": "Chevron 주도 합작",
            "majorHolders": [
              {
                "holder": "Chevron",
                "country": "미국",
                "pct": 50
              },
              {
                "holder": "ExxonMobil",
                "country": "미국",
                "pct": 25
              },
              {
                "holder": "KazMunayGas",
                "country": "카자흐스탄",
                "pct": 20
              },
              {
                "holder": "Lukoil",
                "country": "러시아",
                "pct": 5
              }
            ]
          }
        ]
      },
      {
        "name": "우라늄",
        "category": "에너지",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 1위(비중 약 40%+)",
          "rank": 1
        },
        "reserve": {
          "text": "세계 2위권(비중 약 13%)",
          "rank": 2
        },
        "note": "ISR 채굴. 서방·중국·러시아 공급 다변화 핵심.",
        "companies": [
          {
            "name": "Kazatomprom",
            "hqCountry": "카자흐스탄",
            "role": "국영 우라늄 생산",
            "ownership": "국가 합산 과반(Samruk-Kazyna+재무부) + 상장 유통 25%",
            "majorHolders": [
              {
                "holder": "Samruk-Kazyna",
                "country": "카자흐스탄",
                "pct": 63
              },
              {
                "holder": "카자흐스탄 재무부",
                "country": "카자흐스탄",
                "pct": 12
              },
              {
                "holder": "일반 주주(자유유통)",
                "country": "다국적",
                "pct": 25
              }
            ]
          }
        ]
      },
      {
        "name": "구리",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 약 9위(비중 약 3%), 악토가이 등",
          "rank": 9
        },
        "reserve": {
          "text": "발하시·동카자흐 벨트(약 9위)",
          "rank": 9
        },
        "note": "중국 수출 비중 높음. KAZ Minerals·Glencore 계열.",
        "companies": [
          {
            "name": "KAZ Minerals",
            "hqCountry": "카자흐스탄",
            "role": "구리 광산",
            "ownership": "민간(상장 폐지 후 지배 구조 단순)",
            "majorHolders": [
              {
                "holder": "현지 대주주",
                "country": "카자흐스탄",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "석탄",
        "category": "에너지",
        "trade": ["생산","수출"],
        "production": {
          "text": "에키바스투스 등 세계 약 8위(비중 약 1.5%)",
          "rank": 8
        },
        "reserve": {
          "text": "대규모(세계 약 8위·비중 약 3%)",
          "rank": 8
        },
        "note": "국내 발전·일부 수출. 탄소 전환 과제.",
        "companies": [
          {
            "name": "Bogatyr Komir 등",
            "hqCountry": "카자흐스탄",
            "role": "대형 노천 석탄",
            "ownership": "국영·현지·합작",
            "majorHolders": [
              {
                "holder": "국영·현지 자본",
                "country": "카자흐스탄",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "금·은",
        "category": "광물",
        "trade": ["생산"],
        "production": {
          "text": "금 세계 약 6위권, 은은 다금속 부산물",
          "rank": 6
        },
        "reserve": {
          "text": "다금속·오르제닉 금 벨트",
          "rank": null
        },
        "note": "Glencore Kazzinc 등 외국 지분 혼재.",
        "companies": [
          {
            "name": "Kazzinc (Glencore)",
            "hqCountry": "스위스·카자흐스탄",
            "role": "아연·납·금·은",
            "ownership": "Glencore 지배+국부 지분",
            "majorHolders": [
              {
                "holder": "Glencore",
                "country": "스위스",
                "pct": 70
              },
              {
                "holder": "Tau-Ken Samruk",
                "country": "카자흐스탄",
                "pct": 30
              }
            ]
          }
        ]
      },
      {
        "name": "밀",
        "category": "농산물",
        "trade": ["생산","수출"],
        "production": {
          "text": "북부 스텝 밀 수출국, 중앙亞·중동 공급",
          "rank": null
        },
        "reserve": {
          "text": "해당 없음",
          "rank": null
        },
        "note": "기후·물류(철도) 변수. 곡물 안보 자산.",
        "companies": [
          {
            "name": "대형 농기업·소농",
            "hqCountry": "카자흐스탄",
            "role": "밀 생산·수출",
            "ownership": "민간·준국영 혼재",
            "majorHolders": [
              {
                "holder": "현지 농기업",
                "country": "카자흐스탄",
                "pct": null
              }
            ]
          }
        ]
      }
    ],
    "confidence": "high",
    "sources": [
      "USGS",
      "Kazatomprom",
      "KazMunayGas",
      "EIA"
    ]
  },
  {
    "id": "peru",
    "country": "페루",
    "resources": [
      {
        "name": "구리",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 3위(비중 약 11%; 2023년부터 DR콩고가 2위), 안타미나·세로베르데·라스밤바스 등",
          "rank": 3
        },
        "reserve": {
          "text": "세계 3위권(약 1.2억 t·비중 약 9%)",
          "rank": 3
        },
        "note": "수출·재정 핵심. 지역 갈등·도로 봉쇄 리스크 상시.",
        "companies": [
          {
            "name": "Antamina",
            "hqCountry": "페루",
            "role": "대형 구리·아연 광산",
            "ownership": "다국적 컨소시엄",
            "majorHolders": [
              {
                "holder": "BHP",
                "country": "호주",
                "pct": 33.75
              },
              {
                "holder": "Glencore",
                "country": "스위스",
                "pct": 33.75
              },
              {
                "holder": "Teck",
                "country": "캐나다",
                "pct": 22.5
              },
              {
                "holder": "Mitsubishi",
                "country": "일본",
                "pct": 10
              }
            ]
          },
          {
            "name": "Cerro Verde (Freeport)",
            "hqCountry": "미국",
            "role": "구리 광산",
            "ownership": "Freeport 과반 합작",
            "majorHolders": [
              {
                "holder": "Freeport-McMoRan",
                "country": "미국",
                "pct": null
              },
              {
                "holder": "Buenaventura·Sumitomo 등",
                "country": "페루·일본",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "은",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 3위권(비중 약 12–13%; 멕시코·중국 다음)",
          "rank": 3
        },
        "reserve": {
          "text": "세계 1위 매장(비중 약 22%)",
          "rank": 1
        },
        "note": "구리·다금속 부산물+전용 은광. 안데스 벨트.",
        "companies": [
          {
            "name": "Buenaventura / Hochschild / 다국적",
            "hqCountry": "페루·영국",
            "role": "은·금 채굴",
            "ownership": "상장 현지·외국",
            "majorHolders": [
              {
                "holder": "현지·외국 주주",
                "country": "페루·영국 등",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "금",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "중남미 유수 금 생산국, 공식+비공식 혼재",
          "rank": null
        },
        "reserve": {
          "text": "안데스 에피서멀·산금 벨트",
          "rank": null
        },
        "note": "비공식 채굴·환경·수은 이슈. Yanacocha 등 대형 광산 성숙.",
        "companies": [
          {
            "name": "Newmont (Yanacocha 등)",
            "hqCountry": "미국",
            "role": "대형 금광",
            "ownership": "상장 메이저",
            "majorHolders": [
              {
                "holder": "기관 주주",
                "country": "미국 등",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "아연·납",
        "category": "광물",
        "trade": ["생산","수출"],
        "production": {
          "text": "세계 상위 아연 산지, 안타미나 등",
          "rank": null
        },
        "reserve": {
          "text": "다금속 안데스 매장",
          "rank": null
        },
        "note": "구리와 동일 벨트 수반 생산.",
        "companies": [
          {
            "name": "Antamina / Volcan 등",
            "hqCountry": "페루·스위스",
            "role": "아연·납·구리",
            "ownership": "다국적·현지",
            "majorHolders": [
              {
                "holder": "Glencore·현지",
                "country": "스위스·페루",
                "pct": null
              }
            ]
          }
        ]
      },
      {
        "name": "어분·수산",
        "category": "농산물",
        "trade": ["생산","수출"],
        "production": {
          "text": "앤초비 기반 어분·어유 세계 최상위 수출",
          "rank": 1
        },
        "reserve": {
          "text": "훔볼트 해류 어장(기후·엘니뇨 변동)",
          "rank": null
        },
        "note": "광업 다음 전통 외화 획득원. 쿼터·금어기.",
        "companies": [
          {
            "name": "Tasa / Copeinca 등",
            "hqCountry": "페루",
            "role": "어획·어분 가공",
            "ownership": "민간",
            "majorHolders": [
              {
                "holder": "현지·외국 민간",
                "country": "페루 등",
                "pct": null
              }
            ]
          }
        ]
      }
    ],
    "confidence": "high",
    "sources": [
      "USGS",
      "MINEM Peru",
      "Cochilco peers",
      "company reports"
    ]
  }
];

const COUNTRY_RESOURCES_BY_ID = Object.fromEntries(
  (typeof COUNTRY_RESOURCES !== "undefined" ? COUNTRY_RESOURCES : []).map(p => [p.id, p])
);
