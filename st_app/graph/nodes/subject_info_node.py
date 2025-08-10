import json, os
from langchain_core.prompts import ChatPromptTemplate
from st_app.rag.llm import get_llm
from st_app.utils.state import AppState

SUBJECTS_PATH = os.getenv("SUBJECTS_JSON", "st_app/db/subject_information/subjects.json")

tmpl = ChatPromptTemplate.from_messages([
    ("system",
     "아래 JSON 안의 정보로만 답해. 없으면 '정보 없음'이라고 답해."),
    ("system", "JSON:\n{json_blob}"),
    ("human", "질문: {q}")
])

def _load_subjects() -> dict:
    with open(SUBJECTS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def run(state: AppState) -> AppState:
    llm = get_llm(temperature=0.2)  # 사실 위주
    ctx = _load_subjects().get("top_gun_maverick", {})
    msgs = tmpl.format_messages(json_blob=json.dumps(ctx, ensure_ascii=False, indent=2), q=state["query"])
    out = llm.invoke(msgs)
    state["answer"] = out.content
    state["citations"] = []
    return state
