# 🚀 YBIGTA 2조

안녕하세요! YBIGTA 27기 교육세션 2조입니다.<br>
영화 <탑건: 매버릭(2022)>의 리뷰 데이터를 기반으로 한 웹 크롤링부터 전처리, 분석, 시각화와 간단한 웹사이트 구현을 진행하고 있습니다.

## 팀원 소개

* <b>어예지</b> (응용통계학과 21) : BE, IMDB 리뷰 데이터 수집
* <b>정지윤</b> (컴퓨터과학과 22) : 팀장, BE, 로튼토마토 리뷰 데이터 수집
* <b>정진욱</b> (사회환경시스템공학 18) : FE, 메타크리틱 리뷰 데이터 수집, 비교분석

## 메인 브랜치 보호 정책

* `main` 브랜치는 직접 push 금지
* Pull Request(PR) 후 Review 1명 이상 승인 시 병합 가능

    <img src="github\branch_protection.png">
    <img src="github\push_rejected.png">
    <img src="github\review_and_merged.png" width="500">

<br>

# ⚡ 코드 실행 방법

1. 저장소 클론

```
git clone https://github.com/jiy0-0nv/YBIGTA_newbie_team_project.git
cd YBIGTA_newbie_team_project
```

2. (optional) 가상환경 활성화

```
python -m venv venv

venv\Scripts\activate # Windows
source venv/Scripts/activate # Macs
```

3. 의존성 설치

```
pip install -r requirements.txt
```

## Web 코드 실행 방법

개발 서버 실행

```bash
uvicorn app.main:app --reload
```

## 크롤링 코드 실행 방법

크롤링 스크립트 실행

```bash
python -m review_analysis.crawling.main -o database --all 
```

## FE 코드 실행 방법

FE 스크립트 실행

```bash
# 추가해주세요
```

<br>

# 📊 EDA

## Metacritic
(추가해주세요)

## Rotten Tomatoes
(추가해주세요)

## IMDB
(추가해주세요)

<br>

# 🔧 Postprocessing / Feature Engineering

## Metacritic
(추가해주세요)

## Rotten Tomatoes
(추가해주세요)

## IMDB
(추가해주세요)

<br>

# 🔎 비교 분석

## 텍스트 비교 분석
(추가해주세요)

## 시계열 비교 분석
(추가해주세요)