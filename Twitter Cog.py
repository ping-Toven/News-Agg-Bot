import discord
from discord.ext import commands
from discord.commands import slash_command, Option
import sqlite_db
import sqlite3

# init SQLite DB Connections
table_twitter_discord = "Twitter_Usernames_Channels"
table_twitter_uid = "Twitter_UID_Map"
db = sqlite_db.SQLITE_DB
conn = db.get_connection(db)


class Twitter_Cog(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
        super().__init__()

    # Add twitter user to post tweets from
    @slash_command(name="twitter-add", description="add a twitter username to your feed list")
    async def add_twitter(self, ctx, username: str):
        """_summary_

        Args:
            ctx (_type_): _description_
            username (str): _description_
        """
        guild_id = ctx.guild.id

        if not db.setup_check(db, conn, guild_id, table_twitter_discord):
            await ctx.respond("Please make sure to run the /twitter-setup command")
            return
        channel_id = str(db.get_posting_channel(db, conn, guild_id, table_twitter_discord))
        posting_channel_mention = "<#" + channel_id + ">"
        result = db.add_feed(db, conn, username, guild_id, table_twitter_discord)
        await ctx.respond(result + f" in {posting_channel_mention}")

    # Remove RSS feed command
    @slash_command(name="twitter-remove", description="Remove a Twitter account from the bot's watchlist.")
    async def remove_twitter(self, ctx, username: str):
        """_summary_

        Args:
            ctx (_type_): _description_
            username (str): _description_
        """
        guild_id = str(ctx.guild.id)
        # if false prompt user to run /setup command
        if not db.setup_check(db, conn, guild_id, table_twitter_discord):
            await ctx.respond("Please make sure to run the /twitter-setup command")
            return
        channel_id = str(db.get_posting_channel(db, conn, guild_id, table_twitter_discord))
        channel_mention = "<#" + channel_id + ">"
        status = db.remove_feed(db, conn, username, guild_id, table_twitter_discord)
        await ctx.respond("Twitter", status,  f" in {channel_mention}")

    # Setup channel for Twitter feed command
    @slash_command(name="twitter-setup", description="Set up the bot's Twitter feeds by selecting a channel to post in")
    async def setup_twitter(self, ctx, channel: discord.TextChannel):
        """_summary_

        Args:
            ctx (_type_): _description_
            channel (discord.TextChannel): _description_
        """
        setup_guild_id = str(ctx.guild.id)
        setup_channel_id = str(channel.id)
        db.setup_guild_channel(db, conn, setup_guild_id, setup_channel_id, table_twitter_discord)
        await ctx.respond(f"Successfully set {channel.mention} as the Twitter feed channel")

    # Check RSS feed setup info command
    @slash_command(name="twitter-info", description="View the bot's configs for your Twitter feeds")
    async def info_twitter(self, ctx):
        """_summary_

        Args:
            ctx (_type_): _description_
        """
        guild_id = str(ctx.guild.id)
        guild = ctx.guild
        try:
            # if false prompt user to run /setup command
            if not db.setup_check(db, conn, guild_id, table_twitter_discord):
                await ctx.respond("Please make sure to run the /twitter-setup command")
                return
            # else list information regarding channel config
            else:
                channel_id = str(db.get_posting_channel(db, conn, guild_id, table_twitter_discord))
                channel_mention = "<#" + channel_id + ">"
                db_feed_list = db.list_guild_feeds(db, conn, table_twitter_discord, guild_id)
                i, feed_list = 0, ''
                while i < len(db_feed_list):
                    feeds = db_feed_list[i]
                    feeds = str(feeds)
                    feeds = feeds.strip("(),'")
                    if feeds == "None":
                        i += 1
                        continue
                    feed_list += "\n> - " + feeds
                    i += 1
                if feed_list == '':
                    await ctx.respond("Please make sure to add a feed with /twitter-add")
                    return
                await ctx.respond(
                    f"{guild}'s Twitter Feed channel is set to {channel_mention}\n{guild}'s Twitter Feeds are: {feed_list}")
        except sqlite3.Error as error:
            print("info command error: ", error)
            await ctx.respond("Please make sure to run the /twitter-setup command")


def setup(client):
    """_summary_

    Args:
        client (_type_): _description_
    """
    client.add_cog(Twitter_Cog(client))
    print("Added Twitter Cog")
