import json
import scrapy
import re
import pprint

pp = pprint.PrettyPrinter()
file = open("tmp/batofollows.json", 'r')
manga_json = json.load(file)
manga_map = {}
regex = 'https://bato.to/comic/[^/]*/[^/]*/(.*)'
for manga in manga_json:
    link = re.search(regex, manga['link']).group(1)
    manga_map[link] = manga['name']

class BatoList(scrapy.Spider):
    name = 'batolist'
    start_urls = map(lambda x: x['link'], manga_json)[0:1]
    custom_settings = {
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_DEBUG': True
    }
    def parse(self, response):
        link = re.search(regex, response.url).group(1)
        xpath = ".//div[@id='content']/div[2]/div[1]/div[3]/div[1]/div[2]/table/tr[4]/td[2]/a/span/text()"
        genres = response.xpath(xpath)
        yield {'name': manga_map[link], 'genres': genres.extract()}
