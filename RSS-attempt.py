import requests
from xml.etree import ElementTree
from xml.dom import minidom
import aiohttp
import asyncio
import io
import hashlib
from xml.dom import Node
import feedparser
from xml.dom.minidom import Element as DOMElement

class RSSListener:
    def __init__(self, url, loop=None, callback=None):
        self.url = url
        self.loop = loop
        self.callback = callback

    async def listen(self):
        pass

class Feed:
    def __init__(self, data):
        self.parsed = minidom.parseString(data.replace("\n", "").replace("\t", "").replace('  ', ""))
        self.root = [el for el in self.parsed.childNodes if type(el) == DOMElement][0]
        # self.root = self.parsed.getElementsByTagName("rdf:RDF")[0]
        self.channel = Item(self.root.firstChild)
        # print(self.root.firstChild)
        self.items = [Item(i) for i in self.root.childNodes[1:]]

class Item:
    def __init__(self, data):
        self.dict = {tag.tagName: tag.firstChild.nodeValue for tag in data.childNodes}
        self.title = self.dict.get("title", None)
        self.link = self.dict.get("link", None)
        self.description = self.dict.get("description", None)

# rdf = requests.get("https://www.heise.de/newsticker/heise.rdf").content.decode()
rdf = requests.get("http://www.tagesschau.de/newsticker.rdf").content.decode()
print(rdf)
"""doc = io.StringIO(r.content.decode())
parsed = minidom.parse(doc)
rss = parsed.getElementsByTagName("rdf:RDF")[0]
print(rss)
channel = rss.getElementsByTagName("channel")[0]
print(channel)
title = channel.getElementsByTagName("title")[0]
print(title.tagName)"""

f = Feed(rdf)
for item in f.items:
    print("---------------------------------------------------------")
    print(item.title)
    print(item.description)
    print(item.link)