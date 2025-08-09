import os
from typing import Literal
from langchain_upstage import ChatUpstage
from langchain_core.language_models.chat_models import BaseChatModel

ModelName = Literal["solar-pro2"]

def get_llm(model: ModelName = "solar-pro2", temperature: float = 0.5) -> BaseChatModel:
    """
    Upstage ChatUpstage 래퍼.
    키는 환경변수 UPSTAGE_API_KEY 로 주입(.env 가능)
    """
    return ChatUpstage(model=model, temperature=temperature)
