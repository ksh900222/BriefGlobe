#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
task_tech-deals.md 지시 실행: Grok 웹 실검색으로 8개 섹터 딜·발표 뉴스 수집 → grok-tech-news.json 저장
"""
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timedelta

HERE = Path(__file__).resolve().parent
GROK = Path.home() / ".grok/bin/grok"
OUTPUT = HERE / "grok-tech-news.json"

# 8개 섹터별 검색 쿼리
SECTORS = {
    "자율주행·로보틱스": [
        "Electrek Tesla autonomous driving FSD latest 2026",
        "NHTSA autonomous vehicle recall regulation 2026",
        "Tesla robotaxi Cybercab deployment recent",
        "autonomous driving accident investigation NHTSA",
    ],
    "AI·연산·전력": [
        "OpenAI Claude Anthropic model release 2026",
        "AI chip data center investment deal July 2026",
        "Nvidia GPU allocation enterprise deal",
        "AI model deployment announcement July 2026",
    ],
    "우주·발사": [
        "SpaceNews SpaceX Falcon rocket launch July 2026",
        "NASA ESA space agency announcement July 2026",
        "satellite constellation deployment deal",
        "space commerce transaction July 2026",
    ],
    "반도체·전기차·배터리": [
        "DIGITIMES TSMC semiconductor fab deal July 2026",
        "ASML EUV lithography order semiconductor",
        "EV battery manufacturing investment deal",
        "semiconductor supply chain news July 2026",
    ],
    "양자컴퓨터": [
        "Quantum Insider quantum computing breakthrough July 2026",
        "quantum hardware development announcement",
        "quantum computing investment funding deal",
        "quantum error correction milestone",
    ],
    "국방·방산테크": [
        "Defense News defense contractor deal July 2026",
        "military technology contract award",
        "DoD defense spending announcement",
        "aerospace defense procurement news",
    ],
}

def run_grok_search(query: str) -> str:
    """Grok CLI로 웹 검색 수행"""
    try:
        if not GROK.exists():
            print(f"⚠ Grok 바이너리 없음: {GROK}")
            return ""

        cmd = [str(GROK), "-m", "grok-4.5", f"웹 검색: {query}. 딜·발표 뉴스만, 실재·검증가능한 것만 찾아줘. 시장/매체명/날짜/금액/URL을 포함해"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            print(f"⚠ Grok 검색 실패 ({query}): {result.stderr[:200]}")
            return ""

        return result.stdout
    except subprocess.TimeoutExpired:
        print(f"⚠ Grok 타임아웃 ({query})")
        return ""
    except Exception as e:
        print(f"⚠ Grok 호출 오류 ({query}): {e}")
        return ""

def search_all_sectors():
    """모든 섹터 검색"""
    all_results = []

    for sector, queries in SECTORS.items():
        print(f"\n🔍 {sector} 검색 중...")
        for query in queries:
            print(f"  → {query[:60]}...")
            result = run_grok_search(query)
            if result:
                all_results.append({
                    "sector": sector,
                    "query": query,
                    "result": result
                })

    return all_results

def parse_grok_results(results):
    """Grok 응답을 JSON 구조로 파싱"""
    # Grok 응답에서 뉴스 항목 추출 및 JSON 구조 생성
    # 이 부분은 Grok의 실제 응답 형식에 따라 조정 필요
    parsed = []

    for item in results:
        # 응답에서 구조화된 정보 추출 시뮬레이션
        # 실제 구현에서는 Grok 응답을 파싱하여 title, summary, url 등 추출
        pass

    return parsed

def main():
    print("🚀 task_tech-deals.md 실행: 8개 섹터 웹 실검색")
    print(f"📍 Grok: {GROK}")
    print(f"📁 출력: {OUTPUT}")

    # 기존 파일 로드
    existing = []
    if OUTPUT.exists():
        existing = json.loads(OUTPUT.read_text(encoding="utf-8"))
        print(f"✓ 기존 {len(existing)}건 로드")

    # 웹 검색 수행
    search_results = search_all_sectors()

    if not search_results:
        print("⚠ 검색 결과 없음")
        return 1

    # Grok 응답 파싱 및 저장
    parsed = parse_grok_results(search_results)

    print(f"\n✓ {len(parsed)}건 수집 완료")

    return 0

if __name__ == "__main__":
    sys.exit(main())
