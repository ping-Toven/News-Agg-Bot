import discord
from discord.ext import commands
from discord.commands import slash_command, Option
import sqlite_db
import sqlite3

#init SQLite DB Conncetions
Twitter_database = "Twitter_Feeds.db"
conn = sqlite3.connect(Twitter_database)
db = sqlite_db.SQLITE_DB
sql_create_twitter_list_table = "CREATE TABLE IF NOT EXISTS Twitter_Feeds (guild_id string, channel_id string, feed_source string);"

if  conn is not None:
    db.create_table(db, conn, sql_create_twitter_list_table)

class Twitter_Cog(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
        super().__init__()

    #Add twitter user to post tweets from
    @slash_command(name = "twitter-add", description = "add a twitter username to your feed list")
    async def add_twitter(self, ctx, username:str):
        guild_id = ctx.guild.id

        if not db.setup_check(self, db, conn, guild_id):
            await ctx.respond("Please make sure to run the /twitter-setup command")
            return
        channel_id = str(db.get_posting_channel(self, db, conn, guild_id))
        posting_channel_mention = "<#" + channel_id + ">"
        result = db.add_feed(self, db, conn, username, guild_id)
        await ctx.respond(result + f" in {posting_channel_mention}")

    #Remove RSS feed command
    @slash_command(name = "twitter-remove", description = "Remove a Twitter account from the bot's watchlist.")
    async def remove_twitter(self, ctx, username: str):
        guild_id = str(ctx.guild.id)
        #if false prompt user to run /setup command
        if not db.setup_check(db, conn, guild_id):
            await ctx.respond("Please make sure to run the /twitter-setup command")
            return
        channel_id = str(db.get_posting_channel(db, conn, guild_id))
        channel_mention = "<#" + channel_id + ">"
        status = db.remove_feed(db, conn, username, guild_id)
        await ctx.respond(status + f" in {channel_mention}")

    #Setup channel for Twitter feed command
    @slash_command(name = "twitter-setup", description = "Set up the bot's Twitter feeds by selecting a channel to post in")
    async def setup_twitter(self, ctx, channel: discord.TextChannel):
        setup_guild_id = str(ctx.guild.id)
        setup_channel_id = str(channel.id)
        db.setup_guild_channel(self, db, conn, setup_guild_id, setup_channel_id)
        await ctx.respond(f"Succesfully set {channel.mention} as the Twitter feed channel")

    #Check RSS feed setup info command
    @slash_command(name = "twitter-info", description = "View the bot's configs for your Twitter feeds")
    async def info_twitter(self, ctx):
        guild_id = str(ctx.guild.id)
        guild = ctx.guild
        try:
            #if false prompt user to run /setup command
            if not db.setup_check(db, conn, guild_id):
                await ctx.respond("Please make sure to run the /twitter-setup command")
            #else list information regarding channel config
            else:
                channel_id = str(db.get_posting_channel(db, conn, guild_id))
                channel_mention = "<#" + channel_id + ">"
                await ctx.respond(f"{guild}'s RSS Feed channel is set to {channel_mention}")
                #cursor.execute("SELECT feed_url FROM RSS_Feeds WHERE guild_id=(?)", [guild_id])
        except sqlite3.Error as error:
            print("info command error: " , error)
            await ctx.respond("Please make sure to run the /twitter-setup command")

def setup(client):
    client.add_cog(Twitter_Cog(client))
    print("Added Twitter Cog")