'''
Retriever
if Retrieve == Yes then
Retrieve relevant text passages D using R given (x, yt-1)
'''
from pydantic import BaseModel, Field
from typing import Literal
from legal_consult_agent.utils.tools import criminal_retriever, money_debt_retriever, marriage_retriever
from legal_consult_agent.utils.state import LegalConsultState as State
from legal_consult_agent.utils.models import llm


class Response(BaseModel):
    LegalTopic: Literal["Criminal", "Marriage", "MoneyDebt"] = Field(..., description="The most relevant legal topic of the question")
    Query: str = Field(..., description="User's legal consultation query from the question and chat history")

async def retriever(state: State):
    '''
    To retrieve information from the vector store
    '''
    question = state["question"]
    messages = state["messages"]

    prompt = f"""
    You are a helpful assistant. You are given a question and chat history.
    Identify the most relevant legal topic from the question and chat history.
    Then, find out user's legal consultation query from the question and chat history
    
    Chat History: {messages}
    
    User's Question: {question}
    """ 
    res: Response = await llm.with_structured_output(Response).ainvoke(prompt)
    
    if res.LegalTopic == "Criminal":
        documents = criminal_retriever.invoke(res.Query)
    elif res.LegalTopic == "Marriage":
        documents = marriage_retriever.invoke(res.Query)
    elif res.LegalTopic == "MoneyDebt":
        documents = money_debt_retriever.invoke(res.Query)

    return {"documents": documents}
