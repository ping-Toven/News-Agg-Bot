import discord
from discord.ext import commands
from discord.commands import slash_command, Option
import sqlite_db
import sqlite3

# init SQLite DB Conncetions
table_RSS_Feeds = "RSS_Feeds_Channels"
db = sqlite_db.SQLITE_DB
conn = db.get_connection(db)

class RSS_Cog(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
        super().__init__()

    # Add RSS feed command
    @slash_command(name="rss-add", description="Add an RSS feed to the bot's watchlist.")
    async def add_rss(self, ctx, feed_url: Option(str, "Enter the URL of the RSS Feed you'd like to add")):
        """_summary_

        Args:
            ctx (_type_): _description_
            feed_url (Option): _description_
        """
        guild_id = str(ctx.guild.id)
        # if false prompt user to run /setup command
        if not db.setup_check(db, conn, guild_id, table_RSS_Feeds):
            await ctx.respond("Please make sure to run the /setup command")
            return
        channel_id = str(db.get_posting_channel(db, conn, guild_id, table_RSS_Feeds))
        channel_mention = "<#" + channel_id + ">"
        status = db.add_feed(db, conn, feed_url, guild_id, table_RSS_Feeds)
        await ctx.respond(status + f" in {channel_mention}")

    # Remove RSS feed command
    @slash_command(name="rss-remove", description="Remove an RSS feed from the bot's watchlist.")
    async def remove_rss(self, ctx, feed_url: str):
        """_summary_

        Args:
            ctx (_type_): _description_
            feed_url (str): _description_
        """
        guild_id = str(ctx.guild.id)
        # if false prompt user to run /setup command
        if not db.setup_check(db, conn, guild_id, table_RSS_Feeds):
            await ctx.respond("Please make sure to run the /setup command")
            return
        channel_id = str(db.get_posting_channel(db, conn, guild_id, table_RSS_Feeds))
        channel_mention = "<#" + channel_id + ">"
        status = db.remove_feed(db, conn, feed_url, guild_id, table_RSS_Feeds)
        await ctx.respond(status + f" in {channel_mention}")

    # Setup channel for RSS feed command
    @slash_command(name="rss-setup", description="Set up the bot's RSS feeds by selecting a channel to post in")
    async def setup_rss(self, ctx, channel: discord.TextChannel):
        """_summary_

        Args:
            ctx (_type_): _description_
            channel (discord.TextChannel): _description_
        """
        setup_guild_id = str(ctx.guild.id)
        setup_channel_id = str(channel.id)
        db.setup_guild_channel(db, conn, setup_guild_id, setup_channel_id, table_RSS_Feeds)
        await ctx.respond(f"Succesfully set {channel.mention} as the RSS feed channel")

    # Check RSS feed setup info command
    @slash_command(name="rss-info", description="View the bot's configs for your RSS feeds")
    async def info_rss(self, ctx):
        """_summary_

        Args:
            ctx (_type_): _description_
        """
        guild_id = str(ctx.guild.id)
        guild = ctx.guild
        try:
            # if false prompt user to run /setup command
            if not db.setup_check(db, conn, guild_id, table_RSS_Feeds):
                await ctx.respond("Please make sure to run the /rss-setup command")
            # else list information regarding channel config
            else:
                channel_id = str(db.get_posting_channel(db, conn, guild_id, table_RSS_Feeds))
                channel_mention = "<#" + channel_id + ">"
                db_feed_list = db.list_guild_feeds(db, conn, table_RSS_Feeds, guild_id)
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
                    await ctx.respond("Please make sure to add a feed with /rss-add")
                    return
                await ctx.respond(
                    f"{guild}'s RSS Feed channel is set to {channel_mention}\n{guild}'s RSS Feeds are: {feed_list}")
        except sqlite3.Error as error:
            print("info command error: ", error)
            await ctx.respond("Please make sure to run the /rss-setup command")


def setup(client):
    """_summary_

    Args:
        client (_type_): _description_
    """
    client.add_cog(RSS_Cog(client))
    print("Added RSS Feed Cog")
