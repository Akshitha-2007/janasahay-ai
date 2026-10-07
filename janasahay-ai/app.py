"""JANASAHAY AI - AI-Powered Government Scheme Assistant. Run: streamlit run app.py"""
try:  # newer SQLite for ChromaDB on Streamlit Community Cloud
    __import__("pysqlite3")
    import sys
    sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
except Exception:
    pass

import streamlit as st

st.set_page_config(page_title="JANASAHAY AI", page_icon="🇮🇳", layout="wide", initial_sidebar_state="expanded")

from core import rag, ui, views  # noqa: E402

ui.inject()
st.session_state.setdefault("nav", ui.NAV[0])

with st.sidebar:
    st.markdown('<div class="tricolor"></div><div class="brand">JANASAHAY <span>AI</span></div>'
                '<div style="opacity:.8;font-size:.8rem;margin-bottom:1rem">AI-Powered Government Scheme Assistant</div>',
                unsafe_allow_html=True)
    st.radio("Navigation", ui.NAV, key="nav", label_visibility="collapsed")
    st.divider()
    st.caption("🟢 Gemini connected" if rag.get_secret("GEMINI_API_KEY") else "🟠 Gemini key missing")
    st.caption("Discover the Government Schemes You Deserve.")

try:
    views.PAGES[st.session_state.nav]()
except rag.RagError as err:
    st.error(f"⚠️ {err}")
except Exception as err:
    st.error("Something went wrong while loading this page. Please try again or reload.")
    with st.expander("Technical details"):
        st.exception(err)
