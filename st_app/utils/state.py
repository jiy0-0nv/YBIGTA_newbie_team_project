from typing import TypedDict, Literal, List, Dict, Any, Optional

Intent = Literal["general_chat", "subject_info", "review_rag"]

class Message(TypedDict):
    role: Literal["user", "assistant"]
    content: str

class Doc(TypedDict):
    text: str
    meta: Dict[str, Any]  # {site, author, date, rating, url}

class AppState(TypedDict, total=False):
    query: str
    history: List[Message]
    intent: Optional[Intent]
    answer: str
    citations: List[Dict[str, Any]]   # [{site, author, date, rating, url, snippet}]
    retrieved: List[Doc]
    user_prefs: Dict[str, Any]        # {spoiler_safe, min_rating, sites}
