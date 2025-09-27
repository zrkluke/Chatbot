from langgraph.graph import MessagesState
from typing import Literal

class LegalConsultState(MessagesState):
    question: str
    documents: list[str]
    Retrieve: Literal["Yes", "No"]
    IsRelevant: Literal["Yes", "No"]
    IsSupport: Literal["Fully", "Partial", "No"]
    IsUseful: Literal["5", "4", "3", "2", "1"]