""" This file will collect twitter data based on a keyword and perform
sentiment analysis on the data for the past 5 days. 
"""
import datetime
import re
import tweepy
import numpy as np
import pandas as pd
from collections import Counter
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from string import punctuation
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.collections import LineCollection
from secret import * # Contains the OAuth authentication tokens.

ROLLING = 100

api = tweepy.Client(BEARER_TOKEN, CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)


def multi_color_plot(y):
    """
    multi_color_plot takes as input sentiment data and returns a fig object
    which is a line plot color-coded to the polarity of the data.
    
    """
    fig, ax = plt.subplots()

    # Creating line segments to be color coded
    x_val = np.linspace(0, len(y), len(y))
    points = np.array([x_val, y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)

    # Setting up bounds for color coding and choosing color theme
    norm = plt.Normalize(y.min(), y.max())
    lc = LineCollection(segments, cmap='seismic_r', norm=norm)
    # Using input array as color reference
    lc.set_array(y)
    lc.set_linewidth(2)
    line = ax.add_collection(lc)

    # This is done to avoid annoying scaling errors
    ax.plot(y*np.nan)

    tick_spacing = round(max(x_val)/5)

    ax.set_yticks([])
    # ax.set_xticks(x_val[0:-1:tick_spacing],labels=['24','18', '12', '6', 'Now'])
    ax.xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
    ax.set_ylabel("Tweet Sentiment")
    ax.set_xlabel("Time")

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

    for date_idx in range(hours_num,1,-1):

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

def clean_tweet(tweet):
    """
    clean_tweet processes the tweet into a list of words for NLP sentiment analysis. 
    Also returns hashtags as list of words.   
    """
    tweet = tweet.lower()

    # Removing RT from tweet (can't figure out how to filter out retweets with Twitter APIv2)
    remove_RT = lambda x: re.compile('rt @').sub('@',x,count=1).strip() 
    remove_amp = lambda x: re.compile('amp @').sub('@',x,count=1).strip() 
    tweet = remove_RT(tweet)
    tweet = remove_amp(tweet)

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

def analyze_tweets(input_tweets):
    """
    analyze_tweets returns statistics on processed set of tweets.
    Returns frequency data as well as sentiment analysis.
    """

    # Empty list to contain sentiment values
    all_sentiment = []

    for idx in range(len(input_tweets)):  

        # nltk sentiment analyzer using polarity scores
        sentiment_analyzer = SentimentIntensityAnalyzer() 
        temp = sentiment_analyzer.polarity_scores(input_tweets[idx])

        # Taking compound portion as sentiment
        # Values greater than 0.4 are positive
        # Values less than -0.4 are negative
        # Values between are neutral
        all_sentiment.append(temp["compound"])

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

    sentiments, word_labels, word_counts = analyze_tweets(processed_tweets)

    # Removes empty entries
    hashtags = list(filter(None, hashtags))

    hashtag_labels, hashtag_counts = sort_freq(hashtags)

    time_tweets_df = pd.DataFrame({"Sentiment":sentiments})#, index = raw_tweet_data["time"])

    return time_tweets_df, word_labels, word_counts, hashtag_labels, hashtag_counts