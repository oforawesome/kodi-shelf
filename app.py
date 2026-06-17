import streamlit as st
from pages import library, watchlist, find_list, settings

st.set_page_config(
    page_title="Kodi Watchlist",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Global CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --bg: #0d0d0f;
    --surface: #16161a;
    --surface2: #1e1e24;
    --border: #2a2a35;
    --accent: #e8c547;
    --accent2: #e87d47;
    --text: #e8e8f0;
    --muted: #7a7a8c;
    --green: #4caf82;
    --red: #e85d47;
}

html, body, [data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] * {
    color: var(--text) !important;
}

h1, h2, h3 {
    font-family: 'Bebas Neue', sans-serif;
    letter-spacing: 0.05em;
    color: var(--text) !important;
}

.stButton > button {
    background: var(--surface2) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    transition: all 0.1s ease !important;
}

.stButton > button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}

.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div {
    background-color: var(--surface2) !important;
    color: var(--text) !important;
    border-color: var(--border) !important;
    border-radius: 6px !important;
}

[data-testid="stMetric"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 16px !important;
}

.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-radius: 8px !important;
    gap: 4px !important;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--muted) !important;
    font-family: 'DM Sans', sans-serif !important;
    border-radius: 6px !important;
}

.stTabs [aria-selected="true"] {
    background: var(--surface2) !important;
    color: var(--accent) !important;
}

.stDivider {
    border-color: var(--border) !important;
}

::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# Sidebar nav
with st.sidebar:
    st.markdown("""
    <div style='padding: 8px 0 24px 0;'>
        <span style='font-family: Bebas Neue, sans-serif; font-size: 28px; color: #e8c547; letter-spacing: 0.1em;'>🎬 KODI</span>
        <span style='font-family: Bebas Neue, sans-serif; font-size: 28px; letter-spacing: 0.1em;'> SHELF</span>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigate",
        ["📚  Library", "⏱  Watchlist", "🔍  Find List", "⚙️  Settings"],
        label_visibility="collapsed"
    )

# Route to page
if page == "📚  Library":
    library.show()
elif page == "⏱  Watchlist":
    watchlist.show()
elif page == "🔍  Find List":
    find_list.show()
elif page == "⚙️  Settings":
    settings.show()