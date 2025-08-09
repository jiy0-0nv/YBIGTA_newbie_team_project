import argparse
import json
from dotenv import load_dotenv

from st_app.utils.state import AppState
from st_app.graph.nodes import chat_node, subject_info_node, rag_review_node

def run_chat(q: str):
    state: AppState = {"query": q, "history": [], "user_prefs": {}}
    out = chat_node.run(state)
    print("\n[Chat Node]")
    print(out["answer"])

def run_subject(q: str):
    state: AppState = {"query": q, "history": [], "user_prefs": {}}
    out = subject_info_node.run(state)
    print("\n[Subject Info Node]")
    print(out["answer"])

def run_rag(q: str, sites=None, min_rating=0.0):
    prefs = {"sites": sites, "min_rating": min_rating}
    state: AppState = {"query": q, "history": [], "user_prefs": prefs}
    out = rag_review_node.run(state)
    print("\n[RAG Review Node]")
    print(out["answer"])
    print("\n[Citations]")
    print(json.dumps(out.get("citations", []), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    load_dotenv()
    p = argparse.ArgumentParser()
    p.add_argument("--node", choices=["chat", "subject", "rag"], required=True)
    p.add_argument("--q", required=True, help="질문")
    p.add_argument("--sites", nargs="*", help="사이트 필터 예: imdb rottentomatoes metacritic")
    p.add_argument("--min_rating", type=float, default=0.0)
    args = p.parse_args()

    if args.node == "chat":
        run_chat(args.q)
    elif args.node == "subject":
        run_subject(args.q)
    else:
        run_rag(args.q, sites=args.sites, min_rating=args.min_rating)
