.. contents: index

==================
What is whale bot?
==================

Abstract
--------

Whale bot is a pet project of mine to identify whales. This was a fun idea
I had a while back and decided to start on it as my entry into machine learning
The idea came to me after reading about the interesting and largll unknown
lives of whales. I wanted to see if I could come up with a way to identify whales by their unique features and log that information in an accessible database where a user could follow the life of a specific whale. 
This data is collected by users and researchers observing these whales when they make contact!

An ansillary function of whale bot is the inclusion of a reddit bot to
identify whales in posts and if that whale is recognized in the database it will link to the profile of that whale!

==========
Reddit bot
==========

Data Collection
---------------

The goal of the data collaction portion of whale bot is in the name. It
utilizes PRAW(Python Reddit API Wrapper) and Beautiful soup(a Python web scrapping library) to crawl reddit for relevant whale posts and when it finds one it logs the **post id**, **post url**, and **photo url**. This is all logged in a database, this is where Beautiful soup comes in. Beautiful soup is called to access the photo url from the database and downloads the raw photo to the dataset, it places the photo in the **id** folder on the host machine. From there it will call the CNN to id the photo which I will explain in more detail further down the page. The next thing Beautiful soup does is logs this function into the **scrapped** database which PRAW will reference on subsequent runs so it knows to skip over posts that have already been scrapped.

CNN(Convoluted Nueral Network)
------------------------------

Currently the CNN is written using tensorflow, and open source machine learning library written and maintained by Google. Right now it is using a template for image recognition supplied by Google as my knowledge of the framework is limited. As I become more familiar with the framework I will start tailoring the network to function better with my use case. 

**My current understanding of how CNN's work:**

The CNN shrinks the image to a managable size in my case 150Px150P. It does this to remove some strain on the memory side of the equation because the next step is to give each pixel in the image a value between 0 nad 1 it does this for each image in the dataset and then proceeds to compare the values for these pixels looking for patterns. It then saves these pattern values and repeats the process for however many iterations you desire. These iterations are called Epochs. The goal is for you to run the cycle enough times for the computer to have a decent "understanding" but not too many that the program "overfits" which is the problem where it is too tailored to a set of data and runs into trouble when a sufficiently different image is feed into the system. The data sets are split up into **Learn** and **Train** and the photos in these datasets are a mixture of datasets retrieved from Kaggle and the images scrapped in the Data Collection phase of the program.

Goal of the reddit bot
----------------------

The ultimate goal of the reddit bot is to build a fun little comment bot that will identify the whale in the post and make a comment about it. The comment will be something to the effect of 

::
    "I found a Whale in this post. I'm X% certain it is Y!
    For more informaition visit whalebot.org!" 

where **X** is the certainty of the models prediction and **Y** is the type of whale the CNN thinks it is! 

===========
The Future!
===========

Website
-------

The website will be the access point for all the data whale bot collects.
It will be laid out with a map of all whale sitings once the mobile app is functional and you will be able to browse the raw data collected for whale bot.
As the model evolves I will post updated version on the site for people to build their own whale bots on it thay'd like. I feel this information is important to the conservation of whales and there for it should be free for all to use as they wish.

Mobile App
----------

Unfortuantly this is the furthest out on my roadmap but this will be how whale watchers and scientists log whale sightings and contribute data to the project. At first the app will be IOS only as I plan on taking advantage of Apple's nueral engine to assist in on the fly reconition. Though as Android processing advances I will try and make an android version as well.

Documentation Plans
-------------------

As I progress further into the project the sections on this page will grow into dedicated pages of their own.
