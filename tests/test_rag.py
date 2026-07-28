import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from rag.vectorstore import search_agents, get_vectorstore

def test_vectorstore_loaded():
    collection = get_vectorstore()
    assert collection.count() > 0

def test_search_returns_results():
    results = search_agents("voilier Méditerranée", n_results=3)
    assert len(results) == 3

def test_search_has_scores():
    results = search_agents("voilier Atlantique", n_results=2)
    for r in results:
        assert "score" in r
        assert r["score"] > 0

def test_search_has_metadata():
    results = search_agents("assurance maritime luxe", n_results=1)
    assert "nom" in results[0]
    assert "specialite" in results[0]
    assert "zone" in results[0]

def test_search_relevance():
    results = search_agents("yacht luxe Caraïbes", n_results=1)
    assert results[0]["nom"] == "Swiss Life Nautique"