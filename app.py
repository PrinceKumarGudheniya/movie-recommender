from flask import Flask, request, jsonify, render_template
from recommender import MovieRecommender

app = Flask(__name__)

# Instantiate once at startup so the TF-IDF matrix is only computed once.
recommender = MovieRecommender()


# ── Pages ──────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ── REST API ───────────────────────────────────────────────────────────────────

@app.route("/api/titles")
def api_titles():
    """Return all movie titles for the autocomplete dropdown."""
    return jsonify(recommender.get_all_titles())


@app.route("/api/search")
def api_search():
    """Partial-title search — used by the search box."""
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([])
    return jsonify(recommender.search_movies(query))


@app.route("/api/recommend")
def api_recommend():
    """
    Content-based recommendations for a given movie title.

    Query params:
        title  (str)  – movie title (required)
        n      (int)  – number of results, default 8
    """
    title = request.args.get("title", "").strip()
    n = min(int(request.args.get("n", 8)), 20)

    if not title:
        return jsonify({"error": "title parameter is required"}), 400

    movie = recommender.get_movie_by_title(title)
    if movie is None:
        return jsonify({"error": f"Movie '{title}' not found"}), 404

    recommendations = recommender.get_recommendations(title, top_n=n)
    return jsonify({
        "query_movie": movie,
        "recommendations": recommendations,
        "algorithm": "TF-IDF + Cosine Similarity",
    })


if __name__ == "__main__":
    print("Movie Recommender running at http://127.0.0.1:5000")
    app.run(debug=True, use_reloader=False)
