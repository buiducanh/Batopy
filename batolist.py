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

attributes_list = [('authors', '/a'), ('artists', '/a'),
                   ('genres', '/a/span'), ('type', ''),
                   ('status', ''), ('description', '')]


class BatoList(scrapy.Spider):
    name = 'batolist'
    start_urls = map(lambda x: x['link'], manga_json)
    custom_settings = {
        'AUTOTHROTTLE_ENABLED': True,
        'AUTOTHROTTLE_DEBUG': True,
        'DOWNLOAD_DELAY': 2,
    }

    def parse(self, response):
        link = re.search(regex, response.url).group(1)
        xpath = ".//div[@id='content']/div[2]/div[1]/div[3]/div[1]/div[2]/table\
        /tr[{0}]/td[2]{1}/text()"
        result_hash = {'name': manga_map[link]}
        for idx, (attr, path) in enumerate(attributes_list, start=2):
            data = response.xpath(xpath.format(idx, path))
            if len(data) > 1:
                data = data.extract()
            else:
                data = data.extract_first()
            result_hash.update({attr: data})
        yield result_hash
