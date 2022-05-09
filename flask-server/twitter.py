""" This file will collect twitter data based on a keyword and perform
sentiment analysis on the data for the past 5 days.
"""
import datetime
import re
import tweepy
import nltk
import numpy as np
from collections import Counter
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.corpus import stopwords
from string import punctuation
from secrets import * # Contains the OAuth authentication tokens.

auth = tweepy.OAuth1UserHandler(
   CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET
)

api = tweepy.API(auth)

def collect_data(keyword):
    result = {"time":[], "text":[]}
    date_until = datetime.datetime.now()
    date_since = date_until - datetime.timedelta(days=5)

    for tweet in tweepy.Cursor(api.search, 
                               q=keyword,
                               since = date_since, 
                               until = date_until,
                               lang="en").items():
        result["time"].append(tweet.created_at)
        result["text"].append(tweet.text)
    return result

def clean_tweet(tweet):
    """
    This function processes the tweet into a string array for NLP sentiment analysis.    
    """
    removing_mentions = r'@[A-Za-z0-9_]+'
    tweet = tweet.lower()

    tweet = re.sub(removing_mentions, '', tweet)

    tokens = tweet.split()
    table = str.maketrans(" "," ",punctuation)
    tokens = [w.translate(table) for w in tokens]
    token = [w for w in tokens if w.isalpha()]
    stop_words = stopwords.words("english")
    new_tweet = [w for w in token if w not in stop_words]

    return ' '.join(new_tweet)

def analyze_tweets(input_tweets):
    """
    This function returns statistics on processed set of tweets.
    Returns frequency data as well as sentiment analysis.
    Returns only top 10 word occurrences because there is too much data.
    """
    all_sentiment = []

    for idx in range(len(input_tweets)):  
        sentiment_analyzer = SentimentIntensityAnalyzer() 
        temp = sentiment_analyzer.polarity_scores(input_tweets[idx])

        # Taking compound portion as sentiment
        # Values greater than 0.4 are positive
        # Values less than -0.4 are negative
        # Values between are neutral
        all_sentiment.append(temp["compound"])

    # Acquiring frequency distribution of words
    counts = Counter(str(input_tweets).split())

    labels, values = zip(*counts.items())

    word_labels = np.array(labels)[np.argsort(values)[::-1]]
    word_counts = np.array(values)[np.argsort(values)[::-1]]

    return all_sentiment, word_labels[0:10], word_counts[0:10]

def get_timeseries(keyword):
    """This specific function will return a json that looks like this
    {"time":[], "sentiment":[]} where time is an array of datetime objects
    and sentiment is an array of sentiment values.
    """
    data = collect_data(keyword)
    input_tweets = []

    all_text = data["text"]

    for idx in range(len(all_text)):
        input_tweets.append(clean_tweet(all_text[idx]))

    # Maybe we can also return the frequency data for another visual in the app
    sentiments, word_labels, word_counts = analyze_tweets(input_tweets)

    return {"time":data["time"], "sentiment":sentiments}