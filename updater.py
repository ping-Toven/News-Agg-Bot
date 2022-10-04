from sqlite_db import SQLITE_DB
from aiohttp import ClientSession
import asyncio
import itertools
from typing import Any
from discord import Client, TextChannel


def start(loop, db: SQLITE_DB, client):
    """Start the async loop that will be checking for updates in RSS feeds

    Args:
        loop (itertools loop): _description_
        db (SQLITE_DB): _description_
        client (aiohttp client): _description_
    """
    update_feeds(loop, db, client)


def schedule_update(loop, db: SQLITE_DB, client):
    """Triggers the next loop cycle in 5 minutes

    Args:
        loop (itertools loop): _description_
        db (SQLITE_DB): _description_
        client (aiohttp client): _description_
    """
    loop.call_later(5*60, update_feeds, loop, db, client)
    print("Scheduled the next feed update")


def update_feeds(loop, db: SQLITE_DB, client):
    """Starts the timed loop cycle and creates the task

    Args:
        loop (_type_): _description_
        db (SQLITE_DB): _description_
        client (_type_): _description_
    """
    schedule_update(loop, db, client)
    loop.create_task(do_feed_update(db, client))


async def do_feed_update(db: SQLITE_DB, client):
    """_summary_

    Args:
        db (SQLITE_DB): _description_
        :param client:
    """
    print("Doing feed update")
    for guild_id, feeds in db.list_feeds(db, conn):
        print(f"Updating feeds for guild ID {guild_id}")
        await do_guild_feed_updates(guild_id, feeds, db, client)


async def do_guild_feed_updates(guild_id: str, feeds: list[str], db: SQLITE_DB, client):
    """_summary_

    Args:
        guild_id (str): _description_
        feeds (list[str]): _description_
        db (SQLITE_DB): _description_
        client (_type_): _description_
    """
    await asyncio.gather(*[update_feed(guild_id, feed_url, db, client) for feed_url in feeds])


async def update_feed(guild_id: str, feed_url: str, db: SQLITE_DB, client):
    """_summary_

    Args:
        guild_id (str): _description_
        feed_url (str): _description_
        db (SQLITE_DB): _description_
        client (_type_): _description_
    """
    feed_data = await get_latest_feed(feed_url)
    if feed_data:
        last_seen_guid = get_last_seen_item_guid(guild_id, feed_url, db)
        current_guid = feed_data[0]["guid"]["#text"]
        if last_seen_guid != current_guid:
            new_items = get_new_items_from_feed(feed_data, last_seen_guid)
            for item in new_items:
                await handle_new_item(item, guild_id, db, client)

                if last_seen_guid is None:
                    break

            save_new_guid(current_guid, guild_id, feed_url, db)


async def handle_new_item(item: dict, guild_id: str, db: SQLITE_DB, client):
    """_summary_

    Args:
        item (dict): _description_
        guild_id (str): _description_
        db (SQLITE_DB): _description_
        client (_type_): _description_
    """
    channel = get_guild_feed_update_channel(db, guild_id, client)
    if channel:
        await channel.send(f"**New Episode**\n{item['title']}\n{item['link']}")


async def get_latest_feed(feed_url: str) -> list[dict[str, Any]]:
    """_summary_

    Args:
        feed_url (str): _description_

    Returns:
        list[dict[str, Any]]: _description_
    """
    async with ClientSession() as session:
        async with session.get(feed_url) as response:
            print(f"Loaded {feed_url}")
            return xmltodict.parse(await response.content.read())["rss"]["channel"].get("item", [])


def get_new_items_from_feed(feed_data: list[dict], last_seen_guid: str) -> list[dict]:
    """_summary_

    Args:
        feed_data (list[dict]): _description_
        last_seen_guid (str): _description_

    Returns:
        list[dict]: _description_
    """
    items = []
    for item in itertools.islice(feed_data, 5):
        if item["guid"]["#text"] != last_seen_guid:
            items.append(item)

    return items


def get_guild_feed_update_channel(db: SQLITE_DB, guild_id: str, client: Client) -> TextChannel:
    """_summary_

    Args:
        db (SQLITE_DB): _description_
        guild_id (str): _description_
        client (Client): _description_

    Returns:
        TextChannel: _description_
    """
    channel_id = db.get("guilds", default={}).get(guild_id, None)
    if channel_id:
        return client.get_channel(channel_id)


def get_last_seen_item_guid(guild_id: str, feed_url: str, db: SQLITE_DB) -> str | None:
    """_summary_

    Args:
        guild_id (str): _description_
        feed_url (str): _description_
        db (SQLITE_DB): _description_

    Returns:
        str | None: _description_
    """
    guilds = db.get("items", default={})
    feeds = guilds.get(guild_id, {})
    guid = feeds.get(feed_url, None)
    return guid


def save_new_guid(new_guid: str, guild_id: str, feed_url: str, db: SQLITE_DB):
    """_summary_

    Args:
        new_guid (str): _description_
        guild_id (str): _description_
        feed_url (str): _description_
        db (SQLITE_DB): _description_
    """
    guilds = db.get("items", default={})
    feeds = guilds.get(guild_id, {})
    feeds[feed_url] = new_guid
    guilds[guild_id] = feeds
    db.set("items", guilds)
