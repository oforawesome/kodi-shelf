import streamlit as st
import urllib.parse
from store import boot_session, add_to_watchlist, load_watchlist
from kodi_client import get_kodi_movies, get_kodi_tvshows, tmdb_search_movie, tmdb_search_tv, poster_url

PLACEHOLDER = "https://via.placeholder.com/150x225/1e1e24/7a7a8c?text=No+Poster"


def kodi_image_url(thumb: str, cfg: dict) -> str:
    if not thumb or not thumb.startswith("image://"):
        return ""
    encoded = urllib.parse.quote(thumb, safe="")
    host = cfg.get("kodi_host", "192.168.0.219")
    port = cfg.get("kodi_port", 8082)
    user = cfg.get("kodi_user", "")
    passwd = cfg.get("kodi_pass", "")
    auth = f"{user}:{passwd}@" if user else ""
    return f"http://{auth}{host}:{port}/image/{encoded}"


def get_poster(item: dict, media_type: str, cfg: dict) -> str:
    kodi_thumb = item.get("thumbnail", "")
    if kodi_thumb and kodi_thumb.startswith("image://"):
        return kodi_image_url(kodi_thumb, cfg)
    if cfg.get("tmdb_key"):
        title = item.get("title", "")
        year = item.get("year") or None
        tmdb = None
        if media_type == "movie":
            tmdb = tmdb_search_movie(title, year)
        else:
            tmdb = tmdb_search_tv(title, year)
        if tmdb and tmdb.get("poster_path"):
            return poster_url(tmdb["poster_path"])
    return PLACEHOLDER


