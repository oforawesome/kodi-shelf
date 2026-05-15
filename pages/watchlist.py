import streamlit as st
from store import boot_session, load_watchlist, save_watchlist, remove_from_watchlist

PLACEHOLDER = "https://via.placeholder.com/80x120/1e1e24/7a7a8c?text=?"


def show():
    boot_session()

    st.markdown("# WATCHLIST")
    st.markdown(
        "<div style='color:#7a7a8c;font-size:14px;margin-bottom:20px;'>"
        "Your queue of things to watch from Kodi. Add titles from the Library.</div>",
        unsafe_allow_html=True
    )

    wl = load_watchlist()

    if not wl:
        st.markdown("""
        <div style='text-align:center;padding:60px 20px;background:#16161a;
                    border:1px dashed #2a2a35;border-radius:12px;color:#5a5a6c;'>
            <div style='font-size:40px;margin-bottom:12px;'>🎬</div>
            <div style='font-family:Bebas Neue,sans-serif;font-size:20px;
                        letter-spacing:0.05em;margin-bottom:8px;'>Watchlist is empty</div>
            <div style='font-size:13px;'>Head to the Library and hit <strong>+ Watchlist</strong> on anything you want to watch.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Stats bar
    movies = sum(1 for i in wl if i.get("media_type") == "movie")
    tv = sum(1 for i in wl if i.get("media_type") == "tv")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total", len(wl))
    c2.metric("Movies", movies)
    c3.metric("TV Shows", tv)

    st.markdown("---")

    # Filter
    filter_type = st.radio(
        "Filter",
        ["All", "Movies", "TV Shows"],
        horizontal=True,
        label_visibility="collapsed"
    )

    filtered = wl
    if filter_type == "Movies":
        filtered = [i for i in wl if i.get("media_type") == "movie"]
    elif filter_type == "TV Shows":
        filtered = [i for i in wl if i.get("media_type") == "tv"]

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    # List view
    for idx, item in enumerate(filtered):
        # Find real index in wl for removal
        real_key = item.get("kodi_id") or item.get("title")

        poster = item.get("poster") or PLACEHOLDER
        title = item.get("title", "Unknown")
        year = item.get("year", "")
        media_type = item.get("media_type", "movie")
        genres = item.get("genres", "")
        plot = item.get("plot", "")
        rating = item.get("rating", 0)

        type_colour = "#e8c547" if media_type == "movie" else "#e87d47"
        type_label = "MOVIE" if media_type == "movie" else "TV"

        with st.container():
            st.markdown(f"""
            <div style='background:#16161a;border:1px solid #2a2a35;border-radius:10px;
                        padding:12px;margin-bottom:8px;display:flex;gap:14px;align-items:flex-start;'>
                <img src='{poster}' style='width:60px;height:90px;object-fit:cover;
                     border-radius:6px;flex-shrink:0;'
                     onerror="this.src='{PLACEHOLDER}'" />
                <div style='flex:1;min-width:0;'>
                    <div style='display:flex;align-items:center;gap:8px;margin-bottom:4px;flex-wrap:wrap;'>
                        <span style='font-family:Bebas Neue,sans-serif;font-size:18px;'>{title}</span>
                        <span style='background:{type_colour};color:#0d0d0f;font-size:10px;
                                     padding:1px 6px;border-radius:8px;font-weight:600;'>{type_label}</span>
                    </div>
                    <div style='color:#7a7a8c;font-size:12px;margin-bottom:6px;'>{year}{" · " + genres if genres else ""}{" · ★ " + str(round(rating,1)) if rating else ""}</div>
                    <div style='color:#5a5a6c;font-size:12px;line-height:1.4;
                                overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;
                                -webkit-box-orient:vertical;'>{plot}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Position buttons just below the card
            btn_col1, btn_col2, btn_col3 = st.columns([4, 1, 1])
            with btn_col3:
                if st.button("✕ Remove", key=f"rm_{real_key}_{idx}", use_container_width=True):
                    remove_from_watchlist(real_key)
                    st.success(f"Removed '{title}'")
                    st.rerun()

    st.markdown("---")
    if st.button("🗑  Clear entire watchlist", type="secondary"):
        save_watchlist([])
        st.rerun()
