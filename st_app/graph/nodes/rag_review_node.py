from langchain_core.prompts import ChatPromptTemplate
from st_app.rag.llm import get_llm
from st_app.utils.state import AppState, Doc
from st_app.rag.retriever import Retriever

prompt = ChatPromptTemplate.from_messages([
    ("system",
     "다음 리뷰 스니펫만 근거로 답하라. 장단점을 요약하고, 모순/편향이 보이면 간단히 경고해. "
     "각 스니펫은 (site|author|date|rating)로 인용해."),
    ("system", "SNIPPETS:\n{snippets}"),
    ("human", "질문: {q}")
])

def _fmt_snippets(docs: list[Doc]) -> str:
    return "\n".join(
        f"- {d['text']}  ({d['meta']['site']}|{d['meta']['author']}|{d['meta']['date']}|{d['meta']['rating']})"
        for d in docs
    )

def run(state: AppState) -> AppState:
    llm = get_llm(temperature=0.2)
    prefs = state.get("user_prefs", {})
    retriever = Retriever()
    docs = retriever.retrieve(
        state["query"],
        k=6,
        filters={"sites": prefs.get("sites"), "min_rating": prefs.get("min_rating")}
    )
    state["retrieved"] = docs
    msgs = prompt.format_messages(snippets=_fmt_snippets(docs), q=state["query"])
    out = llm.invoke(msgs)
    state["answer"] = out.content
    state["citations"] = [{**d["meta"], "snippet": d["text"]} for d in docs]
    return state
