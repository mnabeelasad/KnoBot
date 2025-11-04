import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient, models
import time

# --- Configuration ---
QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = "wattos_ai_documents"

# --- Service Initialization ---
embeddings_model = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
qdrant_client = QdrantClient(url=QDRANT_URL)

def check_qdrant_connection():
    max_retries = 5
    for i in range(max_retries):
        try:
            qdrant_client.get_collections()
            print("Successfully connected to Qdrant.")
            return True
        except Exception:
            print(f"Attempt {i+1}/{max_retries}: Could not connect to Qdrant. Retrying...")
            time.sleep(5)
    print("FATAL: Could not connect to Qdrant.")
    return False

if check_qdrant_connection():
    try:
        # We only need a simple collection, no special text index needed for basic RAG.
        qdrant_client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
        )
        print(f"Qdrant collection '{COLLECTION_NAME}' created successfully.")
    except Exception:
        print(f"Qdrant collection '{COLLECTION_NAME}' may already exist.")
else:
    exit("Exiting: Qdrant connection failed.")

vector_store = Qdrant(
    client=qdrant_client,
    collection_name=COLLECTION_NAME,
    embeddings=embeddings_model,
)

# In-memory store for document names
uploaded_files_db = []

def add_document_to_vector_store(file_path: str, file_name: str):
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(documents)
    for i, chunk in enumerate(chunks):
        chunk.metadata = {"source": file_name, "chunk_id": i}
    vector_store.add_documents(chunks)
    if file_name not in uploaded_files_db:
        uploaded_files_db.append(file_name)
    return True

def get_retriever():
    """Returns a simple retriever for the RAG agent."""
    return vector_store.as_retriever()

def get_uploaded_files():
    """Returns a list of uploaded file names."""
    return uploaded_files_db