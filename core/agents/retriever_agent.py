import os
import json
from langchain_core.tools import tool
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from core.s3_storage import S3Manager

# Initialize local FAISS vector store
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vector_store = None

def init_vector_store():
    global vector_store
    vector_path = "data/faiss_index"
    s3_manager = S3Manager()
    
    if not os.path.exists(vector_path):
        os.makedirs(vector_path, exist_ok=True)
        # Attempt to download from S3
        s3_manager.download_file("index.faiss", os.path.join(vector_path, "index.faiss"))
        s3_manager.download_file("index.pkl", os.path.join(vector_path, "index.pkl"))
        
    try:
        vector_store = FAISS.load_local(vector_path, embeddings, allow_dangerous_deserialization=True)
        print("Loaded FAISS index from disk.")
    except Exception as e:
        print(f"Could not load vector store from {vector_path}, attempting to build from JSON: {e}")
        json_path = "data/financial_products.json"
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                products = json.load(f)
            texts = [
                f"Name: {p['name']} | Category: {p['category']} | Description: {p['description']} | Benefits: {', '.join(p['benefits'])}"
                for p in products
            ]
            metadatas = [{"id": p["id"], "name": p["name"]} for p in products]
            vector_store = FAISS.from_texts(texts, embeddings, metadatas=metadatas)
            vector_store.save_local(vector_path)
            print("Built and saved FAISS index.")
        else:
            print("No data found to build vector store.")

init_vector_store()

@tool
def retrieve_financial_docs(query: str) -> str:
    """Retrieve financial product documentation and context from the Capital One knowledge base."""
    if not vector_store:
        return "No vector store available."
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(query)
    return "\n\n".join(doc.page_content for doc in docs)
