import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import chromadb
from chromadb.utils import embedding_functions
from rag.data import MARITIME_AGENTS_DOCS

COLLECTION_NAME = "maritime_agents"

def get_vectorstore():
    """
    Initialise et retourne la collection ChromaDB
    """
    client = chromadb.PersistentClient(path="./chroma_db")
    
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )
    
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef
    )
    
    # Charge les documents si la collection est vide
    if collection.count() == 0:
        print("📚 Chargement de la base RAG agents maritimes...")
        collection.add(
            ids=[doc["id"] for doc in MARITIME_AGENTS_DOCS],
            documents=[doc["content"] for doc in MARITIME_AGENTS_DOCS],
            metadatas=[doc["metadata"] for doc in MARITIME_AGENTS_DOCS]
        )
        print(f"✅ {collection.count()} agents chargés dans ChromaDB")
    
    return collection


def search_agents(query: str, n_results: int = 3) -> list:
    """
    Recherche sémantique des agents les plus pertinents
    """
    collection = get_vectorstore()
    
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    
    agents = []
    for i, doc in enumerate(results["documents"][0]):
        agents.append({
            "nom": results["metadatas"][0][i]["agent"],
            "specialite": results["metadatas"][0][i]["specialite"],
            "zone": results["metadatas"][0][i]["zone"],
            "score": round(1 - results["distances"][0][i], 3),
            "description": doc[:200]
        })
    
    return agents


if __name__ == "__main__":
    query = "voilier 80000€ traversée Méditerranée Atlantique assistance 24h"
    results = search_agents(query)
    print("\n🔍 Résultats RAG :")
    for r in results:
        print(f"  → {r['nom']} (score: {r['score']}) — {r['zone']}")