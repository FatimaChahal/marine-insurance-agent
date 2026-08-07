# Dataset d'évaluation RAG — questions difficiles et variées
EVAL_DATASET = [
    {
        "query": "voilier 80000€ traversée Méditerranée Atlantique assistance 24h",
        "expected_agents": ["Allianz Maritime", "AXA Marine", "Generali Nautique"],
        "ground_truth": "Pour une traversée Méditerranée-Atlantique avec un voilier de 80000€, les assureurs spécialisés hauturier comme Allianz Maritime et AXA Marine sont les plus adaptés."
    },
    {
        "query": "petit bateau moteur 8000€ navigation côtière Méditerranée budget limité",
        "expected_agents": ["MAIF Mer", "April Marine"],
        "ground_truth": "Pour un petit bateau côtier avec budget limité, MAIF Mer et April Marine proposent les formules les plus économiques."
    },
    {
        "query": "yacht luxe 500000€ navigation mondiale équipage professionnel",
        "expected_agents": ["Swiss Life Nautique", "Allianz Maritime"],
        "ground_truth": "Pour un yacht de luxe en navigation mondiale, Swiss Life Nautique est le spécialiste avec des solutions premium sur-mesure."
    },
    {
        "query": "flotte charter 5 bateaux navigation professionnelle Corse",
        "expected_agents": ["Covéa Fleet", "Groupama Maritime"],
        "ground_truth": "Pour une flotte charter professionnelle, Covéa Fleet est spécialisé dans les flottes et le charter professionnel."
    },
    {
        "query": "catamaran tour du monde circumnavigation couverture mondiale",
        "expected_agents": ["Allianz Maritime", "Swiss Life Nautique"],
        "ground_truth": "Pour une circumnavigation, Allianz Maritime couvre le Pacifique et les zones mondiales avec assistance internationale."
    }
]