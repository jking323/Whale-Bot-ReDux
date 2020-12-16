import praw

reddit = praw.Reddit(client_id="IWswRQc_7hLrAQ",
                     client_secret="vpXZRnAWHb1NIifcnB6lgPuEeoL-yw",
                     redirect_uri="http://localhost:8080",
                     user_agent="whale-id-bot")

#print(reddit.auth.url(["identity"], "...", "permanent"))


