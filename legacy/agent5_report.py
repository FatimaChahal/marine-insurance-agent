import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from utils.azure_client import call_phi
from utils.logger import log_agent

def generate_report(client_needs: dict, offers: list) -> str:
    """
    Agent 5 : Génère le rapport final et recommandation au client
    """
    best_offer = min(offers, key=lambda x: int(x['prime_annuelle'].replace('€', '').replace(' ', '')))

    prompt = f"""
    Tu es un expert en assurance maritime.
    Client : {client_needs['type_bateau']} de {client_needs['valeur_estimee']}€, 
    zone {client_needs['zone_navigation']}, besoin : {client_needs['besoins_specifiques']}.
    
    Offres reçues : {json.dumps(offers, ensure_ascii=False)}
    Meilleure offre prix : {best_offer['agent']} à {best_offer['prime_annuelle']}
    
    Génère un rapport client avec :
    1. Recommandation claire et justifiée
    2. Comparaison rapide des offres
    3. Prochaine étape
    
    Ton professionnel, maximum 10 lignes.
    """

    result = call_phi(prompt, temperature=0.1, max_tokens=500)
    log_agent("Agent5_Report", result, result["tokens_used"], result["response_time"])

    print(f"✅ Agent 5 — Rapport généré :\n{result['content']}")
    return result['content']

if __name__ == "__main__":
    test_needs = {
        "type_bateau": "voilier",
        "valeur_estimee": 80000,
        "zone_navigation": "Méditerranée-Atlantique",
        "besoins_specifiques": "couverture tous risques incluant assistance 24h/24"
    }
    test_offers = [
        {"agent": "AXA Marine", "prime_annuelle": "1200€", "franchise": "500€", "note": 8},
        {"agent": "Swiss Life Nautique", "prime_annuelle": "1000€", "franchise": "300€", "note": 9},
        {"agent": "Allianz Maritime", "prime_annuelle": "1100€", "franchise": "400€", "note": 8}
    ]
    generate_report(test_needs, test_offers)