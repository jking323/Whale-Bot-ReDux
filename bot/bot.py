"""
Bot.py
Author: Jeremy King
Version: 0.01a
TODO: Add logging for overall bot function
TODO: Add logging for posts access and keep database of posts containing 'whale' for future training and validation
"""

import praw
import torch
import numpy
import os
import logging
import csv
import cython
import json


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
    is_whale = {}
    print('test')
    with open('data.json') as read_data:
        data = json.load(read_data)
        for p in data.title:
            print('title: ' + p)


#post = input("Enter number of posts to scrape! ")
#postint = int(post)
#sub = input("Enter subreddit without /r/ ")
#main(postint, sub)
filter_whales()