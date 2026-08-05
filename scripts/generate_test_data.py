import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph.pipeline import build_pipeline, run_with_monitoring
from medallion.pipeline import init_db
from datetime import datetime
import time

init_db()

# 20 emails tests variés et réalistes
TEST_EMAILS = [
    {
        "client_id": "client_001",
        "email": """Bonjour, je souhaite assurer mon voilier de 12m (80 000€) pour une traversée Méditerranée-Atlantique en septembre. Couverture tous risques + assistance 24h/24. Merci, Jean Dupont"""
    },
    {
        "client_id": "client_002",
        "email": """Bonjour, propriétaire d'un yacht 18m (250 000€), navigation Méditerranée et Caraïbes. Cherche assurance premium tous risques avec assistance VIP. Cordialement, Pierre Martin"""
    },
    {
        "client_id": "client_003",
        "email": """Bonjour, bateau moteur 6m (15 000€), navigation côtière Méditerranée uniquement. Budget limité, cherche formule économique. Merci, Marie Leblanc"""
    },
    {
        "client_id": "client_004",
        "email": """Bonjour, catamaran 14m (120 000€) pour tour du monde prévu l'année prochaine. Besoin couverture mondiale tous risques équipage inclus. Thomas Bernard"""
    },
    {
        "client_id": "client_005",
        "email": """Bonjour, j'ai un voilier de compétition 9m (45 000€) que je veux assurer pour les régates en Atlantique. Besoin couverture spécifique compétition. Sophie Moreau"""
    },
    {
        "client_id": "client_006",
        "email": """Bonjour, je loue des bateaux à moteur (flotte de 5 bateaux, valeur totale 200 000€) pour du charter en Méditerranée. Cherche assurance flotte professionnelle. Marc Dubois"""
    },
    {
        "client_id": "client_007",
        "email": """Bonjour, voilier ancien 10m (30 000€) pour navigation côtière Bretagne et Manche. Bateau de plus de 20 ans, cherche assurance adaptée. Anne Petit"""
    },
    {
        "client_id": "client_008",
        "email": """Bonjour, semi-rigide 5m (8 000€) pour la plongée en Méditerranée. Navigation côtière courte distance. Cherche assurance simple et pas chère. Paul Simon"""
    },
    {
        "client_id": "client_009",
        "email": """Bonjour, yacht luxe 25m (500 000€) pour navigation Méditerranée, Atlantique et Caraïbes avec équipage professionnel de 3 personnes. Besoin couverture premium. Isabelle Laurent"""
    },
    {
        "client_id": "client_010",
        "email": """Bonjour, voilier 11m (65 000€) pour traversée Atlantique solo prévu dans 6 mois. Besoin assurance spécifique navigation hauturière solo. François Roux"""
    },
    {
        "client_id": "client_011",
        "email": """Bonjour, péniche habitation 20m (90 000€) sur canaux français. Cherche assurance navigation fluviale + habitation. Caroline Blanc"""
    },
    {
        "client_id": "client_012",
        "email": """Bonjour, voilier école 8m (25 000€) utilisé pour cours de voile avec élèves débutants. Besoin assurance responsabilité civile renforcée. Philippe Garcia"""
    },
    {
        "client_id": "client_013",
        "email": """Bonjour, jet ski (12 000€) pour navigation côtière Côte d'Azur été uniquement. Cherche assurance saisonnière. Julien Martinez"""
    },
    {
        "client_id": "client_014",
        "email": """Bonjour, voilier 13m (95 000€) pour navigation Méditerranée + participation régates offshore. Double usage plaisance et compétition. Nathalie Leroy"""
    },
    {
        "client_id": "client_015",
        "email": """Bonjour, catamaran charter 12m (150 000€) avec activité professionnelle de location en Corse et Sardaigne. Besoin assurance professionnelle + responsabilité passagers. Eric Morin"""
    },
    {
        "client_id": "client_016",
        "email": """Bonjour, voilier 9m (40 000€) pour navigation Manche et mer du Nord. Conditions météo difficiles, besoin couverture solide tempête et naufrage. Véronique Simon"""
    },
    {
        "client_id": "client_017",
        "email": """Bonjour, bateau moteur 8m (35 000€) pour pêche sportive en Atlantique, jusqu'à 50 miles des côtes. Besoin assurance pêche hauturière. Bernard Dupuis"""
    },
    {
        "client_id": "client_018",
        "email": """Bonjour, voilier de collection 1960 restauré (70 000€), navigation très occasionnelle Méditerranée. Cherche assurance valeur agréée pour bateau ancien. Michel Lambert"""
    },
    {
        "client_id": "client_019",
        "email": """Bonjour, trimaran de course 11m (180 000€) pour participation transat et courses offshore. Besoin assurance compétition haute mer avec assistance hauturière. Stéphanie Rousseau"""
    },
    {
        "client_id": "client_020",
        "email": """Bonjour, voilier familial 10m (55 000€) pour croisières estivales Méditerranée avec 2 enfants. Besoin couverture familiale tous risques avec assistance. Christine Fournier"""
    }
]

def generate_data():
    print("🚀 Génération de données de test Medallion...")
    print(f"📧 {len(TEST_EMAILS)} emails à traiter\n")

    pipeline = build_pipeline()
    success = 0
    errors = 0

    for i, test in enumerate(TEST_EMAILS):
        print(f"\n[{i+1}/{len(TEST_EMAILS)}] Traitement de {test['client_id']}...")
        try:
            initial_state = {
                "raw_email": test["email"],
                "client_id": test["client_id"],
                "client_needs": None,
                "client_anonymized": None,
                "selected_agents": None,
                "rag_scores": None,
                "emails_sent": None,
                "offers_collected": None,
                "final_report": None,
                "silver_id": None,
                "metadata": [],
                "errors": [],
                "start_time": datetime.now().isoformat(),
                "status": "running"
            }

            result = pipeline.invoke(initial_state)

            if result["status"] == "completed":
                success += 1
                print(f"✅ {test['client_id']} — {result['selected_agents']}")
            else:
                errors += 1

        except Exception as e:
            errors += 1
            print(f"❌ {test['client_id']} — Erreur : {e}")

        if (i + 1) % 5 == 0:
            print(f"\n⏸️ Pause 60s pour respecter le rate limit Groq...")
            time.sleep(60)
        else:
            time.sleep(3)

    print(f"\n{'='*50}")
    print(f"✅ Succès : {success}/{len(TEST_EMAILS)}")
    print(f"❌ Erreurs : {errors}/{len(TEST_EMAILS)}")

    from medallion.pipeline import get_medallion_stats
    stats = get_medallion_stats()
    print(f"\n📊 Stats Medallion finales :")
    print(f"   🥉 Bronze : {stats['bronze_count']} emails")
    print(f"   🥈 Silver : {stats['silver_count']} requêtes")
    print(f"   🥇 Gold   : {stats['gold_count']} résultats")
    print(f"   📊 RAG score moyen : {stats['avg_rag_score']}")
    print(f"   ⏱️  Durée moyenne : {stats['avg_duration']}s")
    print(f"   🔢 Total tokens : {stats['total_tokens']}")

if __name__ == "__main__":
    generate_data()