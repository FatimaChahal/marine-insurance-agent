# Base de connaissance des agents maritimes
# En production : alimentée par de vrais documents PDF/contrats

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