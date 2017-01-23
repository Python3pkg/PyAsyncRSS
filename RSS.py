import feedparser
import requests
import asyncio
import aiohttp
import hashlib

class RSSListener:
    def __init__(self, url, loop=None, callback=None):
        self.url = url
        self.loop = loop
        self.callback = callback
        self.feed = None
        self.hashes = set()
        if not loop:
            self.loop = loop
            asyncio.ensure_future(self.listen(), loop=self.loop)
            self.loop.run_forever()
        elif loop:
            self.loop = loop
            asyncio.ensure_future(self.listen(), loop=self.loop)

    async def listen(self):
        async with aiohttp.ClientSession(loop=self.loop) as session:
            async with session.get(self.url) as r:
                feed = Feed(await r.text())
        for item in feed.items:
            self.hashes.add(item.hash)
        diff = list(self.diff(feed))
        if self.feed and diff and callable(self.callback): asyncio.ensure_future(self.callback(diff, feed), loop=self.loop)
        self.feed = feed
        asyncio.ensure_future(self.listen(), loop=self.loop)

    def diff(self, feed):
        for item in feed.items:
            if not item.hash in self.hashes:
                yield item
class Feed:
    def __init__(self, rss):
        feed = feedparser.parse(rss)
        self.channel = Item(feed["channel"], self)
        self.items = [Item(i, self) for i in feed["items"]]

class Item:
    def __init__(self, i, feed):
        self.feed = feed
        self.dict = i
        self.title = self.dict.get("title", None)
        self.link = self.dict.get("link", None)
        self.description = self.dict.get("description", None)
        self.hash = hashlib.md5(str(self.title).encode()+str(self.link).encode()+str(self.description).encode())

async def callback(new, feed):
    print("-------------------------------")
    print(new.title)
    print(new.description)
    print(new.link)

loop = asyncio.get_event_loop()
RSSListener("https://www.welt.de/feeds/latest.rss", callback=callback, loop=loop)
RSSListener("https://www.heise.de/newsticker/heise.rdf", callback=callback, loop=loop)
RSSListener("http://www.tagesschau.de/newsticker.rdf", callback=callback, loop=loop)
RSSListener("http://www.gamespot.com/feeds/reviews/", callback=callback, loop=loop)
RSSListener("http://www.gamespot.com/feeds/new-games/", callback=callback, loop=loop)
RSSListener("http://www.gamespot.com/feeds/news/", callback=callback, loop=loop)
RSSListener("http://rss.nytimes.com/services/xml/rss/nyt/World.xml", callback=callback, loop=loop)
RSSListener("http://rss.focus.de/fol/XML/rss_folnews_eilmeldungen.xml", callback=callback, loop=loop)
RSSListener("http://rss.focus.de/fol/XML/rss_folnews.xml", callback=callback, loop=loop)
loop.run_forever()