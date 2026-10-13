# 🎬 CineMatch — Content-Based Movie Recommender

A full-stack movie recommendation system powered by **TF-IDF vectorisation** and
**Cosine Similarity**, built with Python, Flask, and a dark-themed web frontend.

---

## How It Works

```
Movie features (genres + cast + director + overview)
        │
        ▼
  Feature "Soup" String
        │
        ▼
  TF-IDF Vectoriser  ──►  Sparse vector per movie  (vocab × movies matrix)
        │
        ▼
  Cosine Similarity Matrix  (n_movies × n_movies)
     score = (A · B) / (‖A‖ × ‖B‖)
        │
        ▼
  Top-N most similar movies  →  Returned as recommendations
```

- **Genres and director** are repeated in the soup string to give them higher
  TF-IDF weight compared to the longer free-text overview.
- **Bigrams** are included (`ngram_range=(1,2)`) so phrases like `"science fiction"`
  or `"dark knight"` are captured as single features.
- The full **cosine similarity matrix** is pre-computed at startup so every
  `/api/recommend` request is an O(1) lookup.

---

## Project Structure

```
movie-recommender/
├── app.py               ← Flask REST API + page routes
├── recommender.py       ← TF-IDF + cosine similarity engine
├── test_recommender.py  ← Smoke tests (no external test runner needed)
├── requirements.txt
├── data/
│   └── movies.csv       ← 50-movie dataset (id, title, genres, cast, director, overview)
├── templates/
│   └── index.html       ← Jinja2 template
└── static/
    ├── style.css        ← Dark-theme CSS
    └── app.js           ← Vanilla JS (search, autocomplete, fetch)
```

---

## Quick Start

```bash
# 1. Install dependencies
cd movie-recommender
pip install -r requirements.txt

# 2. Run the tests (optional but recommended)
python test_recommender.py

# 3. Start the web server
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

---

## REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/titles` | All movie titles (for autocomplete) |
| `GET` | `/api/search?q=<query>` | Partial-title search |
| `GET` | `/api/recommend?title=<title>&n=<N>` | Get N recommendations |

### Example

```
GET /api/recommend?title=Inception&n=5
```

```json
{
  "query_movie": {
    "id": 2,
    "title": "Inception",
    "genres": "action adventure sci-fi",
    "director": "christopher nolan",
    "cast": "leonardo dicaprio joseph gordon-levitt elliot page tom hardy ken watanabe",
    "overview": "A thief who steals corporate secrets..."
  },
  "recommendations": [
    {
      "id": 3,
      "title": "Interstellar",
      "genres": "adventure drama sci-fi",
      "director": "christopher nolan",
      "similarity": 0.6842
    },
    ...
  ],
  "algorithm": "TF-IDF + Cosine Similarity"
}
```

---

## Extending the Dataset

The dataset lives in [`data/movies.csv`](data/movies.csv). Add rows following the
same column structure — the recommender auto-reloads on next server start.

You can also replace the CSV with a larger public dataset (e.g. the
[TMDB 5000 dataset](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata)) by
pointing `MovieRecommender(data_path="...")` at the new file and adjusting column
names in `recommender.py`.
