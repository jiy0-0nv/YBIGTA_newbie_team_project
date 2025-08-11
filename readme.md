# 🚀 YBIGTA 2조

안녕하세요! YBIGTA 27기 교육세션 2조입니다.<br>

* <b>어예지</b> (응용통계학과 21)
* <b>정지윤</b> (컴퓨터과학과 22)
* <b>정진욱</b> (사회환경시스템공학 18)

## RAG AGENT 과제 명세서

### 프로젝트 목표

IMDB/Metacritic/Rotten Tomatoes 3개 소스의 \<탑건: 매버릭\> 리뷰를 기반으로 <br>
RAG Review / Subject Info / Chat 노드를 LangGraph 라우팅으로 연결한 Q\&A 챗봇 구현 및 Streamlit Cloud 데모 제공

### 담당자

어예지, 정지윤, 정진욱

### 산출물 목록

  * **프로젝트 코드**: [https://github.com/jiy0-0nv/YBIGTA\_newbie\_team\_project](https://github.com/jiy0-0nv/YBIGTA_newbie_team_project)

-----

### 데이터셋

  * **내용**: 리뷰 텍스트, 작성자, 작성 시각, 별점
  * **특징**: 다중 출처(사이트별 평점 스케일 상이), 리뷰 길이 편차 큼, 중복/유사 리뷰 존재 가능, 대부분 영문

-----

### 전체 파이프라인

#### 데이터 구축 단계

| 단계 | 설명 |
| :--- | :--- |
| Data Loader | IMDb, Metacritic, Rotten Tomatoes에서 리뷰 원천 수집 후 적재 |
| 스키마 표준화 | 평점을 0–5 스케일로 정규화, 컬럼명/타입 일괄 정리 |
| 결측치 처리 | 평점, 시간 표준화 |
| 이상치 처리 | 정규화된 score가 0–5 범위를 벗어나면 제거 |
| 텍스트 데이터 전처리 | 비정상 길이 리뷰 제거, HTML/이모지/공백 정규화 |
| 파생 변수 생성 | text\_length(문자/토큰 길이), days\_since\_release(개봉일 기준 작성일까지 일수) |
| 텍스트 벡터화(TF-IDF) | 전처리된 리뷰에 TF-IDF 적용 후 문서 단위 요약 지표 추가: tfidf\_mean, tfidf\_max, tfidf\_nnz |

#### 사용자 시나리오

| 단계 | 설명 |
| :--- | :--- |
| 질문 입력 | 앱에 접속한 사용자가 입력창에 질문 내용을 입력 |
| Router(LLM) 실행 | 사용자의 질문을 분석하여 의도를 파악 → chat / subject\_info / review\_rag 결정 |
| 분기 처리 | <b>Chat</b>: 즉시 답변 생성<br><b>Subject Info</b>: subjects.json 조회<br><b>RAG Review</b>: Embedding → Text Clarification → Retrieval → Summarize |
| Dash 응답 표시 | 근거/출처와 함께 답변 표시 |
| 후속 질문 입력 | 입력창에서 후속 질문 입력 |

-----

### 프로젝트 기능 명세서

#### 시스템 구축 파이프라인

| \# | 모듈 | 설명 | 입력 | 출력 | 비고 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 데이터 수집/정제 | IMDb/Metacritic/RottenTomatoes 리뷰 데이터 전처리 | .csv | .parquet | |
| 2 | 벡터화/인덱싱 | 장문 리뷰 청크 분할 → 문장 임베딩 → FAISS 인덱스 생성, 메타데이터 저장 | .parquet | .faiss, .jsonl | |
| 3 | RAG/에이전트 | LangGraph를 사용해 사용자 질문에 따라 `chat`, `subject_info`, `rag_review` 노드를 실행하고 답변을 생성함 | 사용자 질문, 대화 기록 | 최종 답변, 참고 자료 | LangGraph 라우팅 |
| 4 | Streamlit/배포 | Streamlit을 이용해 사용자에게 질문 입력창과 답변 표시 화면을 제공하고, 전체 파이프라인을 실행함 | 사용자 질문, 시스템 응답 | UI 화면 | Streamlit Cloud 데모 제공 |

-----

### 사용자 실시간 흐름

| \# | 모듈 | 설명 | 입력 | 출력 | 비고 |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | 질문 입력 | 사용자 질문을 입력·전송 | 자연어 질문 | state 초기화 | Streamlit 입력창 |
| 2 | Router | 의도 판단(chat/subject\_info/review\_rag) 및 subject 추출 | query, history | subject, answer | Upstage Document Parse API |
| 3 | Subject Info | 로컬 subjects.json만 근거로 작품 정보 답변 | query, subject | answer, citations | 전처리 통일 |
| 4 | RAG-Embedding | 임베딩 생성 | query | refined\_query or query, corpus\_ids | Upstage Embedding API 사용 |
| 5 | RAF-Retrieval | 벡터 유사도 기반 검색 | refined\_query or query (문서+메타) | Vector DB(FAISS) | |
| 6 | RAG Summarize | 스니펫 근거로 최종 답변 생성 | query, retrieved | answer, citations | |
| 7 | Chat 응답 | 일반 답변 | query | answer | |
| 8 | Dash | 응답 및 답변/근거 표시 | answer | 화면 출력 | Streamlit Cloud|

-----

### 대시보드 구성

| 섹션 | 구성 요소 | 예시 |
| :--- | :--- | :--- |
| ① 입력창 | 질문 입력창, 전송 버튼 | “탑건: 매버릭 대중 반응 요약해줘” |
| ② 답변창 | Chat 스타일 응답 본문, 제목(요약 타이틀) | “탑건: 매버릭 대중 반응 요약” + 3\~5문장 요약 |
| ③ 근거/참고자료 | 참고자료 보기 버튼, 참고자료 원문 | {'site': 'metacritic', 'author': 'arrivist', 'date': '2022-05-28T00:00:00Z', ...} |


## State Class 구현 방식

`State` 클래스는 노드 간 데이터 전달을 표준화하는 구조로, RAG 및 LangGraph 파이프라인 설계에서 핵심적인 역할을 합니다.

### 역할

- 노드 Input/Output을 일관된 key-value 형태로 관리
- 각 노드가 필요한 데이터만 선택적으로 읽거나 갱신 가능
- 전체 파이프라인에서 데이터의 흐름을 명확히 추적

### 장점

- **일관성**: 모든 노드가 동일 인터페이스로 접근
- **확장성**: 필드 추가 또는 변경 시에도 기존 노드 영향 최소화
- **유지보수성**: 데이터 흐름이 명확하기 때문에 디버깅이나 로깅 편리
- **LangGraph 친화성**: 노드 간 데이터 공유와 분기, 병렬 실행을 간단히 구현할 수 있도록 지원

### 노드별 사용

- Chat: `query`, `history`를 읽고 `answer`만 기록
- Subject Info: `query`를 읽고 로컬 `subjects.json`만 근거로 `answer` 기록
- RAG Review: `query`, `user_prefs`를 읽고 `retrieved`, `citations`, `answer` 기록


## Streamlit 배포
- 배포 링크: https://ybigtasession9teamproject-knjbnfuvs2gmw9k7bd9o3c.streamlit.app/

1. Chat 노드 작동사진
<img src="images/image 4.png">

2. Subject info 노드 작동사진
<img src="images/image 5.png">

3. RAG Review 노드 작동사진
<img src="images/image 6.png">
<br><br>

---

### LangGraph 기반 라우팅 로직 설명


이 워크플로우는 영화 리뷰 앱에서 사용자의 질문을 받아, LLM이 질문의 의도를 분석한 뒤 해당 의도에 맞는 노드로 연결하는 구조입니다.

<img src="images/image 7.png">
<br><br>

먼저 `START`에서 **`chat`** 노드로 이동하면, LLM이 입력을 분석하여 다음 세 가지 중 하나로 의도를 분류합니다.

1.  **`rag_review`**: 리뷰 분석, 평가, 추천 요청
2.  **`subject_info`**: 작품 정보, 줄거리, 감독, 출연진 요청
3.  **`end`**: 인사, 감사 표현 등 일반 대화

`chat` 노드는 분류 결과에 따라 해당 노드(`rag_review` 또는 `subject_info`)로 보냅니다.

* **`rag_review` 노드**: 검색된 리뷰 데이터를 분석해 객관적인 평가를 제공하고 `END`로 종료
* **`subject_info` 노드**: 작품 정보나 줄거리를 제공하고 `END`로 종료
* **`end` 의도**: 바로 `END`로 종료

후속 질문 발화 시 다시 `chat` 노드로 복귀하여 시작합니다.

---

- EC2 Deploy 관련 문제가 지속되어 추후 다시 구성할 예정입니다.
  
### Docker Hub 주소

[https://hub.docker.com/r/jinoogi/session8](https://hub.docker.com/r/jinoogi/session8)

---

### RDS 퍼블릭 액세스 비활성화 및 VPC를 이용한 보안 설정
<img src="images/image 1.png">
<img src="images/image 2.png">
Amazon RDS (Relational Database Service)를 사용할 때, 데이터베이스의 보안을 강화하기 위해 퍼블릭 액세스를 허용하지 않는 것이 중요합니다. 대신, VPC(Virtual Private Cloud) 내에서 EC2 인스턴스와 같은 허가된 리소스만 데이터베이스에 접근할 수 있도록 보안 그룹을 설정하는 것이 안전한 방법입니다.

다음은 이 프로젝트에서 적용한 보안 설정 과정입니다:

1.  **RDS 인스턴스 보안 그룹 설정**:
    * RDS 데이터베이스의 보안 그룹을 생성하고, 외부에서의 직접적인 접근을 막기 위해 모든 인바운드 규칙을 기본적으로 차단합니다.
2.  **인바운드 규칙 추가**:
    * EC2 인스턴스가 RDS 데이터베이스에 접근할 수 있도록 인바운드 규칙을 추가합니다.
    * 규칙 유형으로 `MYSQL/Aurora` (TCP 포트 3306)를 선택합니다.
    * 소스(Source)에는 특정 IP 주소 대신, 애플리케이션이 실행되고 있는 **EC2 인스턴스의 보안 그룹 ID**를 지정합니다.
    * 이 설정을 통해 지정된 보안 그룹에 속한 EC2 인스턴스만이 VPC 내부 네트워크를 통해 RDS 데이터베이스에 접근할 수 있게 됩니다.

<br>

*설정 화면 예시*
*EC2 보안 그룹 인바운드 규칙 편집 화면. MYSQL/Aurora(3306) 포트에 대해 특정 보안 그룹(sg-...)의 접근을 허용하고 있습니다.*
![EC2 보안 그룹 인바운드 규칙 편집 화면](https://storage.googleapis.com/generativeai-downloads/images/image%201.png)

---

### 프로젝트를 통해 배운 점 및 오류 해결 경험
<img src="images/image 3.png">

**1. Docker를 통한 배포 자동화의 편리성**

과거에는 FileZilla와 같은 FTP 클라이언트를 사용하여 개발한 서비스 파일들을 직접 EC2 인스턴스 서버에 수동으로 업로드하는 방식을 사용했습니다. 이 방법은 과정이 번거롭고 배포 실수가 발생할 가능성이 높았습니다.

하지만 이번 프로젝트에서는 Docker를 도입하여 배포 과정을 자동화했습니다. Docker 이미지를 빌드하여 Docker Hub에 올리고, EC2 인스턴스에서는 간단한 `docker run` 명령어만으로 애플리케이션을 실행할 수 있었습니다. 이를 통해 배포 과정이 매우 간편해졌고, 일관된 환경에서 서비스를 실행할 수 있어 안정성이 크게 향상되었습니다.

**2. CPU 아키텍처 불일치로 인한 실행 오류 해결**

프로젝트를 진행하며 중요한 기술적 문제를 마주하고 해결하는 경험을 했습니다. 로컬 개발 환경인 M1 MacBook (ARM64 아키텍처)에서 Docker 이미지를 빌드한 후, 해당 이미지를 AWS EC2의 기본 인스턴스(x86, AMD64 아키텍처)에서 실행하려고 시도했습니다.

컨테이너 실행 시 다음과 같은 경고 메시지가 나타났고, 컨테이너는 정상적으로 작동하지 않았습니다.

```bash
ubuntu@ip-172-31-41-126:~$ docker run -d -p 8000:8000 --env-file ./.env --name my-app-container jinoogi/session8

WARNING: The requested image's platform (linux/arm64) does not match the detected host platform (linux/amd64/v3) and no specific platform was requested
58e8a28e0d294cfa7c8b482565fba42d0792dc79b603e2c891b8a8e63e1295cf

ubuntu@ip-172-31-41-126:~$ docker logs 58e8a28e0d29
exec /usr/local/bin/uvicorn: exec format error


```

로그에서 보이는 exec format error는 빌드된 이미지의 CPU 아키텍처(ARM64)와 컨테이너를 실행하려는 호스트 서버의 아키텍처(AMD64)가 호환되지 않아 발생한 문제였습니다.

이 문제를 해결하기 위해 두 가지 방법이 있음을 알게 되었습니다.

--platform linux/amd64 옵션을 사용하여 빌드 시 타겟 아키텍처를 명시하는 방법.

실행 환경인 EC2 인스턴스를 ARM 아키텍처 기반(AWS Graviton) 인스턴스로 변경하는 방법.

저는 후자의 방법을 선택하여 ARM 아키텍처 기반의 새 EC2 인스턴스를 생성하여 문제를 해결했습니다. 이 경험을 통해 Docker 이미지를 빌드하고 배포할 때, 개발 환경과 실행 환경의 CPU 아키텍처 호환성을 반드시 고려해야 한다는 점의 중요성을 깨달을 수 있었습니다.
