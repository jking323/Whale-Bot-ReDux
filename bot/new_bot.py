"""
New_bot.py
Author: Jeremy King
Version 0.01a
*******0.01a*******
Initial
"""

import praw
from creds import r
import torch
import numpy
import os
import logging
import csv
import cython
import urllib.request as request
import openpyxl as op
import collections

def bot_main(lim, sub):
    
    log_created = 0
    reddit = r
    if os.path.isfile('log.xlsx'):
        print('Log exists, skipping!')
        log_created += 1
    else:
        make_xlxs()
    if log_created == 1:
        main_sheet = op.load_workbook('log.xlsx')
        unfiltered_work_sheet = main_sheet['Logs']
        working_sheet = main_sheet.active
        row_count = unfiltered_work_sheet
    subreddit = reddit.subreddit(sub).hot(limit=lim)
    for submission in subreddit:
        process_submission(submission)
    



def make_xlxs():
    print('Log not found, Creating!')
    book = op.workbook()
    ws = book.active
    log1 = book.create_sheet("Logs")
    log2 = book.create_sheet("Filtered logs")

    book.save('log.xlsx')
    return

