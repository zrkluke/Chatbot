from dotenv import load_dotenv
import os
from langchain_openai import OpenAIEmbeddings

load_dotenv()
embedding_model = os.getenv("OPENAI_EMBEDDING_MODEL")
embeddings = OpenAIEmbeddings(model=embedding_model)