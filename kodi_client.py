"""
kodi_client.py — Kodi JSON-RPC + TMDB metadata helpers
"""
import requests
import streamlit as st
import json
import time
from typing import Optional, Union


# ── Kodi JSON-RPC ─────────────────────────────────────────────────────────────

def _kodi_request(method: str, params: dict) -> Optional[dict]:
    cfg = st.session_state.get("config", {})
    host = str(cfg.get("kodi_host", "192.168.1.100")).strip()
    port = str(cfg.get("kodi_port", "8080")).strip()
    user = cfg.get("kodi_user", "")
    passwd = cfg.get("kodi_pass", "")

    # 1. Build the target URL dynamically based on input type
    if host.startswith("http://") or host.startswith("https://"):
        # If it's a full public web domain (like ngrok), use it directly
        base_url = host.rstrip("/")
    else:
        # If it's a raw local IP, combine it with the port using http
        if port:
            base_url = f"http://{host}:{port}"
        else:
            base_url = f"http://{host}"

    url = f"{base_url}/jsonrpc"
    payload = {"jsonrpc": "2.0", "method": method, "params": params, "id": 1}

    # 2. Add custom headers to skip ngrok browser interstitial alerts
    headers = {
        "Content-Type": "application/json",
        "Ngrok-Skip-Browser-Warning": "true",
        "User-Agent": "Kodi-Shelf-App"
    }

    try:
        auth = (user, passwd) if user else None
        resp = requests.post(url, json=payload, headers=headers, auth=auth, timeout=6)
        resp.raise_for_status()
        data = resp.json()
        if "error" in data:
            st.error(f"Kodi error: {data['error']['message']}")
            return None
        return data.get("result")
    except requests.exceptions.ConnectionError:
        st.error(f"❌ Cannot reach Kodi at {host}{':' + port if port and not host.startswith('http') else ''}. Check your Settings.")
        return None
    except requests.exceptions.Timeout:
        st.error(f"⏱ Kodi timed out at {host}.")
        return None
    except Exception as e:
        st.error(f"Kodi request failed: {e}")
        return None


@st.cache_data(ttl=300)
def get_kodi_movies() -> list[dict]:
    result = _kodi_request("VideoLibrary.GetMovies", {
        "properties": [
            "title", "year", "genre", "rating", "runtime",
            "plot", "thumbnail", "art", "playcount", "dateadded", "file",
            "director", "cast"
        ],
        "sort": {"order": "ascending", "method": "title"}
    })
    if result:
        return result.get("movies", [])
    return []


@st.cache_data(ttl=300)
def get_kodi_tvshows() -> list[dict]:
    result = _kodi_request("VideoLibrary.GetTVShows", {
        "properties": [
            "title", "year", "genre", "rating", "plot",
            "thumbnail", "art", "playcount", "dateadded", "episode",
            "watchedepisodes", "cast"
        ],
        "sort": {"order": "ascending", "method": "title"}
    })
    if result:
        return result.get("tvshows", [])
    return []


def ping_kodi() -> bool:
    result = _kodi_request("JSONRPC.Ping", {})
    return result == "pong"


# ── TMDB ──────────────────────────────────────────────────────────────────────

TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_IMG  = "https://image.tmdb.org/t/p/w300"


def _tmdb_get(endpoint: str, params: dict) -> Optional[dict]:
    cfg = st.session_state.get("config", {})
    api_key = cfg.get("tmdb_key", "")
    if not api_key:
        return None
    params["api_key"] = api_key
    try:
        resp = requests.get(f"{TMDB_BASE}/{endpoint}", params=params, timeout=5)
        if resp.status_code == 401:
            return None  # bad key — handled at call site
        resp.raise_for_status()
        return resp.json()
    except Exception:
        return None


@st.cache_data(ttl=86400, show_spinner=False)
def tmdb_search_movie(title: str, year: Optional[int] = None) -> Optional[dict]:
    params = {"query": title, "include_adult": False}
    if year:
        params["year"] = year
    data = _tmdb_get("search/movie", params)
    if data and data.get("results"):
        return data["results"][0]
    return None


@st.cache_data(ttl=86400, show_spinner=False)
def tmdb_search_tv(title: str, year: Optional[int] = None) -> Optional[dict]:
    params = {"query": title}
    if year:
        params["first_air_date_year"] = year
    data = _tmdb_get("search/tv", params)
    if data and data.get("results"):
        return data["results"][0]
    return None


def extract_kodi_poster(item: dict) -> str:
    """Extract a usable poster URL from Kodi art dict."""
    import urllib.parse
    art = item.get("art", {})
    raw = art.get("poster") or art.get("fanart", "")
    if not raw:
        return ""
    # Strip image:// wrapper and trailing slash
    if raw.startswith("image://"):
        raw = raw[8:]
        if raw.endswith("/"):
            raw = raw[:-1]
    decoded = urllib.parse.unquote(raw)
    # Only return if it's a web URL - local file paths won't work remotely
    if decoded.startswith('http://') or decoded.startswith('https://'):
        return decoded
    return ""


def poster_url(path: Optional[str]) -> Optional[str]:
    if path:
        return f"{TMDB_IMG}{path}"
    return None


@st.cache_data(ttl=86400, show_spinner=False)
def tmdb_search_any(title: str, year: Optional[int] = None) -> Optional[dict]:
    """Try movie first, then TV."""
    result = tmdb_search_movie(title, year)
    if result:
        result["_media_type"] = "movie"
        return result
    result = tmdb_search_tv(title, year)
    if result:
        result["_media_type"] = "tv"
    return result
