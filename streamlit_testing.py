import streamlit as st
import pandas as pd
import twitter as tpy
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('dark_background')

st.title("Twitter Sentiment Trend Analysis")

st.text("This app takes a keyword as input and returns the sentiment of related tweets over time.")
st.text("The line chart is coded as blue being more positive and red being more negative.")
st.text("Histograms of associated words and hashtags are also provided.")

st.text_input("Enter keyword", key="keyword", value="cibc")

keyword = st.session_state.keyword

tweet_time_df, word_labels, word_counts, hashtag_labels, hashtag_counts = tpy.get_timeseries(keyword)

# Getting figure object handle (copy and to_numpy are used to get correct array dimensions)
fig = tpy.multi_color_plot(tweet_time_df["Sentiment"].copy().to_numpy())
st.pyplot(fig)

freq_df = pd.DataFrame({"":word_counts}, index = word_labels)
hash_df = pd.DataFrame({"":hashtag_counts}, index = hashtag_labels)

col1, col2 = st.columns(2)
with col1:
    st.header("Associated Keywords")
    # st.bar_chart(freq_df.head())
    st.bar_chart(freq_df.iloc[1:6], width=300, height=500)

with col2:
    st.header("Associated Hashtags")
    # st.bar_chart(hash_df.head())
    st.bar_chart(hash_df.iloc[1:6], width=300, height=500)

