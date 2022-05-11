import streamlit as st
import pandas as pd
import numpy as np
import twitter as tpy

st.title('Twitter Sentiment Trend Analysis')

st.text('This app takes a keyword as input and returns the sentiment over time.')
st.text('A histogram of most commonly used words and hashtags is also provided.')

st.text_input("Enter keyword", key="keyword", value="cibc")

keyword = st.session_state.keyword

tweet_time_df, word_labels, word_counts, hashtags = tpy.get_timeseries(keyword)

st.line_chart(tweet_time_df)





