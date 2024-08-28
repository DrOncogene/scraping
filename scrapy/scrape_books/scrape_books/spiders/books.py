import scrapy
from scrapy.responsetypes import Response
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose

from scrape_books.items import Book


def scrape_page(url: str) -> list[str]:
    pass


class BooksSpider(scrapy.Spider):
    name = "books"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]
    page = 0
    custom_settings = {
        "FEEDS": {
            "data/books.json": {
                'format': 'json',
                'encoding': 'utf-8',
                'indent': 2,
                'overwrite': True

            }
        },
        "FEED_EXPORTERS": {
            'json': 'scrape_books.exporters.JsonGroupedItemExporter'
        }
    }

    def parse(self, response: Response):
        self.page += 1
        print(f"SCRAPING PAGE {self.page}...")

        books_on_page = response.css('.product_pod .image_container a::attr(href)').getall()
        next_page = response.css('li.next a::attr(href)').get()

        for book in books_on_page:
            yield response.follow(url=book, callback=self.parse_book)

        if next_page:
            yield response.follow(url=next_page, callback=self.parse)


    def parse_book(self, response: Response):
        """
        scrapes individual book page
        """

        loader = ItemLoader(item=Book(), response=response)
        loader.default_output_processor = TakeFirst()
        loader.image_url_in = MapCompose(lambda s: response.urljoin(s))

        rating = response.css(".star-rating::attr(class)").get()
        available = response.css(".availability::attr(class)").get()

        loader.add_value('rating', rating.split()[1] if rating else "")
        loader.add_value('available', "instock" in str(available).lower())
        loader.add_value('url', response.url)
        loader.add_css('image_url', '.thumbnail img::attr(src)')
        loader.add_css('name', '.product_main h1::text')
        loader.add_css('price', '.product_main .price_color::text')
        loader.add_css('category', '.breadcrumb li:nth-last-child(2) a::text')

        yield loader.load_item()
