# 🎬 Kodi Shelf

A Streamlit app to browse your Kodi library, manage a watchlist, and track movies/shows you want to find.

## Features

- **Library** — pulls all movies and TV shows live from Kodi's JSON-RPC API, with TMDB posters
- **Watchlist** — a queue of things on Kodi you intend to watch
- **Find List** — a tracker for things you want to hunt down and add to Kodi
- **Settings** — configure Kodi connection and TMDB API key, stored in `data/config.json`

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Enable Kodi's web interface

In Kodi: **Settings → Services → Control → Allow remote control via HTTP**

Note the IP and port (default 8080).

### 3. Get a TMDB API key (free)

Sign up at https://www.themoviedb.org/settings/api — grab the **v3 auth** API key.

### 4. Run the app

```bash
streamlit run app.py
```

Then go to **Settings** in the sidebar to configure your Kodi IP and TMDB key.

## Data storage

All data lives in `data/`:
- `config.json` — Kodi host/port/credentials and TMDB key
- `watchlist.json` — your watch queue
- `findlist.json` — movies/shows to hunt down

These are plain JSON — easy to back up or edit manually.

## Deploying to Streamlit Cloud

Add your config as secrets in `.streamlit/secrets.toml` if needed, or just fill in Settings after deploy.

The `data/` directory is ephemeral on Streamlit Cloud — consider persisting to a mounted volume or using Streamlit's `st.session_state` with an external store if you want persistence across restarts.
