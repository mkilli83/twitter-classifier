# -*- coding: utf-8 -*-

import datetime
import os
import re
import time
from pprint import pformat

import GetOldTweets3 as got
import pandas as pd
from tabulate import tabulate

from sample.utils import Timer, load_csv, paths

pd.set_option("display.max_columns", 100)

print("here world")

def get_raw_tweets(query_dict):
    """
    Get raw tweets
    :param query_dict:
        query_string: 'datacamp lang:en'
        time_since: '2019-03-01'
        time_until: '2019-05-01'
        max_tweets: 0 for unlimited
    :return: dataframe
    """
    file_name = _convert_query_dict_to_str_as_filename(query_dict)
    save_raw_file_name = paths.raw_tweets / f"raw_{file_name}.csv"

    if save_raw_file_name.is_file():
        print(f"Raw file {repr(save_raw_file_name)} already exists, reload")
        tweet_df = load_csv(save_raw_file_name)
    else:
        _validate_query(query_dict)

        print(f"Getting raw tweets with query:\n{query_dict!r}")
        tweet_criteria = _create_search_criteria(**query_dict)
        tweet_objects = _get_tweet_object(tweet_criteria)
        tweet_df = _convert_tweets_to_dataframe(tweet_objects)

        print(f"Saving raw tweets to: {repr(save_raw_file_name)}")
        tweet_df.to_csv(save_raw_file_name, index=False)

    print("Done getting raw tweets.")
    return tweet_df


def _convert_query_dict_to_str_as_filename(query_dict):
    query_str_formatted = "_".join(str(query_dict.values()))
    print("_".join([str(v) for v in query_dict.values()]).replace(" ", "_"))
    return query_str_formatted


def _validate_query(query_dict):
    required_keys = ("query_string", "time_since", "time_until", "max_tweets")
    if all(k in query_dict for k in required_keys):
        print("(All required query arguments are provided)")
    else:
        raise ValueError(f"{query_dict} does not have all required keys")


def _create_search_criteria(query_string, time_since, time_until, max_tweets):
    """
    query_string: 'datacamp lang:en'
    since: '2019-03-01'
    until: '2019-05-01'
    max_tweets: 0 for unlimited
    """
    tweetCriteria = (
        got.manager.TweetCriteria()
        .setQuerySearch(f"{query_string} lang:en")
        .setSince(time_since)
        .setUntil(time_until)
        .setMaxTweets(max_tweets)
    )
    return tweetCriteria


def _get_tweet_object(tweet_criteria):
    with Timer("Get tweets"):
        current_time = datetime.datetime.now().replace(microsecond=0)
        print(f"Start tweet query at: {current_time}")
        tweets = got.manager.TweetManager.getTweets(tweet_criteria)
        print(f"Done query, {len(tweets):,} tweets returned")
    return tweets


def _convert_tweets_to_dataframe(tweets):
    """
    tweets: list of tweet object
    """
    pd.options.display.max_colwidth = 100
    data = [vars(t) for t in tweets]
    df = pd.DataFrame.from_records(data)
    return df


q = {
    "query_string": "privacy PWC Canada",
    "time_since": "2020-01-01",
    "time_until": "2020-04-01",
    "max_tweets": 100,
}
s = _convert_query_dict_to_str_as_filename(q)
c = _create_search_criteria(**q)
t = _convert_tweets_to_dataframe(_get_tweet_object(c))
t = t.sort_values(by=["favorites"], ascending=False).reindex()
# print(tabulate(t, headers="keys"))
