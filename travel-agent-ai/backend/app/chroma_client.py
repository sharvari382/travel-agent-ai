"""
ChromaDB setup.

Single local, file-based vector store (persisted under ./chroma_data).
No separate DB server needed — this is the entire "database layer" now.

One collection ("chat_memory") holds every message from every session as
a document. Each document carries metadata (session_id, role, timestamp)
so we can both:
  - filter by session_id + sort by timestamp -> exact conversation history
  - run a similarity search across everything -> semantic recall
"""
import os
import chromadb

CHROMA_PATH = os.getenv("CHROMA_PATH", "./chroma_data")

client = chromadb.PersistentClient(path=CHROMA_PATH)

chat_memory = client.get_or_create_collection(
    name="chat_memory",
    metadata={"hnsw:space": "cosine"},
)

trip_plans = client.get_or_create_collection(
    name="trip_plans",
    metadata={"hnsw:space": "cosine"},
)
