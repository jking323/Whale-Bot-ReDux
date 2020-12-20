"""
Bot.py
Author: Jeremy King
Version: 0.01a
TODO: Add logging for overall bot function
TODO: Add logging for posts access and keep database of posts containing 'whale' for future training and validation
TODO: convery https to http for links
"""

import praw
import torch
import numpy
import os
import logging
import csv
import cython
import json
from bs4 import BeautifulSoup as bs
import requests
import urllib.request as request


def main(lim, sub):
    reddit = praw.Reddit(client_id="IWswRQc_7hLrAQ",
                         client_secret="vpXZRnAWHb1NIifcnB6lgPuEeoL-yw",
                         redirect_uri="http://localhost:8080",
                         refresh_token="616064543729-XZQcu8Zw8EXXqOkP1Loze2tlwn5f5Q",
                         user_agent="whale-id-bot",
                         username="whale-id")

    subreddit = reddit.subreddit(sub).hot(limit=lim)
    for submission in subreddit:
        process_submission(submission)


handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
for logger_name in ("praw", "prawcore"):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

# logging function
list_of_stuff = []
fields = ('title', 'url', 'id')


def process_submission(submission):

    to_dict = vars(submission)
    sub_dict = {field: to_dict[field] for field in fields}
    list_of_stuff.append(sub_dict)
    json_str = json.dumps(list_of_stuff)
    with open('data.json', 'w') as f:
        json.dump(list_of_stuff, f, indent=4, sort_keys=True)


def filter_whales():
    is_whale = "Wild"
    with open('data.json') as read_data:
        data = json.load(read_data)
        print(len(data))
        for title in data:
            post_id = [title['id']]
            post_title = [title['title']]
            url = [title['url']]
            if is_whale in title['title']:
                print(post_id + post_title + url)
                url = str(url)
                url = url.removeprefix("['")
                url = url.removesuffix("']")
                print(url)
                ml_input(url, data)


def ml_input(url, data):
    end_doc = len(data)
    print(end_doc)
    print(url)
    filename = 0
    file_name =str(filename) + ".jpg"
    if filename is not end_doc:
        request.urlretrieve(url,file_name)

#post = input("Enter number of posts to scrape! ")
#postint = int(post)
#sub = input("Enter subreddit without /r/ ")
#main(postint, sub)
filter_whales()
