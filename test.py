import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
import numpy as np

# --- (Optional) Verify Embedding Model ---
# List available models (uncomment to check)
# from sentence_transformers import util
# print(util.get_model_list())

# --- Initialize Embedding Model ---
# Use 'all-MiniLM-L6-v2' (384-dimensional embeddings, ~80MB)
model_name = "all-MiniLM-L6-v2"
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name=model_name
)

# --- Initialize ChromaDB (Persistent Storage) ---
chroma_client = chromadb.PersistentClient(path="./chroma_db")  # Saves to disk

# --- Create a Collection ---
collection_name = "doc_embeddings"
collection = chroma_client.create_collection(
    name=collection_name,
    embedding_function=embedding_function,
    metadata={"model": model_name, "embedding_dim": 384}
)

# --- Sample Documents to Embed ---
documents = [
    "Machine learning is a subset of artificial intelligence.",
    "Deep learning uses neural networks with many layers.",
    "Natural language processing helps computers understand human language.",
    "Python is a popular programming language for data science.",
    "ChromaDB is a vector database for storing embeddings."
]

# --- Add Documents to ChromaDB ---
ids = [f"id_{i}" for i in range(len(documents))]  # Unique IDs
metadatas = [{"category": "AI"}, {"category": "AI"}, {"category": "NLP"}, {"category": "Programming"}, {"category": "Database"}]

collection.add(
    documents=documents,
    metadatas=metadatas,
    ids=ids
)

print(f"✅ Successfully stored {len(documents)} embeddings in ChromaDB!")

# --- Query Similar Documents ---
query_text = "What is AI?"
results = collection.query(
    query_texts=[query_text],
    n_results=2  # Top 2 matches
)

print("\n🔍 Query Results:")
for i, (doc, meta) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
    print(f"{i+1}. {doc} (Category: {meta['category']})")

# --- Retrieve All Embeddings (Optional) ---
print("\n📊 Fetching stored embeddings...")
stored_data = collection.get(include=["embeddings", "documents", "metadatas"])
print(f"Total embeddings stored: {len(stored_data['ids'])}")
print(f"Sample embedding shape: {np.array(stored_data['embeddings'][0]).shape}")  # Should be (384,)