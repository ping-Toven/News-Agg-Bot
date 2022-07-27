import tweepy
import os
import sqlite_db
from dotenv import load_dotenv

# Auth Stuff
load_dotenv()
b_token = os.getenv("B_TOKEN")
client = tweepy.Client(b_token)
table_twitter_discord = "Twitter Discord Map"
table_twitter_uid = "Twitter Usernames UID Map"

def get_uids(conn):
    """ grab and update uids for all twitter accounts in the twitter table
    :param conn: db connection obj
    :return str: Error or feed channel id
    """
    u_list = []
    db = sqlite_db.SQLITE_DB
    for gid, feeds in db.list_feeds(db, conn, table_twitter_discord):
        gid, feeds = str(gid), str(feeds)
        u_list += feeds

    for x in u_list:
        info = client.get_user(username=x).data
        users[info.username] = info.id

    for username in users:
        uid = users[username]
        tweets = client.get_users_tweets(uid).data
        for i in tweets:
            print("https://twitter.com/{}/status/{}".format(username, i.id))
