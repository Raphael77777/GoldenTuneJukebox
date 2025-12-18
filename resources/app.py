import os, time
import requests
from flask import Flask, jsonify, send_from_directory
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder="static")

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("SPOTIFY_REFRESH_TOKEN")

_access_token = None
_access_exp = 0

def get_access_token():
    global _access_token, _access_exp
    now = int(time.time())
    if _access_token and now < _access_exp - 30:
        return _access_token

    r = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": REFRESH_TOKEN,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
        timeout=15,
    )
    r.raise_for_status()
    data = r.json()
    _access_token = data["access_token"]
    _access_exp = now + int(data.get("expires_in", 3600))
    return _access_token

@app.get("/api/now")
def now():
    token = get_access_token()
    h = {"Authorization": f"Bearer {token}"}

    r = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers=h, timeout=15)
    if r.status_code == 204:
        return jsonify({"is_playing": False})

    r.raise_for_status()
    data = r.json()

    item = data.get("item") or {}
    artists = ", ".join([a["name"] for a in item.get("artists", [])])
    images = item.get("album", {}).get("images", [])
    cover = images[0]["url"] if images else None

    return jsonify({
        "is_playing": data.get("is_playing", False),
        "progress_ms": data.get("progress_ms", 0),
        "duration_ms": item.get("duration_ms", 0),
        "name": item.get("name", ""),
        "artists": artists,
        "album": item.get("album", {}).get("name", ""),
        "cover": cover,
        "device": (data.get("device") or {}).get("name", ""),
    })

@app.get("/")
def index():
    return send_from_directory("static", "index.html")

@app.get("/<path:path>")
def static_files(path):
    return send_from_directory("static", path)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8787)
