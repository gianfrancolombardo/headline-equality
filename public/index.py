from datetime import datetime
import streamlit as st
import pandas as pd

import os
import sys
# sys.path.append('../')
# sys.path.append('../scripts')

# print(os.path.abspath(os.path.join(os.path.dirname(__file__))))
# print(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# print(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))
from scripts.headline_manager import HeadlineManager, Tables
from scripts.helpers.supabase_db import SupabaseDB

def margin_top(num):
    for _ in range(num):
        st.write("") 

def fetch_news():
    """ Get all news with pagination """
    all_data = []
    limit = 1000
    offset = 0

    while True:
        response = db.table('news').select('*').range(offset, offset + limit - 1).execute()
        
        data_news = response.data
        all_data.extend(data_news)

        if len(data_news) < limit:
            break
        offset += limit
    return all_data

def fetch_metric():
    data_news = fetch_news()
    data_news_df = pd.DataFrame(data_news)

    total_news = len(data_news_df)
    total_news_misogynistic_validated = data_news_df[(data_news_df['is_misogynistic'] == True) & (data_news_df['validated'] == True)].shape[0]

    return (total_news, total_news_misogynistic_validated)

def fetch_validated():
    return (
        db.table(Tables.NEWS)
        .select('*')
        .eq('is_misogynistic', True)
        .is_('validated', True)
        .order("id", desc=True)
        .execute()
    ).data

def main():
    
    data_news = fetch_validated()

    metrics = fetch_metric()

    st.title("📰 Titulares sin machismo")
    st.write("Análisis de titulares con IA para detectar sesgos machistas y misóginos")

    margin_top(3)
    st.subheader("📊 Metricas")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Tituales analizados", value=metrics[0])
    with col2:
        st.metric(label="Tituales machistas", value=metrics[1])
    with col3:
        if metrics[0] > 0:
            percentage = (metrics[1] / metrics[0]) * 100
        else:
            percentage = 0
        st.metric(label="% Titulares machistas", value=f"{percentage:.2f}%")


    margin_top(3)
    st.subheader("🕒 Ultimos titulares")

    for news in data_news:
        # Formatear created_at
        formatted_date = datetime.fromisoformat(news['created_at']).strftime("%d-%m-%Y")
        
        card_content = f"""
        <div style="
            background-color: #1C1C1E; 
            border: 1px solid #333; 
            border-radius: 15px; 
            padding: 25px; 
            margin-bottom: 35px; 
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
            color: #E1E1E6;
        ">
            <h4 style="color: #E1E1E6; margin-bottom: 5px;">{news['headline']}</h4>
            <p style="color: #8E8E93; font-size: 13px; margin: 0;">
                {formatted_date} | <strong>📰</strong> 
                <a href="{news['url']}" target="_blank" style="color: #5AC8FA; text-decoration: none;">{news['source']}</a>
            </p>
            <hr style="border: 1px solid #444; margin: 15px 0;">
            <h5 style="margin-top: 25px;">🟢 {news['refactored_es']}</h5>
            <p style="font-size: 16px; margin-top: 15px;">
                <strong>🧠</strong> {news['reason']}
            </p>
        </div>
        """
        st.markdown(card_content, unsafe_allow_html=True)

def init():
    if 'db' not in st.session_state:
        st.session_state.db = SupabaseDB(
            st.secrets["supabase"]["supabase_url"], 
            st.secrets["supabase"]["supabase_key"])
    if 'manager' not in st.session_state:
        st.session_state.manager = HeadlineManager(
            st.session_state.db)

if __name__ == "__main__":
    init()

    db = st.session_state.db.client

    main()