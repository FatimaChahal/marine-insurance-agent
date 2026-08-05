# 🎯 Problématique Métier — Marine Insurance Agent

## Contexte

Dans le secteur du courtage d'assurance maritime, les courtiers traitent
**50 à 100 demandes clients par jour**. Chaque demande suit un processus
manuel long et répétitif :

| Étape | Temps moyen (manuel) |
|-------|---------------------|
| Lecture et analyse du mail client | 15-20 min |
| Sélection des assureurs pertinents | 20-30 min |
| Rédaction et envoi des demandes de devis | 30-45 min |
| Collecte et comparaison des offres reçues | 45-60 min |
| Rédaction du rapport de recommandation | 30-45 min |
| **Total par dossier** | **2h30 à 3h** |

## Problèmes identifiés

- **Coût opérationnel élevé** : 2h30 de travail humain par dossier
- **Erreurs humaines** : mauvaise sélection d'assureurs, oublis de critères
- **Conformité RGPD** : données clients sensibles manipulées manuellement
- **Scalabilité nulle** : impossible de traiter plus de dossiers sans recruter
- **Traçabilité insuffisante** : pas d'audit trail des décisions prises

## Solution proposée

Pipeline multi-agents IA qui automatise le processus de bout en bout :

| Étape | Temps avec le pipeline |
|-------|----------------------|
| Analyse mail + extraction besoins | ~2 secondes |
| Sélection assureurs (RAG sémantique) | ~1 seconde |
| Génération et envoi des demandes | ~2 secondes |
| Collecte et comparaison des offres | ~2 secondes |
| Génération du rapport final | ~2 secondes |
| **Total par dossier** | **< 30 secondes** |

## Gains mesurables

- ⏱️ **Réduction du temps de traitement : -98%** (3h → 30 secondes)
- 💰 **Réduction des coûts opérationnels** : 1 courtier peut gérer 10x plus de dossiers
- 🛡️ **Conformité RGPD garantie** : anonymisation automatique des données personnelles
- 📊 **Traçabilité complète** : chaque décision loggée (Langfuse + MLflow)
- 🎯 **Qualité améliorée** : sélection sémantique des assureurs vs sélection manuelle

## Architecture de données — Medallion
Bronze → Emails bruts reçus (données non traitées)
Silver → Emails anonymisés, besoins structurés, assureurs sélectionnés
Gold → Offres comparées, rapport final, métriques qualité

## Conformité réglementaire

- **RGPD** : anonymisation automatique avant traitement LLM
- **AI Act** : traçabilité des décisions IA (audit trail complet)
- **ACPR** : logging de chaque recommandation pour audit régulateur