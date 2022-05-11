""" This file will collect twitter data based on a keyword and perform
sentiment analysis on the data for the past 5 days.
"""
import datetime
import re
import tweepy
import nltk
import urllib.parse
import numpy as np
import pandas as pd
from collections import Counter
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from string import punctuation
from secrets import * # Contains the OAuth authentication tokens.

keys_file = open("secrets.txt")
lines = keys_file.readlines()

BEARER_TOKEN = lines[0].rstrip()
CONSUMER_KEY = lines[1].rstrip()
CONSUMER_SECRET = lines[2].rstrip()
ACCESS_TOKEN = lines[3].rstrip()
ACCESS_TOKEN_SECRET = lines[4].rstrip()


api = tweepy.Client(BEARER_TOKEN,CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

def collect_data(keyword):
    result = {"time":[], "text":[]}
    date_until = datetime.datetime.now()
    date_start = date_until - datetime.timedelta(days = 5)
    number_of_tweets = 100
    # Will query up to 7 days maximum

    keyword = keyword + " lang:en"

    tweets = api.search_recent_tweets(query=keyword,
                                max_results=number_of_tweets,
                                end_time=date_until,
                                start_time=date_start,
                                tweet_fields=["text","created_at"])

    raw_tweets = []
    tweet_time = []
    
    for twt in tweets.data:
        raw_tweets.append(twt.text)
        tweet_time.append(twt.created_at)
    
    result = {"time": tweet_time, "text":raw_tweets}

    return result

def clean_tweet(tweet):
    """
    This function processes the tweet into a string array for NLP sentiment analysis. 
    Also returns hashtags.   
    """

    # Removing RT from tweet (can't figure out how to filter out retweets with Twitter APIv2)
    remove_RT = lambda x: re.compile('RT @').sub('@',x,count=1).strip() 
    tweet = remove_RT(tweet)

    # Removing mentions with regex
    tweet = re.sub(r'@[A-Za-z0-9_]+', '', tweet)

    # Removing links
    tweet = re.sub(r"http\S+", "", tweet)
    tweet = re.sub(r"www.\S+", "", tweet) 

    # Extracting then removing hashtags
    hashtags = re.findall(r"#(\w+)", tweet)
    tweet = re.sub("#[A-Za-z0-9_]+","", tweet)

    # Converting uppercase characters
    tweet = tweet.lower()

    # Splitting up all words into array of strings
    tokens = tweet.split()

    # Removing punctuation
    table = str.maketrans(" "," ",punctuation)
    tokens = [w.translate(table) for w in tokens]

    # Removing numerical characters
    token = [w for w in tokens if w.isalpha()]

    # Removing stopwords e.g., "a", "the", "for", etc.
    stop_words = stopwords.words("english")
    new_tweet = [w for w in token if w not in stop_words]


    return ' '.join(new_tweet), hashtags

def analyze_tweets(input_tweets):
    """
    This function returns statistics on processed set of tweets.
    Returns frequency data as well as sentiment analysis.
    Returns only top 10 word occurrences because there is too much data.
    """
    def moving_average(a, n=1):
    
        # Cumulative sum
        ret = np.cumsum(a, dtype=float)

        # Calculating mean
        ret[n:] = ret[n:] - ret[:-n]
        return ret[n - 1:] / n

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

    # Acquiring frequency distribution of words
    counts = Counter(str(input_tweets).split())

    # Sorting distribution from highest to lowest frequency
    labels, values = zip(*counts.items())
    word_labels = np.array(labels)[np.argsort(values)[::-1]]
    word_counts = np.array(values)[np.argsort(values)[::-1]]

    rolling_sentiment = moving_average(all_sentiment)

    return rolling_sentiment, word_labels, word_counts

def get_timeseries(keyword):

    raw_tweet_data = collect_data(keyword)

    processed_tweets = []
    hashtags = []
    
    for idx in range(len(raw_tweet_data["text"])):
        temptweet, temphash = clean_tweet(str(raw_tweet_data["text"][idx]))
        processed_tweets.append(temptweet)
        hashtags.append(temphash)

    sentiments, word_labels, word_counts = analyze_tweets(processed_tweets)

    time_tweets_df = pd.DataFrame({"Sentiment":sentiments}, index = raw_tweet_data["time"])

    return time_tweets_df, word_labels, word_counts, hashtags