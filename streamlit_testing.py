import streamlit as st
import pandas as pd
import twitter as tpy
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('dark_background')

st.set_page_config(page_title="Twitter Sentiment Trend Analysis", page_icon="🐦", layout="centered")

st.image("CIBC x Innovation Logo - Simplified Grey.png")
st.title("Twitter Sentiment Trend Analysis")

st.markdown("Type in a keyword and see how people on twitter \
            have felt about it. The higher the point is the more \
            positive the tweet is, the lower the point is the more \
            negative the tweet is.")

st.text_input("Enter keyword", key="keyword", value="cibc")

keyword = st.session_state.keyword

tweet_time_df, word_labels, word_counts, hashtag_labels, hashtag_counts = tpy.get_timeseries(keyword)

# Getting figure object handle (copy and to_numpy are used to get correct array dimensions)
chart = tpy.get_line_chart(tweet_time_df)
st.markdown("\# of Tweets: " + str(tweet_time_df.shape[0]))

st.altair_chart(
    chart.interactive(),
    use_container_width=True
)

freq_df = pd.DataFrame({"Count":word_counts}, index = word_labels)
hash_df = pd.DataFrame({"Count":hashtag_counts}, index = hashtag_labels)

col1, col2 = st.columns(2)
with col1:
    st.header("Associated Keywords")
    st.markdown("The top 10 keywords that are most frequently used in the tweets")
    fig = tpy.get_bar_chart(freq_df.iloc[1:11])
    st.pyplot(fig)

with col2:
    st.header("Associated Hashtags")
    st.markdown("The top 10 hashtags that are most frequently used in the tweets")
    fig = tpy.get_bar_chart(hash_df.iloc[1:11])
    st.pyplot(fig)


