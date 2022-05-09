""" This file will collect twitter data based on a keyword and perform
sentiment analysis on the data for the past 5 days.
"""

def get_timeseries(keyword):
    """This specific function will return a json that looks like this
    {"time":[], "sentiment":[]} where time is an array of datetime objects
    and sentiment is an array of sentiment values.
    """
    return {"time":[], "sentiment":[]}