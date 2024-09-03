import scrapy


class Book(scrapy.Item):
    name: str = scrapy.Field()
    price: str = scrapy.Field()
    rating: str = scrapy.Field()
    available: bool = scrapy.Field()
    category: str = scrapy.Field()
    url: str = scrapy.Field()
    image_url: str = scrapy.Field()
