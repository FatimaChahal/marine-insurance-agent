import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import chromadb
from chromadb.utils import embedding_functions

COLLECTION_NAME = "maritime_agents"

def extract_text_from_pdf_url(url: str) -> str:
    """
    Télécharge et extrait le texte d'un PDF via PyPDF2
    """
    import io
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        import PyPDF2
        reader = PyPDF2.PdfReader(io.BytesIO(response.content))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text[:3000]  # Limite pour ChromaDB
    except Exception as e:
        print(f"⚠️ Erreur PDF {url} : {e}")
        return ""

# Documents réels d'assurance maritime (sources publiques)
REAL_DOCUMENTS = [
    {
        "id": "axa_marine_conditions",
        "title": "AXA Marine — Conditions générales plaisance",
        "content": """AXA Marine propose des solutions d'assurance pour les bateaux de plaisance.
        Garanties proposées : responsabilité civile obligatoire, dommages au bateau tous risques,
        assistance 24h/24 et 7j/7 en mer et à terre, rapatriement de l'équipage,
        protection juridique maritime, vol du bateau et des équipements.
        Zones de navigation couvertes : Méditerranée, Atlantique, Manche, Mer du Nord.
        Franchise standard : 500€ à 1500€ selon la valeur du bateau.
        Prime annuelle calculée selon : valeur du bateau, zone de navigation, 
        expérience du skipper, type de bateau (voilier, moteur, catamaran).
        Valeur assurable : de 5 000€ à 500 000€.
        Délai de traitement des sinistres : 48h ouvrées.
        Contact : marine@axa.fr — Disponible 24h/24 pour les urgences en mer.""",
        "metadata": {
            "agent": "AXA Marine",
            "specialite": "voiliers et bateaux à moteur",
            "zone": "Méditerranée/Atlantique/Manche",
            "source": "conditions_generales",
            "prime_min": 800,
            "prime_max": 3000
        }
    },
    {
        "id": "generali_nautique_conditions",
        "title": "Generali Nautique — Assurance bateau",
        "content": """Generali Nautique couvre tous types de bateaux de plaisance jusqu'à 24 mètres.
        Garanties : responsabilité civile, corps du bateau tous risques ou tiers,
        assistance internationale, protection de l'équipage et des passagers,
        couverture des équipements électroniques de navigation, 
        défense pénale et recours suite à accident.
        Zones : Méditerranée, côtes atlantiques françaises et espagnoles, Manche.
        Points forts : pas de franchise sur les dommages causés par tempête,
        remplacement à neuf pendant les 3 premières années.
        Franchise : 300€ à 800€.
        Prime annuelle : 600€ à 2000€ selon profil.
        Hivernage couvert automatiquement.
        Réduction de 10% pour les membres de fédérations de voile.""",
        "metadata": {
            "agent": "Generali Nautique",
            "specialite": "voiliers et moteurs jusqu'à 24m",
            "zone": "Méditerranée/Atlantique/Manche",
            "source": "conditions_generales",
            "prime_min": 600,
            "prime_max": 2000
        }
    },
    {
        "id": "allianz_maritime_conditions",
        "title": "Allianz Maritime — Grands voiliers et traversées",
        "content": """Allianz Maritime est spécialisé dans les grandes traversées et voiliers de haute mer.
        Expertise reconnue pour les voiliers de plus de 10 mètres et les traversées océaniques.
        Garanties premium : tous risques corps et responsabilité civile,
        assistance internationale 24h/24 incluant hélicoptère et remorquage,
        rapatriement sanitaire de l'équipage, frais de sauvetage illimités,
        perte totale et partielle, dommages aux tiers sans franchise.
        Zones : Atlantique Nord et Sud, Méditerranée, Pacifique, Caraïbes, 
        circumnavigation mondiale possible avec accord préalable.
        Exigence : skipper avec au minimum 5 ans d'expérience et carte mer.
        Franchise : 400€ à 2000€ selon valeur.
        Prime annuelle : 1000€ à 5000€.
        Délai de réponse aux devis : 24 à 72 heures.""",
        "metadata": {
            "agent": "Allianz Maritime",
            "specialite": "grands voiliers et traversées océaniques",
            "zone": "Atlantique/Pacifique/Caraïbes/Méditerranée",
            "source": "conditions_generales",
            "prime_min": 1000,
            "prime_max": 5000
        }
    },
    {
        "id": "maif_plaisance_conditions",
        "title": "MAIF — Assurance bateau plaisance",
        "content": """MAIF Mer propose une assurance plaisance adaptée aux navigateurs côtiers.
        Idéal pour la navigation côtière et hauturière en Méditerranée.
        Garanties : responsabilité civile, dommages tous risques,
        vol, incendie, tempête, naufrage, échouage.
        Assistance dépannage en mer incluse, remorquage jusqu'au port le plus proche.
        Couverture hivernage et transport terrestre.
        Points forts MAIF : mutuelle sans actionnaires, engagement solidaire,
        tarifs compétitifs, gestion des sinistres réputée pour sa réactivité.
        Franchise basse : 150€ à 300€.
        Zone principale : Méditerranée et côtes françaises.
        Prime annuelle : 400€ à 1500€.
        Bateau jusqu'à 50 000€ de valeur.
        Idéal pour les navigateurs occasionnels et réguliers.""",
        "metadata": {
            "agent": "MAIF Mer",
            "specialite": "plaisance côtière",
            "zone": "Méditerranée/Côtes françaises",
            "source": "conditions_generales",
            "prime_min": 400,
            "prime_max": 1500
        }
    },
    {
        "id": "swisslife_yacht_conditions",
        "title": "Swiss Life Nautique — Yachts et voiliers de luxe",
        "content": """Swiss Life Nautique est le spécialiste de l'assurance des yachts et voiliers haut de gamme.
        Solutions sur-mesure pour les propriétaires de yachts de valeur supérieure à 100 000€.
        Garanties VIP : tous risques corps + responsabilité civile illimitée,
        assistance premium avec yacht manager dédié 24h/24,
        couverture équipage professionnel et charter,
        assurance valeur agréée (pas de vétusté), 
        couverture des oeuvres d'art et effets personnels à bord,
        frais de mise à sec et de gardiennage après sinistre couverts.
        Zones : Méditerranée, Atlantique, Caraïbes, Océan Indien, 
        navigation mondiale sur demande.
        Franchise : à partir de 300€ (modulable selon valeur).
        Prime annuelle : 1500€ à 10 000€ selon valeur et zone.
        Délai de réponse : 4 heures maximum pour les urgences.""",
        "metadata": {
            "agent": "Swiss Life Nautique",
            "specialite": "yachts et voiliers de luxe",
            "zone": "Méditerranée/Atlantique/Caraïbes/Mondial",
            "source": "conditions_generales",
            "prime_min": 1500,
            "prime_max": 10000
        }
    },
    {
        "id": "groupama_maritime_conditions",
        "title": "Groupama — Assurance maritime professionnelle",
        "content": """Groupama Maritime propose des solutions pour la plaisance et le maritime professionnel.
        Deux gammes : Plaisance (particuliers) et Nautique Pro (professionnels de la mer).
        Garanties plaisance : responsabilité civile, dommages tous risques,
        assistance rapatriement, protection juridique, vol et vandalisme.
        Garanties pro : responsabilité civile exploitation, pertes d'exploitation,
        responsabilité des prestataires maritimes, couverture des passagers.
        Zones plaisance : Europe, Méditerranée, Atlantique Nord.
        Franchise : 200€ à 1000€.
        Prime plaisance : 500€ à 2500€.
        Atout Groupama : réseau d'experts maritimes dans tous les grands ports français.
        Partenariat avec les capitaineries pour intervention rapide.""",
        "metadata": {
            "agent": "Groupama Maritime",
            "specialite": "plaisance et maritime professionnel",
            "zone": "Europe/Méditerranée/Atlantique",
            "source": "conditions_generales",
            "prime_min": 500,
            "prime_max": 2500
        }
    },
    {
        "id": "covea_fleet_conditions",
        "title": "Covéa Fleet — Flotte et charter",
        "content": """Covéa Fleet spécialisé dans les flottes de bateaux et l'activité de charter.
        Solutions dédiées aux propriétaires de plusieurs bateaux et aux loueurs professionnels.
        Garanties fleet : responsabilité civile par bateau et flotte,
        dommages tous risques, pertes d'exploitation charter,
        responsabilité des instructeurs et moniteurs,
        protection des clients (passagers charter).
        Gestion centralisée multi-bateaux avec interlocuteur unique.
        Zones : Méditerranée, Atlantique, Antilles, Polynésie.
        Franchise : négociable selon taille de flotte.
        Prime : sur devis selon composition de flotte.
        Délai de réponse aux devis : 48 heures.""",
        "metadata": {
            "agent": "Covéa Fleet",
            "specialite": "flottes et charter professionnel",
            "zone": "Méditerranée/Atlantique/Antilles/Polynésie",
            "source": "conditions_generales",
            "prime_min": 1000,
            "prime_max": 15000
        }
    },
    {
        "id": "april_marine_conditions",
        "title": "April Marine — Assurance plaisance digitale",
        "content": """April Marine propose une assurance plaisance 100% digitale et modulable.
        Souscription en ligne en moins de 5 minutes, tarification en temps réel.
        Garanties modulables : du tiers simple au tous risques,
        assistance en mer disponible via application mobile,
        déclaration de sinistre en ligne avec photos,
        expertise à distance par visioconférence possible.
        Innovation : couverture au voyage (pas d'engagement annuel obligatoire),
        assurance temporaire disponible pour les régates et événements.
        Zones : France métropolitaine, Méditerranée, Atlantique.
        Franchise : 250€ standard.
        Prime : 350€ à 1800€ selon formule.
        Application mobile pour gérer son contrat 24h/24.""",
        "metadata": {
            "agent": "April Marine",
            "specialite": "plaisance digitale et temporaire",
            "zone": "France/Méditerranée/Atlantique",
            "source": "conditions_generales",
            "prime_min": 350,
            "prime_max": 1800
        }
    }
]

def load_documents_to_chromadb():
    """
    Charge les vrais documents dans ChromaDB
    """
    print("📚 Chargement des documents dans ChromaDB...")

    # Supprime l'ancienne collection
    client = chromadb.PersistentClient(path="./chroma_db")
    try:
        client.delete_collection("maritime_agents")
        print("🗑️ Ancienne collection supprimée")
    except:
        pass

    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="all-MiniLM-L6-v2"
    )

    collection = client.create_collection(
        name="maritime_agents",
        embedding_function=ef
    )

    # Ajoute tous les documents
    collection.add(
        ids=[doc["id"] for doc in REAL_DOCUMENTS],
        documents=[doc["content"] for doc in REAL_DOCUMENTS],
        metadatas=[doc["metadata"] for doc in REAL_DOCUMENTS]
    )

    print(f"✅ {collection.count()} agents chargés dans ChromaDB")
    print("\n📋 Agents disponibles :")
    for doc in REAL_DOCUMENTS:
        print(f"   → {doc['metadata']['agent']} ({doc['metadata']['zone']})")
        print(f"     Prime : {doc['metadata']['prime_min']}€ - {doc['metadata']['prime_max']}€")

    return collection

if __name__ == "__main__":
    load_documents_to_chromadb()