def media_card(item: dict, media_type: str, in_watchlist: bool):
    kodi_id = item.get("movieid") or item.get("tvshowid")
    title = item.get("title", "Unknown")
    year = item.get("year", "")
    rating = item.get("rating", 0)
    plot = item.get("plot", "")
    genres = ", ".join(item.get("genre", [])[:2])
    playcount = item.get("playcount", 0)
    watched = playcount > 0
    cfg = st.session_state.get("config", {})

    poster = get_poster(item, media_type, cfg)

    watched_badge = (
        "<span style='background:#4caf82;color:#0d0d0f;font-size:10px;"
        "padding:2px 6px;border-radius:10px;font-weight:600;'>WATCHED</span>"
        if watched else ""
    )
    type_badge = (
        f"<span style='background:{'#e8c547' if media_type=='movie' else '#e87d47'};"
        f"color:#0d0d0f;font-size:10px;padding:2px 6px;border-radius:10px;"
        f"font-weight:600;'>{'MOVIE' if media_type=='movie' else 'TV'}</span>"
    )

    st.markdown(f"""
    <div style='background:#16161a;border:1px solid #2a2a35;border-radius:10px;
                padding:0;overflow:hidden;height:100%;display:flex;flex-direction:column;'>
        <div style='position:relative;'>
            <img src='{poster}' style='width:100%;aspect-ratio:2/3;object-fit:cover;display:block;'
                 onerror="this.src='{PLACEHOLDER}'" />
            <div style='position:absolute;top:8px;left:8px;display:flex;gap:4px;flex-wrap:wrap;'>
                {type_badge} {watched_badge}
            </div>
        </div>
        <div style='padding:10px;flex:1;display:flex;flex-direction:column;gap:4px;'>
            <div style='font-family:Bebas Neue,sans-serif;font-size:16px;
                        line-height:1.2;color:#e8e8f0;'>{title}</div>
            <div style='font-size:12px;color:#7a7a8c;'>{year} · {genres}</div>
            {"<div style='font-size:12px;color:#e8c547;'>★ " + f"{rating:.1f}" + "</div>" if rating else ""}
            <div style='font-size:11px;color:#5a5a6c;margin-top:4px;
                        overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;
                        -webkit-box-orient:vertical;'>{plot}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    wl_key = f"wl_{media_type}_{kodi_id}"
    if in_watchlist:
        st.markdown(
            "<div style='text-align:center;font-size:12px;color:#4caf82;"
            "padding:4px 0;'>✓ In watchlist</div>",
            unsafe_allow_html=True
        )
    else:
        if st.button("+ Watchlist", key=wl_key, use_container_width=True):
            entry = {
                "kodi_id": f"{media_type}_{kodi_id}",
                "title": title,
                "year": year,
                "media_type": media_type,
                "poster": poster,
                "genres": genres,
                "plot": plot[:200] if plot else "",
                "rating": rating,
            }
            ok = add_to_watchlist(entry)
            if ok:
                st.success(f"Added '{title}'")
                st.rerun()
            else:
                st.info("Already in watchlist")


def show():
    boot_session()

    cfg = st.session_state.get("config", {})
    if not cfg.get("kodi_host"):
        st.warning("Configure your Kodi connection in Settings first.")
        return

    st.markdown("# LIBRARY")

    tab_movies, tab_tv = st.tabs(["🎬  Movies", "📺  TV Shows"])

    wl = load_watchlist()
    wl_keys = {i.get("kodi_id") for i in wl}

    with tab_movies:
        col_search, col_filter, col_refresh = st.columns([3, 2, 1])
        with col_search:
            search = st.text_input("Search movies", placeholder="Filter by title…", label_visibility="collapsed")
        with col_filter:
            watched_filter = st.selectbox("Show", ["All", "Unwatched", "Watched"], label_visibility="collapsed")
        with col_refresh:
            if st.button("↻ Refresh", use_container_width=True):
                get_kodi_movies.clear()
                st.rerun()

        with st.spinner("Loading movies from Kodi..."):
            movies = get_kodi_movies()

        if not movies:
            st.info("No movies found. Make sure Kodi is running and the library is scanned.")
        else:
            if search:
                movies = [m for m in movies if search.lower() in m.get("title", "").lower()]
            if watched_filter == "Unwatched":
                movies = [m for m in movies if m.get("playcount", 0) == 0]
            elif watched_filter == "Watched":
                movies = [m for m in movies if m.get("playcount", 0) > 0]

            st.markdown(
                f"<div style='color:#7a7a8c;font-size:13px;margin-bottom:12px;'>{len(movies)} titles</div>",
                unsafe_allow_html=True
            )

            cols = st.columns(5, gap="small")
            for i, movie in enumerate(movies):
                kodi_id = f"movie_{movie.get('movieid')}"
                with cols[i % 5]:
                    media_card(movie, "movie", kodi_id in wl_keys)

    with tab_tv:
        col_search2, col_filter2, col_refresh2 = st.columns([3, 2, 1])
        with col_search2:
            search2 = st.text_input("Search TV", placeholder="Filter by title…", label_visibility="collapsed", key="tv_search")
        with col_filter2:
            watched_filter2 = st.selectbox("Show", ["All", "Unwatched", "Watched"], label_visibility="collapsed", key="tv_filter")
        with col_refresh2:
            if st.button("↻ Refresh", use_container_width=True, key="tv_refresh"):
                get_kodi_tvshows.clear()
                st.rerun()

        with st.spinner("Loading TV shows from Kodi..."):
            shows = get_kodi_tvshows()

        if not shows:
            st.info("No TV shows found.")
        else:
            if search2:
                shows = [s for s in shows if search2.lower() in s.get("title", "").lower()]
            if watched_filter2 == "Unwatched":
                shows = [s for s in shows if s.get("playcount", 0) == 0]
            elif watched_filter2 == "Watched":
                shows = [s for s in shows if s.get("playcount", 0) > 0]

            st.markdown(
                f"<div style='color:#7a7a8c;font-size:13px;margin-bottom:12px;'>{len(shows)} shows</div>",
                unsafe_allow_html=True
            )

            cols = st.columns(5, gap="small")
            for i, show_item in enumerate(shows):
                kodi_id = f"tv_{show_item.get('tvshowid')}"
                with cols[i % 5]:
                    eps = show_item.get("episode", 0)
                    watched_eps = show_item.get("watchedepisodes", 0)
                    if eps:
                        show_item = dict(show_item)
                        show_item["plot"] = (
                            f"{watched_eps}/{eps} episodes watched\n\n"
                            + (show_item.get("plot") or "")
                        )
                    media_card(show_item, "tv", kodi_id in wl_keys)
