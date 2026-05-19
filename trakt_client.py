"""
trakt_client.py — Trakt API helpers
"""
import requests
import streamlit as st
from typing import Optional

TRAKT_BASE = "https://api.trakt.tv"


def _trakt_get(endpoint: str) -> Optional[list]:
    cfg = st.session_state.get("config", {})
    client_id = cfg.get("trakt_client_id", "")
    username = cfg.get("trakt_username", "")
    if not client_id or not username:
        return None
    try:
        resp = requests.get(
            f"{TRAKT_BASE}/{endpoint}",
            headers={
                "trakt-api-key": client_id,
                "trakt-api-version": "2",
                "Content-Type": "application/json",
            },
            timeout=8
        )
        if resp.status_code == 200:
            return resp.json()
        return None
    except Exception:
        return None


@st.cache_data(ttl=300, show_spinner=False)
def get_trakt_watchlist(username: str, client_id: str) -> list:
    """Fetch Trakt movie and TV show watchlist combined."""
    headers = {
        "trakt-api-key": client_id,
        "trakt-api-version": "2",
        "Content-Type": "application/json",
    }
    results = []
    for media_type in ["movies", "shows"]:
        try:
            resp = requests.get(
                f"{TRAKT_BASE}/users/{username}/watchlist/{media_type}",
                headers=headers,
                timeout=8
            )
            if resp.status_code == 200:
                results.extend(resp.json())
        except Exception:
            pass
    return results


def get_trakt_recommendations(username: str, client_id: str) -> list:
    """Fetch Trakt personalised recommendations."""
    try:
        resp = requests.get(
            f"{TRAKT_BASE}/movies/trending",
            headers={
                "trakt-api-key": client_id,
                "trakt-api-version": "2",
                "Content-Type": "application/json",
            },
            timeout=8
        )
        if resp.status_code == 200:
            return resp.json()[:20]
        return []
    except Exception:
        return []
