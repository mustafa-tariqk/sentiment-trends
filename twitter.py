""" This file will collect twitter data based on a keyword and perform
sentiment analysis on the data for the past 5 days. 
"""
import datetime
import altair as alt
import re
import tweepy
import numpy as np
import pandas as pd
from collections import Counter
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from string import punctuation
import matplotlib.pyplot as plt
from transformers import AutoModelForSequenceClassification
from transformers import AutoTokenizer, AutoConfig
from scipy.special import softmax
from secret import * # Contains the OAuth authentication tokens.
import os
from proxy_utils import *


os.environ['http_proxy'] = 'http://' + get_proxy()
os.environ['https_proxy'] = 'http://' + get_proxy()

MODEL = f"cardiffnlp/twitter-roberta-base-sentiment-latest"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
config = AutoConfig.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL)

ROLLING = 50

api = tweepy.Client(BEARER_TOKEN, CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)


# Line chart 
def get_line_chart(data):
    hover = alt.selection_single(
        fields=["Time"],
        nearest=True,
        on="mouseover",
        empty="none",
    )

    lines = (
        alt.Chart(data, title="Twitter Tweet Sentiment in 24 Hours")
        .mark_line(color='red')
        .encode(
            x="Time",
            y="Sentiment:Q",
        )
    )

    # Draw points on the line, and highlight based on selection
    points = lines.transform_filter(hover).mark_circle(size=65)

    # Draw a rule at the location of the selection
    tooltips = (
        alt.Chart(data)
        .mark_rule()
        .encode(
            x="Time",
            y="Sentiment",
            opacity=alt.condition(hover, alt.value(0.3), alt.value(0)),
            tooltip=[
                alt.Tooltip("Sentiment", title="Sentiment"),
                alt.Tooltip("Tweets", title="Tweet"),
            ],
        )
        .add_selection(hover)
    )
    return (lines + points + tooltips).interactive()

# Bar chart using pyploy
def get_bar_chart(data):

    fig, axe = plt.subplots()
    data.plot.bar(color='red', rot=45, ax=axe, legend=False)
    
    # Make background transparent
    fig.patch.set_alpha(0)
    axe.patch.set_alpha(0)

    return fig

def sort_freq(input_text_list):
    """
    sort_freq takes as input a list of words and returns two lists, 
    word_counts which is the count of the word in the word_labels list.
    Both lists are sorted in descending order.
    """
    
    counts = Counter(" ".join(input_text_list).split(" "))

    # Sorting distribution from highest to lowest frequency
    labels, values = zip(*counts.items())
    word_labels = np.array(labels)[np.argsort(values)[::-1]]
    word_counts = np.array(values)[np.argsort(values)[::-1]]

    return word_labels, word_counts

def moving_average(x):
    """
    moving_average calculates the moving average of an array of numbers using
    convolution. The input array is convolved with a smaller array of ones,
    equivalent to a cumulative sum, then divided by the length of the array of
    ones. 
    """
    return np.convolve(x, np.ones(ROLLING), 'same') / ROLLING

def collect_data(keyword, hours_num, hour_interval=2):
    """
    collect_data uses the Twitter API via tweepy module to collect tweets based
    on a search query. WIth current Essential Access, only Twitter API v2 can
    be used. Searches are limited to a maximum of 7 days before current day and
    only 100 tweets can be accessed per search. This function collects 100 tweets
    per hour and returns a dictionary with the raw text and timestamp.
    """

    raw_tweets = []
    tweet_time = []
    
    # Query
    keyword = keyword + " lang:en"

    for date_idx in range(hours_num,0,-1):

        date_start = datetime.datetime.now() - datetime.timedelta(hours = date_idx*hour_interval)
        date_until = date_start + datetime.timedelta(hours=hour_interval)

        tweets = api.search_recent_tweets(query=keyword,
                                    max_results=ROLLING,
                                    end_time=date_until,
                                    start_time=date_start,
                                    tweet_fields=["text","created_at"])

   # if not tweets.data:
    #    return {"time": date_start, "text": [""]}
    #else:
        if tweets.data:
            for twt in tweets.data:
                raw_tweets.append(twt.text)
                tweet_time.append(twt.created_at)
    
    if not raw_tweets:
        return {"time": [date_start], "text": [""]} 

    return {"time": tweet_time, "text": raw_tweets}

