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
    filter_whales()


def filter_whales():
    is_whale = "whale"
    with open('data.json') as read_data:
        data = json.load(read_data)
        #print(len(data))
        for title in data:
            post_id = [title['id']]
            post_title = [title['title']]
            url = [title['url']]
            count = 0
            end_data = len(data)
            whale_dict = {}
            if is_whale in title['title'.lower()]:  # dictionary that the ID and URL of filtered posts gets added to
                whale_dict.update({"id": post_id})  # updates dict with the id
                whale_dict.update({"url": url})  # update dict with post
                print(whale_dict)  # debug print statement
                key = ["id", "url"]
                try:
                    with open('filter.csv', 'a') as filter_csv:
                        write = csv.DictWriter(filter_csv, fieldnames = key)
                        #write.writeheader()
                        print(whale_dict)
                        write.writerow(whale_dict)
                except IOError:
                    print('I/O error!')
                get_image()


def get_image():
    data = "aads"
    with open('filter.csv', 'r') as url_dict:
        read = csv.reader(url_dict)
        for row in read:
            filter_id = row[0]
            filter_url = row[1]
            whale_dict2 = {'id': row[0], 'url': row[1]}
            print(whale_dict2)
    end_doc = len(data)
    print(end_doc)
    print(url)
    filename = 0
    file_name =str(filter_id) + ".jpg"
    #path = os.path.join(pictures/, file_name)
    if filename is not end_doc:
        request.urlretrieve(url,file_name)
        filename +=1

#post = input("Enter number of posts to scrape! ")
#postint = int(post)
#sub = input("Enter subreddit without /r/ ")
#main(postint, sub)
filter_whales()
#get_image()