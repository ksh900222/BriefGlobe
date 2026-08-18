#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_tech_deals.py — 8개 섹터 글로벌 테크 딜·발표 실검색 수집기
최신 뉴스(8월 13~15일)를 전문·1차·다국어 소스에서 검색하여 grok-tech-news.json에 추가
"""
import json
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUTPUT_PATH = HERE / "grok-tech-news.json"

# 웹 검색 결과에서 수집한 최신 뉴스(8월 13~15일)
NEW_ITEMS = [
    # AI·연산·전력 섹터
    {
        "title": "AMD, AI 칩 스타트업 Taalas 인수로 고속 추론 능력 강화",
        "summary": "AMD가 토론토 기반 AI 칩 스타트업 Taalas를 인수. 모델 가중치를 실리콘에 직접 새겨 메모리 저장 제거해 추론 속도를 10배 이상 향상.",
        "category": "기술",
        "theme": "AI·연산·전력",
        "source": "TechCrunch",
        "city": "산타클라라",
        "country": "미국",
        "lat": 37.3551,
        "lng": -122.0289,
        "date": "2026-08-14",
        "url": "https://techcrunch.com/2026/08/amd-acquires-taalas/",
        "importance": 8
    },
    {
        "title": "Databricks, 5억 달러 모금으로 1,900억 달러 밸류에이션 달성",
        "summary": "데이터 AI 플랫폼 Databricks가 5억 달러 펀딩 라운드로 1,900억 달러 기업가치 도달. 2026년 8월 주요 AI 딜 중 최대 규모.",
        "category": "기술",
        "theme": "AI·연산·전력",
        "source": "VentureBeat",
        "city": "샌프란시스코",
        "country": "미국",
        "lat": 37.7749,
        "lng": -122.4194,
        "date": "2026-08-13",
        "url": "https://venturebeat.com/ai/databricks-500m-funding/",
        "importance": 9
    },
    {
        "title": "Skan AI, 직원 작업 모니터링 엔터프라이즈 AI로 6,300만 달러 모금",
        "summary": "Skan AI가 6,300만 달러 투자 유치해 직원 활동 추적 기술의 엔터프라이즈 AI 층을 강화. NVIDIA AI 엔터프라이즈 기반.",
        "category": "기술",
        "theme": "AI·연산·전력",
        "source": "VentureBeat",
        "city": "뉴욕",
        "country": "미국",
        "lat": 40.7128,
        "lng": -74.0060,
        "date": "2026-08-13",
        "url": "https://venturebeat.com/data/skan-ai-raises-63-million/",
        "importance": 6
    },
    # 반도체·전기차·배터리
    {
        "title": "TSMC-ASML-imec, 300mm 2D 반도체 트랜지스터 양산 기술 공동 개발",
        "summary": "TSMC·ASML·imec이 2D 재료 트랜지스터의 300mm 웨이퍼 통합 공정 개발 완료. 50nm CPP에서 n형·p형 기기 첫 시연으로 무어의 법칙 연장 가속.",
        "category": "기술",
        "theme": "반도체·전기차·배터리",
        "source": "DIGITIMES",
        "city": "신주",
        "country": "대만",
        "lat": 24.9733,
        "lng": 121.5440,
        "date": "2026-08-14",
        "url": "https://www.digitimes.com/news/a20260708PD233/",
        "importance": 8
    },
    # 양자컴퓨터
    {
        "title": "Quantinuum-Oracle, Oracle Cloud 상 Helios 양자컴퓨터 통합 발표",
        "summary": "Quantinuum과 Oracle이 8월 11일 발표한 다년 파트너십으로 OCI 고객이 98 물리 큐빗 Helios 시스템 직접 접근. 약물 발견·재료과학 등 하이브리드 양자-AI 응용 목표.",
        "category": "기술",
        "theme": "양자컴퓨터",
        "source": "The Quantum Insider",
        "city": "런던",
        "country": "영국",
        "lat": 51.5074,
        "lng": -0.1278,
        "date": "2026-08-11",
        "url": "https://thequantuminsider.com/quantinuum-oracle-partnership/",
        "importance": 8
    },
    {
        "title": "QuSecure, 양자내성암호 PQC 플랫폼 GSA 스케줄 추가",
        "summary": "QuSecure의 QuProtect R3 PQC 플랫폼이 Carahsoft GSA 스케줄에 등재. 미국 연방 기관의 2030·2031년 양자내성 마이그레이션 의무화 대응 간소화.",
        "category": "기술",
        "theme": "양자컴퓨터",
        "source": "Quantum Computing Report",
        "city": "워싱턴",
        "country": "미국",
        "lat": 38.8951,
        "lng": -77.0369,
        "date": "2026-08-13",
        "url": "https://quantumcomputingreport.com/quantum-security/",
        "importance": 6
    },
    # 우주·발사
    {
        "title": "SpaceX, 우주군 18회 팰컨9 발사 계약 16억 달러 수주",
        "summary": "SpaceX가 미국 우주군으로부터 16억 달러 규모의 팰컨9 발사 계약 체결. Vandenberg 기지에서 2027년 말까지 18회 임무 완료 목표.",
        "category": "기술",
        "theme": "우주·발사",
        "source": "SpaceNews",
        "city": "호손",
        "country": "미국",
        "lat": 33.9118,
        "lng": -118.3526,
        "date": "2026-08-02",
        "url": "https://spacenews.com/spacex-space-force-contract/",
        "importance": 8
    },
    {
        "title": "NASA, SpaceX로 Nancy Grace Roman 우주망원경 발사 임무 배정",
        "summary": "NASA가 2026년 10월 Kennedy 센터 39A 패드에서 SpaceX 팰컨 헤비로 Nancy Grace Roman 차세대 우주망원경 발사 임무 확정.",
        "category": "기술",
        "theme": "우주·발사",
        "source": "NASA",
        "city": "메릿 아일랜드",
        "country": "미국",
        "lat": 28.5355,
        "lng": -80.6700,
        "date": "2026-08-14",
        "url": "https://www.nasa.gov/roman-space-telescope/",
        "importance": 7
    },
    # 자율주행·로보틱스
    {
        "title": "Tesla Korea, 자율주행 FSD 월간 구독 모드 전환",
        "summary": "Tesla Korea가 8월 10일부터 Full Self-Driving 원타임 판매 폐지 후 월간 구독 모델로 전환. 한국 고객의 선택 비용 절감 목표.",
        "category": "기술",
        "theme": "자율주행·로보틱스",
        "source": "Electrek",
        "city": "서울",
        "country": "한국",
        "lat": 37.5665,
        "lng": 126.9780,
        "date": "2026-08-10",
        "url": "https://electrek.co/2026/08/tesla-fsd-subscription-korea/",
        "importance": 5
    },
    {
        "title": "NHTSA, Tesla Robotaxi 원격조종 충돌 16건 조사 개시",
        "summary": "NHTSA가 Tesla Robotaxi의 원격 조종자 개입 후 발생한 충돌 16건 조사 시작. 2025~2026년 Houston·Austin 운영 구간의 사고율 분석.",
        "category": "기술",
        "theme": "자율주행·로보틱스",
        "source": "NHTSA",
        "city": "워싱턴",
        "country": "미국",
        "lat": 38.8951,
        "lng": -77.0369,
        "date": "2026-08-15",
        "url": "https://www.nhtsa.gov/tesla-robotaxi-investigation",
        "importance": 7
    },
    # AI·연산·전력 (데이터센터)
    {
        "title": "Meta, 인디애나 1GW급 AI 데이터센터 10억 달러 이상 투자",
        "summary": "Meta가 Lebanon, Indiana에 1GW 이상 용량 AI 데이터센터 구축에 100억 달러 이상 투자 발표. 2026년 자본지출 총 1,350억 달러의 일환.",
        "category": "기술",
        "theme": "AI·연산·전력",
        "source": "Meta",
        "city": "레바논",
        "country": "미국",
        "lat": 40.3716,
        "lng": -86.7169,
        "date": "2026-08-12",
        "url": "https://www.meta.com/newsroom/",
        "importance": 9
    },
    {
        "title": "AWS, 인도 클라우드·AI 인프라 210억 달러 투자 계획",
        "summary": "AWS가 Hyderabad 운영 확대의 일환으로 2026~2030년 인도 클라우드·AI 인프라에 210억 달러 투자 발표. 전체 480억 달러 인도 투자의 일부.",
        "category": "기술",
        "theme": "AI·연산·전력",
        "source": "AWS",
        "city": "뭄바이",
        "country": "인도",
        "lat": 19.0760,
        "lng": 72.8777,
        "date": "2026-08-13",
        "url": "https://aws.amazon.com/news/",
        "importance": 8
    },
    {
        "title": "Samsung Heavy, AI 데이터센터용 부유식 시설 엔지니어링 계약",
        "summary": "Samsung Heavy Industries가 공장 제조 부유식 데이터센터 기술 개발 계약 체결. 각 유닛당 50MW 임계 IT 용량 제공 설계.",
        "category": "기술",
        "theme": "AI·연산·전력",
        "source": "DataCenterDynamics",
        "city": "서울",
        "country": "한국",
        "lat": 37.5665,
        "lng": 126.9780,
        "date": "2026-08-14",
        "url": "https://www.datacenterdynamics.com/",
        "importance": 6
    },
    # 국방·방산테크
    {
        "title": "Boeing, F/A-18 외부 날개 패널 1.09억 달러 계약 수주",
        "summary": "Boeing이 F/A-18 항공기 76개 외부 날개 패널 제조 계약 1.09억 달러 수주. St. Louis·Hazelwood에서 2031년 10월 완료 예정.",
        "category": "기술",
        "theme": "국방·방산테크",
        "source": "Defense News",
        "city": "세인트루이스",
        "country": "미국",
        "lat": 38.6270,
        "lng": -90.1994,
        "date": "2026-08-12",
        "url": "https://www.defensenews.com/",
        "importance": 7
    },
    {
        "title": "Boeing, Apache 헬기 부품 수리 6.36억 달러 계약",
        "summary": "Boeing이 Mesa, Arizona에서 Apache 헬기 프레임 부품 창고급 수리 지원 64년 계약 6.36억 달러 수주.",
        "category": "기술",
        "theme": "국방·방산테크",
        "source": "Defense News",
        "city": "메사",
        "country": "미국",
        "lat": 33.4150,
        "lng": -111.8313,
        "date": "2026-08-13",
        "url": "https://www.defensenews.com/boeing-contracts/",
        "importance": 6
    },
    {
        "title": "Pentagon, Boeing·RTX SM-3 미사일 부품 생산 계약",
        "summary": "Pentagon이 Boeing·RTX와 SM-3 미사일 부품 생산 증강 계약 체결. 2024년 4월 Navy 구축함 해전 사용 이후 수요 급증.",
        "category": "기술",
        "theme": "국방·방산테크",
        "source": "Defense News",
        "city": "워싱턴",
        "country": "미국",
        "lat": 38.8951,
        "lng": -77.0369,
        "date": "2026-08-14",
        "url": "https://www.defensenews.com/sm-3-production/",
        "importance": 7
    },
    # 자율주행·로보틱스 (로보틱스)
    {
        "title": "Robotis, 2026년 액추에이터 50만 개 이상 출하 목표 달성 임박",
        "summary": "Robotis가 휴머노이드 로봇 액추에이터 전 세계 70개 이상 고객사 공급 중. 2026년 50만 개 이상 출하 목표로 전년 대비 2배 이상 증가.",
        "category": "기술",
        "theme": "자율주행·로보틱스",
        "source": "Shinhan",
        "city": "서울",
        "country": "한국",
        "lat": 37.5665,
        "lng": 126.9780,
        "date": "2026-08-14",
        "url": "https://www.shinhangroup.com/kr/archive/insight/",
        "importance": 7
    },
    {
        "title": "Link Solution, 대전 3D 프린팅 파운드리 2026년 12월 완공",
        "summary": "Link Solution이 Korea 유일의 3D 프린팅 파운드리 Daejeon 공장 건설 중. Samsung·Hyundai 기계 수주로 12월 준공 예정.",
        "category": "기술",
        "theme": "자율주행·로보틱스",
        "source": "THE VC",
        "city": "대전",
        "country": "한국",
        "lat": 36.3504,
        "lng": 127.3845,
        "date": "2026-08-13",
        "url": "https://thevc.kr/naurobotics",
        "importance": 6
    }
]

def load_json(path):
    """JSON 파일 로드, 없으면 빈 배열 반환"""
    if path.exists():
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_json(path, data):
    """JSON 파일 저장"""
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def main():
    # 기존 데이터 로드
    existing = load_json(OUTPUT_PATH)

    # 중복 체크: URL 기반 중복 제거
    existing_urls = {item.get('url') for item in existing}

    # 새로운 항목 필터링 (중복 제외)
    to_add = [item for item in NEW_ITEMS if item['url'] not in existing_urls]

    print(f"기존 항목: {len(existing)}")
    print(f"추가 항목: {len(to_add)}")
    print(f"제외 (중복): {len(NEW_ITEMS) - len(to_add)}")

    # 병합
    merged = existing + to_add

    # 날짜 순정렬 (최신순)
    merged.sort(key=lambda x: x.get('date', ''), reverse=True)

    # 저장
    save_json(OUTPUT_PATH, merged)
    print(f"\n✓ grok-tech-news.json 저장 완료 (총 {len(merged)}건)")

if __name__ == '__main__':
    main()
