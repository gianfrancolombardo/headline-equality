import streamlit as st

from scripts.headline_analyzer import HeadlineAnalyzer
from scripts.headline_main import HeadlineMain

if 'manager' in st.session_state:
    manager = st.session_state.manager

if 'progress_bars' not in st.session_state:
    st.session_state.progress_bars = {}

st.title("🔍 Analyze headlines and save")

with st.form("year_page_form"):
    medias_source = st.session_state.config.get('medias')
    media = st.text_area("URL", "\n".join(medias_source), height=200)
    submit_button = st.form_submit_button("Analyze headline")

    if submit_button:

        with st.status(f"Scanning medias and analyze headline...", expanded=True) as status:
            analyzer = HeadlineAnalyzer()
            
            analysis_manager = HeadlineMain(st.session_state.config, manager, analyzer)
            
            def progress_callback(current, total, url):
                if not current:
                    st.write(f"Fetching headline from {url}")
                    st.session_state.progress_bars[url] = st.progress(0.0)
                else:
                    progress = current / total
                    st.session_state.progress_bars[url].progress(progress, text=f"Processing link {current}/{total}")
            
            medias = media.split('\n')
            results = analysis_manager.analyze_headlines(medias, progress_callback)
            
            status.update(label=f"{len(results)} headlines analyzed and saved!", state="complete", expanded=True)