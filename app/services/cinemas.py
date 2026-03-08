import os
import requests

GOOGLE_API_KEY = os.environ.get("GOOGLE_MAPS_API_KEY", "")
GEOCODE_URL    = "https://maps.googleapis.com/maps/api/geocode/json"
PLACES_URL     = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
DETAILS_URL    = "https://maps.googleapis.com/maps/api/place/details/json"

print(os.environ.get("GOOGLE_MAPS_API_KEY"))
def _miles_to_metres(miles: float) -> int:
    return int(miles * 1609.34)


def _geocode(location: str) -> tuple:
    """Convert a postcode or city name to (lat, lng, display_name)."""
    r = requests.get(GEOCODE_URL, params={
        "address": location + ", UK",
        "key": GOOGLE_API_KEY,
    }, timeout=8)
    r.raise_for_status()
    data = r.json()

    status = data.get("status")
    if status == "REQUEST_DENIED":
        raise RuntimeError(
            "Google API key is invalid or missing. "
            "Check GOOGLE_MAPS_API_KEY and ensure Geocoding API is enabled. "
            f"Google message: {data.get('error_message', 'none')}"
        )
    if status == "OVER_DAILY_LIMIT" or status == "OVER_QUERY_LIMIT":
        raise RuntimeError("Google API quota exceeded. Please try again later.")
    if status != "OK" or not data.get("results"):
        raise ValueError(f"Could not find location '{location}'. Try a different postcode or city name.")

    result  = data["results"][0]
    loc     = result["geometry"]["location"]
    display = result["formatted_address"]
    return loc["lat"], loc["lng"], display


def _nearby_cinemas(lat: float, lng: float, radius_metres: int) -> list:
    """Search Google Places for cinemas near a coordinate."""
    r = requests.get(PLACES_URL, params={
        "location": f"{lat},{lng}",
        "radius":   radius_metres,
        "type":     "movie_theater",
        "key":      GOOGLE_API_KEY,
    }, timeout=8)
    r.raise_for_status()
    data = r.json()

    status = data.get("status")
    if status == "REQUEST_DENIED":
        raise RuntimeError(
            "Google API key is invalid or Places API is not enabled. "
            f"Google message: {data.get('error_message', 'none')}"
        )
    if status not in ("OK", "ZERO_RESULTS"):
        raise RuntimeError(f"Google Places error: {status} — {data.get('error_message', '')}")

    return data.get("results", [])


def _place_details(place_id: str) -> dict:
    """Fetch website + phone for a place."""
    r = requests.get(DETAILS_URL, params={
        "place_id": place_id,
        "fields":   "website,formatted_phone_number,url",
        "key":      GOOGLE_API_KEY,
    }, timeout=8)
    r.raise_for_status()
    return r.json().get("result", {})


def _haversine(lat1, lng1, lat2, lng2) -> float:
    import math
    R = 3958.8
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
    return round(R * 2 * math.asin(math.sqrt(a)), 1)


def _chain_colour(name: str) -> str:
    name_lower = name.lower()
    if "odeon"        in name_lower: return "#e63946"
    if "vue"          in name_lower: return "#1d3557"
    if "cineworld"    in name_lower: return "#e76f51"
    if "picturehouse" in name_lower: return "#2a9d8f"
    if "curzon"       in name_lower: return "#6a4c93"
    if "everyman"     in name_lower: return "#c77dff"
    if "showcase"     in name_lower: return "#f4a261"
    if "empire"       in name_lower: return "#264653"
    return "#888888"


# ── Public API ───────────────────────────────────────────────────────────────

def find_nearby_cinemas(location: str, radius_miles: float = 15, limit: int = 10):
    """
    Search Google Places for cinemas near `location` (postcode or city).
    Returns (list_of_cinemas, display_name_string).
    """
    if not GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_MAPS_API_KEY is not set.")

    lat, lng, display = _geocode(location)
    radius_m = _miles_to_metres(radius_miles)
    places   = _nearby_cinemas(lat, lng, radius_m)

    results = []
    for place in places[:limit]:
        place_lat  = place["geometry"]["location"]["lat"]
        place_lng  = place["geometry"]["location"]["lng"]
        place_id   = place["place_id"]
        name       = place["name"]
        address    = place.get("vicinity", "")
        rating     = place.get("rating")
        distance   = _haversine(lat, lng, place_lat, place_lng)

        # Fetch website for ticket link (one extra call per cinema)
        details    = _place_details(place_id)
        website    = details.get("website")
        maps_url   = details.get("url") or \
                     f"https://www.google.com/maps/place/?q=place_id:{place_id}"
        ticket_url = website if website else maps_url

        results.append({
            "name":           name,
            "address":        address,
            "distance_miles": distance,
            "rating":         rating,
            "ticket_url":     ticket_url,
            "maps_url":       maps_url,
            "chain_colour":   _chain_colour(name),
            "has_website":    bool(website),
        })

    results.sort(key=lambda c: c["distance_miles"])
    return results, display