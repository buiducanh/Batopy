from scrapy.item import Item, Field

class Manga(Item):
    link = Field()
    name = Field()
