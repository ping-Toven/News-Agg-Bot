import logging
import sqlite3
import os
import discord
import tweepy
from dotenv import load_dotenv
import sqlite_db

load_dotenv()
#set up logging module for pycord
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
#init discord bot
catvenBot = discord.Bot()
#init SQLite DB Conncetions
RSS_database = "RSS_Feeds.db"
Twitter_database = "Twitter_Feeds.db"
RSS_conn = sqlite3.connect(RSS_database)
Twitter_conn = sqlite3.connect(Twitter_database)
db = sqlite_db.SQLITE_DB

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
    print(f'Disconnected as {catvenBot.user}')

#Slash command template
@catvenBot.slash_command(name = "hello", description = "Say hello to the bot")
async def hello(ctx):
    await ctx.respond("Hey!")

#
#RSS RELATED COMMANDS BELOW
#

#Add RSS feed command
@catvenBot.slash_command(name = "rss-add", description = "Add an RSS feed to the bot's watchlist.")
async def add_rss(ctx, feed_url: str):
    guild_id = str(ctx.guild.id)
    #if false prompt user to run /setup command
    if not db.setup_check(db, RSS_conn, guild_id):
        await ctx.respond("Please make sure to run the /setup command")
        return
    channel_id = str(db.get_posting_channel(db, RSS_conn, guild_id))
    channel_mention = "<#" + channel_id + ">"
    status = db.add_feed(db, RSS_conn, feed_url, guild_id)
    await ctx.respond(status + f" in {channel_mention}")

#Remove RSS feed command
@catvenBot.slash_command(name = "rss-remove", description = "Remove an RSS feed from the bot's watchlist.")
async def remove_rss(ctx, feed_url: str):
    guild_id = str(ctx.guild.id)
    #if false prompt user to run /setup command
    if not db.setup_check(db, RSS_conn, guild_id):
        await ctx.respond("Please make sure to run the /setup command")
        return
    channel_id = str(db.get_posting_channel(db, RSS_conn, guild_id))
    channel_mention = "<#" + channel_id + ">"
    status = db.remove_feed(db, RSS_conn, feed_url, guild_id)
    await ctx.respond(status + f" in {channel_mention}")

#Setup channel for RSS feed command
@catvenBot.slash_command(name = "rss-setup", description = "Set up the bot's RSS feeds by selecting a channel to post in")
async def setup_rss(ctx, channel: discord.TextChannel):
    setup_guild_id = str(ctx.guild.id)
    setup_channel_id = str(channel.id)
    db.setup_guild_channel(db, RSS_conn, setup_guild_id, setup_channel_id)
    await ctx.respond(f"Succesfully set {channel.mention} as the RSS feed channel")

#Check RSS feed setup info command
@catvenBot.slash_command(name = "rss-info", description = "View the bot's configs for your RSS feeds")
async def info_rss(ctx):
    guild_id = str(ctx.guild.id)
    guild = ctx.guild
    try:
        #if false prompt user to run /setup command
        if not db.setup_check(db, RSS_conn, guild_id):
            await ctx.respond("Please make sure to run the /setup command")
        #else list information regarding channel config
        else:
            channel_id = str(db.get_posting_channel(db, RSS_conn, guild_id))
            channel_mention = "<#" + channel_id + ">"
            await ctx.respond(f"{guild}'s RSS Feed channel is set to {channel_mention}")
            #cursor.execute("SELECT feed_url FROM RSS_Feeds WHERE guild_id=(?)", [guild_id])
    except sqlite3.Error as error:
        print("info command error: " , error)
        await ctx.respond("Please make sure to run the /setup command")

#
#TWITTER RELATED COMMANDS BELOW
#

#Add twitter user to post tweets from
@catvenBot.slash_command(name = "twitter-add", description = "add a twitter username to your feed list")
async def add_twitter(ctx, username:str):
    guild_id = ctx.guild.id

    if not db.setup_check(db, Twitter_conn, guild_id):
        await ctx.respond("Please make sure to run the /setup command")
        return
    channel_id = str(db.get_posting_channel(db, Twitter_conn, guild_id))
    posting_channel_mention = "<#" + channel_id + ">"
    result = db.add_feed(db, Twitter_conn, username, guild_id)
    await ctx.respond(result + f" in {posting_channel_mention}")

#Setup channel for Twitter feed command
@catvenBot.slash_command(name = "twitter-setup", description = "Set up the bot's Twitter feeds by selecting a channel to post in")
async def setup_twt(ctx, channel: discord.TextChannel):
    setup_guild_id = str(ctx.guild.id)
    setup_channel_id = str(channel.id)
    db.setup_guild_channel(db, Twitter_conn, setup_guild_id, setup_channel_id)
    await ctx.respond(f"Succesfully set {channel.mention} as the Twitter feed channel")

#run on startup - create tables, check connections, run bot token
def main():
    sql_create_feeds_table = "CREATE TABLE IF NOT EXISTS RSS_Feeds (guild_id string, channel_id string, feed_source string);"
    sql_create_twitter_list_table = "CREATE TABLE IF NOT EXISTS Twitter_Feeds (guild_id string, channel_id string, feed_source string);"
    if RSS_conn and Twitter_conn is not None:
        db.create_table(db, RSS_conn, sql_create_feeds_table)
        db.create_table(db, Twitter_conn, sql_create_twitter_list_table)
    else:
        print("Error: Cannot create the DB connection")

    catvenBot.run(os.getenv('TOKEN'))
    client = tweepy.Client(os.getenv('B_TOKEN'))
if __name__ == '__main__':
    main()
