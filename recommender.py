import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os


class MovieRecommender:
    """
    Content-Based Movie Recommender using TF-IDF + Cosine Similarity.

    How it works:
    1. A 'soup' of textual features is built for each movie:
       genres + cast + director + overview (weighted by repetition).
    2. TF-IDF transforms each soup into a high-dimensional vector.
    3. Cosine similarity measures the angle between any two movie vectors.
       score = (A · B) / (‖A‖ × ‖B‖)  →  range [0, 1]
    4. The N most similar movies (highest scores) are returned.
    """

    def __init__(self, data_path: str = None):
        if data_path is None:
            data_path = os.path.join(os.path.dirname(__file__), "data", "movies.csv")
        self.df = pd.read_csv(data_path)
        self._preprocess()
        self._build_tfidf()

    # ------------------------------------------------------------------
    # Pre-processing
    # ------------------------------------------------------------------

    def _clean(self, text: str) -> str:
        """Lower-case and strip extra whitespace."""
        if pd.isna(text):
            return ""
        return str(text).lower().strip()

    def _preprocess(self):
        """Build a feature 'soup' string for every movie."""
        for col in ("genres", "cast", "director", "overview"):
            self.df[col] = self.df[col].apply(self._clean)

        # Genres and cast are repeated to give them more weight relative to
        # the longer free-text overview so cosine similarity emphasises them.
        self.df["soup"] = (
            self.df["genres"].str.replace(" ", "_") + " "          # action_crime_drama
            + self.df["genres"].str.replace(" ", "_") + " "        # doubled weight
            + self.df["cast"].str.replace(" ", "_") + " "          # cast names
            + self.df["director"].str.replace(" ", "_") + " "      # director
            + self.df["director"].str.replace(" ", "_") + " "      # doubled weight
            + self.df["overview"]                                   # natural language
        )

    # ------------------------------------------------------------------
    # TF-IDF + Cosine Similarity matrix
    # ------------------------------------------------------------------

    def _build_tfidf(self):
        """Fit TF-IDF on the soup corpus and compute the similarity matrix."""
        tfidf = TfidfVectorizer(
            analyzer="word",
            stop_words="english",
            ngram_range=(1, 2),      # unigrams + bigrams
            min_df=1,
            max_features=10_000,
        )
        tfidf_matrix = tfidf.fit_transform(self.df["soup"])
        # cosine_similarity returns shape (n_movies, n_movies)
        self.cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
        # Map lowercase title → DataFrame index for fast lookup
        self.indices = pd.Series(
            self.df.index.values, index=self.df["title"].str.lower()
        ).drop_duplicates()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_recommendations(self, title: str, top_n: int = 8):
        """
        Return top_n recommended movies for the given title.

        Parameters
        ----------
        title : str   Movie title (case-insensitive).
        top_n : int   Number of recommendations to return.

        Returns
        -------
        list[dict]  Each dict has keys: id, title, genres, director, similarity.
        """
        title_lower = title.lower().strip()
        if title_lower not in self.indices:
            return []

        idx = self.indices[title_lower]
        sim_scores = list(enumerate(self.cosine_sim[idx]))
        # Sort by similarity descending, skip the movie itself (score=1.0)
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = [s for s in sim_scores if s[0] != idx][:top_n]

        results = []
        for movie_idx, score in sim_scores:
            row = self.df.iloc[movie_idx]
            results.append({
                "id": int(row["id"]),
                "title": row["title"],
                "genres": row["genres"],
                "director": row["director"],
                "overview": row["overview"][:180] + "…" if len(row["overview"]) > 180 else row["overview"],
                "similarity": round(float(score), 4),
            })
        return results

    def search_movies(self, query: str):
        """Return movies whose title contains the query string (case-insensitive)."""
        q = query.lower().strip()
        mask = self.df["title"].str.lower().str.contains(q, na=False)
        matches = self.df[mask][["id", "title", "genres", "director"]]
        return matches.to_dict(orient="records")

    def get_all_titles(self):
        """Return all movie titles sorted alphabetically."""
        return sorted(self.df["title"].tolist())

    def get_movie_by_title(self, title: str):
        """Return full detail for a single movie."""
        mask = self.df["title"].str.lower() == title.lower().strip()
        rows = self.df[mask]
        if rows.empty:
            return None
        row = rows.iloc[0]
        return {
            "id": int(row["id"]),
            "title": row["title"],
            "genres": row["genres"],
            "director": row["director"],
            "cast": row["cast"],
            "overview": row["overview"],
        }
