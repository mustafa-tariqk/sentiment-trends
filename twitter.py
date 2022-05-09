""" This file will collect twitter data based on a keyword and perform
sentiment analysis on the data for the past 5 days.
"""
import datetime
import tweepy
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

def get_timeseries(keyword):
    """This specific function will return a json that looks like this
    {"time":[], "sentiment":[]} where time is an array of datetime objects
    and sentiment is an array of sentiment values.
    """
    return {"time":[], "sentiment":[]}