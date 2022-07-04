from venv import create
import discord
import logging
import os
import sqlite3
from sqlite3 import Error
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
RSS_database = "RSS_Feeds.db"
testBot = discord.Bot()
RSS_conn = sqlite3.connect(RSS_database)


#Function to create the tables & set cursor
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

def db_add_feed(feed_url, channel_id):
    """ add a feed URL from slash command to the db
    :param conn: Connection object
    :param feed_url: RSS feed url submitted by user in command "add"
    :param channel_id: Channel ID 
    :return:
    """
    cursor = RSS_conn.cursor()
    cursor.execute("INSERT INTO RSS_Feeds (feed_url) VALUES(?) WHERE channel_id=:cid", [feed_url], {"cid":channel_id})
    RSS_conn.commit()

def db_setup_guild_channel(guild_id, channel_id):
    """ add a guild_id:channel_id row in db
    :param guild_id: Guild ID
    :param channel_id: Channel ID 
    :return:
    """
    try:
        cursor = RSS_conn.cursor()
        cursor.execute("SELECT guild_id FROM RSS_Feeds WHERE guild_id = (?)", [guild_id])
        if cursor.fetchone() is None:
                cursor.execute("INSERT INTO RSS_Feeds (guild_id, channel_id) VALUES (?,?)", [guild_id, channel_id])
                RSS_conn.commit()
        else:
            cursor.execute("UPDATE RSS_Feeds SET channel_id=:cid WHERE guild_id=:gid", {"cid":channel_id, "gid":guild_id})
            RSS_conn.commit()
    except sqlite3.Error as error:
        print("Failed to setup guild's channel. Error: ", error)

#Write to terminal on login
@testBot.event
async def on_ready():
    print(f'Logged on as {testBot.user}!')

#Write to terminal on disconnect
@testBot.event
async def on_disconnect():
    #RSS_conn.close()
    print(f'Disconnected as {testBot.user} & closed DB connection')

#Slash command template
@testBot.slash_command(name = "hello", description = "Say hello to the bot")
async def hello(ctx):
    await ctx.respond("Hey!")

#Add RSS feed command
@testBot.slash_command(name = "add", description = "Add an RSS feed to the bot's watchlist.")
async def add(ctx, feed_url: str): 
    ...

#Remove RSS feed command
@testBot.slash_command(name = "remove", description = "Remove an RSS feed from the bot's watchlist.")
async def add(ctx, feed_url: str): 
    ...

#Setup channel for RSS feed command
@testBot.slash_command(name = "setup_rss", description = "Set up the bot's RSS feeds by selecting a channel to post in")
async def setup_rss(ctx, channel: discord.TextChannel): 
    setup_guild_id = str(ctx.guild.id)
    setup_channel_id = str(channel.id)
    db_setup_guild_channel(guild_id=setup_guild_id, channel_id=setup_channel_id)
    await ctx.respond(f"Succesfully set {channel.mention} as the RSS feed channel")

#Check RSS feed setup info command
@testBot.slash_command(name = "info", description = "View the bot's configs for your RSS feeds")
async def info(ctx):
    cursor = RSS_conn.cursor()
    guild_id = str(ctx.guild.id)
    guild = ctx.guild
    try:
        cursor.execute("SELECT guild_id FROM RSS_Feeds WHERE guild_id = (?)", [guild_id])
        if cursor.fetchone() is None:
            await ctx.respond("Please make sure to run the /setup command")
        else:
            cursor.execute("SELECT channel_id FROM RSS_Feeds WHERE guild_id=:gid", {"gid":guild_id})
            feed_channel_id = str(cursor.fetchone()[0])
            feed_channel_mention = "<#" + feed_channel_id + ">"
            await ctx.respond(f"{guild}'s RSS Feed channel is set to {feed_channel_mention}")

    except sqlite3.Error as error:
        print("info command error: " , error)
        await ctx.respond("Please make sure to run the /setup command")

def main():
    sql_create_feeds_table = "CREATE TABLE IF NOT EXISTS RSS_Feeds (guild_id string, channel_id string, feed_url string);"

    if RSS_conn is not None:
        create_table(conn = RSS_conn, create_table_sql = sql_create_feeds_table)
    else:
        print("Error: Cannot create the DB connection")

    testBot.run(os.getenv('TOKEN'))

if __name__ == '__main__':
    main()
