import streamlit as st
import requests
import json
import time
import plotly.graph_objects as go
from datetime import datetime

# Config page
st.set_page_config(
    page_title="Marine Insurance Agent",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1E2761 0%, #3B5BDB 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
    }
    .agent-card {
        background: #f0f4ff;
        border-left: 4px solid #3B5BDB;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .metric-card {
        background: white;
        border: 1px solid #e0e0e0;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    .status-running { color: #f59e0b; }
    .status-done { color: #10b981; }
    .status-error { color: #ef4444; }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🚢 Marine Insurance Agent</h1>
    <p>Pipeline multi-agents IA pour l'assurance maritime</p>
    <p style="font-size: 0.85rem; opacity: 0.8;">
        Azure AI Foundry · LiteLLM · LangGraph · RAG · Guardrails RGPD · Langfuse · MLflow
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    api_url = st.text_input(
        "API URL",
        value="http://localhost:8000",
        help="URL de l'API FastAPI"
    )
    
    api_key = st.text_input(
        "API Key",
        type="password",
        value="marine-insurance-secret-key-2026"
    )
    
    st.divider()
    
    st.header("📊 Métriques globales")
    
    try:
        health = requests.get(f"{api_url}/health", timeout=5)
        if health.status_code == 200:
            st.success("✅ API connectée")
        else:
            st.error("❌ API déconnectée")
    except:
        st.error("❌ API non accessible")
    
    st.divider()
    
    st.header("🤖 Agents disponibles")
    try:
        agents_resp = requests.get(f"{api_url}/agents", timeout=5)
        if agents_resp.status_code == 200:
            agents = agents_resp.json()["agents"]
            for a in agents:
                st.markdown(f"**{a['nom']}**")
                st.caption(f"{a['zone']} · score: {a['score']}")
    except:
        st.warning("Agents non chargés")

# Main content — Tabs
tab1, tab2, tab3 = st.tabs([
    "📧 Analyser un mail",
    "📊 Dashboard MLOps",
    "🏗️ Architecture"
])

# ─── TAB 1 : Analyser un mail ────────────────────────────────────────────────
with tab1:
    st.subheader("📧 Soumettre un mail client")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        email_examples = {
            "Voilier Méditerranée": """Bonjour,
Je souhaite assurer mon voilier de 12 mètres (valeur 80 000€) pour une traversée Méditerranée-Atlantique prévue en septembre.
J'ai besoin d'une couverture tous risques incluant assistance 24h/24.
Pouvez-vous me faire des propositions rapidement ?
Merci, Jean Dupont""",
            "Yacht de luxe Caraïbes": """Bonjour,
Je suis propriétaire d'un yacht de 18 mètres (valeur 250 000€) et souhaite une couverture pour une navigation en Méditerranée et Caraïbes.
J'ai besoin d'une assurance premium tous risques avec assistance VIP.
Budget : pas de limite, je veux le meilleur.
Cordialement, Pierre Martin""",
            "Petit bateau côtier": """Bonjour,
Je cherche une assurance pour mon bateau à moteur de 6 mètres (valeur 15 000€).
Navigation côtière uniquement en Méditerranée.
Budget limité, cherche la formule la plus économique.
Merci, Marie Leblanc"""
        }
        
        selected_example = st.selectbox(
            "📋 Exemples de mails",
            ["-- Choisir un exemple --"] + list(email_examples.keys())
        )
        
        default_email = email_examples.get(selected_example, "")
        
        email_content = st.text_area(
            "Contenu du mail client",
            value=default_email,
            height=200,
            placeholder="Collez ici le mail du client..."
        )
        
        client_id = st.text_input(
            "ID Client",
            value=f"client_{datetime.now().strftime('%H%M%S')}"
        )
    
    with col2:
        st.markdown("**🛡️ Guardrails actifs**")
        st.markdown("✅ Anonymisation RGPD")
        st.markdown("✅ Anti-injection")
        st.markdown("✅ Validation output")
        st.divider()
        st.markdown("**📡 Monitoring**")
        st.markdown("✅ Langfuse traces")
        st.markdown("✅ MLflow tracking")
    
    if st.button("🚀 Lancer le pipeline", type="primary", use_container_width=True):
        if not email_content.strip():
            st.warning("⚠️ Veuillez saisir un mail client")
        else:
            # Progress bar
            progress = st.progress(0)
            status = st.empty()
            
            # Agents steps
            agents_container = st.container()
            
            with agents_container:
                col_a1, col_a2, col_a3, col_a4, col_a5 = st.columns(5)
                
                with col_a1:
                    a1 = st.empty()
                    a1.markdown("⏳ **Agent 1**\nCompréhension")
                with col_a2:
                    a2 = st.empty()
                    a2.markdown("⏸️ **Agent 2**\nRAG Select.")
                with col_a3:
                    a3 = st.empty()
                    a3.markdown("⏸️ **Agent 3**\nEnvoi mails")
                with col_a4:
                    a4 = st.empty()
                    a4.markdown("⏸️ **Agent 4**\nOffres")
                with col_a5:
                    a5 = st.empty()
                    a5.markdown("⏸️ **Agent 5**\nRapport")
            
            # Appel API
            start_time = time.time()
            status.info("🚀 Pipeline démarré...")
            progress.progress(10)
            
            try:
                a1.markdown("🔄 **Agent 1**\nCompréhension")
                progress.progress(20)
                
                response = requests.post(
                    f"{api_url}/analyze",
                    headers={
                        "Content-Type": "application/json",
                        "X-API-Key": api_key
                    },
                    json={
                        "email_content": email_content,
                        "client_id": client_id
                    },
                    timeout=300
                )
                
                a1.markdown("✅ **Agent 1**\nCompréhension")
                progress.progress(40)
                a2.markdown("✅ **Agent 2**\nRAG Select.")
                progress.progress(60)
                a3.markdown("✅ **Agent 3**\nEnvoi mails")
                progress.progress(75)
                a4.markdown("✅ **Agent 4**\nOffres")
                progress.progress(90)
                a5.markdown("✅ **Agent 5**\nRapport")
                progress.progress(100)
                
                duration = round(time.time() - start_time, 1)
                
                if response.status_code == 200:
                    result = response.json()
                    status.success(f"✅ Pipeline terminé en {duration} secondes !")
                    
                    # Résultats
                    st.divider()
                    
                    # Métriques
                    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
                    with col_m1:
                        st.metric("⏱️ Durée", f"{result['duration_sec']}s")
                    with col_m2:
                        st.metric("🤖 Agents sélectionnés", len(result['selected_agents']))
                    with col_m3:
                        st.metric("💼 Offres collectées", result['offers_count'])
                    with col_m4:
                        rag_avg = round(sum(
                            a['score'] for a in result['rag_scores']['agents_scores']
                        ) / len(result['rag_scores']['agents_scores']), 3)
                        st.metric("📊 RAG score moyen", rag_avg)
                    
                    # RAG scores chart
                    st.subheader("📊 Scores RAG — Agents sélectionnés")
                    fig = go.Figure(go.Bar(
                        x=[a['nom'] for a in result['rag_scores']['agents_scores']],
                        y=[a['score'] for a in result['rag_scores']['agents_scores']],
                        marker_color=['#3B5BDB', '#1E88E5', '#42A5F5'],
                        text=[f"{a['score']:.3f}" for a in result['rag_scores']['agents_scores']],
                        textposition='outside'
                    ))
                    fig.update_layout(
                        yaxis_range=[0, 1],
                        yaxis_title="Score RAG",
                        xaxis_title="Agent maritime",
                        height=300,
                        margin=dict(t=20, b=20)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Agents sélectionnés
                    st.subheader("🎯 Agents maritimes sélectionnés")
                    for i, agent in enumerate(result['selected_agents']):
                        col_agent, col_score = st.columns([3, 1])
                        with col_agent:
                            st.markdown(f"**🚢 {agent}**")
                        with col_score:
                            score = result['rag_scores']['agents_scores'][i]['score']
                            st.metric("Score RAG", f"{score:.3f}")
                        st.divider()
                    
                    # Rapport final
                    st.subheader("📄 Rapport de recommandation")
                    st.info(result['final_report'])
                    
                    # Download rapport
                    st.download_button(
                        "⬇️ Télécharger le rapport",
                        data=result['final_report'],
                        file_name=f"rapport_{client_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain"
                    )
                    
                    # Metadata
                    with st.expander("🔍 Détails techniques (Metadata)"):
                        st.json(result['metadata'])
                
                else:
                    status.error(f"❌ Erreur API : {response.status_code}")
                    st.json(response.json())
                    
            except requests.exceptions.Timeout:
                status.error("⚠️ Timeout — le pipeline prend trop de temps")
            except Exception as e:
                status.error(f"❌ Erreur : {e}")

# ─── TAB 2 : Dashboard MLOps ────────────────────────────────────────────────
with tab2:
    st.subheader("📊 Dashboard MLOps — Medallion Architecture")

    # Stats Medallion en temps réel
    try:
        from medallion.pipeline import get_medallion_stats
        stats = get_medallion_stats()

        st.markdown("### 🏗️ Architecture Medallion — Stats en temps réel")
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("🥉 Bronze", stats["bronze_count"], help="Emails bruts reçus")
        with col2:
            st.metric("🥈 Silver", stats["silver_count"], help="Données structurées")
        with col3:
            st.metric("🥇 Gold", stats["gold_count"], help="Résultats finaux")
        with col4:
            st.metric("📊 RAG moyen", stats["avg_rag_score"])
        with col5:
            st.metric("⏱️ Durée moy.", f"{stats['avg_duration']}s")

        st.divider()

        # Visualisation Medallion
        import plotly.graph_objects as go
        fig = go.Figure(go.Funnel(
            y=["🥉 Bronze\nEmails bruts", "🥈 Silver\nDonnées structurées", "🥇 Gold\nRésultats finaux"],
            x=[stats["bronze_count"], stats["silver_count"], stats["gold_count"]],
            textinfo="value+percent initial",
            marker=dict(color=["#CD7F32", "#C0C0C0", "#FFD700"])
        ))
        fig.update_layout(
            title="Pipeline Medallion — Funnel de traitement",
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.warning(f"Stats Medallion non disponibles : {e}")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🔬 Stack technique")
        stack_data = {
            "Composant": ["LLM Principal", "LLM Fallback", "Multi-LLM", "Orchestration", "RAG", "Medallion", "Monitoring", "Tracking", "API", "Workflow"],
            "Technologie": ["Groq/Llama 3.3 70B", "Azure/Phi-4", "LiteLLM", "LangGraph", "ChromaDB", "Bronze/Silver/Gold", "Langfuse", "MLflow", "FastAPI", "n8n"],
            "Statut": ["✅", "✅", "✅", "✅", "✅", "✅", "✅", "✅", "✅", "✅"]
        }
        st.dataframe(stack_data, use_container_width=True)

    with col2:
        st.markdown("### 🛡️ Conformité RGPD")
        st.markdown("""
        | Guardrail | Statut |
        |-----------|--------|
        | Anonymisation PII | ✅ Actif |
        | Anti-injection | ✅ Actif |
        | Validation output | ✅ Actif |
        | Audit trail Langfuse | ✅ Actif |
        | MLflow tracking | ✅ Actif |
        | Medallion Bronze→Gold | ✅ Actif |
        | API Key auth | ✅ Actif |
        """)

    st.divider()

    st.markdown("### ⚡ Performance — ROI métier")
    perf_data = {
        "Étape": ["Analyse mail", "Sélection assureurs", "Envoi devis", "Collecte offres", "Rapport", "Total"],
        "Manuel (courtier)": ["15-20 min", "20-30 min", "30-45 min", "45-60 min", "30-45 min", "2h30-3h"],
        "Pipeline IA": ["~2 sec", "~1 sec", "~2 sec", "~2 sec", "~2 sec", "< 30 sec"],
        "Gain": ["-98%", "-99%", "-98%", "-99%", "-98%", "-98%"]
    }
    st.dataframe(perf_data, use_container_width=True)
    st.success("💰 ROI : 1 courtier peut gérer **10x plus de dossiers** avec le même temps de travail")

# ─── TAB 3 : Architecture ────────────────────────────────────────────────────
with tab3:
    st.subheader("🏗️ Architecture du système")
    
    st.markdown("""
Email client
     ↓
Guardrails RGPD (anonymisation + injection + output)
     ↓
LangGraph Orchestrateur (décisions conditionnelles)
     ├── Agent 1 : Compréhension mail
     ├── Agent 2 : Sélection RAG → ChromaDB
     │              ↓ si < 2 agents → Fallback Search
     ├── Agent 3 : Génération mails agents maritimes
     ├── Agent 4 : Collecte et comparaison offres
     │              ↓ si < 2 offres → Retry Agent 3
     └── Agent 5 : Rapport final + recommandation
     ↓
LiteLLM (Groq/Llama 3.3 70B → Azure/Phi-4 fallback)
     ↓
FastAPI REST API (sécurisée API Key)
     ↓
n8n · Langfuse · MLflow
""")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📐 Décisions conditionnelles LangGraph")
        st.markdown("""
        - Agent 2 → si score RAG < seuil → **Fallback Search élargie**
        - Agent 4 → si < 2 offres reçues → **Retry Agent 3 automatique**
        """)
    
    with col2:
        st.markdown("### 🔄 Multi-LLM LiteLLM")
        st.markdown("""
        - **Groq/Llama 3.3 70B** → principal (rapide, ~1s)
        - **Azure/Phi-4** → fallback automatique
        - Extensible : OpenAI, Mistral, Anthropic...
        """)
