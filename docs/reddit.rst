**Reddit PRAW Bot Documentation**
*********************************
The reddit PRAW bot is desinged to scrape reddit's "Hot" page for the top 100 posts and log them in a .JSON file.
Then the bot will call the post processor function which will filter out the non whale related posts and pass only the whale posts to the urllib which will then 
download any photos linked. These will then be placed into the "Guest" queue. This is the extent of the PRAW bot at this time. Once the deep learning portion is 
complete the bot will recieve the "guess" from the model and reply to the post with the prediction alond with the certinty percentage of the guess.
----------------------------------
.. include:: ../bot/bot.py
