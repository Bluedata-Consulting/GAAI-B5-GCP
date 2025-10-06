
# pip install pypdf2 langchain langchain-chroma langchain-google-genai

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
import numpy as np
from PyPDF2 import PdfReader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
import os

embedding_model_name = "models/gemini-embedding-001"

# Data ingestion pipeline
file = "/home/zadmin/Desktop/test/GAAI-B5-GCP/datasets/SalesforceFinancial.pdf"

reader = PdfReader(file)
raw_text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
print(raw_text)



# load embedding model
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
import sys
sys.path.append("/home/zadmin/Desktop/test/GAAI-B5-GCP/custom_modules")


from customchunking import create_chunk
# def create_chunk(text,chunk_size=1000,overlap=200):
#     chunk = []
#     start = 0
#     while start< len(text):
#         end = start + chunk_size
#         chunk.append(Document(page_content=text[start:end]))
#         start = start + chunk_size - overlap
#     return chunk

chunk = create_chunk(raw_text)


# load embeddings and text into FAISS vector db
embeddings = GoogleGenerativeAIEmbeddings(model=embedding_model_name)
vector_db_path = "VectorDB_Chroma"
os.makedirs(vector_db_path,exist_ok=True)



vectorstore = Chroma.from_documents(documents=chunk, embedding=embeddings,
                                    persist_directory=vector_db_path,collection_name="salesforce2",
                                    collection_metadata={"use_type":"TRAINING AND EXPERIMENTATION"})

# using vector db object to initialize a retriever object - to perform vector search/retrieval
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 2})



def retrieve(query:str):
    docs = retriever.invoke(query)
    output = "/n".join([pg.page_content for pg in docs])
    return output

retriever_tool = FunctionTool(func=retrieve)

root_agent = LlmAgent(name="RAGAGent",
                      model="gemini-2.0-flash",
                      instruction="""
                      You are an expert assistant. You must ALWAYS use the `retriever_tool` to retrieve relevant information from the document.
                Never answer directly unless the `retriever_tool` is called.

            Always follow these steps:
            1. Use `retriever_tool` to find relevant info.
            2. Read the output from the tool.
            3. Then format a helpful, clear answer.

            If you don’t find the info, say “I couldn’t find it in the document.”
                      """,
                      description="Assitant Agent",
                      tools=[retriever_tool])

