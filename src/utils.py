import logging
import os
import pickle
from datetime import datetime as dt
from time import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix
from sklearn.utils.multiclass import unique_labels

plt.style.use("ggplot")


def load_csv(file_name, list_type_colname=None, **kwargs):
    df = pd.read_csv(file_name, **kwargs)
    if list_type_colname is not None:
        from ast import literal_eval

        df[list_type_colname] = df[list_type_colname].apply(literal_eval)
    return df


# __enter(exit)__ allow you to use the when function
class Timer(object):
    def __init__(self, description):
        self.description = description

    def __enter__(self):
        self.start = time()

    def __exit__(self, type, value, traceback):
        self.end = time()
        print(f"{self.description}, time took: {(self.end - self.start) / 60:.2f} mins")


def get_paths(create_dir=True):
    from pathlib import Path
    from types import SimpleNamespace  # SimpleNamespace is just quick class

    cwd = Path(os.getcwd())
    print(f"Current working directory: {repr(cwd)}")
    file_paths = [
        "cleaned_tweets",
        "raw_tweets",
    ]  # file_paths = ['cleaned_tweets', 'raw_tweets', 'pics', 'models']
    # Creates dictionary of paths
    file_paths = {fp: cwd / fp for fp in file_paths}

    if create_dir:
        for fp in file_paths.values():
            os.makedirs(str(fp), exist_ok=True)

    file_paths = SimpleNamespace(**file_paths)
    return file_paths

paths = get_paths()
print("test")