import math
import requests

# ── UK Cinema Database ──────────────────────────────────────────────────────
# Add or remove entries here as needed.
CINEMAS = [
    # ── ODEON ──
    {"name": "Odeon Liverpool ONE",        "chain": "Odeon",    "city": "Liverpool",      "lat": 53.4033, "lng": -2.9862, "ticket_url": "https://www.odeon.co.uk/cinemas/liverpool-liverpool-one/"},
    {"name": "Odeon Manchester Great Northern","chain":"Odeon", "city": "Manchester",     "lat": 53.4773, "lng": -2.2507, "ticket_url": "https://www.odeon.co.uk/cinemas/manchester-great-northern/"},
    {"name": "Odeon Birmingham",           "chain": "Odeon",    "city": "Birmingham",     "lat": 52.4778, "lng": -1.8985, "ticket_url": "https://www.odeon.co.uk/cinemas/birmingham/"},
    {"name": "Odeon Leeds",                "chain": "Odeon",    "city": "Leeds",          "lat": 53.7974, "lng": -1.5461, "ticket_url": "https://www.odeon.co.uk/cinemas/leeds/"},
    {"name": "Odeon Sheffield",            "chain": "Odeon",    "city": "Sheffield",      "lat": 53.3811, "lng": -1.4701, "ticket_url": "https://www.odeon.co.uk/cinemas/sheffield/"},
    {"name": "Odeon Leicester Square",     "chain": "Odeon",    "city": "London",         "lat": 51.5107, "lng": -0.1297, "ticket_url": "https://www.odeon.co.uk/cinemas/london-leicester-square/"},
    {"name": "Odeon Luxe Glasgow",         "chain": "Odeon",    "city": "Glasgow",        "lat": 55.8609, "lng": -4.2525, "ticket_url": "https://www.odeon.co.uk/cinemas/glasgow/"},
    {"name": "Odeon Cardiff",              "chain": "Odeon",    "city": "Cardiff",        "lat": 51.4816, "lng": -3.1791, "ticket_url": "https://www.odeon.co.uk/cinemas/cardiff/"},
    {"name": "Odeon Nottingham",           "chain": "Odeon",    "city": "Nottingham",     "lat": 52.9541, "lng": -1.1563, "ticket_url": "https://www.odeon.co.uk/cinemas/nottingham/"},
    {"name": "Odeon Bristol",              "chain": "Odeon",    "city": "Bristol",        "lat": 51.4545, "lng": -2.5879, "ticket_url": "https://www.odeon.co.uk/cinemas/bristol/"},

    # ── VUE ──
    {"name": "Vue Liverpool",              "chain": "Vue",      "city": "Liverpool",      "lat": 53.4084, "lng": -2.9784, "ticket_url": "https://www.myvue.com/cinema/liverpool"},
    {"name": "Vue Manchester Printworks",  "chain": "Vue",      "city": "Manchester",     "lat": 53.4847, "lng": -2.2370, "ticket_url": "https://www.myvue.com/cinema/manchester-printworks"},
    {"name": "Vue Birmingham Star City",   "chain": "Vue",      "city": "Birmingham",     "lat": 52.4962, "lng": -1.8594, "ticket_url": "https://www.myvue.com/cinema/birmingham-star-city"},
    {"name": "Vue Leeds",                  "chain": "Vue",      "city": "Leeds",          "lat": 53.7930, "lng": -1.5490, "ticket_url": "https://www.myvue.com/cinema/leeds"},
    {"name": "Vue London Islington",       "chain": "Vue",      "city": "London",         "lat": 51.5362, "lng": -0.1033, "ticket_url": "https://www.myvue.com/cinema/london-islington"},
    {"name": "Vue Edinburgh",              "chain": "Vue",      "city": "Edinburgh",      "lat": 55.9440, "lng": -3.1725, "ticket_url": "https://www.myvue.com/cinema/edinburgh"},
    {"name": "Vue Bristol",                "chain": "Vue",      "city": "Bristol",        "lat": 51.4600, "lng": -2.6010, "ticket_url": "https://www.myvue.com/cinema/bristol"},
    {"name": "Vue Sheffield",              "chain": "Vue",      "city": "Sheffield",      "lat": 53.3784, "lng": -1.4743, "ticket_url": "https://www.myvue.com/cinema/sheffield"},
    {"name": "Vue Newcastle",              "chain": "Vue",      "city": "Newcastle",      "lat": 54.9680, "lng": -1.6150, "ticket_url": "https://www.myvue.com/cinema/newcastle"},
    {"name": "Vue Nottingham",             "chain": "Vue",      "city": "Nottingham",     "lat": 52.9490, "lng": -1.1440, "ticket_url": "https://www.myvue.com/cinema/nottingham"},

    # ── CINEWORLD ──
    {"name": "Cineworld Liverpool",        "chain": "Cineworld","city": "Liverpool",      "lat": 53.4095, "lng": -2.9772, "ticket_url": "https://www.cineworld.co.uk/cinemas/liverpool"},
    {"name": "Cineworld Manchester",       "chain": "Cineworld","city": "Manchester",     "lat": 53.4731, "lng": -2.2913, "ticket_url": "https://www.cineworld.co.uk/cinemas/manchester-the-lowry"},
    {"name": "Cineworld Birmingham NEC",   "chain": "Cineworld","city": "Birmingham",     "lat": 52.4521, "lng": -1.7310, "ticket_url": "https://www.cineworld.co.uk/cinemas/birmingham-nec"},
    {"name": "Cineworld London O2",        "chain": "Cineworld","city": "London",         "lat": 51.5030, "lng":  0.0030, "ticket_url": "https://www.cineworld.co.uk/cinemas/london-the-o2"},
    {"name": "Cineworld Glasgow",          "chain": "Cineworld","city": "Glasgow",        "lat": 55.8512, "lng": -4.2757, "ticket_url": "https://www.cineworld.co.uk/cinemas/glasgow"},
    {"name": "Cineworld Edinburgh",        "chain": "Cineworld","city": "Edinburgh",      "lat": 55.9415, "lng": -3.2157, "ticket_url": "https://www.cineworld.co.uk/cinemas/edinburgh"},
    {"name": "Cineworld Cardiff",          "chain": "Cineworld","city": "Cardiff",        "lat": 51.4772, "lng": -3.1697, "ticket_url": "https://www.cineworld.co.uk/cinemas/cardiff"},
    {"name": "Cineworld Leeds",            "chain": "Cineworld","city": "Leeds",          "lat": 53.8008, "lng": -1.5491, "ticket_url": "https://www.cineworld.co.uk/cinemas/leeds"},
    {"name": "Cineworld Sheffield",        "chain": "Cineworld","city": "Sheffield",      "lat": 53.3840, "lng": -1.4760, "ticket_url": "https://www.cineworld.co.uk/cinemas/sheffield"},
    {"name": "Cineworld Bristol",          "chain": "Cineworld","city": "Bristol",        "lat": 51.4490, "lng": -2.5810, "ticket_url": "https://www.cineworld.co.uk/cinemas/bristol"},

    # ── PICTUREHOUSE ──
    {"name": "Picturehouse Liverpool FACT","chain": "Picturehouse","city": "Liverpool",   "lat": 53.3990, "lng": -2.9750, "ticket_url": "https://www.picturehouses.com/cinema/fact-liverpool"},
    {"name": "Picturehouse Edinburgh Cameo","chain":"Picturehouse","city": "Edinburgh",   "lat": 55.9390, "lng": -3.2010, "ticket_url": "https://www.picturehouses.com/cinema/cameo-picturehouse"},
    {"name": "Picturehouse Central London","chain": "Picturehouse","city": "London",      "lat": 51.5101, "lng": -0.1340, "ticket_url": "https://www.picturehouses.com/cinema/picturehouse-central"},
    {"name": "Picturehouse Cambridge",     "chain": "Picturehouse","city": "Cambridge",   "lat": 52.2045, "lng":  0.1218, "ticket_url": "https://www.picturehouses.com/cinema/cambridge-picturehouse"},
    {"name": "Picturehouse Brighton Duke's","chain":"Picturehouse","city": "Brighton",    "lat": 50.8210, "lng": -0.1370, "ticket_url": "https://www.picturehouses.com/cinema/dukes-at-komedia"},
]

