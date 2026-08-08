import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import fitz  # pymupdf
import requests
import chromadb
from chromadb.utils import embedding_functions
from datetime import datetime

COLLECTION_NAME = "maritime_agents"
PDF_DIR = "data/pdfs"

# Documents publics réels sur l'assurance maritime
PUBLIC_DOCS = [
    {
        "url": "https://www.maif.fr/content/documents/public/maif-fr/pdf/contrat/pp/CGNautisMaif.pdf",
        "filename": "maif_nautis.pdf",
        "agent": "MAIF Mer",
        "type": "conditions_generales"
    },
    {
        "url": "https://www.assurback.com/static/pdf/Conditions-Generales-AXA-Yachting-Solutions.pdf",
        "filename": "axa_yachting.pdf",
        "agent": "Swiss Life Nautique",
        "type": "conditions_generales"
    },
    {
        "url": "https://www.assurback.com/static/pdf/DISPOSITIONS-GENERALES-GENERALI-GA9F21J.pdf",
        "filename": "generali_plaisance.pdf",
        "agent": "Generali Nautique",
        "type": "conditions_generales"
    },
    {
        "url": "https://www.assurback.com/static/pdf/DG-Generali-Plaisance.pdf",
        "filename": "generali_plaisance2.pdf",
        "agent": "Allianz Maritime",
        "type": "conditions_generales"
    },
    {
        "url": "https://guide.reassurez-moi.fr/guide/wp-content/uploads/2019/06/conditions-generales-assurance-bateau-gmf.pdf",
        "filename": "gmf_plaisance.pdf",
        "agent": "April Marine",
        "type": "conditions_generales"
    }
]

def download_pdf(url: str, filename: str) -> str:
    """Télécharge un PDF et le sauvegarde localement"""
    filepath = os.path.join(PDF_DIR, filename)
    if os.path.exists(filepath):
        print(f"✅ Déjà téléchargé : {filename}")
        return filepath
    
    try:
        print(f"📥 Téléchargement : {filename}...")
        response = requests.get(url, timeout=30, headers={
            "User-Agent": "Mozilla/5.0"
        })
        response.raise_for_status()
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"✅ Téléchargé : {filename} ({len(response.content)} bytes)")
        return filepath
    except Exception as e:
        print(f"⚠️ Échec téléchargement {filename} : {e}")
        return None

def extract_text_from_pdf(filepath: str, max_chars: int = 3000) -> str:
    """Extrait le texte d'un PDF avec PyMuPDF"""
    try:
        doc = fitz.open(filepath)
        text = ""
        for page in doc:
            text += page.get_text()
            if len(text) > max_chars:
                break
        doc.close()
        return text[:max_chars].strip()
    except Exception as e:
        print(f"⚠️ Erreur extraction {filepath} : {e}")
        return ""

def load_pdfs_to_chromadb():
    """
    Télécharge, extrait et indexe les PDFs dans ChromaDB
    """
    print("📚 Chargement des PDFs réels dans ChromaDB...")
    os.makedirs(PDF_DIR, exist_ok=True)

    client = chromadb.PersistentClient(path="./chroma_db")
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    # Récupère la collection existante
    try:
        collection = client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=ef
        )
        print(f"✅ Collection existante : {collection.count()} documents")
    except:
        collection = client.create_collection(
            name=COLLECTION_NAME,
            embedding_function=ef
        )

    added = 0
    for i, doc in enumerate(PUBLIC_DOCS):
        filepath = download_pdf(doc["url"], doc["filename"])
        if not filepath:
            continue

        text = extract_text_from_pdf(filepath)
        if not text:
            continue

        doc_id = f"pdf_{doc['agent'].replace(' ', '_')}_{i}"

        try:
            collection.add(
                ids=[doc_id],
                documents=[text],
                metadatas=[{
                    "agent": doc["agent"],
                    "type": doc["type"],
                    "source": "pdf_reel",
                    "filename": doc["filename"],
                    "indexed_at": datetime.now().isoformat()
                }]
            )
            print(f"✅ Indexé : {doc['agent']} ({len(text)} chars)")
            added += 1
        except Exception as e:
            print(f"⚠️ Déjà indexé ou erreur : {e}")

    print(f"\n✅ {added} PDFs indexés dans ChromaDB")
    print(f"📊 Total documents : {collection.count()}")
    return collection

if __name__ == "__main__":
    load_pdfs_to_chromadb()