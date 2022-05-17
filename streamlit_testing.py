import streamlit as st
import pandas as pd
import twitter as tpy
import numpy as np
import matplotlib.pyplot as plt
# plt.style.use('grayscale')

st.title("Twitter Sentiment Trend Analysis")

st.text("This app takes a keyword as input and returns the sentiment of related tweets over time.")
st.text("A histogram of most commonly used words and hashtags is also provided.")

st.text_input("Enter keyword", key="keyword", value="cibc")

keyword = st.session_state.keyword

tweet_time_df, word_labels, word_counts, hashtag_labels, hashtag_counts = tpy.get_timeseries(keyword)

fig, ax = plt.subplots()
# Needs some work to fill in gaps
# pos_signal = tweet_time_df["Sentiment"].copy()
# neg_signal = tweet_time_df["Sentiment"].copy()
# pos_signal[pos_signal <= 0] = np.nan
# neg_signal[neg_signal > 0] = np.nan
# ax.plot(pos_signal, color='b')
# ax.plot(neg_signal, color='r')
ax.plot(tweet_time_df, color='red')
st.pyplot(fig)

# st.line_chart(tweet_time_df)

freq_df = pd.DataFrame({"Count":word_counts}, index = word_labels)
hash_df = pd.DataFrame({"Count":hashtag_counts}, index = hashtag_labels)

st.header("Common words associated with keyword")
# st.bar_chart(freq_df.head())
st.bar_chart(freq_df.iloc[1:6])

st.header("Hashtags associated with keyword")
# st.bar_chart(hash_df.head())
st.bar_chart(hash_df.iloc[1:6])

