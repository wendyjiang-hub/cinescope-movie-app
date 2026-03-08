# 🎬 Cinescope — Movie Discovery App

A cinematic film discovery web application built with **Python**, **Flask**, and the **TMDB API**.

---

## Features

- **Trending Films** — Browse weekly or daily trending movies
- **Film Detail Pages** — Full synopsis, cast, ratings, trailers, budget, and more
- **Search** — Full-text movie search with pagination
- **Similar Movies** — Discover related films from any detail page
- **Responsive Design** — Works on desktop and mobile

---

## Project Structure

```
movie-app/
├── app/
│   ├── app.py                  # Flask application & routes
│   ├── templates/
│   │   ├── base.html           # Shared layout + nav
│   │   ├── index.html          # Trending movies grid
│   │   ├── movie.html          # Film detail page
│   │   ├── search.html         # Search results
│   │   └── error.html          # Error page
│   └── services/
│       └── tmdb_api.py         # TMDB API wrapper
├── data/
│   ├── u.data                  # MovieLens rating data (optional)
│   └── u.item                  # MovieLens item data (optional)
├── notebooks/
│   └── exploration.ipynb       # Data exploration notebook
├── requirements.txt
├── .env.example
└── README.md
```

---

## Setup

### 1. Get a TMDB API Key

1. Create a free account at [themoviedb.org](https://www.themoviedb.org/)
2. Go to **Settings → API** and request a free API key

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env and add your TMDB_API_KEY
```

### 4. Run the App

```bash
cd app
python app.py
```

Visit `http://localhost:5000` in your browser.

---

## Running in Production

```bash
cd app
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## API Reference

The `services/tmdb_api.py` module exposes:

| Function | Description |
|---|---|
| `get_trending_movies(time_window, page)` | Fetch trending movies (day/week) |
| `get_movie_details(movie_id)` | Full details + cast + trailer + similar |
| `search_movies(query, page)` | Text search |
| `get_genres()` | List all genre IDs and names |
| `build_image_url(path, size)` | Construct TMDB image URL |

---

## Data Files (Optional)

The `data/` folder contains MovieLens 100K dataset files for offline exploration:
- `u.data` — User ratings (user_id, item_id, rating, timestamp)
- `u.item` — Movie metadata (id, title, genres…)

Use `notebooks/exploration.ipynb` to explore collaborative filtering ideas.
