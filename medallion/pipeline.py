import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import sqlite3
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

DB_PATH = "medallion/medallion.db"

def init_db():
    """
    Initialise la base de données Medallion (Bronze/Silver/Gold)
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # BRONZE — emails bruts
    c.execute("""
        CREATE TABLE IF NOT EXISTS bronze_emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_id TEXT,
            raw_email TEXT,
            received_at TEXT,
            source TEXT DEFAULT 'api'
        )
    """)

    # SILVER — données nettoyées et structurées
    c.execute("""
        CREATE TABLE IF NOT EXISTS silver_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bronze_id INTEGER,
            client_id TEXT,
            anonymized_email TEXT,
            type_bateau TEXT,
            valeur_estimee REAL,
            zone_navigation TEXT,
            besoins_specifiques TEXT,
            urgence TEXT,
            pii_count INTEGER,
            processed_at TEXT,
            FOREIGN KEY (bronze_id) REFERENCES bronze_emails(id)
        )
    """)

    # GOLD — résultats finaux et métriques
    c.execute("""
        CREATE TABLE IF NOT EXISTS gold_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            silver_id INTEGER,
            client_id TEXT,
            selected_agents TEXT,
            offers_count INTEGER,
            best_offer TEXT,
            final_report TEXT,
            rag_score_avg REAL,
            duration_sec REAL,
            total_tokens INTEGER,
            model_used TEXT,
            created_at TEXT,
            FOREIGN KEY (silver_id) REFERENCES silver_requests(id)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Base Medallion initialisée (Bronze/Silver/Gold)")

def save_bronze(client_id: str, raw_email: str) -> int:
    """
    Bronze : stockage de l'email brut non traité
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO bronze_emails (client_id, raw_email, received_at)
        VALUES (?, ?, ?)
    """, (client_id, raw_email, datetime.now().isoformat()))
    bronze_id = c.lastrowid
    conn.commit()
    conn.close()
    print(f"🥉 Bronze — Email sauvegardé (id: {bronze_id})")
    return bronze_id

def save_silver(bronze_id: int, client_id: str, anonymized_email: str, 
                needs: dict, pii_count: int) -> int:
    
    # Convertir besoins_specifiques en string si c'est une liste
    besoins = needs.get("besoins_specifiques", "")
    if isinstance(besoins, list):
        besoins = ", ".join(besoins)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO silver_requests 
        (bronze_id, client_id, anonymized_email, type_bateau, valeur_estimee,
         zone_navigation, besoins_specifiques, urgence, pii_count, processed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        bronze_id,
        client_id,
        anonymized_email,
        needs.get("type_bateau", ""),
        float(str(needs.get("valeur_estimee", 0)).replace("€", "").replace(" ", "") or 0),
        needs.get("zone_navigation", ""),
        besoins,
        needs.get("urgence", ""),
        pii_count,
        datetime.now().isoformat()
    ))

def save_gold(silver_id: int, client_id: str, result: dict) -> int:
    """
    Gold : résultats finaux + métriques qualité
    """
    rag_scores = result.get("rag_scores", {}).get("agents_scores", [])
    rag_avg = round(sum(a["score"] for a in rag_scores) / len(rag_scores), 3) if rag_scores else 0
    
    total_tokens = sum(
        m.get("tokens", 0) for m in result.get("metadata", [])
    )

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO gold_results
        (silver_id, client_id, selected_agents, offers_count, final_report,
         rag_score_avg, duration_sec, total_tokens, model_used, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        silver_id,
        client_id,
        json.dumps(result.get("selected_agents", [])),
        result.get("offers_count", 0),
        result.get("final_report", ""),
        rag_avg,
        result.get("duration_sec", 0),
        total_tokens,
        "Groq/Llama-3.3-70B + Azure/Phi-4",
        datetime.now().isoformat()
    ))
    gold_id = c.lastrowid
    conn.commit()
    conn.close()
    print(f"🥇 Gold — Résultats finaux sauvegardés (id: {gold_id})")
    return gold_id

def get_medallion_stats() -> dict:
    """
    Retourne les statistiques de la base Medallion
    """
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    stats = {}
    
    c.execute("SELECT COUNT(*) FROM bronze_emails")
    stats["bronze_count"] = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM silver_requests")
    stats["silver_count"] = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM gold_results")
    stats["gold_count"] = c.fetchone()[0]
    
    c.execute("SELECT AVG(rag_score_avg), AVG(duration_sec), SUM(total_tokens) FROM gold_results")
    row = c.fetchone()
    stats["avg_rag_score"] = round(row[0] or 0, 3)
    stats["avg_duration"] = round(row[1] or 0, 1)
    stats["total_tokens"] = int(row[2] or 0)
    
    c.execute("""
        SELECT selected_agents, COUNT(*) as cnt 
        FROM gold_results 
        GROUP BY selected_agents 
        ORDER BY cnt DESC LIMIT 3
    """)
    stats["top_agents"] = c.fetchall()
    
    conn.close()
    return stats

if __name__ == "__main__":
    init_db()
    
    # Test
    bronze_id = save_bronze("client_test", "Bonjour, voilier 80000€ Méditerranée")
    silver_id = save_silver(
        bronze_id, "client_test",
        "Bonjour, voilier [VALEUR]€ [ZONE]",
        {"type_bateau": "voilier", "valeur_estimee": 80000,
         "zone_navigation": "Méditerranée", "urgence": "haute"},
        pii_count=1
    )
    gold_id = save_gold(silver_id, "client_test", {
        "selected_agents": ["AXA Marine", "Allianz Maritime"],
        "offers_count": 3,
        "final_report": "Rapport test",
        "rag_scores": {"agents_scores": [{"score": 0.85}, {"score": 0.72}]},
        "metadata": [{"tokens": 500}],
        "duration_sec": 25.3
    })
    
    stats = get_medallion_stats()
    print(f"\n📊 Stats Medallion :")
    print(f"   🥉 Bronze : {stats['bronze_count']} emails")
    print(f"   🥈 Silver : {stats['silver_count']} requêtes")
    print(f"   🥇 Gold   : {stats['gold_count']} résultats")
    print(f"   📊 RAG score moyen : {stats['avg_rag_score']}")
    print(f"   ⏱️  Durée moyenne : {stats['avg_duration']}s")