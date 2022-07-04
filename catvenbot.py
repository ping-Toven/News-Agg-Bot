from venv import create
import discord
import tweepy
import logging
import os
import sqlite3
from sqlite3 import Error
from dotenv import load_dotenv
from setuptools import setup

load_dotenv()
#set up logging module for pycord
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
#Set db name var, init discord bot, init db connection
RSS_database = "RSS_Feeds.db"
Twitter_database = "Twitter_Feeds.db"
catvenBot = discord.Bot()
RSS_conn = sqlite3.connect(RSS_database)
Twitter_conn = sqlite3.connect(Twitter_database)


#
#SQLite DB Helper functions
#

#Function to create the tables
def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
        print("Table created if it didn't already exist")
    except Error as e:
        print(e)

#Function to setup a guild with a specific channel id for a feed (RSS & Twitter separate dbs / channels)
def db_setup_guild_channel(conn, guild_id:str, channel_id:str):
    """ add a guild_id:channel_id row in db
    :param conn: Connection object
    :param guild_id: Guild ID str
    :param channel_id: Channel ID str
    :return:
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        table_name = str(cursor.fetchone()[0])
        #if setup has not happened, insert new row
        if not setup_check(conn, guild_id):
            cursor.execute("INSERT INTO {} (guild_id, channel_id) VALUES (?,?)".format(table_name), [guild_id, channel_id])
            conn.commit()
        #else update existing
        else:
            cursor.execute("UPDATE {} SET channel_id = (?) WHERE guild_id = (?)".format(table_name), [channel_id, guild_id])
            conn.commit()        
    except sqlite3.Error as error:
        print("Failed to setup guild's channel. Error: ", error)

def get_posting_channel(conn, guild_id:str):
    """ fetch posting channel from guild
    :param guild_id: Guild ID str
    :return str: Error or feed channel id
    """
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    table_name = str(cursor.fetchone()[0])
    #if setup has not happened, abort
    if not setup_check(conn, guild_id):
        return 
    else:
        cursor.execute("SELECT channel_id FROM {} WHERE guild_id=(?)".format(table_name),[guild_id])
        feed_channel_id = str(cursor.fetchone()[0])
        return feed_channel_id

#Function to check if guild has been set up in DB
def setup_check(conn, gid:str):
    """ Check for the guild_id in the DB
    :param gid: command's ctx guild id
    :return bool: True = guild has been set up in this DB, False = not set up
    """
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    table_name = str(cursor.fetchone()[0])
    cursor.execute("SELECT guild_id FROM {} WHERE guild_id = (?)".format(table_name), [gid])
    #SQL statement will return guild_id as provided by command if the DBs are set up. Otherwise returns None
    if cursor.fetchone() is None:
        return False
    else:
        return True

#Function to check if Feed URL has been added to guild specific DB
def feed_check(feed_url):
    """ Check for the RSS Feed's URL in the Guild's DB
    :param feed_url: command's feed URL
    :return bool:
    """
    cursor = RSS_conn.cursor()
    cursor.execute("SELECT feed_url FROM RSS_Feeds WHERE feed_url = (?)", [feed_url])
    #SQL statement will return feed_url as provided by command if this feed has already been added. Otherwise returns None
    if cursor.fetchone() is None:
        return False
    else:
        return True

#Function to check if Feed URL has been added to guild specific DB
def twt_user_check(twt_user):
    """ Check for the twitter username in the Guild's DB
    :param twt_user: Twitter username
    :return bool:
    """
    cursor = Twitter_conn.cursor()
    cursor.execute("SELECT usernames FROM Twitter_Feeds WHERE usernames = (?)", [twt_user])
    #SQL statement will return twt_user as provided by command if this feed has already been added. Otherwise returns None
    if cursor.fetchone() is None:
        return False
    else:
        return True

#Function to add an RSS Feed url to the guild's DB
def db_add_feed_url(RSS_url, guild_id):
    """ add a feed URL from slash command to the db
    :param feed_url: RSS feed url submitted by user in command "add"
    :param guild_id: Guild ID
    :return str: one of the 2 statuses
    """
    existing_feed = "Feed already added"
    successful = "RSS Feed added successfully"
    feed_channel_id = get_posting_channel(RSS_conn, guild_id)
    cursor = RSS_conn.cursor()
    if feed_check(RSS_url):
        return existing_feed
    else:
        cursor.execute("INSERT INTO RSS_Feeds (guild_id, channel_id, feed_url) VALUES (?,?,?)", [guild_id, feed_channel_id, RSS_url])
        RSS_conn.commit()
        return successful

#Function to remove an existing RSS Feed url from guild's DB
def db_remove_feed(RSS_url:str, guild_id:str):
    """ remove an existing feed URL from guild specific DB entries
    :param feed_url: RSS feed url submitted by user in command (str)
    :param guild_id: Guild ID (str)
    :return str: one of the 2 statuses
    """
    unknown_feed = "Feed does not exist"
    successful = "RSS Feed removed successfully"
    cursor = RSS_conn.cursor()
    if not feed_check(RSS_url):
        return unknown_feed
    else:
        cursor.execute("DELETE FROM RSS_Feeds WHERE feed_url = (?) AND guild_id = (?)", [RSS_url, guild_id])
        RSS_conn.commit()
        return successful

#Function to add an RSS Feed url to the guild's DB
def db_add_twitter_user(twt_user:str, guild_id:str):
    """ add a twitter username from slash command to the db
    :param twt_user: Twitter username submitted by user in command "add"
    :param guild_id: Guild ID
    :return str: one of the 2 statuses
    """
    existing_user = "Twitter account already added"
    successful = "Account added successfully"
    feed_channel_id = get_posting_channel(Twitter_conn, guild_id)
    cursor = Twitter_conn.cursor()
    if twt_user_check(twt_user):
        return existing_user
    else:
        cursor.execute("INSERT INTO Twitter_Feeds (guild_id, channel_id, usernames) VALUES (?,?,?)", [guild_id, feed_channel_id, twt_user])
        Twitter_conn.commit()
        return successful

#
#Basic bot event listeners below
#

#Write to terminal on login
@catvenBot.event
async def on_ready():
    print(f'Logged on as {catvenBot.user}!')

#Write to terminal on disconnect
@catvenBot.event
async def on_disconnect():
    #RSS_conn.close()
    print(f'Disconnected as {catvenBot.user} & closed DB connection')

#Slash command template
@catvenBot.slash_command(name = "hello", description = "Say hello to the bot")
async def hello(ctx):
    await ctx.respond("Hey!")

#
#RSS RELATED COMMANDS BELOW 
#

#Add RSS feed command
@catvenBot.slash_command(name = "add_rss", description = "Add an RSS feed to the bot's watchlist.")
async def add_rss(ctx, feed_url: str): 
    guild_id = str(ctx.guild.id)
    #if false prompt user to run /setup command
    if not setup_check(RSS_conn, guild_id):
        await ctx.respond("Please make sure to run the /setup command")
        return
    channel = get_posting_channel(RSS_conn, guild_id)
    channel_mention = "<#" + channel + ">"
    status = db_add_feed_url(feed_url, guild_id)
    await ctx.respond(status + f" in {channel_mention}")

#Remove RSS feed command
@catvenBot.slash_command(name = "remove_rss", description = "Remove an RSS feed from the bot's watchlist.")
async def remove_rss(ctx, feed_url: str):
    guild_id = str(ctx.guild.id)
    #if false prompt user to run /setup command
    if not setup_check(RSS_conn, guild_id):
        await ctx.respond("Please make sure to run the /setup command")
        return
    channel = get_posting_channel(RSS_conn, guild_id)
    channel_mention = "<#" + channel + ">"
    status = db_remove_feed(feed_url, guild_id)
    await ctx.respond(status + f" in {channel_mention}")

#Setup channel for RSS feed command
@catvenBot.slash_command(name = "setup_rss", description = "Set up the bot's RSS feeds by selecting a channel to post in")
async def setup_rss(ctx, channel: discord.TextChannel): 
    setup_guild_id = str(ctx.guild.id)
    setup_channel_id = str(channel.id)
    db_setup_guild_channel(conn = RSS_conn, guild_id=setup_guild_id, channel_id=setup_channel_id)
    await ctx.respond(f"Succesfully set {channel.mention} as the RSS feed channel")

#Check RSS feed setup info command
@catvenBot.slash_command(name = "info_rss", description = "View the bot's configs for your RSS feeds")
async def info_rss(ctx):
    cursor = RSS_conn.cursor()
    guild_id = str(ctx.guild.id)
    guild = ctx.guild
    try:
        #if false prompt user to run /setup command
        if not setup_check(RSS_conn, guild_id):
            await ctx.respond("Please make sure to run the /setup command")
        #else list information regarding channel config
        else:
            channel = get_posting_channel(RSS_conn, guild_id)
            channel_mention = "<#" + channel + ">"
            await ctx.respond(f"{guild}'s RSS Feed channel is set to {channel_mention}")
            #cursor.execute("SELECT feed_url FROM RSS_Feeds WHERE guild_id=(?)", [guild_id])
    except sqlite3.Error as error:
        print("info command error: " , error)
        await ctx.respond("Please make sure to run the /setup command")

#
#TWITTER RELATED COMMANDS BELOW 
#

#Add twitter user to post tweets from
@catvenBot.slash_command(name = "add_twitter", description = "add a twitter username to your feed list")
async def add_twitter(ctx, username:str):
    guild_id = ctx.guild.id

    if not setup_check(Twitter_conn, guild_id):
        await ctx.respond("Please make sure to run the /setup command")
        return
    channel = get_posting_channel(Twitter_conn, guild_id)
    posting_channel_mention = "<#" + channel + ">"
    result = db_add_twitter_user(username,guild_id)
    await ctx.respond(result + f" in {posting_channel_mention}")

#Setup channel for Twitter feed command
@catvenBot.slash_command(name = "setup_twt", description = "Set up the bot's Twitter feeds by selecting a channel to post in")
async def setup_twt(ctx, channel: discord.TextChannel): 
    setup_guild_id = str(ctx.guild.id)
    setup_channel_id = str(channel.id)
    db_setup_guild_channel(Twitter_conn, setup_guild_id, setup_channel_id)
    await ctx.respond(f"Succesfully set {channel.mention} as the Twitter feed channel")

def main():
    sql_create_feeds_table = "CREATE TABLE IF NOT EXISTS RSS_Feeds (guild_id string, channel_id string, feed_url string);"
    sql_create_twitter_list_table = "CREATE TABLE IF NOT EXISTS Twitter_Feeds (guild_id string, channel_id string, usernames);"
    if RSS_conn and Twitter_conn is not None:
        create_table(conn = RSS_conn, create_table_sql = sql_create_feeds_table)
        create_table(conn = Twitter_conn, create_table_sql =sql_create_twitter_list_table)
    else:
        print("Error: Cannot create the DB connection")

    catvenBot.run(os.getenv('TOKEN'))
    client = tweepy.Client(os.getenv('B_TOKEN'))
if __name__ == '__main__':
    main()
