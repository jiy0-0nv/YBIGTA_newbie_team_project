from langgraph.graph import StateGraph, START, END
from st_app.utils.state import AppState
from st_app.graph.nodes.chat_node import run as chat_run
from st_app.graph.nodes.rag_review_node import run as rag_run
from st_app.graph.nodes.subject_info_node import run as subject_run

def create_workflow():
    """LangGraph 기반 LLM 의도 판단 라우팅 워크플로우"""
    workflow = StateGraph(AppState)
    
    # 노드 추가
    workflow.add_node("chat", chat_run)
    workflow.add_node("rag_review", rag_run)
    workflow.add_node("subject_info", subject_run)
    
    # 시작점: Chat Node에서 의도 판단
    workflow.add_edge(START, "chat")
    
    # Chat Node에서 LLM이 의도를 판단하여 조건부 라우팅
    workflow.add_conditional_edges(
        "chat",
        lambda state: (print(f" 선택된 노드: {state.get('next_action', 'end')}"), state.get("next_action", "end"))[1], 
        # lambda state: state.get("next_action", "end"),  # LLM이 결정한 다음 액션
        {
            "rag_review": "rag_review",
            "subject_info": "subject_info", 
            "end": END
        }
    )
    
    # 각 노드 처리 후 Chat Node로 복귀
    workflow.add_edge("rag_review", END)
    workflow.add_edge("subject_info", END)
    
    return workflow.compile()