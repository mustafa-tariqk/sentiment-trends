import streamlit as st
import pandas as pd
import twitter as tpy
import numpy as np
import matplotlib.pyplot as plt
# plt.style.use('dark_background')

st.set_page_config(page_title="Twitter Sentiment Trend Analysis", page_icon="🐦", layout="centered")

st.image("CIBC x Innovation Logo - Simplified Grey.png")
st.title("Twitter Sentiment Trend Analysis")

st.markdown("Type in a keyword and see how people on twitter have felt about it!  \n\
            The higher the point on the graph, the better people feel about the keyword.  \n\
            We also share the most associated words and hashtags below the graph.")


st.text_input("Enter keyword", key="keyword", value="cibc")

keyword = st.session_state.keyword

tweet_time_df, word_labels, word_counts, hashtag_labels, hashtag_counts = tpy.get_timeseries(keyword)

# Getting figure object handle (copy and to_numpy are used to get correct array dimensions)
chart = tpy.get_line_chart(tweet_time_df)

# fig = tpy.multi_color_plot(tweet_time_df["Sentiment"].copy().to_numpy())
# st.pyplot(fig)

st.altair_chart(
    chart.interactive(),
    use_container_width=True
)

# st.line_chart(tweet_time_df["Sentiment"])

freq_df = pd.DataFrame({"Count":word_counts, "Word": word_labels})#, index = word_labels)
hash_df = pd.DataFrame({"Count":hashtag_counts, "Word": hashtag_labels})#, index = hashtag_labels)

col1, col2 = st.columns(2)
with col1:
    st.header("Associated Keywords")
    # st.bar_chart(freq_df.head())
    chart = tpy.get_bar_chart(freq_df.iloc[1:11])

    st.altair_chart(
        chart.interactive(),
        use_container_width=True
    )
    # st.bar_chart(freq_df.iloc[1:11], width=300, height=500)

with col2:
    st.header("Associated Hashtags")
    # st.bar_chart(hash_df.head())
    chart = tpy.get_bar_chart(hash_df.iloc[1:11])

    st.altair_chart(
        chart.interactive(),
        use_container_width=True
    )
    # st.bar_chart(hash_df.iloc[1:11], width=300, height=500)

