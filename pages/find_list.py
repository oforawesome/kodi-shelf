import streamlit as st
from store import boot_session, load_findlist, add_to_findlist, remove_from_findlist, mark_found
from kodi_client import tmdb_search_any, poster_url

PLACEHOLDER = "https://via.placeholder.com/80x120/1e1e24/7a7a8c?text=?"


def show():
    boot_session()

    st.markdown("# FIND LIST")
    st.markdown(
        "<div style='color:#7a7a8c;font-size:14px;margin-bottom:20px;'>"
        "Movies and shows you want to track down and add to Kodi.</div>",
        unsafe_allow_html=True
    )

    # ── Add new item ──────────────────────────────────────────────────────────
    with st.expander("➕  Add something to find", expanded=False):
        st.markdown("#### Search TMDB or add manually")

        search_col, year_col, type_col = st.columns([3, 1, 1])
        with search_col:
            search_q = st.text_input("Title", placeholder="e.g. Interstellar", key="fl_search")
        with year_col:
            search_year = st.number_input("Year (optional)", min_value=1900, max_value=2030,
                                          value=None, placeholder="Year", key="fl_year")
        with type_col:
            search_type = st.selectbox("Type", ["Auto", "Movie", "TV"], key="fl_type")

        if search_q and st.button("🔍  Search TMDB", key="fl_search_btn"):
            cfg = st.session_state.get("config", {})
            if not cfg.get("tmdb_key"):
                st.warning("Add a TMDB API key in Settings to search.")
            else:
                with st.spinner("Searching..."):
                    if search_type == "Movie":
                        from kodi_client import tmdb_search_movie
                        r = tmdb_search_movie(search_q, search_year)
                        if r:
                            r["_media_type"] = "movie"
                        tmdb_result = r
                    elif search_type == "TV":
                        from kodi_client import tmdb_search_tv
                        r = tmdb_search_tv(search_q, search_year)
                        if r:
                            r["_media_type"] = "tv"
                        tmdb_result = r
                    else:
                        tmdb_result = tmdb_search_any(search_q, search_year)

                if tmdb_result:
                    st.session_state["fl_tmdb_preview"] = tmdb_result
                else:
                    st.warning("Nothing found on TMDB. You can still add it manually below.")
                    st.session_state["fl_tmdb_preview"] = None

        # Preview & confirm
        preview = st.session_state.get("fl_tmdb_preview")
        if preview:
            ptype = preview.get("_media_type", "movie")
            ptitle = preview.get("title") or preview.get("name", "Unknown")
            pyear = (preview.get("release_date") or preview.get("first_air_date") or "")[:4]
            pposter = poster_url(preview.get("poster_path"))
            poverview = preview.get("overview", "")

            pc1, pc2 = st.columns([1, 4])
            with pc1:
                if pposter:
                    st.image(pposter, width=80)
            with pc2:
                st.markdown(f"**{ptitle}** ({pyear})")
                st.markdown(f"*{ptype.upper()}*")
                st.caption(poverview[:200])

            if st.button("✅  Add to Find List", key="fl_confirm_add"):
                item = {
                    "title": ptitle,
                    "year": pyear,
                    "media_type": ptype,
                    "poster": pposter,
                    "overview": poverview[:300],
                    "found": False,
                }
                ok = add_to_findlist(item)
                if ok:
                    st.success(f"Added '{ptitle}'!")
                    st.session_state["fl_tmdb_preview"] = None
                    st.rerun()
                else:
                    st.info("Already on the list.")

        st.markdown("---")
        st.markdown("##### Or add manually")
        mc1, mc2, mc3 = st.columns([3, 1, 1])
        with mc1:
            manual_title = st.text_input("Title", key="fl_manual_title", placeholder="Title")
        with mc2:
            manual_year = st.text_input("Year", key="fl_manual_year", placeholder="2024")
        with mc3:
            manual_type = st.selectbox("Type", ["movie", "tv"], key="fl_manual_type")

        if st.button("Add manually", key="fl_manual_add"):
            if manual_title.strip():
                item = {
                    "title": manual_title.strip(),
                    "year": manual_year.strip(),
                    "media_type": manual_type,
                    "poster": None,
                    "overview": "",
                    "found": False,
                }
                ok = add_to_findlist(item)
                if ok:
                    st.success(f"Added '{manual_title}'!")
                    st.rerun()
                else:
                    st.info("Already on the list.")
            else:
                st.warning("Enter a title.")

    # ── List ──────────────────────────────────────────────────────────────────
    fl = load_findlist()

    if not fl:
        st.info("🔍 Nothing to find yet — add movies or shows using the form above.")
        return

    # Stats
    total = len(fl)
    found_count = sum(1 for i in fl if i.get("found"))
    pending = total - found_count

    c1, c2, c3 = st.columns(3)
    c1.metric("Total", total)
    c2.metric("Still Looking", pending)
    c3.metric("Found ✓", found_count)

    st.markdown("---")

    show_filter = st.radio("Show", ["All", "Still Looking", "Found"], horizontal=True,
                           label_visibility="collapsed", key="fl_filter")

    st.markdown("")

    indexed = list(enumerate(fl))
    if show_filter == "Still Looking":
        indexed = [(i, item) for i, item in indexed if not item.get("found")]
    elif show_filter == "Found":
        indexed = [(i, item) for i, item in indexed if item.get("found")]

    for real_idx, item in indexed:
        poster = item.get("poster") or PLACEHOLDER
        title = item.get("title", "Unknown")
        year = item.get("year", "")
        media_type = item.get("media_type", "movie")
        overview = item.get("overview", "")
        is_found = item.get("found", False)
        type_label = "🎬 MOVIE" if media_type == "movie" else "📺 TV"

        # Use native Streamlit columns for layout
        img_col, info_col, btn_col = st.columns([1, 6, 2])

        with img_col:
            st.image(poster, width=60)

        with info_col:
            title_display = f"~~{title}~~" if is_found else f"**{title}**"
            year_str = f" ({year})" if year else ""
            found_str = " ✓" if is_found else ""
            st.markdown(f"{title_display}{year_str}{found_str}")
            st.caption(f"{type_label}  ·  {overview[:120]}{'...' if len(overview) > 120 else ''}")

        with btn_col:
            found_label = "↩ Unmark" if is_found else "✓ Found!"
            if st.button(found_label, key=f"found_{real_idx}", use_container_width=True):
                mark_found(real_idx)
                st.rerun()
            if st.button("✕ Remove", key=f"fl_rm_{real_idx}", use_container_width=True):
                remove_from_findlist(real_idx)
                st.rerun()

        st.divider()
