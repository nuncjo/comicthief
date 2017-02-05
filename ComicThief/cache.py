# -*- coding:utf-8 -*-

from collections import namedtuple
from functools import wraps
from pathlib import Path
import pickle
import os
import re
import time

from .config import get_config, CONFIG

config = get_config(CONFIG)
TMP_DIR = config['SETTINGS'].get('tmp_dir', 'tmp')


def search_cached_file(name, tmp_dir):
    """
    Searches for existing temp files with function name and tmp extension.
    :param name: str
    :param tmp_dir: str
    :return:
    """
    for item in sorted(os.listdir(str(Path(tmp_dir))), reverse=True):
        if name in item and item.endswith(".tmp"):
            return item


def check_cache_validity(name, tmp_dir, seconds, time_stamp):
    """
    Checks if cached file exists and is valid.
    :param name: str
    :param tmp_dir: str
    :param seconds: int
    :param time_stamp: int
    :return: (str, bool)
    """
    Validity = namedtuple('Validity', ['file', 'valid'])
    file_name = search_cached_file(name, tmp_dir)
    if file_name:
        name, cache_timestamp, ext = re.split('[-.]', file_name)
        if time_stamp - seconds > int(cache_timestamp):
            Path(tmp_dir, file_name).unlink()
            return Validity(None, False)
        return Validity(file_name, True)
    return Validity(file_name, False)


def pickle_cache(seconds):
    """
    Decorator. Caches function result to pickle serialized text file.
    Loads cached content if cache didn't expired.
    Recreates cache if is expired.
    :param seconds: int
    :return: object
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            Path(TMP_DIR).mkdir(parents=True, exist_ok=True)
            time_stamp = int(time.time())
            old_cache_file, valid = check_cache_validity(func.__name__, TMP_DIR, seconds, time_stamp)
            if valid:
                with open(str(Path(TMP_DIR, old_cache_file)), 'rb') as cache_file:
                    results = pickle.load(cache_file)
            else:
                with open(str(Path(TMP_DIR, "{}-{}.tmp".format(func.__name__, time_stamp))), "wb") as new_cache_file:
                    results = func(*args, **kwargs)
                    pickle.dump(results, new_cache_file, protocol=pickle.HIGHEST_PROTOCOL)
            return results
        return wrapper
    return decorator
