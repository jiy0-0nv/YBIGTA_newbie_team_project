from typing import List, Dict
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

SYSTEM_RAG = (
    "주어진 리뷰 스니펫만 근거로 답해. 장단점을 요약하고, 모순/편향이 보이면 경고해. "
    "각 스니펫을 (site|author|date|rating)로 인용해. 추측 금지."
)

def format_snippets(docs: List[Dict]) -> str:
    # docs[i] = {"text": "...", "meta": {...}}
    lines = []
    for d in docs:
        m = d["meta"]
        lines.append(f"- {d['text']}  ({m['site']}|{m['author']}|{m['date']}|{m['rating']})")
    return "\n".join(lines)

def build_rag_messages(query: str, docs: List[Dict]):
    tmpl = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_RAG),
        ("system", "SNIPPETS:\n{snippets}"),
        ("human", "질문: {q}")
    ])
    return tmpl.format_messages(snippets=format_snippets(docs), q=query)
