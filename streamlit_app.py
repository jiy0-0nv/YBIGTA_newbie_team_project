# st_app/main.py
import streamlit as st
from st_app.graph.router import create_workflow

# Streamlit UI
def main():
    st.title("영화 리뷰 RAG 시스템")
    
    # 사용자 입력
    query = st.text_input("질문을 입력하세요:")
    
    if st.button("질문하기"):
        if query:
            # 워크플로우 실행
            workflow = create_workflow()
            state = {"query": query}
            result = workflow.invoke(state)
            
            st.write("답변:", result["answer"])
            if result.get("citations"):
                st.write("참고 자료:", result["citations"])

if __name__ == "__main__":
    main()