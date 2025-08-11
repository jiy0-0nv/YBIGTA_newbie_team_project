from langchain_core.prompts import ChatPromptTemplate
from st_app.rag.llm import get_llm
from st_app.utils.state import AppState

def create_chat_prompt() -> ChatPromptTemplate:
    """의도 판단 및 응답 생성 프롬프트"""
    system_prompt = """당신은 영화 리뷰 앱의 도우미입니다.

사용자 질문을 분석하여 다음 중 하나로 분류하고 응답해주세요:

1. "rag_review": 리뷰 분석, 평가, 추천 요청인 경우
2. "subject_info": 작품 정보, 줄거리, 감독, 출연진 요청인 경우  
3. "end": 일반적인 대화, 인사, 감사 표현인 경우

응답 형식:
- 먼저 의도 분류를 한 줄로 출력 (예: "의도: rag_review")
- 그 다음에 실제 응답을 출력

예시:
의도: rag_review
탑건 매버릭의 리뷰를 분석해드리겠습니다. 검색된 리뷰 데이터를 바탕으로 객관적인 분석을 제공하겠습니다.
"""

    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{user_input}")
    ])

def run(state: AppState) -> AppState:
    """Chat Node 실행 - 의도 판단 및 응답 생성"""
    llm = get_llm()
    prompt = create_chat_prompt()
    
    # LLM 호출
    response = llm.invoke(prompt.format(user_input=state["query"]))
    response_text = response.content
    
    # 의도 추출
    if "의도: rag_review" in response_text:
        state["next_action"] = "rag_review"
        print(f"�� LLM이 의도 판단: rag_review")
    elif "의도: subject_info" in response_text:
        state["next_action"] = "subject_info"
        print(f"🎯 LLM이 의도 판단: subject_info")
    else:
        state["next_action"] = "end"
        print(f"�� LLM이 의도 판단: end")
    
    # 응답에서 의도 부분 제거
    answer = response_text.split("의도:")[1].strip() if "의도:" in response_text else response_text
    state["answer"] = answer
    
    return state