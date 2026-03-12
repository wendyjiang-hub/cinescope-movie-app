import os
import sys
from dotenv import load_dotenv
from flask import jsonify
load_dotenv()

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
    from datetime import datetime
    genres = []
    try:
        genres = get_genres()
    except Exception:
        pass
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

    cinema_status = "unknown"
    release_str = movie.get("release_date", "")
    if release_str:
        try:
            rel = datetime.strptime(release_str, "%Y-%m-%d").date()
            today = date.today()
            days_since = (today - rel).days
            if days_since < 0:
                cinema_status = "coming_soon"
            elif days_since <= 42:
                cinema_status = "in_cinemas"
            else:
                cinema_status = "left_cinemas"
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
    import traceback
    location = request.args.get("location", "").strip()
    radius = request.args.get("radius", 15, type=float)

    if not location:
        return jsonify({"error": "Please enter a city or postcode."}), 400

    if not os.environ.get("GOOGLE_MAPS_API_KEY"):
        return jsonify({"error": "Google Maps API key is not configured on the server."}), 500

    try:
        cinemas, display = find_nearby_cinemas(location, radius_miles=radius)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except RuntimeError as e:
        return jsonify({"error": str(e)}), 502
    except Exception as e:
        app.logger.error("Cinema search failed: %s\n%s", e, traceback.format_exc())
        return jsonify({"error": "Search failed: " + str(e)}), 500

    return jsonify({"location": display, "cinemas": cinemas})


@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", message="Page not found."), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", message="Something went wrong."), 500


@app.route('/insights')
def insights():
    """Analytics & scheduling insights page."""
    genre_map = {}
    try:
        genres = get_genres()
        genre_map = {str(g['id']): g['name'] for g in genres}
    except Exception as e:
        app.logger.error('insights: failed to load genres: %s', e)
    return render_template('analytics.html', genre_map=genre_map)


@app.route('/api/analytics-data')
def analytics_data():
    """
    JSON endpoint consumed by the analytics dashboard.
    Returns up to 5 pages of trending movies for richer data.
    Query params:
        time_window  – 'week' (default) or 'day'
    """
    time_window = request.args.get('time_window', 'week')
    if time_window not in ('day', 'week'):
        time_window = 'week'
    movies = []
    try:
        for page in range(1, 6):
            result = get_trending_movies(time_window=time_window, page=page)
            batch = result.get('results', [])
            if not batch:
                break
            movies.extend(batch)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    return jsonify({'movies': movies, 'time_window': time_window})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)