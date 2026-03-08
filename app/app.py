import os
import sys

# Ensure the app directory is on the path so 'services' is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, abort, jsonify
from services.tmdb_api import (
    get_trending_movies,
    get_movie_details,
    search_movies,
    get_genres,
)
from services.cinemas import find_nearby_cinemas

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))


@app.context_processor
def inject_globals():
    genres = []
    try:
        genres = get_genres()
    except Exception:
        pass
    from datetime import datetime
    return {"genres": genres, "now": datetime.utcnow, "datetime": datetime}


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
    from datetime import datetime, date
    try:
        movie = get_movie_details(movie_id)
    except Exception:
        abort(404)

    # Work out cinema status from release_date
    cinema_status = "unknown"   # no date info
    release_str = movie.get("release_date", "")
    if release_str:
        try:
            rel = datetime.strptime(release_str, "%Y-%m-%d").date()
            today = date.today()
            days_since = (today - rel).days
            if days_since < 0:
                cinema_status = "coming_soon"      # future
            elif days_since <= 42:
                cinema_status = "in_cinemas"       # released within 6 weeks
            else:
                cinema_status = "left_cinemas"     # older than 6 weeks
        except ValueError:
            pass

    return render_template("movie.html", movie=movie, cinema_status=cinema_status)


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


@app.route("/api/cinemas")
def api_cinemas():
    """GET /api/cinemas?location=Liverpool&radius=15"""
    location = request.args.get("location", "").strip()
    radius = request.args.get("radius", 15, type=float)

    if not location:
        return jsonify({"error": "Please enter a city or postcode."}), 400

    try:
        cinemas, display = find_nearby_cinemas(location, radius_miles=radius)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Something went wrong. Please try again."}), 500

    return jsonify({"location": display, "cinemas": cinemas})


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