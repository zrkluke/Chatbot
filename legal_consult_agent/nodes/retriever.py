'''
Retriever
if Retrieve == Yes then
Retrieve relevant text passages D using R given (x, yt-1)
'''
from utils.tools import criminal_retriever_tool, money_debt_retriever_tool, marriage_retriever_tool
from utils.state import LegalConsultState as State
from utils.models import llm
from pydantic import BaseModel, Field
from typing import Literal

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
        documents = await criminal_retriever_tool.ainvoke(res.Query)
    elif res.LegalTopic == "Marriage":
        documents = await marriage_retriever_tool.ainvoke(res.Query)
    elif res.LegalTopic == "MoneyDebt":
        documents = await money_debt_retriever_tool.ainvoke(res.Query)

    return {"documents": documents}
