from langchain_core.prompts import ChatPromptTemplate
from st_app.rag.llm import get_llm
from st_app.utils.state import AppState

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "너는 영화 리뷰 앱의 간결한 도우미야. 앱에는 작품 정보 제공, 리뷰 분석의 기능이 있어."
     "이외의 기능이나, 사실 확인이 필요한 질문을 하면 모른다고 답해."),
    ("human", "{user_input}")
])

def run(state: AppState) -> AppState:
    llm = get_llm(temperature=0.5)  # solar-pro2
    msgs = prompt.format_messages(user_input=state["query"])
    out = llm.invoke(msgs)
    state["answer"] = out.content
    state["citations"] = []
    return state
