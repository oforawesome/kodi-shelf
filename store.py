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


def add_to_watchlist(item: dict):
    wl = load_watchlist()
    # Avoid dupes by kodi id or title
    key = item.get("kodi_id") or item.get("title")
    existing_keys = [i.get("kodi_id") or i.get("title") for i in wl]
    if key not in existing_keys:
        wl.append(item)
        save_watchlist(wl)
        return True
    return False


def remove_from_watchlist(key: str):
    wl = load_watchlist()
    wl = [i for i in wl if (i.get("kodi_id") or i.get("title")) != key]
    save_watchlist(wl)


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
        st.session_state["config"] = load_config()
    if "watchlist" not in st.session_state:
        st.session_state["watchlist"] = load_watchlist()
    if "findlist" not in st.session_state:
        st.session_state["findlist"] = load_findlist()
