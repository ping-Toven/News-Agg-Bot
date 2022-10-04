import tweepy
import os
import sqlite_db
from dotenv import load_dotenv

# Auth Stuff
load_dotenv()
b_token = os.getenv("B_TOKEN")
client = tweepy.Client(b_token)
table_twitter_discord = "Twitter_Usernames_Channels"
table_twitter_uid = "Twitter Usernames UID Map"
db = sqlite_db.SQLITE_DB
conn = db.get_connection(db)


def get_uids():
    """ grab and update uids for all Twitter accounts in the twitter table
    :return str: Error or feed channel id
    """
    u_list = []
    userids = {}
    db = sqlite_db.SQLITE_DB
    for gid, feeds in db.list_feeds(db, conn, table_twitter_discord):
        gid, feeds = str(gid), str(feeds)
        if feeds != "None":
            u_list.append(feeds)
            print(u_list)

    for user in u_list:
        info = client.get_user(username=user).data
        userids.update({info.username: info.id})
        print(userids)

    for username in userids:
        uid = userids.get(username)
        tweets = client.get_users_tweets(uid).data
        for i in tweets:
            print("https://twitter.com/{}/status/{}".format(username, i.id))


if __name__ == '__main__':
    get_uids()