# Chain colour mapping for badges
CHAIN_COLOURS = {
    "Odeon":       "#e63946",
    "Vue":         "#1d3557",
    "Cineworld":   "#e76f51",
    "Picturehouse":"#2a9d8f",
}

# ── Haversine distance (miles) ───────────────────────────────────────────────
def _haversine(lat1, lng1, lat2, lng2):
    R = 3958.8  # Earth radius in miles
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
    return R * 2 * math.asin(math.sqrt(a))


# ── Postcode / city → coordinates ───────────────────────────────────────────
def _geocode_uk(location: str):
    """
    Try postcodes.io first (works for UK postcodes).
    Fall back to Nominatim (OpenStreetMap) for city names.
    Returns (lat, lng, display_name) or raises ValueError.
    """
    loc = location.strip().upper()

    # 1. Try postcodes.io
    try:
        r = requests.get(f"https://api.postcodes.io/postcodes/{loc}", timeout=5)
        if r.status_code == 200:
            res = r.json().get("result", {})
            return res["latitude"], res["longitude"], res.get("admin_district", loc)
    except Exception:
        pass

    # 2. Fall back to Nominatim for city names
    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": location + ", UK", "format": "json", "limit": 1},
            headers={"User-Agent": "Cinescope/1.0"},
            timeout=5,
        )
        results = r.json()
        if results:
            return float(results[0]["lat"]), float(results[0]["lon"]), results[0].get("display_name", location)
    except Exception:
        pass

    raise ValueError(f"Could not find location: {location}")


# ── Public API ───────────────────────────────────────────────────────────────
def find_nearby_cinemas(location: str, radius_miles: float = 15, limit: int = 8):
    """
    Given a UK postcode or city name, return cinemas within `radius_miles`,
    sorted by distance, up to `limit` results.
    Each result includes distance_miles and chain_colour.
    """
    lat, lng, display = _geocode_uk(location)

    results = []
    for cinema in CINEMAS:
        dist = _haversine(lat, lng, cinema["lat"], cinema["lng"])
        if dist <= radius_miles:
            results.append({
                **cinema,
                "distance_miles": round(dist, 1),
                "chain_colour": CHAIN_COLOURS.get(cinema["chain"], "#555"),
            })

    results.sort(key=lambda c: c["distance_miles"])
    return results[:limit], display