import os
import sys

# Ensure the app directory is on the path so 'services' is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, abort
from services.tmdb_api import (
    get_trending_movies,
    get_movie_details,
    search_movies,
    get_genres,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))


@app.context_processor
def inject_globals():
    genres = []
    try:
        genres = get_genres()
    except Exception:
        pass
    return {"genres": genres}


@app.route("/")
def index():
    page = request.args.get("page", 1, type=int)
    window = request.args.get("window", "week")
    if window not in ("day", "week"):
        window = "week"
    try:
        data = get_trending_movies(time_window=window, page=page)
    except Exception as e:
        return render_template("error.html", message=str(e)), 500
    return render_template(
        "index.html",
        movies=data.get("results", []),
        page=page,
        total_pages=min(data.get("total_pages", 1), 500),
        window=window,
    )


@app.route("/movie/<int:movie_id>")
def movie_detail(movie_id):
    try:
        movie = get_movie_details(movie_id)
    except Exception as e:
        abort(404)
    return render_template("movie.html", movie=movie)


@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)
    if not query:
        return render_template("search.html", movies=[], query="", page=1, total_pages=1)
    try:
        data = search_movies(query=query, page=page)
    except Exception as e:
        return render_template("error.html", message=str(e)), 500
    return render_template(
        "search.html",
        movies=data.get("results", []),
        query=query,
        page=page,
        total_pages=min(data.get("total_pages", 1), 500),
    )


@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", message="Page not found."), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", message="Something went wrong."), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)