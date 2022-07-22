import discord
from discord.ext import commands
from discord.commands import slash_command, Option
import sqlite_db
import sqlite3

# init SQLite DB Conncetions
table_RSS = "RSS"
conn = sqlite3.connect("Feeds.DB")
db = sqlite_db.SQLITE_DB
sql_create_RSS_Feeds_table = "CREATE TABLE IF NOT EXISTS RSS (guild string, channel string, " \
                                "source string); "
if conn is not None:
    db.create_table(db, conn, sql_create_RSS_Feeds_table)


class RSS_Cog(commands.Cog):
    def __init__(self, client) -> None:
        self.client = client
        super().__init__()

    # Add RSS feed command
    @slash_command(name="rss-add", description="Add an RSS feed to the bot's watchlist.")
    async def add_rss(self, ctx, feed_url: Option(str, "Enter the URL of the RSS Feed you'd like to add")):
        guild_id = str(ctx.guild.id)
        # if false prompt user to run /setup command
        if not db.setup_check(db, conn, guild_id, table_RSS):
            await ctx.respond("Please make sure to run the /setup command")
            return
        channel_id = str(db.get_posting_channel(db, conn, guild_id, table_RSS))
        channel_mention = "<#" + channel_id + ">"
        status = db.add_feed(db, conn, feed_url, guild_id, table_RSS)
        await ctx.respond(status + f" in {channel_mention}")

    # Remove RSS feed command
    @slash_command(name="rss-remove", description="Remove an RSS feed from the bot's watchlist.")
    async def remove_rss(self, ctx, feed_url: str):
        guild_id = str(ctx.guild.id)
        # if false prompt user to run /setup command
        if not db.setup_check(db, conn, guild_id, table_RSS):
            await ctx.respond("Please make sure to run the /setup command")
            return
        channel_id = str(db.get_posting_channel(db, conn, guild_id, table_RSS))
        channel_mention = "<#" + channel_id + ">"
        status = db.remove_feed(db, conn, feed_url, guild_id, table_RSS)
        await ctx.respond(status + f" in {channel_mention}")

    # Setup channel for RSS feed command
    @slash_command(name="rss-setup", description="Set up the bot's RSS feeds by selecting a channel to post in")
    async def setup_rss(self, ctx, channel: discord.TextChannel):
        setup_guild_id = str(ctx.guild.id)
        setup_channel_id = str(channel.id)
        db.setup_guild_channel(db, conn, setup_guild_id, setup_channel_id, table_RSS)
        await ctx.respond(f"Succesfully set {channel.mention} as the RSS feed channel")

    # Check RSS feed setup info command
    @slash_command(name="rss-info", description="View the bot's configs for your RSS feeds")
    async def info_rss(self, ctx):
        guild_id = str(ctx.guild.id)
        guild = ctx.guild
        try:
            # if false prompt user to run /setup command
            if not db.setup_check(db, conn, guild_id, table_RSS):
                await ctx.respond("Please make sure to run the /setup command")
            # else list information regarding channel config
            else:
                channel_id = str(db.get_posting_channel(db, conn, guild_id, table_RSS))
                channel_mention = "<#" + channel_id + ">"
                await ctx.respond(f"{guild}'s RSS Feed channel is set to {channel_mention}")
                # cursor.execute("SELECT feed_url FROM RSS_Feeds WHERE guild_id=(?)", [guild_id])
        except sqlite3.Error as error:
            print("info command error: ", error)
            await ctx.respond("Please make sure to run the /setup command")


def setup(client):
    client.add_cog(RSS_Cog(client))
    print("Added RSS Feed Cog")
