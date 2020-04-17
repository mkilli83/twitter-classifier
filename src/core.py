# -*- coding: utf-8 -*-

import datetime
import re
from pprint import pformat

import GetOldTweets3 as got
import pandas as pd

from src.utils import Timer, load_csv, paths


USE_TWEETS_COLS = ["username", "formatted_date", "cleaned_text", "text"]


PRE_PROCESSING_OPTIONS = {
    # custom
    "lower_string": True,
    "remove_url": True,
    "remove_at_string": True,
    # gensim
    "remove_stopwords": True,
    "split_alphanum": False,
    "stem_text": False,
    "strip_non_alphanum": False,
    "strip_punctuation": True,
    "strip_tags": True,
    "strip_numeric": True,
    "strip_multiple_whitespaces": True,
}


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
    print(file_name)
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


def clean_tweets_text(tweet_df):
    with Timer("clean tweets text"):
        processing_func = create_preprocessing_functions(PRE_PROCESSING_OPTIONS)
        tweet_df["cleaned_text"] = tweet_df["text"].apply(processing_func)

        empty_str_after_cleaning = (tweet_df["cleaned_text"].isna()) | (
            tweet_df["cleaned_text"] == ""
        )
        num_empty_str_after_cleaning = empty_str_after_cleaning.sum()
        print(
            f"There are {num_empty_str_after_cleaning:,} number of empty text after cleaning, dropping them"
        )
        tweet_df = tweet_df[~empty_str_after_cleaning].reset_index(drop=True)
    return tweet_df


def create_preprocessing_functions(pre_processing_options):
    """
    Creates a preprocessing function that iterates through user-defined preprocessing steps to clean a tweet
    :param pre_processing_options:
        # custom
        'lower_string': True,
        'remove_url': True,
        'remove_at_string': True,

        # gensim
        'remove_stopwords': True,
        'split_alphanum': False,
        'stem_text': False,
        'strip_non_alphanum': False,
        'strip_punctuation': True,
        'strip_tags': True,
        'strip_numeric': True,
        'strip_multiple_whitespaces': True,
    :return: function
    """
    import gensim.parsing.preprocessing as p
    import preprocessor

    pre_processing_options_str_formatted = pformat(pre_processing_options, indent=2)
    print(
        f"Preprocessing tweet text with following choices:\n{pre_processing_options_str_formatted}\n"
    )

    # remove URL and emoji and simple smiley
    preprocessor.set_options(
        preprocessor.OPT.URL, preprocessor.OPT.EMOJI, preprocessor.OPT.SMILEY
    )
    # Complete list of pre-processing functions
    pre_processing_funcs = {
        # custom
        "lower_string": lambda s: s.lower(),
        "remove_url": preprocessor.clean,
        "remove_at_string": lambda s: re.sub(r"@\w+", "", s),
        # gensim
        "remove_stopwords": p.remove_stopwords,
        "split_alphanum": p.split_alphanum,
        "stem_text": p.stem_text,
        "strip_non_alphanum": p.strip_non_alphanum,
        "strip_numeric": p.strip_numeric,
        "strip_punctuation": p.strip_punctuation,
        "strip_tags": p.strip_tags,
        "strip_multiple_whitespaces": p.strip_multiple_whitespaces,
    }

    # Select preprocessing functions defined in PRE_PROCESSING_OPTIONS
    use_preprocessing_funcs = []
    for k, v in pre_processing_options.items():
        if v:
            use_preprocessing_funcs.append(pre_processing_funcs[k])
    # Additional preprocessing function to remove quotations
    patch = lambda s: re.sub(r"(“|”|’)", "", s)
    use_preprocessing_funcs.append(patch)

    # Defines function that iterates through preprocessing items and applies them on tweet
    def _preprocessing_func(s):
        s_processed = s
        for f in use_preprocessing_funcs:
            s_processed = f(s_processed)
        return s_processed

    return _preprocessing_func


def _convert_query_dict_to_str_as_filename(query_dict):
    query_str_formatted = "_".join([str(v) for v in query_dict.values()]).replace(
        " ", "_"
    )
    return query_str_formatted


def _validate_query(query_dict):
    required_keys = ("query_string", "time_since", "time_until", "max_tweets")
    if all(k in query_dict for k in required_keys):
        print("(All required query arguments are provided)")
    else:
        raise ValueError(f"{query_dict} does not have all required keys")


def _create_search_criteria(query_string, time_since, time_until, max_tweets):
    """
    Creates a tweet query using the twitter API
    :params
    query_string: 'datacamp lang:en'
    since: '2019-03-01'
    until: '2019-05-01'
    max_tweets: 0 for unlimited
    :returns tweetCriteria
    """
    tweetcriteria = (
        got.manager.TweetCriteria()
        .setQuerySearch(f"{query_string} lang:en")
        .setSince(time_since)
        .setUntil(time_until)
        .setMaxTweets(max_tweets)
    )
    return tweetcriteria


def _get_tweet_object(tweet_criteria):
    with Timer("Get tweets"):
        current_time = datetime.datetime.now().replace(microsecond=0)
        print(f"Start tweet query at: {current_time}")
        tweets = got.manager.TweetManager.getTweets(tweet_criteria)
        print(f"Done query, {len(tweets):,} tweets returned")
    return tweets


def _convert_tweets_to_dataframe(tweets):
    """
    :param:
        tweets: list of tweet object
    :returns dataframe
    """
    data = [vars(t) for t in tweets]
    df = pd.DataFrame.from_records(data)
    return df


def validation_of_ci():
    return None


# print(tabulate(t, headers="keys"))
