from dotenv import load_dotenv
import os
from langchain_openai import ChatOpenAI

load_dotenv()

def create_model() -> ChatOpenAI:
    '''
    Normal model
    '''
    model = os.getenv("OPENAI_MODEL")
    return  ChatOpenAI(model=model, temperature=0.1)

def create_reasoning_model() -> ChatOpenAI:
    '''
    Reasoning model
    '''
    model = os.getenv("OPENAI_REASONING_MODEL")
    return ChatOpenAI(model=model, temperature=1.0)

llm = create_model()
reasoning_model = create_reasoning_model()