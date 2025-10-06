from flask import Flask, request, jsonify, render_template
import requests

app = Flask(__name__)

# --- Function to get the speed limit using Overpass API ---
def get_speed_limit(lat, lon):
    """
    Try to get a UK speed limit near (lat, lon).
    1) Look for a nearby way (<= 150m) with maxspeed.
    2) If missing, look for 'maxspeed:type' or 'zone:maxspeed'.
    3) If still missing, infer a sensible default and label it '(inferred)'.
    """

    OVERPASS_PRIMARY = "https://overpass-api.de/api/interpreter"
    OVERPASS_FALLBACK = "https://overpass.kumi.systems/api/interpreter"

    def query_overpass(url, query):
        """Helper to call Overpass API safely with timeout and fallback"""
        try:
            r = requests.get(
                url,
                params={"data": query},
                headers={"User-Agent": "NelsonSpeedFinder/1.0"},
                timeout=20
            )
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"Overpass error from {url}: {e}")
            return None

    # 1️⃣ Try to fetch a way that explicitly has maxspeed
    query_with_maxspeed = f"""
    [out:json][timeout:25];
    way(around:150,{lat},{lon})["highway"]["maxspeed"];
    out tags center;
    """

    data = query_overpass(OVERPASS_PRIMARY, query_with_maxspeed) or query_overpass(OVERPASS_FALLBACK, query_with_maxspeed)
    if data and data.get("elements"):
        tags = data["elements"][0].get("tags", {})
        ms = tags.get("maxspeed")
        if ms:
            return ms  # e.g. "30", "30 mph", "20", etc.

    # 2️⃣ No explicit maxspeed → fetch nearest highway and inspect other tags
    query_any_highway = f"""
    [out:json][timeout:25];
    way(around:150,{lat},{lon})["highway"];
    out tags center 1;
    """

    data2 = query_overpass(OVERPASS_PRIMARY, query_any_highway) or query_overpass(OVERPASS_FALLBACK, query_any_highway)
    if data2 and data2.get("elements"):
        tags = data2["elements"][0].get("tags", {})
        # Handle UK national speed limit types if present
        ms_type = tags.get("maxspeed:type") or tags.get("source:maxspeed") or ""
        zone_ms = tags.get("zone:maxspeed")

        if "nsl_single" in ms_type:
            return "60 mph (national)"
        if "nsl_dual" in ms_type:
            return "70 mph (national)"
        if zone_ms:
            if "20" in zone_ms:
                return "20 mph (zone)"
            if "30" in zone_ms:
                return "30 mph (zone)"

        # 3️⃣ Infer by highway type (simple + conservative for towns)
        highway = tags.get("highway", "")
        if highway in {"living_street"}:
            return "20 mph (inferred)"
        if highway in {"residential", "service", "unclassified", "tertiary", "secondary", "primary"}:
            return "30 mph (inferred)"
        if highway == "motorway":
            return "70 mph (inferred)"

    # 4️⃣ If all else fails
    return None


# --- Home page route ---
@app.route("/")
def home():
    return render_template("index.html")


# --- Lookup route ---
@app.route("/lookup")
def lookup():
    street = request.args.get("street")
    if not street:
        return jsonify({"error": "Please provide a street name using ?street="}), 400

    # Use OpenStreetMap Nominatim API to find coordinates
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": f"{street}, Nelson, Lancashire, UK",
        "format": "json",
        "limit": 1
    }

    response = requests.get(url, params=params, headers={"User-Agent": "NelsonSpeedFinder/1.0"}, timeout=20)
    data = response.json()

    if not data:
        return jsonify({"message": "Street not found."}), 404

    result = data[0]
    lat = float(result["lat"])
    lon = float(result["lon"])
    speed_limit = get_speed_limit(lat, lon)

    return jsonify({
        "street": street,
        "display_name": result["display_name"],
        "latitude": result["lat"],
        "longitude": result["lon"],
        "speed_limit": speed_limit
    })


import json
from math import radians, sin, cos, sqrt, atan2

def haversine_distance(lat1, lon1, lat2, lon2):
    """Return distance in meters between two lat/lon points."""
    R = 6371000  # Earth radius in meters
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


@app.route("/cameras")
def cameras():
    """Return all cameras within 400 m of the given coordinates."""
    try:
        lat = float(request.args.get("lat"))
        lon = float(request.args.get("lon"))
    except (TypeError, ValueError):
        return jsonify({"error": "Provide lat and lon parameters"}), 400

    with open("static/cameras.json", "r") as f:
        cameras = json.load(f)

    nearby = []
    for cam in cameras:
        dist = haversine_distance(lat, lon, cam["lat"], cam["lon"])
        if dist <= 400:  # within 400 m radius
            cam_with_dist = dict(cam)
            cam_with_dist["distance_m"] = round(dist, 1)
            nearby.append(cam_with_dist)

    return jsonify(nearby)


# --- Run the app ---
if __name__ == "__main__":
    app.run(debug=True)
