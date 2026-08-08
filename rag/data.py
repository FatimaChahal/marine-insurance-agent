# Base de connaissance des agents maritimes
# En production : alimentée par de vrais documents PDF/contrats

"""
Base de connaissance des agents maritimes — VERSION MOCK (POC)

En production, cette base serait alimentée par :
- Import automatique de PDFs de contrats d'assurance
- API externe des compagnies d'assurance
- Base de données relationnelle (PostgreSQL)
- Mise à jour périodique via pipeline ETL

Pour alimenter la base vectorielle en production :
    from rag.vectorstore import get_vectorstore
    collection = get_vectorstore()
    collection.add(ids=[...], documents=[...], metadatas=[...])
"""

MARITIME_AGENTS_DOCS = [
    {
        "id": "axa_marine",
        "content": """AXA Marine est spécialisé dans l'assurance des voiliers et bateaux de plaisance.
        Couvre les zones Méditerranée et Atlantique. Prime annuelle entre 800€ et 2000€.
        Franchise standard 500€. Garanties : responsabilité civile, dommages, assistance 24h/24.
        Idéal pour voiliers entre 20 000€ et 150 000€. Délai de réponse : 48h.""",
        "metadata": {"agent": "AXA Marine", "specialite": "voiliers", "zone": "Méditerranée/Atlantique"}
    },
    {
        "id": "generali_nautique",
        "content": """Generali Nautique couvre voiliers et bateaux à moteur en Méditerranée et Manche.
        Prime annuelle entre 600€ et 1800€. Franchise 300€.
        Garanties : responsabilité civile, vol, incendie, naufrage.
        Spécialisé bateaux jusqu'à 100 000€. Délai réponse : 24h.""",
        "metadata": {"agent": "Generali Nautique", "specialite": "voiliers et moteurs", "zone": "Méditerranée/Manche"}
    },
    {
        "id": "allianz_maritime",
        "content": """Allianz Maritime spécialisé grands voiliers et traversées Atlantique et Pacifique.
        Prime annuelle entre 1000€ et 3000€. Franchise 400€.
        Garanties complètes : responsabilité civile, assistance internationale 24h/24,
        rapatriement équipage, couverture tous risques.
        Idéal voiliers haute valeur 50 000€ à 500 000€. Délai réponse : 72h.""",
        "metadata": {"agent": "Allianz Maritime", "specialite": "grands voiliers", "zone": "Atlantique/Pacifique"}
    },
    {
        "id": "maif_mer",
        "content": """MAIF Mer spécialisé plaisance côtière Méditerranée.
        Prime annuelle entre 400€ et 1200€. Franchise 200€.
        Garanties : responsabilité civile, dommages matériels, vol.
        Idéal petits bateaux jusqu'à 50 000€. Délai réponse : 24h.""",
        "metadata": {"agent": "MAIF Mer", "specialite": "plaisance côtière", "zone": "Méditerranée"}
    },
    {
        "id": "swisslife_nautique",
        "content": """Swiss Life Nautique spécialisé yachts de luxe et voiliers haute gamme.
        Zones Méditerranée, Atlantique et Caraïbes. Prime annuelle entre 1500€ et 5000€.
        Franchise 300€. Garanties premium : tous risques, assistance VIP 24h/24,
        couverture équipage, rapatriement international.
        Idéal yachts et voiliers de luxe 100 000€ à 2 000 000€. Délai réponse : 24h.""",
        "metadata": {"agent": "Swiss Life Nautique", "specialite": "yachts luxe", "zone": "Méditerranée/Atlantique/Caraïbes"}
    }
]

# Tarifs réalistes par assureur — simulés mais cohérents
TARIFS_REELS = {
    "AXA Marine": lambda valeur, zone: {
        "prime_annuelle": f"{round(valeur * 0.015)}€",
        "franchise": "500€" if valeur < 100000 else "1000€",
        "garanties": "RC, tous risques, assistance 24h/24, rapatriement",
        "note": 8,
        "delai_reponse": "48h"
    },
    "MAIF Mer": lambda valeur, zone: {
        "prime_annuelle": f"{round(valeur * 0.012)}€",
        "franchise": "300€",
        "garanties": "RC, dommages, vol, tempête",
        "note": 7,
        "delai_reponse": "24h"
    },
    "Generali Nautique": lambda valeur, zone: {
        "prime_annuelle": f"{round(valeur * 0.016)}€",
        "franchise": "400€",
        "garanties": "RC, tous risques, assistance, protection juridique",
        "note": 9,
        "delai_reponse": "24h"
    },
    "Swiss Life Nautique": lambda valeur, zone: {
        "prime_annuelle": f"{round(valeur * 0.022)}€",
        "franchise": "300€",
        "garanties": "RC, tous risques, assistance VIP, rapatriement, équipage",
        "note": 9,
        "delai_reponse": "24h"
    },
    "Allianz Maritime": lambda valeur, zone: {
        "prime_annuelle": f"{round(valeur * 0.018)}€",
        "franchise": "500€" if zone != "Atlantique" else "800€",
        "garanties": "RC, tous risques, assistance internationale, frais sauvetage",
        "note": 8,
        "delai_reponse": "72h"
    },
    "Groupama Maritime": lambda valeur, zone: {
        "prime_annuelle": f"{round(valeur * 0.013)}€",
        "franchise": "250€",
        "garanties": "RC, dommages, vol, incendie",
        "note": 7,
        "delai_reponse": "48h"
    },
    "Covéa Fleet": lambda valeur, zone: {
        "prime_annuelle": f"{round(valeur * 0.020)}€",
        "franchise": "600€",
        "garanties": "RC flotte, tous risques, pertes exploitation",
        "note": 8,
        "delai_reponse": "48h"
    },
    "April Marine": lambda valeur, zone: {
        "prime_annuelle": f"{round(valeur * 0.010)}€",
        "franchise": "200€",
        "garanties": "RC, dommages modulables, assistance mobile",
        "note": 7,
        "delai_reponse": "24h"
    }
}

def get_offer(agent_nom: str, valeur: float, zone: str) -> dict:
    """
    Retourne une offre réaliste pour un agent donné
    """
    if agent_nom in TARIFS_REELS:
        offer = TARIFS_REELS[agent_nom](valeur, zone)
        offer["agent"] = agent_nom
        return offer
    return {
        "agent": agent_nom,
        "prime_annuelle": f"{round(valeur * 0.015)}€",
        "franchise": "500€",
        "garanties": "RC, dommages",
        "note": 7,
        "delai_reponse": "48h"
    }