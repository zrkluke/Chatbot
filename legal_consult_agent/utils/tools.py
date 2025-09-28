'''
ChromaDB Retrieval Tool
'''
from langchain_chroma import Chroma
from .embeddings import embeddings


criminal_vector_store = Chroma(
    collection_name="criminal_collection",
    embedding_function=embeddings,
    persist_directory="./vectorDB",
)
criminal_retriever = criminal_vector_store.as_retriever()


money_debt_vector_store = Chroma(
    collection_name="money_debt_collection",
    embedding_function=embeddings,
    persist_directory="./vectorDB",
)
money_debt_retriever = money_debt_vector_store.as_retriever()


marriage_vector_store = Chroma(
    collection_name="marriage_collection",
    embedding_function=embeddings,
    persist_directory="./vectorDB",
)
marriage_retriever = marriage_vector_store.as_retriever()
