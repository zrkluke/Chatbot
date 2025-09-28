'''
Generator LM
if Retrieve == Yes then
1. LLM predicts IsRelevant given x, d and yt given x, d, y<t for each d in Dataset

else if Retrieve == No then
2. LLM predicts yt given x
'''

from utils.state import LegalConsultState as State
from utils.models import llm, reasoning_model
from pydantic import BaseModel, Field
from typing import Literal
from langchain_core.messages import AIMessage

class Response(BaseModel):
    IsRelevant: Literal["Yes", "No"] = Field(..., description="To Determine whether the text passage provides useful information to solve the question")

async def generator(state: State):
    messages = state["messages"]
    question = state["question"]
    result_isRelevant = []
    result_yt = []

    if state["Retrieve"] == "Yes":
        # Predict x, d is relevant for each d in D
        for d in state["documents"]:
            judge_relevence_prompt = f"""
            You are a helpful assistant. You are given a question and a text passage.
            Determine whether the text passage provides useful information to solve the question.

            User's Question: {question}
            Text Passage: {d.page_content}
            """
            res: Response = await llm.with_structured_output(Response).ainvoke(judge_relevence_prompt)
            result_isRelevant.append(res.IsRelevant)

            # Predict yt given x, d and y<t for each d in D
            predict_yt_prompt = f"""
            You are a legal consultant. You are very knowledgeable in the marriage, law, criminal law, and money debt law.
            You are given a question, a text passage and a chat history.
            Think Deeply and Generate the answer to the question based on the text passage and chat history.
            
            User's Question: {question}
            Text Passage: {d.page_content}
            Chat History: {messages}
            Your Answer:
            """
            res: AIMessage = await reasoning_model.ainvoke(predict_yt_prompt)
            result_yt.append(res.content)
        
        return {"IsRelevant": result_isRelevant, "ConsultationAnswers": result_yt}
    else:
        # Predict yt given x
        prompt = f"""
        You are a helpful assistant. You are given a question.
        Generate the answer to the question.

        User's Question: {question}
        """
        res: AIMessage = await reasoning_model.ainvoke(prompt)
        result_yt.append(res.content)

        return {"ConsultationAnswers": result_yt}