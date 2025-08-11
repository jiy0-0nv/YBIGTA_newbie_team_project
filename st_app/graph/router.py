# st_app/graph/router.py
from __future__ import annotations
from typing import Optional, Literal, Tuple
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from pydantic import BaseModel

from st_app.graph.nodes.chat_node import run as chat_run
from st_app.graph.nodes.subject_info_node import run as subject_info_run
from st_app.graph.nodes.rag_review_node import run as review_rag_run
from st_app.utils.state import AppState
from st_app.rag.llm import get_llm


def _last_user(history: list[dict] | None) -> Optional[str]:
    if not history:
        return None
    for m in reversed(history):
        if m.get("role") == "user":
            return m.get("content", "")
    return None


# 구조화 스키마(참고용, with_structured_output은 사용 안 함)
class RouteSchema(BaseModel):
    route: Literal["chat", "subject_info", "review_rag", "end"]
    subject: Optional[str] = None  # 탑건 계열이면 'top_gun_maverick', 아니면 None


# ===== LLM 라우터 프롬프트 (간결) =====
ROUTER_PROMPT = ChatPromptTemplate.from_messages([
    ("system", "너는 영화 리뷰 앱의 라우터야. JSON 형식으로만 응답해."),
    ("human", "사용자 입력: {user_input}\n응답 형식: {{\"route\": \"chat|subject_info|review_rag|end\", \"subject\": \"top_gun_maverick\"|null}}")
])


def _infer_route(llm, text: str) -> Tuple[str, Optional[str]]:
    try:
        msgs = ROUTER_PROMPT.format_messages(user_input=text)
        raw = (llm.invoke(msgs).content or "").strip()
        # 코드펜스 제거
        if raw.startswith("```json"): raw = raw[7:]
        if raw.endswith("```"): raw = raw[:-3]
        import json
        obj = json.loads(raw.strip())
        route = str(obj.get("route", "chat")).lower().strip()
        subject = obj.get("subject")
        subj = "top_gun_maverick" if subject == "top_gun_maverick" else None
        # 주제 없이 세부 노드로 가는 응답은 chat로 보정
        if route not in {"chat","subject_info","review_rag","end"}:
            route = "chat"
        if subj is None and route in {"subject_info","review_rag"}:
            route = "chat"
        return route, subj
    except Exception:
        return "chat", None


def router(state: AppState) -> AppState:
    llm = get_llm(temperature=0)
    query = state.get("query") or _last_user(state.get("history")) or ""
    route, subj = _infer_route(llm, query)

    state["route"] = route
    state["subject"] = subj
    state["query"] = query
    state["conversation_context"] = (state.get("history", []) or [])[-5:]
    return state


def _branch_by_route(state: AppState) -> str:
    return {
        "subject_info": "subject_info",
        "review_rag": "review_rag",
        "end": "end",
    }.get(state.get("route", "chat"), "chat")


def build_graph():
    g = StateGraph(AppState)
    g.add_node("router", router)
    g.add_node("chat", chat_run)
    g.add_node("subject_info", subject_info_run)
    g.add_node("review_rag", review_rag_run)

    g.add_conditional_edges("router", _branch_by_route, {
        "chat": "chat",
        "subject_info": "subject_info",
        "review_rag": "review_rag",
        "end": END,
    })

    g.add_edge("chat", END)
    g.add_edge("subject_info", END)
    g.add_edge("review_rag", END)

    g.set_entry_point("router")
    return g.compile()
