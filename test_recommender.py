"""
Quick smoke-test for the recommender engine.
Run with:  python test_recommender.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from recommender import MovieRecommender


def test_basic():
    rec = MovieRecommender()

    # ── Test 1: known title returns results ──────────────────────────
    results = rec.get_recommendations("Inception")
    assert len(results) > 0, "Expected at least one recommendation"
    print(f"[PASS] get_recommendations('Inception') → {len(results)} results")

    # ── Test 2: similarity scores are in [0, 1] ──────────────────────
    for r in results:
        assert 0.0 <= r["similarity"] <= 1.0, f"Bad similarity: {r['similarity']}"
    print("[PASS] All similarity scores in [0, 1]")

    # ── Test 3: the query movie is NOT in its own recommendations ────
    titles = [r["title"] for r in results]
    assert "Inception" not in titles, "Query movie should not appear in results"
    print("[PASS] Query movie excluded from recommendations")

    # ── Test 4: unknown title returns empty list ─────────────────────
    empty = rec.get_recommendations("NonExistentMovie12345")
    assert empty == [], "Unknown title should return []"
    print("[PASS] Unknown title returns []")

    # ── Test 5: search works ─────────────────────────────────────────
    hits = rec.search_movies("dark")
    assert any("Dark" in h["title"] for h in hits), "Expected 'The Dark Knight' in search"
    print(f"[PASS] search_movies('dark') → {[h['title'] for h in hits]}")

    # ── Test 6: Nolan films cluster together ─────────────────────────
    nolan_recs = rec.get_recommendations("The Dark Knight", top_n=5)
    nolan_directors = [r["director"] for r in nolan_recs]
    assert any("nolan" in d.lower() for d in nolan_directors), \
        "Expected other Nolan films near The Dark Knight"
    print(f"[PASS] Nolan films cluster: {[r['title'] for r in nolan_recs[:3]]}")

    print("\n✅ All tests passed.")


if __name__ == "__main__":
    test_basic()
