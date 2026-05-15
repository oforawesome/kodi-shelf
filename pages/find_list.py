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
            search_q = st.text_input("Title", placeholder="e.g. Oppenheimer", key="fl_search")
        with year_col:
            search_year = st.number_input("Year (optional)", min_value=1900, max_value=2030,
                                          value=None, placeholder="Year", key="fl_year")
        with type_col:
            search_type = st.selectbox("Type", ["Auto", "Movie", "TV"], key="fl_type")

        tmdb_result = None
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
                st.markdown(f"<span style='font-size:12px;color:#7a7a8c;'>{poverview[:200]}...</span>",
                            unsafe_allow_html=True)

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
        st.markdown("""
        <div style='text-align:center;padding:60px 20px;background:#16161a;
                    border:1px dashed #2a2a35;border-radius:12px;color:#5a5a6c;margin-top:20px;'>
            <div style='font-size:40px;margin-bottom:12px;'>🔍</div>
            <div style='font-family:Bebas Neue,sans-serif;font-size:20px;
                        letter-spacing:0.05em;margin-bottom:8px;'>Nothing to find yet</div>
            <div style='font-size:13px;'>Add movies or shows you want to track down using the form above.</div>
        </div>
        """, unsafe_allow_html=True)
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

    # Filter
    show_filter = st.radio("Show", ["All", "Still Looking", "Found"], horizontal=True,
                           label_visibility="collapsed", key="fl_filter")

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    # Get filtered with real indices
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

        type_colour = "#e8c547" if media_type == "movie" else "#e87d47"
        type_label = "MOVIE" if media_type == "movie" else "TV"
        found_style = "opacity:0.5;" if is_found else ""

        st.markdown(f"""
        <div style='background:#16161a;border:1px solid {"#4caf82" if is_found else "#2a2a35"};
                    border-radius:10px;padding:12px;margin-bottom:8px;
                    display:flex;gap:14px;align-items:flex-start;{found_style}'>
            <img src='{poster}' style='width:60px;height:90px;object-fit:cover;
                 border-radius:6px;flex-shrink:0;'
                 onerror="this.src='{PLACEHOLDER}'" />
            <div style='flex:1;min-width:0;'>
                <div style='display:flex;align-items:center;gap:8px;margin-bottom:4px;flex-wrap:wrap;'>
                    {"<span style='color:#4caf82;font-size:14px;'>✓</span>" if is_found else ""}
                    <span style='font-family:Bebas Neue,sans-serif;font-size:18px;
                                 {"text-decoration:line-through;color:#5a5a6c;" if is_found else ""}'>{title}</span>
                    <span style='background:{type_colour};color:#0d0d0f;font-size:10px;
                                 padding:1px 6px;border-radius:8px;font-weight:600;'>{type_label}</span>
                    {f"<span style='color:#7a7a8c;font-size:12px;'>{year}</span>" if year else ""}
                </div>
                <div style='color:#5a5a6c;font-size:12px;line-height:1.4;
                            overflow:hidden;display:-webkit-box;-webkit-line-clamp:2;
                            -webkit-box-orient:vertical;'>{overview}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        b1, b2, b3 = st.columns([4, 1, 1])
        with b2:
            found_label = "↩ Unmark" if is_found else "✓ Found!"
            if st.button(found_label, key=f"found_{real_idx}", use_container_width=True):
                mark_found(real_idx)
                st.rerun()
        with b3:
            if st.button("✕ Remove", key=f"fl_rm_{real_idx}", use_container_width=True):
                remove_from_findlist(real_idx)
                st.rerun()
