import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
import json
import random
from datetime import datetime, timedelta
from medallion.pipeline import init_db, DB_PATH

init_db()

AGENTS = ["April Marine", "MAIF Mer", "Generali Nautique", 
          "Swiss Life Nautique", "AXA Marine", "Allianz Maritime"]

BATEAUX = [
    ("voilier", 80000, "Méditerranée-Atlantique"),
    ("yacht", 250000, "Méditerranée/Caraïbes"),
    ("catamaran", 120000, "Tour du monde"),
    ("bateau moteur", 35000, "Côtes françaises"),
    ("semi-rigide", 8000, "Méditerranée"),
    ("voilier de course", 180000, "Atlantique"),
    ("péniche", 90000, "Canaux français"),
    ("voilier ancien", 70000, "Méditerranée"),
]

CLIENTS = [
    ("client_001", "Jean Dupont"), ("client_002", "Pierre Martin"),
    ("client_003", "Marie Leblanc"), ("client_004", "Thomas Bernard"),
    ("client_005", "Sophie Moreau"), ("client_006", "Marc Dubois"),
    ("client_007", "Anne Petit"), ("client_008", "Paul Simon"),
    ("client_009", "Isabelle Laurent"), ("client_010", "François Roux"),
    ("client_011", "Caroline Blanc"), ("client_012", "Philippe Garcia"),
    ("client_013", "Julien Martinez"), ("client_014", "Nathalie Leroy"),
    ("client_015", "Eric Morin"), ("client_016", "Véronique Simon"),
    ("client_017", "Bernard Dupuis"), ("client_018", "Michel Lambert"),
    ("client_019", "Stéphanie Rousseau"), ("client_020", "Christine Fournier"),
]

def generate_mock_data(n=20):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    print(f"🚀 Génération de {n} enregistrements Medallion...")

    for i in range(n):
        client_id, client_name = CLIENTS[i % len(CLIENTS)]
        bateau, valeur, zone = random.choice(BATEAUX)
        date = (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()

        # BRONZE
        email = f"Bonjour, je veux assurer mon {bateau} ({valeur}€) en {zone}. Merci, {client_name}"
        c.execute("""INSERT INTO bronze_emails (client_id, raw_email, received_at) 
                     VALUES (?, ?, ?)""", (client_id, email, date))
        bronze_id = c.lastrowid

        # SILVER
        anonymized = email.replace(client_name, "[NOM_1]")
        c.execute("""INSERT INTO silver_requests 
                     (bronze_id, client_id, anonymized_email, type_bateau, valeur_estimee,
                      zone_navigation, besoins_specifiques, urgence, pii_count, processed_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (bronze_id, client_id, anonymized, bateau, float(valeur),
                   zone, "couverture tous risques assistance 24h",
                   random.choice(["haute", "moyenne", "basse"]), 1, date))
        silver_id = c.lastrowid

        # GOLD
        n_agents = random.randint(3, 6)
        selected = random.sample(AGENTS, n_agents)
        rag_avg = round(random.uniform(0.42, 0.65), 3)
        duration = round(random.uniform(15, 35), 1)
        tokens = random.randint(1200, 2000)

        report = f"""**Rapport Client : {bateau.title()} {valeur}€**

**Classement des offres :**
1. {selected[0]} — Prime 2200€, franchise 400€, garanties complètes, note 9
2. {selected[1]} — Prime 1800€, franchise 350€, garanties RC+dommages, note 8
3. {selected[2] if len(selected) > 2 else selected[0]} — Prime 1200€, franchise 250€, garanties de base, note 7

**Recommandation : {selected[0]}**
Meilleur rapport qualité/prix pour votre {bateau} en {zone}.

**Prochaine étape :** Contacter {selected[0]} pour finaliser."""

        c.execute("""INSERT INTO gold_results 
                     (silver_id, client_id, selected_agents, offers_count, final_report,
                      rag_score_avg, duration_sec, total_tokens, model_used, created_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                  (silver_id, client_id, json.dumps(selected), n_agents,
                   report, rag_avg, duration, tokens,
                   "Groq/Llama-3.3-70B + Azure/Phi-4", date))

        print(f"✅ [{i+1}/{n}] {client_id} — {bateau} {valeur}€ — {len(selected)} agents")

    conn.commit()
    conn.close()

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
    generate_mock_data(20)