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
from secret import * # Contains the OAuth authentication tokens.

api = tweepy.Client(BEARER_TOKEN, CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

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

def moving_average(x, w=3):
    """
    moving_average calculates the moving average of an array of numbers using
    convolution. The input array is convolved with a smaller array of ones,
    equivalent to a cumulative sum, then divided by the length of the array of
    ones. 
    """
    return np.convolve(x, np.ones(w), 'same') / w

def collect_data(keyword, hours_num):
    """
    collect_data uses the Twitter API via tweepy module to collect tweets based
    on a search query. WIth current Essential Access, only Twitter API v2 can
    be used. Searches are limited to a maximum of 7 days before current day and
    only 100 tweets can be accessed per search. This function collects 100 tweets
    per hour and returns a dictionary with the raw text and timestamp.
    """

    raw_tweets = []
    tweet_time = []
    
    number_of_tweets = 100
    
    # Query
    keyword = keyword + " lang:en"

    hour_interval = 5

    for date_idx in range(1,hours_num):

        date_start = datetime.datetime.now() - datetime.timedelta(hours = date_idx*hour_interval)
        date_until = date_start + datetime.timedelta(hours=hour_interval)

        tweets = api.search_recent_tweets(query=keyword,
                                    max_results=number_of_tweets,
                                    end_time=date_until,
                                    start_time=date_start,
                                    tweet_fields=["text","created_at"])

   # if not tweets.data:
    #    return {"time": date_start, "text": [""]}
    #else:
    for twt in tweets.data:
        raw_tweets.append(twt.text)
        tweet_time.append(twt.created_at)
    
    result = {"time": tweet_time, "text": raw_tweets}

    return result

def clean_tweet(tweet):
    """
    clean_tweet processes the tweet into a list of words for NLP sentiment analysis. 
    Also returns hashtags as list of words.   
    """
    tweet = tweet.lower()

    # Removing RT from tweet (can't figure out how to filter out retweets with Twitter APIv2)
    remove_RT = lambda x: re.compile('rt @').sub('@',x,count=1).strip() 
    tweet = remove_RT(tweet)

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
    
    raw_tweet_data = collect_data(keyword, 10)
    
    for idx in range(len(raw_tweet_data["text"])):
        temptweet, temphash = clean_tweet(str(raw_tweet_data["text"][idx]))
        processed_tweets.append(temptweet)
        hashtags.append(temphash)

    sentiments, word_labels, word_counts = analyze_tweets(processed_tweets)

    # Removes empty entries
    hashtags = list(filter(None, hashtags))

    hashtag_labels, hashtag_counts = sort_freq(hashtags)

    time_tweets_df = pd.DataFrame({"Sentiment":sentiments}, index = raw_tweet_data["time"])

    return time_tweets_df, word_labels, word_counts, hashtag_labels, hashtag_counts