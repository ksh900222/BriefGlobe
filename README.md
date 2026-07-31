<p align="center">
  <img src="favicon-master.png" alt="BriefGlobe" width="96" height="96">
</p>

<h1 align="center">BriefGlobe</h1>

<p align="center">세계 <b>뉴스 · 지정학 · 시장</b>을 하나의 인터랙티브 지구본에서 보는 웹앱</p>

<p align="center">
  🌍 <a href="https://world-info.pages.dev">world-info.pages.dev</a>
</p>

---

## 소개

BriefGlobe는 전 세계에서 일어나는 일을 **지도 위에서 한눈에** 읽기 위한 개인 프로젝트입니다. 세 가지 모드를 제공합니다.

- **뉴스** — 실시간 세계 뉴스와 속보를 위치 기반으로 지구본에 표시
- **지정학** — 군사·핵·반도체·해운·에너지 등 전략 인프라와 도달권 오버레이
- **시장** — 주요국 지수·주식·환율·금리·원자재·암호화폐 대시보드와 거시 지표

MapLibre GL 기반 3D 지구본 위에 기상(바람·기온·구름·태풍) 레이어까지 얹습니다.

## 기술 개요

- **프런트엔드** — 단일 `index.html`(인라인 JS), MapLibre GL(지구본) + Leaflet(평면 오버레이), Chart.js
- **데이터 수집** — Python 스크립트(`fetch_*.py`)가 각 소스에서 주기적으로 수집·가공
- **호스팅** — Cloudflare Pages(정적) + Pages Functions(엣지 API 프록시)
- **자동화** — 로컬 스케줄러(launchd)가 수집 → 배포 파이프라인을 주기 실행

## ⚠️ 데이터 파일에 대하여

이 저장소에는 **코드만 포함되며, 수집된 데이터 값 파일은 포함하지 않습니다.**

시세·뉴스·시계열 등의 데이터는 외부 소스에서 받아온 것으로, 저장소에 담아 재배포하지 않습니다(각 소스의 이용약관 존중, 그리고 어차피 시시각각 바뀌어 낡기 때문). 데이터 파일은 수집 스크립트를 실행하면 로컬에 생성됩니다.

```bash
# 예: 시장 시세 수집 → market-data.js 생성
python3 fetch_markets.py

# 뉴스 · 거시 · 기상 등도 각 fetch_*.py 로 생성
```

즉, 클론 직후에는 지정학 오버레이(저장소에 포함)는 바로 보이지만, 뉴스·시세 등은 수집 스크립트를 돌려야 채워집니다.

## 로컬에서 보기

```bash
# 의존성(지도 계산용 turf 등)
npm install

# 로컬 미리보기 서버
python3 serve.py
# → http://localhost:8001
```

## 데이터 소스 및 고지

이 프로젝트는 여러 공개 소스를 **개인 학습·비상업 목적**으로 활용합니다.

| 분야 | 소스 |
|---|---|
| 시세(시장) | Yahoo Finance 비공식 API, 한국투자증권(KIS) OpenAPI *(시세 조회 전용, 거래 기능 없음)* |
| 거시·금리 | FRED(미국 세인트루이스 연준), 한국은행 ECOS |
| 뉴스 | GDELT Project, 각 언론사 RSS(제목·요약·원문 링크) |
| 지도·지형 | MapLibre · OpenFreeMap · OpenStreetMap · Esri(위성) |
| 기상 | NOAA(GFS) · ECMWF · DWD(ICON) · Open-Meteo |
| 대기질 | CAMS / Copernicus Atmosphere Monitoring Service |

- 시장 데이터에는 지연이 있으며(장중 20분 이상 등), **투자 판단의 근거가 아닙니다.**
- 각 소스의 데이터 권리는 해당 제공자에게 있습니다. 이용 시 각 소스의 약관을 확인하세요.
- 지정학 오버레이 데이터는 공개 자료를 바탕으로 직접 정리·검증한 것으로, 오류가 있을 수 있습니다.

## 후원

이 프로젝트가 마음에 드신다면 [GitHub Sponsors](https://github.com/sponsors/ksh900222)로 후원하실 수 있습니다.

후원은 **완전히 자발적**입니다. 후원 여부와 무관하게 **모든 기능은 누구에게나 동일하게 제공**되며, 후원자에게 어떤 특권·보상도 없고, 후원자 명단을 공개하거나 활용하지 않습니다. 순수하게 프로젝트의 지속을 응원하는 마음이면 충분합니다.

## 라이선스

코드: [MIT](LICENSE) — 자유롭게 사용·수정·재배포·상업적 이용까지 허용됩니다(저작권 표시만 유지).
데이터: 위 「데이터 소스 및 고지」의 각 제공자 약관을 따릅니다.
