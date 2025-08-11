from langchain_core.prompts import ChatPromptTemplate
from st_app.rag.llm import get_llm
from st_app.utils.state import AppState
from st_app.rag.retriever import Retriever
from st_app.rag.prompt import build_rag_messages

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
    msgs = build_rag_messages(state["query"], docs)
    out = llm.invoke(msgs)
    state["answer"] = out.content
    state["citations"] = [{**d["meta"], "snippet": d["text"]} for d in docs]
    return state
