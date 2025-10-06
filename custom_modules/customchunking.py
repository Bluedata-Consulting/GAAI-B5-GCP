

from langchain_core.documents import Document

def create_chunk(text,chunk_size=1000,overlap=200):
    chunk = []
    start = 0
    while start< len(text):
        end = start + chunk_size
        chunk.append(Document(page_content=text[start:end]))
        start = start + chunk_size - overlap
    return chunk
