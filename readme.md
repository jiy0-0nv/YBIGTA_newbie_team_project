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
python -m review_analysis.preprocessing.main -a
```

<br>

# 📊 EDA

## Metacritic
* Review Text Length Distribution

    <img src="review_analysis\plots\metacritic_review_text_length_distribution.png">

    대부분은 200자 부근에 몰려있음.

* Distribution of Ratings (0~5)

    <img src="review_analysis\plots\metacritic_distribution_of_rating.png">
    대부분 높은 점수에 몰려있고, 중간이나 낮은 점수보다 오히려 1점같은 극단값에 더많이 분포하는 형태를 보였다.

* Review accumulation

    <img src="review_analysis\plots\metacritic_days_after_release_hist.png">
    누적 리뷰 수는 초기에 대부분의 리뷰가 작성되고 시간이 지날수록 로그함수처럼 줄어든다.

## Rotten Tomatoes
* Review Text Length Distribution

    <img src="review_analysis\plots\rottentomatoes_review_text_length_distribution.png">

    대부분은 0~500자 사이의 짧은 리뷰이나 드물게 5000자 이상의 매우 긴 리뷰가 존재했다.

* Distribution of Ratings (0~5)

    <img src="review_analysis\plots\rottentomatoes_distribution_of_rating.png">
    5.0이 매우 큰 비율을 보였다. 4.0 이상이 대부분이며 0.5~3.5 데이터는 비교적 고르게 분포해 있다.

* Monthly Review Count

    <img src="review_analysis\plots\rottentomatoes_monthly_review_count.png">
    월별 리뷰 수는 최근 들어 눈에 띄는 향상폭을 보인다.

## IMDB

* Review Text Length Distribution

    <img src="review_analysis/plots/imdb_text_length_distribution_eng.png">

    리뷰 길이는 100~1000자 사이가 가장 많으며, 일부는 3000자 가까이 되는 긴 리뷰도 존재했다.  
    너무 긴 리뷰는 이상치로 간주해 제거하였다.

* Distribution of Ratings (0~10)

    <img src="review_analysis/plots/imdb_rating_distribution_eng.png">

    10점 만점 기준으로 8~10점 사이의 고득점 리뷰가 가장 많았으며,  
    1~7점 사이도 비교적 고르게 분포되어 있다.

* Days Since Release — Histogram

    <img src="review_analysis/plots/imdb_days_after_release_hist.png">

    개봉 직후 며칠간 리뷰 수가 급증하고 이후 점점 줄어드는 형태를 보인다.

* Days Since Release — Boxplot

    <img src="review_analysis/plots/imdb_days_after_release_boxplot.png">

    박스플롯에서도 대다수 리뷰가 개봉 후 0~100일 사이에 집중된 것을 확인할 수 있다.


<br>

# 🔧 Postprocessing / Feature Engineering

## Metacritic
* **결측치**:
    - `score`, `date`, `content` 결측 시 행 제거
* **이상치**:
    - 별점 범위 아닌 경우 제거
* **텍스트 데이터 전처리**:
    - 텍스트에서 이모지 제거
* **파생 변수**:
    - `hatescore`: 3점이하의 점수를 준 사람들이 쓴 리뷰길이의 루트값
* **텍스트 벡터화**:
    - TF‑IDF 

## Rotten Tomatoes
* **결측치**:
    - `score`, `date`, `content` 결측 시 행 제거
    - `author` 결측 시 `unknown` 대체
* **이상치**:
    - 별점 범위 아닌 경우 제거
* **텍스트 데이터 전처리**:
    - 비정상적으로 길거나 짧은 리뷰 제거 (`text_length < 10` 또는 `> 1000`)
* **파생 변수**:
    - `text_length`: 리뷰 텍스트 길이
    - `days_since_release`: 영화 개봉일 대비 작성일 차이
* **텍스트 벡터화**:
    - TF‑IDF 요약 지표 추가 (`tfidf_mean`, `tfidf_max`, `tfidf_nnz`)

## IMDB
* **결측치**:
    - `score`, `date`, `content` 결측 시 행 제거
* **이상치**:
    - `text_length > 3000`인 경우 제거
* **텍스트 데이터 전처리**:
    - `text_length`: 리뷰 텍스트 길이 계산 후 3000자 이하만 유지 (이상치 제거)
* **파생 변수**:
    - `text_length`: 리뷰 텍스트 길이
    - `days_since_release`: 영화 개봉일(2022-05-27) 기준 작성일 차이
* **텍스트 벡터화**:
    - TF‑IDF 요약 지표 추가 (`tfidf_mean`, `tfidf_max`, `tfidf_nnz`)

<br>

# 🔎 비교 분석

## 텍스트 비교 분석
<img src="review_analysis/plots/compare_analysis_text.png">

## 시계열 비교 분석
<img src="review_analysis/plots/compare_analysis_serial.png">
