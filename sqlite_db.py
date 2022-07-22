import sqlite3
from sqlite3 import Error


class SQLITE_DB:
    # Function to create the tables
    def create_table(self, conn: sqlite3.Connection, create_table_sql):
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

    def get_connection(self):
        """ Get the corresponding db connection object
        :param db_name: name of database to connect to
        :return sqlite3.Connection: returns connection object
        """
        conn_feeds = sqlite3.connect("Feeds.db")
        return conn_feeds

    # Function to check if guild has been set up in DB
    def setup_check(self, conn: sqlite3.Connection, gid: str, table: str):
        """ Check for the guild_id in the DB
        :param table: table to check in db
        :param conn: sqlite3 connection obj
        :param gid: command's ctx guild id
        :return bool: True = guild has been set up in this DB, False = not set up
        """
        cursor = conn.cursor()
        cursor.execute("SELECT guild FROM {} WHERE guild = (?)".format(table), [gid])
        # SQL statement will return guild_id as provided by command if the DBs are set up. Otherwise, returns None
        if cursor.fetchone() is None:
            return False
        else:
            return True

    # Function to set up a guild with a specific channel id for a feed (RSS & Twitter separate dbs / channels)
    def setup_guild_channel(self, conn: sqlite3.Connection, guild_id: str, channel_id: str, table: str):
        """ add a guild_id:channel_id row in db
        :param table: table within which to set up this guild
        :param conn: Connection object
        :param guild_id: Guild ID str
        :param channel_id: Channel ID str
        :return:
        """
        try:
            cursor = conn.cursor()
            # if setup has not happened, insert new row
            if not self.setup_check(self, conn, guild_id):
                cursor.execute("INSERT INTO {} (guild, channel) VALUES (?,?)".format(table),
                               [guild_id, channel_id])
                conn.commit()
            # else update existing
            else:
                cursor.execute("UPDATE {} SET channel = (?) WHERE guild = (?)".format(table),
                               [channel_id, guild_id])
                conn.commit()
        except sqlite3.Error as error:
            print("Failed to setup guild's channel. Error: ", error)

    def get_posting_channel(self, conn: sqlite3.Connection, guild_id: str, table: str):
        """ fetch posting channel from guild
        :param table: table within which to grab channel from
        :param conn: db connection obj
        :param guild_id: Guild ID str
        :return str: Error or feed channel id
        """
        cursor = conn.cursor()
        # if setup has not happened, abort
        if not self.setup_check(self, conn, guild_id):
            return
        else:
            cursor.execute("SELECT channel FROM {} WHERE guild = (?)".format(table), [guild_id])
            feed_channel_id, = cursor.fetchone()
            return feed_channel_id

    # Function to check if a specified feed source has been added to a specified guild
    def feed_check(self, conn: sqlite3.Connection, feed_key: str, gid: str, table: str):
        """ Check for a feed value in the Guild's DB
        :param table: table within which to check feed_key for
        :param conn: sqlite3 connection obj
        :param feed_key: command's feed input to check against
        :param gid: Guild ID in which to look for search_key
        :return bool:
        """
        cursor = conn.cursor()
        cursor.execute("SELECT source FROM {} WHERE guild = (?)".format(table), [gid])
        guild_feeds = cursor.fetchall()
        for feed, in guild_feeds:
            if feed == feed_key:
                return True
        return False

    # Function to add a feed source to the guild's DB
    def add_feed(self, conn: sqlite3.Connection, feed_source: str, guild_id: str, table: str):
        """ add a feed source from slash command to the db
        :param table: table within which to add the feed_source to
        :param conn: sqlite3 connection object
        :param feed_source: feed source submitted by user in command "add"
        :param guild_id: Guild ID
        :return str: one of the 2 statuses
        """
        existing_feed = "Feed already added"
        successful = "Feed added successfully"
        feed_channel_id = self.get_posting_channel(self, conn=conn, guild_id=guild_id, table=table)
        cursor = conn.cursor()
        if self.feed_check(self, conn, feed_source, guild_id, table):
            return existing_feed
        else:
            cursor.execute("INSERT INTO {} (guild, channel, source) VALUES (?,?,?)".format(table),
                           [guild_id, feed_channel_id, feed_source])
            conn.commit()
            return successful

    # Function to remove an existing RSS Feed url from guild's DB
    def remove_feed(self, conn: sqlite3.Connection, feed_source: str, guild_id: str, table: str):
        """ remove an existing feed URL from guild specific DB entries
        :param table: table within which to remove feed_source
        :param conn: sqlite3 connection object
        :param feed_source: feed submitted by user in command
        :param guild_id: Guild ID
        :return str: one of the 2 statuses
        """
        unknown_feed = "Feed does not exist"
        successful = "Feed removed successfully"
        cursor = conn.cursor()
        if not self.feed_check(self, conn, feed_source, guild_id, table):
            return unknown_feed
        else:
            cursor.execute("DELETE FROM {} WHERE source = (?) AND guild = (?)".format(table),
                           [feed_source, guild_id])
            conn.commit()
            return successful

    def list_feeds(self, conn: sqlite3.Connection, table: str):
        """ Fetch all guild:feeds in a list from a single table
        :param table: table name from which to pull
        :param conn: sqlite3 connection object
        :return feed_list: returns a list of all the feeds
        """
        cursor = conn.cursor()
        cursor.execute("SELECT guild, source FROM {}".format(table))
        feed_list = cursor.fetchall()
        return feed_list
