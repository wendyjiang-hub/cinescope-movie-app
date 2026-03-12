# 🎬 Cinescope — Movie Discovery App

A cinematic film discovery web application built with **Python**, **Flask**, and the **TMDB API**.<br>
🌐 **Live Demo:**https://cinescope-movie-app.onrender.com/<br>
📂 **GitHub Repository:** https://github.com/yourusername/cinescope-movie-app

---

## Features

- **Trending Films** — Browse daily or weekly trending movies powered by the TMDB API  
- **Film Detail Pages** — View full movie information including synopsis, cast, ratings, trailers, and budget  
- **Search** — Full-text movie search with paginated results  
- **Similar Movies** — Discover related films from any movie detail page  
- **Responsive Design** — Optimized layout for both desktop and mobile devices  

### Cinema Intelligence Dashboard

- **Genre Popularity Analysis** — Visualise the distribution of trending film genres  
- **Rating Distribution Insights** — Understand how trending films are rated by audiences  
- **Popularity vs Quality Analysis** — Compare genre popularity with audience ratings  
- **Trend Prediction** — Estimate which genres are likely to trend next week  
- **Scheduling Recommendations** — Data-driven cinema screening suggestions based on audience behaviour
---

## Project Structure

```
## Project Structure

movie-app/
├── app/
│   ├── app.py                     # Flask application and routes
│   ├── templates/
│   │   ├── base.html              # Shared layout and navigation
│   │   ├── index.html             # Trending movies page
│   │   ├── movie.html             # Movie detail page
│   │   ├── search.html            # Search results page
│   │   ├── analytics.html         # Cinema Intelligence Dashboard
│   │   └── error.html             # Error page
│   │
│   └── services/
│       ├── __init__.py
│       ├── tmdb_api.py            # TMDB API integration
│       └── cinemas.py             # Cinema scheduling / analytics logic
│
├── data/
│   ├── u.data                     # MovieLens ratings dataset (optional)
│   └── u.item                     # MovieLens movie metadata (optional)
│
├── notebooks/
│   └── exploration.ipynb          # Data exploration and analysis
│
├── requirements.txt               # Python dependencies
├── .gitignore
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
