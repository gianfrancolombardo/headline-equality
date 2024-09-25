import datetime
import streamlit as st

from private.index import init

from scripts.headline_analyzer import HeadlineAnalyzer
from scripts.headline_manager import Tables
from scripts.twitterbot import TwitterBot
from scripts.webscraper import WebScraper
from scripts.sources import Sources


if 'db' not in st.session_state:
    init()
db = st.session_state.db.client
if 'manager' in st.session_state:
    manager = st.session_state.manager
if 'config' in st.session_state:
    hashtags = st.session_state.config.get('hashtags')

x_bot = TwitterBot(
    st.session_state.config.get('consumer_key'),
    st.session_state.config.get('consumer_secret'),
    st.session_state.config.get('access_token'),
    st.session_state.config.get('access_token_secret')
)

sources = Sources()

def create_texts(news):
    max_chars = 270 
    # base = f"""#{news['id']}\n🔴 {news['headline']}\n\n🟢 {news['refactored_es']}"""
    base = f"""🔴 {news['headline']}\n\n🟢 {news['refactored_es']}"""

    texts = {
        'base': base,
        'simple': len(base) <= max_chars,
    }

    if len(base) > max_chars:
        texts['base'] = f"""#{news['id']}\n🔴 \"{news['headline']}\""""
        texts['secondary'] = f"""🟢 {news['refactored_es']}"""

    if news['reason'] is not None:
        texts['reason'] = f"🧠 {news['reason']}"

    texts['url'] = f"\n📰 {news['url']}"

    source_username = sources.get_username(news['source'])
    texts['base'] += f"\n{source_username}" if source_username else ""
    
    if len(hashtags) > 0:
        hashtags_text = "" if source_username else "\n"
        for tag in hashtags:
            if len(texts['base']) + len(hashtags_text) + len(tag) + 1 <= (max_chars - 2):
                hashtags_text += f" #{tag}"
            else:
                break
        texts['base'] += hashtags_text

    texts['base'] += "\n👇"

    return texts

def publish(news, tweet_texts):
    main_tweet = x_bot.tweet(tweet_texts['base'])
    last_tweet_id = main_tweet.data['id']

    if 'secondary' in tweet_texts:
        secondary_comment = x_bot.add_comment(last_tweet_id, tweet_texts['secondary'])
        last_tweet_id = secondary_comment.data['id']
    
    if 'reason' in tweet_texts:
        reason_comment = x_bot.add_comment(last_tweet_id, tweet_texts['reason'])
        last_tweet_id = reason_comment.data['id']
    
    if 'url' in tweet_texts:
        url_comment = x_bot.add_comment(last_tweet_id, tweet_texts['url'])
        last_tweet_id = url_comment.data['id']

    news['post_id'] = main_tweet.data['id']
    news['published'] = datetime.datetime.now().isoformat()
    manager.save(news)

    st.toast(f"Headline #{news['id']} published", icon="✅")
    st.rerun()


data_news = (
    db.table(Tables.NEWS)
    .select('*')
    .eq('is_misogynistic', True)
    .eq('validated', True)
    .eq('useful', True)
    .is_('published', 'null')
    .order("id")
    .execute()
)

st.title(f"🚀 Publish on X ({len(data_news.data)})")


for news in data_news.data[:2]:
    with st.form(key=f"publish_{news['id']}"):
        tweet_texts = create_texts(news)

        st.subheader(f"#{news['id']}")

        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Original:**  \n{news['headline']}")

            st.write("Simple tweet:", "🟢" if tweet_texts['simple'] else "🔴", len(tweet_texts['base'])) 
            st.write(f"📢 [{news['source']}]({news['url']})")
        with col2:
            st.write(f"**Refactored:**  \n{news['refactored_es']}")
            st.write(f"**Reason:**  \n{news['reason']}")

        st.divider()

        submit_button = st.form_submit_button("Publish", use_container_width=True)
        if submit_button:
            publish(news, tweet_texts)


if len(data_news.data) == 0:
    st.write("No headlines to publish")
    st.balloons()