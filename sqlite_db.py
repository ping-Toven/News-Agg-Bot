import sqlite3
from sqlite3 import Error


#
# SQLite DB Helper functions
#

class SQLITE_DB:
    # Function to create the tables
    def create_table(self, conn, create_table_sql):
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

    # Function to check if guild has been set up in DB
    def setup_check(self, conn: sqlite3.Connection, gid: str):
        """ Check for the guild_id in the DB
        :param conn: sqlite3 connection obj
        :param gid: command's ctx guild id
        :return bool: True = guild has been set up in this DB, False = not set up
        """
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        table_name, = cursor.fetchone()
        cursor.execute("SELECT guild_id FROM {} WHERE guild_id = (?)".format(table_name), [gid])
        # SQL statement will return guild_id as provided by command if the DBs are set up. Otherwise, returns None
        if cursor.fetchone() is None:
            return False
        else:
            return True

    # Function to set up a guild with a specific channel id for a feed (RSS & Twitter separate dbs / channels)
    def setup_guild_channel(self, conn:sqlite3.Connection, guild_id: str, channel_id: str):
        """ add a guild_id:channel_id row in db
        :param conn: Connection object
        :param guild_id: Guild ID str
        :param channel_id: Channel ID str
        :return:
        """
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            table_name, = cursor.fetchone()
            # if setup has not happened, insert new row
            if not self.setup_check(conn, guild_id):
                cursor.execute("INSERT INTO {} (guild_id, channel_id) VALUES (?,?)".format(table_name),
                               [guild_id, channel_id])
                conn.commit()
            # else update existing
            else:
                cursor.execute("UPDATE {} SET channel_id = (?) WHERE guild_id = (?)".format(table_name),
                               [channel_id, guild_id])
                conn.commit()
        except sqlite3.Error as error:
            print("Failed to setup guild's channel. Error: ", error)

    def get_posting_channel(self, conn:sqlite3.Connection, guild_id: str):
        """ fetch posting channel from guild
        :param conn: db connection obj
        :param guild_id: Guild ID str
        :return str: Error or feed channel id
        """
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        table_name, = cursor.fetchone()
        # if setup has not happened, abort
        if not self.setup_check(conn, guild_id):
            return
        else:
            cursor.execute("SELECT channel_id FROM {} WHERE guild_id=(?)".format(table_name), [guild_id])
            feed_channel_id, = cursor.fetchone()
            return feed_channel_id

    #Function to check if feed_source has been added to guild specific DB
    def feed_check(self, conn: sqlite3.Connection, feed_key:str, gid:str):
        """ Check for a feed value in the Guild's DB
        :param search_key: command's feed input to check against
        :param gid: Guild ID in which to look for search_key 
        :return bool:
        """
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        table_name, = cursor.fetchone()
        cursor.execute("SELECT feed_source FROM {} WHERE guild_id = (?)".format(table_name), [gid])
        guild_feeds = cursor.fetchall()
        for feed, in guild_feeds:
            if feed == feed_key:
                return True
        return False

    # Function to add a feed source to the guild's DB
    def add_feed(self, conn:sqlite3.Connection, feed_source:str, guild_id:str):
        """ add a feed source from slash command to the db
        :param conn: sqlite3 connection object
        :param feed_source: feed source submitted by user in command "add"
        :param guild_id: Guild ID
        :return str: one of the 2 statuses
        """
        existing_feed = "Feed already added"
        successful = "Feed added successfully"
        feed_channel_id = self.get_posting_channel(conn, guild_id)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        table_name, = cursor.fetchone()
        if self.feed_check(conn, feed_source, guild_id):
            return existing_feed
        else:
            cursor.execute("INSERT INTO {} (guild_id, channel_id, feed_source) VALUES (?,?,?)".format(table_name),
                           [guild_id, feed_channel_id, feed_source])
            conn.commit()
            return successful

    # Function to remove an existing RSS Feed url from guild's DB
    def remove_feed(self, conn, feed_source: str, guild_id: str):
        """ remove an existing feed URL from guild specific DB entries
        :param conn: sqlite3 connection object
        :param feed_source: feed submitted by user in command
        :param guild_id: Guild ID
        :return str: one of the 2 statuses
        """
        unknown_feed = "Feed does not exist"
        successful = "Feed removed successfully"
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        table_name, = cursor.fetchone()
        if not self.feed_check(conn, feed_source, guild_id):
            return unknown_feed
        else:
            cursor.execute("DELETE FROM {} WHERE feed_source = (?) AND guild_id = (?)".format(table_name), [feed_source, guild_id])
            conn.commit()
            return successful