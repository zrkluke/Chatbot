from langgraph.graph import MessagesState
from typing import Literal
from langchain_core.documents import Document

class LegalConsultState(MessagesState):
    question: str
    documents: list[Document]
    Retrieve: Literal["Yes", "No"]
    IsRelevant: list[Literal["Yes", "No"]]
    IsSupport: Literal["Fully", "Partial", "No"]
    IsUseful: Literal["5", "4", "3", "2", "1"]
    ConsultationAnswers: list[str]  # yt