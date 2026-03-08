import os
import requests

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p"
API_KEY = "e6570729c7399ce171a006d51a161e4b"

def _get(endpoint: str, params: dict = None) -> dict:
    """Make a GET request to the TMDB API."""
    if params is None:
        params = {}
    params["api_key"] = API_KEY
    response = requests.get(f"{TMDB_BASE_URL}{endpoint}", params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def get_trending_movies(time_window: str = "week", page: int = 1) -> dict:
    """Fetch trending movies for a given time window ('day' or 'week')."""
    data = _get(f"/trending/movie/{time_window}", {"page": page})
    for movie in data.get("results", []):
        movie["poster_url"] = build_image_url(movie.get("poster_path"), "w500")
        movie["backdrop_url"] = build_image_url(movie.get("backdrop_path"), "w1280")
    return data
print(API_KEY)

def get_movie_details(movie_id: int) -> dict:
    """Fetch full details for a single movie, including credits and videos."""
    movie = _get(f"/movie/{movie_id}", {"append_to_response": "credits,videos,similar"})
    movie["poster_url"] = build_image_url(movie.get("poster_path"), "w500")
    movie["backdrop_url"] = build_image_url(movie.get("backdrop_path"), "original")

    # Extract trailer
    movie["trailer_key"] = None
    for video in movie.get("videos", {}).get("results", []):
        if video.get("type") == "Trailer" and video.get("site") == "YouTube":
            movie["trailer_key"] = video["key"]
            break

    # Process cast
    cast = movie.get("credits", {}).get("cast", [])[:12]
    for member in cast:
        member["profile_url"] = build_image_url(member.get("profile_path"), "w185")
    movie["top_cast"] = cast

    # Process similar movies
    similar = movie.get("similar", {}).get("results", [])[:6]
    for s in similar:
        s["poster_url"] = build_image_url(s.get("poster_path"), "w342")
    movie["similar_movies"] = similar

    return movie


def search_movies(query: str, page: int = 1) -> dict:
    """Search for movies by title."""
    data = _get("/search/movie", {"query": query, "page": page})
    for movie in data.get("results", []):
        movie["poster_url"] = build_image_url(movie.get("poster_path"), "w500")
    return data


def get_genres() -> list:
    """Fetch all movie genre IDs and names."""
    data = _get("/genre/movie/list")
    return data.get("genres", [])


def build_image_url(path: str, size: str = "w500") -> str:
    """Build a full TMDB image URL from a relative path."""
    if not path:
        return None
    return f"{TMDB_IMAGE_BASE}/{size}{path}"
