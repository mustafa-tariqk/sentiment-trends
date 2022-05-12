import streamlit as st
import pandas as pd
import twitter as tpy

st.title("Twitter Sentiment Trend Analysis")

st.text("This app takes a keyword as input and returns the sentiment over time.")
st.text("A histogram of most commonly used words and hashtags is also provided.")

st.text_input("Enter keyword", key="keyword", value="cibc")

keyword = st.session_state.keyword

tweet_time_df, word_labels, word_counts, hashtag_labels, hashtag_counts = tpy.get_timeseries(keyword)

st.line_chart(tweet_time_df)

freq_df = pd.DataFrame({"Count":word_counts}, index = word_labels)
hash_df = pd.DataFrame({"Count":hashtag_counts}, index = hashtag_labels)

st.header("Common words associated with keyword")
st.bar_chart(freq_df.head())

st.header("Hashtags associated with keyword")
st.bar_chart(hash_df.head())

