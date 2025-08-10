from langchain_core.prompts import ChatPromptTemplate
from st_app.rag.llm import get_llm
from st_app.utils.state import AppState

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "너는 영화 리뷰 앱의 간결한 도우미야. 사실 확인이 필요한 질문엔 모른다고 말해."
     " 사용자가 작품 정보나 리뷰 분석을 원하면 한 문장으로 확인 질문을 해."),
    ("human", "{user_input}")
])

def run(state: AppState) -> AppState:
    llm = get_llm(temperature=0.5)  # solar-pro2
    msgs = prompt.format_messages(user_input=state["query"])
    out = llm.invoke(msgs)
    state["answer"] = out.content
    state["citations"] = []
    return state
