import streamlit as st
from store import load_config, save_config, boot_session
from kodi_client import ping_kodi


def show():
    boot_session()
    cfg = st.session_state.get("config", {})

    st.markdown("# SETTINGS")
    st.markdown("---")

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("### Kodi Connection")

        kodi_host = st.text_input(
            "Kodi IP Address",
            value=cfg.get("kodi_host", "192.168.1.100"),
            placeholder="192.168.x.x",
            help="The local IP of your Kodi / piserver box"
        )
        kodi_port = st.number_input(
            "Kodi Port",
            value=int(cfg.get("kodi_port", 8080)),
            min_value=1, max_value=65535,
            help="Default Kodi HTTP port is 8080"
        )
        kodi_user = st.text_input(
            "Username (optional)",
            value=cfg.get("kodi_user", ""),
            placeholder="kodi"
        )
        kodi_pass = st.text_input(
            "Password (optional)",
            value=cfg.get("kodi_pass", ""),
            type="password"
        )

        c1, c2 = st.columns(2)
        with c1:
            if st.button("💾  Save Kodi Settings", use_container_width=True):
                new_cfg = {**cfg,
                    "kodi_host": kodi_host,
                    "kodi_port": kodi_port,
                    "kodi_user": kodi_user,
                    "kodi_pass": kodi_pass,
                }
                save_config(new_cfg)
                st.success("Saved!")
        with c2:
            if st.button("🔌  Test Connection", use_container_width=True):
                # Temporarily apply to session for ping
                st.session_state["config"] = {
                    **cfg,
                    "kodi_host": kodi_host,
                    "kodi_port": kodi_port,
                    "kodi_user": kodi_user,
                    "kodi_pass": kodi_pass,
                }
                with st.spinner("Pinging Kodi..."):
                    ok = ping_kodi()
                if ok:
                    st.success("✅ Kodi is responding!")
                else:
                    st.error("❌ Could not reach Kodi. Check IP, port, and that the web interface is enabled in Kodi settings.")

    with col2:
        st.markdown("### TMDB API")
        st.markdown(
            "Get a free API key at [themoviedb.org](https://www.themoviedb.org/settings/api). "
            "Used for posters and metadata.",
            unsafe_allow_html=False
        )

        tmdb_key = st.text_input(
            "TMDB API Key (v3 auth)",
            value=cfg.get("tmdb_key", ""),
            type="password",
            placeholder="Paste your TMDB API key here"
        )

        if st.button("💾  Save TMDB Key", use_container_width=True):
            new_cfg = {**cfg, "tmdb_key": tmdb_key}
            save_config(new_cfg)
            st.success("Saved!")

        if cfg.get("tmdb_key"):
            st.markdown(
                "<span style='color: #4caf82; font-size: 13px;'>✓ API key configured</span>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                "<span style='color: #7a7a8c; font-size: 13px;'>⚠ No API key — posters won't load</span>",
                unsafe_allow_html=True
            )

        st.markdown("---")
        st.markdown("### Kodi setup tip")
        st.markdown("""
To enable the JSON-RPC web interface in Kodi:

1. **Settings → Services → Control**
2. Enable **Allow remote control via HTTP**
3. Note the port (default 8080)
4. Optionally set a username/password
        """)
