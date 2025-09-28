'''
ChromaDB Retrieval Tool
'''

from langchain_chroma import Chroma
from .embeddings import embeddings
from langchain_core.tools.retriever import create_retriever_tool

criminal_vector_store = Chroma(
    collection_name="criminal_collection",
    embedding_function=embeddings,
    persist_directory="./vectorDB",
)
criminal_retriever = criminal_vector_store.as_retriever()
criminal_retriever_tool = create_retriever_tool(
    retriever=criminal_retriever,
    name="criminal_retriever",
    description="A tool to retrieve criminal law related information from the vector store"
)

money_debt_vector_store = Chroma(
    collection_name="money_debt_collection",
    embedding_function=embeddings,
    persist_directory="./vectorDB",
)
money_debt_retriever = money_debt_vector_store.as_retriever()
money_debt_retriever_tool = create_retriever_tool(
    retriever=money_debt_retriever,
    name="money_debt_retriever",
    description="A tool to retrieve money debt law related information from the vector store"
)

marriage_vector_store = Chroma(
    collection_name="marriage_collection",
    embedding_function=embeddings,
    persist_directory="./vectorDB",
)
marriage_retriever = marriage_vector_store.as_retriever()
marriage_retriever_tool = create_retriever_tool(
    retriever=marriage_retriever,
    name="marriage_retriever",
    description="A tool to retrieve marriage law related information from the vector store"
)