import streamlit as st
import pandas as pd

# Temporal
pd.set_option('future.no_silent_downcasting', True)

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'scripts')))

from scripts.helpers.config import Config
from scripts.helpers.supabase_db import SupabaseDB

from scripts.headline_analyzer import HeadlineAnalyzer
from scripts.headline_manager import HeadlineManager
from scripts.webscraper import WebScraper


def fetch_news(db):
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

def main():
    st.set_page_config(page_title="Headline Equality Backoffice", page_icon=":newspaper:")

    st.title(":newspaper: Headline Equality Backoffice")
    st.write("Headline analyzer with AI to detect bias")

    db = st.session_state.db.client

    data_news = fetch_news(db)

    if len(data_news) > 0:
        data_news_df = pd.DataFrame(data_news)

        total_news = len(data_news_df)
        total_news_misogynistic = data_news_df[data_news_df['is_misogynistic'] == True].shape[0]
        total_news_misogynistic_validated = data_news_df[(data_news_df['is_misogynistic'] == True) & (data_news_df['validated'] == True)].shape[0]

        # General metrics
        st.subheader("Statistics")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Total Headline", value=total_news)
        with col2:
            st.metric(label="Total Misogynistic", value=total_news_misogynistic)
        with col3:
            st.metric(label="Total Validated", value=total_news_misogynistic_validated)

        # Gruped by source
        grouped_by_source = data_news_df.groupby('source').agg(
            total_news=('is_misogynistic', 'size'),
            misogynistic_news=('validated', 'sum')
        )
        grouped_by_source['percentage_misogynistic'] = (grouped_by_source['misogynistic_news'] / grouped_by_source['total_news']) * 100
        grouped_by_source = grouped_by_source.sort_values(by='percentage_misogynistic', ascending=True)

        st.subheader("News misogyinistic by source")
        st.bar_chart(grouped_by_source['percentage_misogynistic'])


        # Metrics by day
        data_news_df['created_at'] = pd.to_datetime(data_news_df['created_at'])
        news_by_day = data_news_df.copy()
        news_by_day['day'] = news_by_day['created_at'].dt.date
        news_by_day['validated'] = news_by_day['validated'].fillna(False).astype(int)
        grouped_by_day = news_by_day.groupby('day').agg(
            total_news=('id', 'size'),
            total_misogynistic=('is_misogynistic', 'sum'),
            total_validated=('validated', 'sum')
        ).reset_index()
        grouped_by_day.columns = ['Day', 'Total Headlines', 'Total Misogynistic', 'Total Validated']
        grouped_by_day['% Misogynistic'] = ((grouped_by_day['Total Misogynistic'] / grouped_by_day['Total Headlines']) * 100).apply(lambda x: f"{x:.1f}")
        grouped_by_day['% Validated'] = ((grouped_by_day['Total Validated'] / grouped_by_day['Total Headlines']) * 100).apply(lambda x: f"{x:.1f}")
        grouped_by_day = grouped_by_day.sort_values(by='Day', ascending=False)

        st.subheader("Metrics by Day")
        st.dataframe(grouped_by_day, use_container_width=True)


        # Published news
        published_news = data_news_df[data_news_df['published'].notnull()].copy()
        st.subheader("Last published tweets")
        published_news['published'] = pd.to_datetime(published_news['published'])
        published_news['published'] = published_news['published'].dt.strftime('%Y-%m-%d %H:%M')
        published_news = published_news.sort_values(by='published', ascending=False)
        published_news = published_news.head(10)
        st.dataframe(published_news[['id', 'published', 'headline']])

def init():
    if 'config' not in st.session_state:
        st.session_state.config = Config(
            '../config.yaml')
    if 'db' not in st.session_state:
        st.session_state.db = SupabaseDB(
            st.session_state.config.get('supabase_url'), 
            st.session_state.config.get('supabase_key'))
    if 'manager' not in st.session_state:
        st.session_state.manager = HeadlineManager(
            st.session_state.db)

if __name__ == "__main__":
    init()
    main()