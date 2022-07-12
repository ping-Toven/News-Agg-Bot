import logging
import sqlite3
import os
import discord
from discord.ext import commands
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
db = sqlite_db.SQLITE_DB
#registering cog names
Cog_Files = ['RSS Cog', 'Twitter Cog']

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

#run on startup - create tables, check connections, run bot token
def main():
    for extension in Cog_Files:
        catvenBot.load_extension(extension)
        print("Cogs Loaded")
    client = tweepy.Client(os.getenv('B_TOKEN'))
    catvenBot.run(os.getenv('TOKEN'))

if __name__ == '__main__':
    main()
