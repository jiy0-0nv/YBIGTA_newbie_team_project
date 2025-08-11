# 🚀 YBIGTA 2조

안녕하세요! YBIGTA 27기 교육세션 2조입니다.<br>

* <b>어예지</b> (응용통계학과 21)
* <b>정지윤</b> (컴퓨터과학과 22)
* <b>정진욱</b> (사회환경시스템공학 18)

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
