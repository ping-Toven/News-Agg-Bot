import logging
import os
import discord
from dotenv import load_dotenv
import sqlite_db

load_dotenv()
# set up logging module for pycord
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
# init discord bot
newsAggBot = discord.Bot()
# init SQLite DB Connections
db = sqlite_db.SQLITE_DB
# registering cog names
Cog_Files = ['RSS Cog', 'Twitter Cog']


# Write to terminal on login
@newsAggBot.event
async def on_ready():
    """_summary_
    """
    print(f'Logged on as {newsAggBot.user}!')


# Write to terminal on disconnect
@newsAggBot.event
async def on_disconnect():
    """_summary_
    """
    print(f'Disconnected as {newsAggBot.user}')


# Slash command template
@newsAggBot.slash_command(name="hello", description="Say hello to the bot")
async def hello(ctx):
    """_summary_

    Args:
        ctx (_type_): _description_
    """
    await ctx.respond("Hey!")


# run on startup - create tables, check connections, run bot token
def main():
    """_summary_
    """
    for extension in Cog_Files:
        newsAggBot.load_extension(extension)
        print("Cogs Loaded")
    newsAggBot.run(os.getenv('TOKEN'))


if __name__ == '__main__':
    main()
