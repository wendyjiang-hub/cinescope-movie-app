import os, sys, traceback
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, render_template, request, abort, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from models import db, User, WatchlistItem
from services.tmdb_api import get_trending_movies, get_movie_details, search_movies, get_genres
from services.cinemas import find_nearby_cinemas

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))

# ── Config ────────────────────────────────────────────────────────────────────
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-me-in-production")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", f"sqlite:///{BASE_DIR}/cinescope.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ── Extensions ────────────────────────────────────────────────────────────────
db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Create tables on first run
with app.app_context():
    db.create_all()


# ── Context processor ─────────────────────────────────────────────────────────
@app.context_processor
def inject_globals():
    genres = []
    try:
        genres = get_genres()
    except Exception:
        pass
    return {"genres": genres, "now": datetime.utcnow, "datetime": datetime}


# ── Main routes ───────────────────────────────────────────────────────────────
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
    from datetime import date
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


@app.route('/insights')
def insights():
    genre_map = {}
    try:
        genres = get_genres()
        genre_map = {str(g['id']): g['name'] for g in genres}
    except Exception as e:
        app.logger.error('insights: failed to load genres: %s', e)
    return render_template('analytics.html', genre_map=genre_map)


@app.route('/api/analytics-data')
def analytics_data():
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


# ── Auth routes ───────────────────────────────────────────────────────────────
@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm  = request.form.get("confirm_password", "")

        error = None
        if not email or not username or not password:
            error = "All fields are required."
        elif password != confirm:
            error = "Passwords do not match."
        elif len(password) < 8:
            error = "Password must be at least 8 characters."
        elif User.query.filter_by(email=email).first():
            error = "An account with that email already exists."
        elif User.query.filter_by(username=username).first():
            error = "That username is already taken."

        if error:
            flash(error, "danger")
            return render_template("register.html")

        user = User(email=email, username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash("Welcome to Cinescope!", "success")
        return redirect(url_for("index"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    if request.method == "POST":
        email    = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user     = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user, remember=request.form.get("remember") == "on")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("index"))

        flash("Invalid email or password.", "danger")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You've been logged out.", "info")
    return redirect(url_for("index"))


# ── Watchlist routes ──────────────────────────────────────────────────────────
@app.route("/watchlist")
@login_required
def watchlist():
    items = current_user.watchlist.order_by(WatchlistItem.added_at.desc()).all()
    return render_template("watchlist.html", items=items)


@app.route("/api/watchlist/toggle", methods=["POST"])
@login_required
def watchlist_toggle():
    data = request.get_json(silent=True) or {}
    tmdb_id = data.get("tmdb_id")
    if not tmdb_id:
        return jsonify({"error": "tmdb_id required"}), 400

    existing = WatchlistItem.query.filter_by(
        user_id=current_user.id, tmdb_id=tmdb_id
    ).first()

    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({"status": "removed", "tmdb_id": tmdb_id})

    try:
        movie = get_movie_details(int(tmdb_id))
    except Exception:
        return jsonify({"error": "Could not fetch movie details"}), 502

    item = WatchlistItem(
        user_id      = current_user.id,
        tmdb_id      = tmdb_id,
        title        = movie.get("title", "Unknown"),
        poster_path  = movie.get("poster_path"),
        release_date = movie.get("release_date"),
        vote_average = movie.get("vote_average"),
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({"status": "added", "tmdb_id": tmdb_id})


@app.route("/api/watchlist/status")
@login_required
def watchlist_status():
    tmdb_id = request.args.get("tmdb_id", type=int)
    if not tmdb_id:
        return jsonify({"error": "tmdb_id required"}), 400
    exists = WatchlistItem.query.filter_by(
        user_id=current_user.id, tmdb_id=tmdb_id
    ).first() is not None
    return jsonify({"in_watchlist": exists, "tmdb_id": tmdb_id})


# ── Error handlers ────────────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return render_template("error.html", message="Page not found."), 404


@app.errorhandler(500)
def server_error(e):
    return render_template("error.html", message="Something went wrong."), 500


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
    app.run(host="0.0.0.0", port=port, debug=debug)