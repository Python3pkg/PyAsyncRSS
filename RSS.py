import bs4
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor

class RSSListener:
    def __init__(self, url, loop=None, callback=None):
        self.url = url
        self.callback = callback
        self.feed = None
        self.p = ThreadPoolExecutor()
        if not loop:
            self.loop = asyncio.get_event_loop()
            asyncio.ensure_future(self.listen(), loop=self.loop)
            self.loop.run_forever()
        else:
            self.loop = loop
            asyncio.ensure_future(self.listen(), loop=self.loop)

    async def listen(self):
        async with aiohttp.ClientSession(loop=self.loop) as session:
            async with session.get(self.url) as r:
                feed = Feed(await r.text())
        if self.feed and self.diff(feed, self.feed) and callable(self.callback):
            asyncio.run_coroutine_threadsafe(self.callback(self.diff(feed, self.feed)), self.loop)
        self.feed = feed
        asyncio.ensure_future(self.listen(), loop=self.loop)

    def diff(self, feed1, feed2):
        out = []
        items2 = [item.attrs for item in feed2.items]
        for item in feed1.items:
            if not item.attrs in items2: out.append(item)
        return out

class Feed:
    def __init__(self, content):
        self.soup = bs4.BeautifulSoup(content, "html.parser")
        self.channel = self.soup.find("channel")
        self.title = self.channel.find("title").text
        self.link = self.channel.find("link").text
        self.description = self.channel.find("description").text
        self.items = [Item(self, i) for i in self.soup.find_all("item")]

class Item:
    def __init__(self, feed, item):
        self.attrs = {child.name: child.text for child in item.findChildren()}
        self.title = item.find("title").text
        self.link = item.find("link").text
        self.description = item.find("description").text

async def callback(new):
    for item in new:
        print(item.title)
        print(item.description)
        print(item.link)
        print("-------------------")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    r = RSSListener("https://www.welt.de/feeds/latest.rss", callback=callback, loop=loop)
    r = RSSListener("https://www.heise.de/newsticker/heise.rdf", callback=callback, loop=loop)
    r = RSSListener("http://www.tagesschau.de/newsticker.rdf", callback=callback, loop=loop)
    loop.run_forever()