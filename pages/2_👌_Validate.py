from datetime import datetime
import streamlit as st

from Home import init

from scripts.headline_analyzer import HeadlineAnalyzer
from scripts.headline_manager import Tables
from scripts.webscraper import WebScraper


if 'db' not in st.session_state:
    init()
db = st.session_state.db.client
if 'manager' in st.session_state:
    manager = st.session_state.manager

analyzer_openia = HeadlineAnalyzer(
    temperature=0.2,
    base_url="https://api.openai.com/v1/",
    model="gpt-4o-mini"
)

analyzer_local = HeadlineAnalyzer(
    temperature=0.2,
    model="gemma2-9b",
)


def validate_headlines(news: dict, value: bool):
    #manager.save(news)
    manager.validate(news['id'], value)

def regenerate_headline(news, analyzer, tone):
    try:
        context = st.session_state[f"context_news_{news['id']}"]
        new_refactored = analyzer.regenerate(news['headline'], context, tone)
        news['refactored'] = new_refactored['refactored']
        news['refactored_es'] = new_refactored['refactored_es']
        news['reason'] = new_refactored['reason']
        manager.save(news)
    except Exception as e:
        st.error(f"Error regenerating headline: {e}. Try again later.")
    return news

@st.experimental_dialog("Edit headline generated")
def edit_headline(news):
    edited = st.text_area("Headline refactored", news['refactored_es'], height=200)
    if st.button("Save"):
        news['refactored_es'] = edited
        
        manager.save(news)
        st.rerun()



data_news = (
    db.table(Tables.NEWS)
    .select('*')
    .eq('is_misogynistic', True)
    .is_('validated', None)
    .order("id")
    .execute()
)

st.title(f"👌 Validate headlines ({len(data_news.data)})")

for news in data_news.data[:5]:
    with st.form(key=f"validate_{news['id']}"):
    
        st.subheader(news['headline'])

        col1, col2 = st.columns(2)
        with col1:
            st.write("Refactored")
            st.write(news['refactored_es'])
        with col2:
            st.write("Refactored EN")
            st.write(news['refactored'])

        col3, col4 = st.columns(2)
        with col3:
            st.write("Reason")
            st.write(news['reason'])
        with col4:
            st.write(f"📢 [{news['source']}]({news['url']})")
            st.write(f"📅 {news['created_at'].split('T')[0]}")

        

        col5, col6, col7, col8 = st.columns([2, 1, 1, 1], vertical_alignment="bottom")
        with col5:
            tone = st.selectbox(
                "Select tone",
                    (
                        "Empowering and Inspirational",
                        "Educational and Informative",
                        "Empathetic and Supportive",
                        "Humorous and Light-hearted",
                        "Assertive and Bold",
                        "Reflective and Thought-Provoking",
                        "Optimistic and Hopeful",
                        "Engaging and Conversational"
                    )
                )
        with col6:
            regenerate_button_web = st.form_submit_button("🔄 GPT", use_container_width=True)
        with col7:
            regenerate_button_local = st.form_submit_button("🔄 Local", use_container_width=True)
        with col8:
            edit_button = st.form_submit_button("Edit", use_container_width=True)
        
        if regenerate_button_web:
            news = regenerate_headline(news, analyzer_openia, tone)
            st.rerun()
        if regenerate_button_local:
            news = regenerate_headline(news, analyzer_local, tone)
            st.rerun()

        if edit_button:
            edit_headline(news)

        with st.expander("Context"):
            scraper = WebScraper(news['url'])
            context = scraper.get_context(length=1000)
            st.session_state[f"context_news_{news['id']}"] = context
            st.write(context)
        
        st.divider()

        btn1, btn2, btn3 = st.columns(3)
        with btn1:
            submit_button = st.form_submit_button("Valid", 
                                                use_container_width=True,
                                                on_click=validate_headlines,
                                                args=(news, True,))
        with btn2:
            submit_button = st.form_submit_button("Valid but unuseful", 
                                                use_container_width=True,
                                                on_click=validate_headlines,
                                                args=(news, None,))
        with btn3:
            submit_button = st.form_submit_button("No valid", 
                                                use_container_width=True, 
                                                on_click=validate_headlines,
                                                args=(news, False,),
                                                type="primary")

if len(data_news.data) == 0:
    st.write("No headlines to validate")
    st.balloons()