def collect_data_by_minutes(keyword, mins_num, min_interval=1):
    """
    collect_data_by_minutes uses the Twitter API via tweepy module to collect tweets based
    on a search query. WIth current Essential Access, only Twitter API v2 can
    be used. Searches are limited to a maximum of 7 days before current day and
    only 100 tweets can be accessed per search. This function collects 100 tweets
    per hour and returns a dictionary with the raw text and timestamp.
    """

    raw_tweets = []
    tweet_time = []
    
    # Query
    keyword = keyword + " lang:en"

    for date_idx in range(mins_num,0,-1):

        date_start = datetime.datetime.now() - datetime.timedelta(minutes = date_idx*min_interval)
        date_until = date_start + datetime.timedelta(minutes=min_interval)

        tweets = api.search_recent_tweets(query=keyword,
                                    max_results=ROLLING,
                                    end_time=date_until,
                                    start_time=date_start,
                                    tweet_fields=["text","created_at"])

   # if not tweets.data:
    #    return {"time": date_start, "text": [""]}
    #else:
        if tweets.data:
            for twt in tweets.data:
                raw_tweets.append(twt.text)
                tweet_time.append(twt.created_at)
    
    if not raw_tweets:
        return {"time": [date_start], "text": [""]} 

    return {"time": tweet_time, "text": raw_tweets}

def clean_tweet(tweet):
    """
    clean_tweet processes the tweet into a list of words for NLP sentiment analysis. 
    Also returns hashtags as list of words.   
    """
    tweet = tweet.lower()

    # Removing RT from tweet (can't figure out how to filter out retweets with Twitter APIv2)
    remove_RT = lambda x: re.compile('rt @').sub('@',x,count=1).strip() 
    tweet = remove_RT(tweet)

    # Remove ampersand &amp;
    tweet = re.sub(r"&amp;+", "", tweet)

    # Removing mentions with regex
    tweet = re.sub(r'@[A-Za-z0-9_]+', '', tweet)

    # Removing links
    tweet = re.sub(r"http\S+", "", tweet)
    tweet = re.sub(r"www.\S+", "", tweet) 

    # Extracting then removing hashtags
    hashtags = re.findall(r"#(\w+)", tweet)
    tweet = re.sub("#[A-Za-z0-9_]+","", tweet)

    tokens = tweet.split()

    # Removing punctuation
    table = str.maketrans(" "," ",punctuation)
    tokens = [w.translate(table) for w in tokens]

    # Removing numerical characters
    token = [w for w in tokens if w.isalpha()]

    # Removing stopwords e.g., "a", "the", "for", etc.
    stop_words = stopwords.words("english")
    new_tweet = [w for w in token if w not in stop_words]

    return ' '.join(new_tweet), ' '.join(hashtags)

def analyze_tweets(input_tweets,analyzer="bert"):
    """
    analyze_tweets returns statistics on processed set of tweets.
    Returns frequency data as well as sentiment analysis.
    Choose between 'bert' and 'nltk' sentiment analyzer.
    """

    # Empty list to contain sentiment values
    all_sentiment = []

    if analyzer == 'nltk':
        for idx in range(len(input_tweets)):  

            # nltk sentiment analyzer using polarity scores
            sentiment_analyzer = SentimentIntensityAnalyzer() 
            temp = sentiment_analyzer.polarity_scores(input_tweets[idx])

            # Taking compound portion as sentiment
            # Values greater than 0.4 are positive
            # Values less than -0.4 are negative
            # Values between are neutral
            all_sentiment.append(temp["compound"])

    if analyzer == 'bert':
        for idx in range(len(input_tweets)): 
            encoded_input = tokenizer(input_tweets[idx], return_tensors='pt')
            output = model(**encoded_input)
            scores = output[0][0].detach().numpy()
            scores = softmax(scores)
            score = (-1*scores[0]/3+scores[1]/3+scores[2]/3)

            all_sentiment.append(score)


    word_labels, word_counts = sort_freq(input_tweets)

    rolling_sentiment = moving_average(all_sentiment)

    return rolling_sentiment, word_labels, word_counts

def get_timeseries(keyword):
    """
    get_timeseries takes as input a keyword from the frontend and returns
    the a dictionary of sentiments over time (timestamps) and histogram data
    for the words in the tweets as well as the used hashtags.
    """
    processed_tweets = []
    hashtags = []
    num_hours = 24
    raw_tweet_data = collect_data(keyword, num_hours, hour_interval=1)
    
    for idx in range(len(raw_tweet_data["text"])):
        temptweet, temphash = clean_tweet(str(raw_tweet_data["text"][idx]))
        processed_tweets.append(temptweet)
        hashtags.append(temphash)

    sentiments, word_labels, word_counts = analyze_tweets(processed_tweets,analyzer='nltk')

    # Removes empty entries
    hashtags = list(filter(None, hashtags))

    hashtag_labels, hashtag_counts = sort_freq(hashtags)

    # time_tweets_df = pd.DataFrame({"Sentiment":sentiments, "Tweets":raw_tweet_data["text"]})#, index = raw_tweet_data["time"])
    time_tweets_df = pd.DataFrame({"Sentiment":sentiments, "Tweets":raw_tweet_data["text"], "Time":raw_tweet_data["time"]})

    return time_tweets_df, word_labels, word_counts, hashtag_labels, hashtag_counts