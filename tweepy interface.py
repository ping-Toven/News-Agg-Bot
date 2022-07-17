import tweepy
import os
import sqlite_db
from dotenv import load_dotenv

# Auth Stuff
load_dotenv()
b_token = os.getenv("B_TOKEN")
client = tweepy.Client(b_token)

# Create dictionary of username <> user_id values
db = sqlite_db.SQLITE_DB
u_list = db.list_feeds()# Eventually import from .csv or something

for x in u_list:
    info = client.get_user(username=x).data
    users[info.username] = info.id

for username in users:
    uid = users[username]
    tweets = client.get_users_tweets(uid).data
    for i in tweets:
        print("https://twitter.com/{}/status/{}".format(username, i.id))
