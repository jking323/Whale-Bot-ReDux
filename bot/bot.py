import praw
import torch
import numpy
import os
import logging
import creds as c
import csv

is_whale = ["whale"]
reply_template = "This is a {predict}, I'm {guess_accuracy}% sure \n  " \
                 "##### I'm a bot, contact /u/goose323 to report issues!"
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
for logger_name in ("praw", "prawcore"):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)


class Mlin:       # input to machine learning layer



class Readcomments:
    ml_in = Mlin
    global is_whale
    subreddit = c.reddit.subreddit("all")


    def process_submission(submission):
        normal_title = submission.title.lower()
        for whale_title in is_whale:
            if is_whale in normal_title:
                print(submission.title)

