from typing import Iterable
import scrapy
from scrapy.http import Request
from scrapy.loader import ItemLoader
from scrapy.responsetypes import Response
from scrapy_splash import SplashRequest, SplashResponse
from itemloaders.processors import TakeFirst, MapCompose
from scrapy.selector import Selector

from scrape_books_splash.items import Book


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
}


class BooksSpider(scrapy.Spider):
    name = "books"
    # allowed_domains = ["books.toscrape.com"]
    custom_settings = {
        "FEEDS": {
            "data/books.json": {
                "format": "json",
                "encoding": "utf-8",
                "indent": 2,
                "overwrite": True,
            }
        },
        "FEED_EXPORTERS": {
            "json": "scrape_books_splash.exporters.JsonGroupedItemExporter"
        },
    }
    page = 0

    def start_requests(self) -> Iterable[Request]:
        urls = ["https://books.toscrape.com"]
        for url in urls:
            yield SplashRequest(
                url,
                callback=self.parse,
                headers=HEADERS,
                encoding="utf-8",
                method="GET",
            )

    def parse(self, response: SplashResponse):
        self.page += 1
        print(f"SCRAPING PAGE {self.page}...")

        books_on_page = response.css(".product_pod h3 a::attr(href)").getall()
        next_page = response.css(".pager .next > a::attr(href)").get()

        for book_url in books_on_page:
            yield response.follow(
                url=book_url,
                callback=self.parse_book,
                headers=HEADERS,
                meta={
                    "splash": {
                        "endpoint": "render.html",
                    }
                },
            )

        yield response.follow(
            url=next_page,
            callback=self.parse,
            headers=HEADERS,
            meta={
                "splash": {
                    "endpoint": "render.html",
                }
            },
            encoding="utf-8",
        )

    def parse_book(self, response: Response):
        """
        scrapes individual book page
        """

        loader = ItemLoader(item=Book(), response=response)
        loader.default_output_processor = TakeFirst()
        loader.image_url_in = MapCompose(lambda s: response.urljoin(s))

        rating = response.css(".star-rating::attr(class)").get()
        available = response.css(".availability::attr(class)").get()

        loader.add_value("rating", rating.split()[1] if rating else "")
        loader.add_value("available", "instock" in str(available).lower())
        loader.add_value("url", response.url)
        loader.add_css("image_url", ".thumbnail img::attr(src)")
        loader.add_css("name", ".product_main h1::text")
        loader.add_css("price", ".product_main .price_color::text")
        loader.add_css("category", ".breadcrumb li:nth-last-child(2) a::text")

        yield loader.load_item()
