"""
store.py — simple JSON-backed persistence for watchlist, find-list, config
"""
import json
import os
import streamlit as st
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

WATCHLIST_FILE = DATA_DIR / "watchlist.json"
FINDLIST_FILE  = DATA_DIR / "findlist.json"
CONFIG_FILE    = DATA_DIR / "config.json"


def _read(path: Path):
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            pass
    return [] if "list" in path.name else {}


def _write(path: Path, data):
    path.write_text(json.dumps(data, indent=2))


# ── Config ────────────────────────────────────────────────────────────────────

def load_config() -> dict:
    return _read(CONFIG_FILE)


def save_config(cfg: dict):
    _write(CONFIG_FILE, cfg)
    st.session_state["config"] = cfg


# ── Watchlist ─────────────────────────────────────────────────────────────────

def load_watchlist() -> list:
    return _read(WATCHLIST_FILE)


def save_watchlist(items: list):
    _write(WATCHLIST_FILE, items)
    st.session_state["watchlist"] = items


def _kodi_tag(kodi_id: str, add: bool):
    """Add or remove the want-to-watch tag on a Kodi movie."""
    import requests
    if not kodi_id or not kodi_id.startswith("movie_"):
        return  # only movies supported in Kodi tagging
    try:
        movie_id = int(kodi_id.replace("movie_", ""))
        cfg = st.session_state.get("config", {})
        host = cfg.get("kodi_host", "")
        port = cfg.get("kodi_port", 8082)
        user = cfg.get("kodi_user", "")
        passwd = cfg.get("kodi_pass", "")
        if not host:
            return
        tag_action = {"method": "add" if add else "remove", "item": {"tag": "want to watch"}}
        requests.post(
            f"http://{host}:{port}/jsonrpc",
            auth=(user, passwd) if user else None,
            json={"jsonrpc": "2.0", "method": "VideoLibrary.SetMovieDetails",
                  "params": {"movieid": movie_id, "tag": ["want to watch"] if add else []},
                  "id": 1},
            timeout=5
        )
    except Exception:
        pass  # tagging failure should not block watchlist


def add_to_watchlist(item: dict):
    wl = load_watchlist()
    key = item.get("kodi_id") or item.get("title")
    existing_keys = [i.get("kodi_id") or i.get("title") for i in wl]
    if key not in existing_keys:
        wl.append(item)
        save_watchlist(wl)
        _kodi_tag(item.get("kodi_id", ""), add=True)
        return True
    return False


def remove_from_watchlist(key: str):
    wl = load_watchlist()
    item = next((i for i in wl if (i.get("kodi_id") or i.get("title")) == key), None)
    wl = [i for i in wl if (i.get("kodi_id") or i.get("title")) != key]
    save_watchlist(wl)
    if item:
        _kodi_tag(item.get("kodi_id", ""), add=False)


# ── Find list ─────────────────────────────────────────────────────────────────

def load_findlist() -> list:
    return _read(FINDLIST_FILE)


def save_findlist(items: list):
    _write(FINDLIST_FILE, items)
    st.session_state["findlist"] = items


def add_to_findlist(item: dict):
    fl = load_findlist()
    key = item.get("title", "").lower().strip()
    existing = [i.get("title", "").lower().strip() for i in fl]
    if key not in existing:
        fl.append(item)
        save_findlist(fl)
        return True
    return False


def remove_from_findlist(idx: int):
    fl = load_findlist()
    if 0 <= idx < len(fl):
        fl.pop(idx)
        save_findlist(fl)


def mark_found(idx: int):
    fl = load_findlist()
    if 0 <= idx < len(fl):
        fl[idx]["found"] = not fl[idx].get("found", False)
        save_findlist(fl)


# ── Session state boot ────────────────────────────────────────────────────────

def boot_session():
    if "config" not in st.session_state:
        cfg = _load_env_defaults()
        cfg.update(load_config())
        st.session_state["config"] = cfg
    if "watchlist" not in st.session_state:
        st.session_state["watchlist"] = load_watchlist()
    if "findlist" not in st.session_state:
        st.session_state["findlist"] = load_findlist()


# ── .env loader ───────────────────────────────────────────────────────────────

def _load_env_defaults() -> dict:
    """Load config defaults from .env file if present."""
    env_path = Path(__file__).parent / ".env"
    defaults = {}
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            mapping = {
                "KODI_HOST": "kodi_host",
                "KODI_PORT": "kodi_port",
                "KODI_USER": "kodi_user",
                "KODI_PASS": "kodi_pass",
                "TMDB_KEY":  "tmdb_key",
            }
            cfg_key = mapping.get(key.strip())
            if cfg_key:
                val = value.strip()
                if cfg_key == "kodi_port":
                    try:
                        val = int(val)
                    except ValueError:
                        pass
                defaults[cfg_key] = val
    return defaults
