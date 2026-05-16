import streamlit as st
from store import boot_session, add_to_watchlist, load_watchlist
from kodi_client import get_kodi_movies, get_kodi_tvshows


def sort_title(title: str) -> str:
    """Strip leading articles for sorting."""
    low = title.lower()
    for article in ("the ", "a ", "an "):
        if low.startswith(article):
            return title[len(article):]
    return title


def media_row(item: dict, media_type: str, in_watchlist: bool):
    kodi_id = item.get("movieid") or item.get("tvshowid")
    title = item.get("title", "Unknown")
    year = item.get("year", "")
    playcount = item.get("playcount", 0)
    watched = playcount > 0

    col_title, col_watched, col_btn = st.columns([6, 1, 1])

    with col_title:
        year_str = f" · {year}" if year else ""
        watched_str = " ✓" if watched else ""
        st.markdown(
            f"**{title}**<span style='color:#7a7a8c;font-size:13px;'>{year_str}</span>"
            f"<span style='color:#4caf82;font-size:12px;'>{watched_str}</span>",
            unsafe_allow_html=True
        )

    with col_btn:
        wl_key = f"wl_{media_type}_{kodi_id}"
        if in_watchlist:
            st.markdown("<span style='color:#4caf82;font-size:12px;'>✓</span>", unsafe_allow_html=True)
        else:
            if st.button("＋", key=wl_key, use_container_width=True):
                entry = {
                    "kodi_id": f"{media_type}_{kodi_id}",
                    "title": title,
                    "year": year,
                    "media_type": media_type,
                    "poster": None,
                    "genres": ", ".join(item.get("genre", [])[:3]),
                    "plot": (item.get("plot") or "")[:200],
                    "rating": item.get("rating", 0),
                }
                ok = add_to_watchlist(entry)
                if ok:
                    st.toast(f"Added '{title}'")
                    st.rerun()


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
        col_search, col_filter, col_sort, col_refresh = st.columns([3, 2, 2, 1])
        with col_search:
            search = st.text_input("Search", placeholder="Filter by title…", label_visibility="collapsed")
        with col_filter:
            watched_filter = st.selectbox("Show", ["All", "Unwatched", "Watched"], label_visibility="collapsed")
        with col_sort:
            sort_by = st.selectbox("Sort", ["Title A–Z", "Year (newest)", "Rating"], label_visibility="collapsed")
        with col_refresh:
            if st.button("↻", use_container_width=True, help="Refresh from Kodi"):
                get_kodi_movies.clear()
                st.rerun()

        with st.spinner("Loading from Kodi..."):
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
            if sort_by == "Title A–Z":
                movies = sorted(movies, key=lambda x: sort_title(x.get("title", "")))
            elif sort_by == "Year (newest)":
                movies = sorted(movies, key=lambda x: x.get("year") or 0, reverse=True)
            elif sort_by == "Rating":
                movies = sorted(movies, key=lambda x: x.get("rating") or 0, reverse=True)

            st.markdown(f"<div style='color:#7a7a8c;font-size:13px;margin-bottom:4px;'>{len(movies)} titles</div>", unsafe_allow_html=True)
            st.divider()

            for movie in movies:
                kodi_id = f"movie_{movie.get('movieid')}"
                media_row(movie, "movie", kodi_id in wl_keys)

    with tab_tv:
        col_search2, col_filter2, col_sort2, col_refresh2 = st.columns([3, 2, 2, 1])
        with col_search2:
            search2 = st.text_input("Search", placeholder="Filter by title…", label_visibility="collapsed", key="tv_search")
        with col_filter2:
            watched_filter2 = st.selectbox("Show", ["All", "Unwatched", "Watched"], label_visibility="collapsed", key="tv_filter")
        with col_sort2:
            sort_by2 = st.selectbox("Sort", ["Title A–Z", "Year (newest)", "Rating"], label_visibility="collapsed", key="tv_sort")
        with col_refresh2:
            if st.button("↻", use_container_width=True, key="tv_refresh", help="Refresh from Kodi"):
                get_kodi_tvshows.clear()
                st.rerun()

        with st.spinner("Loading from Kodi..."):
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
            if sort_by2 == "Title A–Z":
                shows = sorted(shows, key=lambda x: sort_title(x.get("title", "")))
            elif sort_by2 == "Year (newest)":
                shows = sorted(shows, key=lambda x: x.get("year") or 0, reverse=True)
            elif sort_by2 == "Rating":
                shows = sorted(shows, key=lambda x: x.get("rating") or 0, reverse=True)

            st.markdown(f"<div style='color:#7a7a8c;font-size:13px;margin-bottom:4px;'>{len(shows)} titles</div>", unsafe_allow_html=True)
            st.divider()

            for show_item in shows:
                kodi_id = f"tv_{show_item.get('tvshowid')}"
                media_row(show_item, "tv", kodi_id in wl_keys)
