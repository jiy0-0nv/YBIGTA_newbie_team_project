# streamlit_app.py
import streamlit as st
from st_app.graph.router import build_graph
from st_app.utils.state import AppState

st.set_page_config(page_title="영화 리뷰 RAG/Agent 챗봇", layout="wide")
st.title("영화 리뷰 RAG/Agent 챗봇")

# 세션 초기화
if "graph" not in st.session_state:
    st.session_state.graph = build_graph()
if "state" not in st.session_state:
    st.session_state.state: AppState = {"history": [], "route": "chat", "subject": None}
if "last_input" not in st.session_state:
    st.session_state.last_input = ""

def _append(history: list[dict], role: str, content: str) -> None:
    if content and not (history and history[-1].get("role") == role and history[-1].get("content") == content):
        history.append({"role": role, "content": content})

# 입력
user_input = st.chat_input("영화에 대해 무엇이든 물어보세요.")

if user_input and user_input != st.session_state.last_input:
    st.session_state.last_input = user_input

    s: AppState = st.session_state.state
    history = s.get("history", [])

    # 1) 사용자 메시지 기록
    _append(history, "user", user_input)

    # 2) 그래프 호출
    s_for_graph = dict(s)
    s_for_graph["history"] = history
    s_for_graph["query"] = user_input

    with st.spinner("처리 중..."):
        result: AppState = st.session_state.graph.invoke(s_for_graph)

    # 3) 결과 반영 (히스토리는 UI가 주도)
    answer = result.get("answer", "")
    if answer:
        _append(history, "assistant", answer)

    s["history"] = history
    s["route"] = result.get("route", s.get("route", "chat"))
    s["subject"] = result.get("subject", s.get("subject"))
    s["citations"] = result.get("citations", [])

    st.session_state.state = s
    st.rerun()

# 렌더
for msg in st.session_state.state.get("history", []):
    role = msg.get("role")
    content = msg.get("content", "")
    with st.chat_message("user" if role == "user" else "assistant"):
        st.write(content)

