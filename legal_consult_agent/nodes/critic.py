'''
Critique
If Retrieve == Yes then
1. LLM predicts IsSupport and IsUseful given x, yt, d for each d in Documents

else if Retrieve == No then
2. LLM predicts IsUseful given x, yt
'''
from pydantic import BaseModel, Field
from typing import Literal
from langchain_core.messages import AIMessage
from legal_consult_agent.utils.models import llm
from legal_consult_agent.utils.state import LegalConsultState as State


class Response(BaseModel):
    IsSupport: Literal["Fully", "Partial", "No"] = Field(
        ..., description="To Determine whether the text passage is fully supported by the question"
    )
    IsUseful: Literal["5", "4", "3", "2", "1"] = Field(
        ..., description="To Determine whether the text passage is useful for the question"
    )


async def critic(state: State):
    question = state["question"]
    consultation_answers = state["ConsultationAnswers"]
    # These accumulators stay as lists to align with LegalConsultState typing.
    result_isSupport: list[str] = []
    result_isUseful: list[str] = []

    if state["Retrieve"] == "Yes":
        documents = state["documents"]
        for i in range(len(documents)):
            prompt = f"""
            You are a helpful critic. You are given a question, a text passage and a consultation answer.
            Determine whether the consultation answer is supported by the document.
            - "Fully" means the consultation answer is fully supported by the document.
            - "Partial" means the consultation answer is partially supported by the document.
            - "No" means the consultation answer is not supported by the document.

            Also, determine whether the consultation answer is an useful response to the question.
            - "5" means the consultation answer is very useful for the question.
            - "4" means the consultation answer is useful for the question.
            - "3" means the consultation answer is somewhat useful for the question.
            - "2" means the consultation answer is not very useful for the question.
            - "1" means the consultation answer is not useful for the question.

            User's Question: {question}
            Text Passage: {documents[i].page_content}
            Consultation Answer: {consultation_answers[i]}
            """
            res: Response = await llm.with_structured_output(Response).ainvoke(prompt)
            result_isSupport.append(res.IsSupport)
            result_isUseful.append(res.IsUseful)

        # Return lists to align with LegalConsultState typing.
        return {"IsSupport": result_isSupport, "IsUseful": result_isUseful}
    else:
        for yt in consultation_answers:
            prompt = f"""
            You are a helpful assistant. You are given a question and a consultation answer.
            Determine whether the consultation answer is an useful response to the question.
            - "5" means the consultation answer is very useful for the question.
            - "4" means the consultation answer is useful for the question.
            - "3" means the consultation answer is somewhat useful for the question.
            - "2" means the consultation answer is not very useful for the question.
            - "1" means the consultation answer is not useful for the question.

            User's Question: {question}
            Consultation Answer: {yt}
            """
            res: Response = await llm.with_structured_output(Response).ainvoke(prompt)
            result_isUseful.append(res.IsUseful)
        # 只有一個 consultation answer，直接返回
        # IsSupport is omitted in this branch because no documents were retrieved to critique.
        return {
            "IsUseful": result_isUseful,
            "messages": [AIMessage(content=consultation_answers[0])],
        }

