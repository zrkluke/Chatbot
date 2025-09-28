'''
LLM predicts Retrieve given (x, y<t)
'''
from typing import Literal
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage
from legal_consult_agent.utils.state import LegalConsultState as State
from legal_consult_agent.utils.models import llm


class Response(BaseModel):
    Retrieve: Literal["Yes", "No"] = Field(..., description="To Determine whether to retrieve from dataset or not")


async def semantic_router(state: State):
    '''
    To determine whether user input needs to retrieve from dataset or not
    '''
    question = state["question"]
    messages = state["messages"]

    prompt = f"""
    You are a semantic router. You are given a question and chat history. You need to determine whether the question needs to be retrieved from the dataset or not.
    If user is asking legal consultation, check whether chat history has enough information to answer the question.
    1. If chat history has enough information, then set Retrieve to "No".
    2. If chat history has insufficient information, then you need to retrieve from the dataset and set Retrieve to "Yes".

    Chat History: {messages}
    
    User's Question: {question}
    """
    res: Response = await llm.with_structured_output(Response).ainvoke(prompt)

    return {"messages": [HumanMessage(content=question)], "Retrieve": res.Retrieve}
    
