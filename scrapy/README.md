## Web Scraping with Scrapy

Practising web scraping with Scrapy and splash. There are multiple Scrapy projects in this directory.

1. `scrape_books`: scraping books.toscrape.com with Scrapy only
2. `scrape_books_splash`: scraping books.toscrape.com with Scrapy and Splash

### Install

- Clone the repo
- Install poetry from [here](https://python-poetry.org/docs/#installation)
- Navigate to this directory: `cd scrapy`
- Run `poetry install`.

### Run the project

1. To execute scrape_books:
   - enter the project directory: `cd scrape_books`
   - crawl using the books spider: `scrapy crawl books`
2. To execute scrape_books_splash:
   - ensure that splash is running: `docker run -p 8050:8050 scrapinghub/splash` or check [splash docs](https://splash.readthedocs.io/en/stable/install.html)
   - enter the project directory: `cd scrape_books_splash`
   - crawl using the books spider: `scrapy crawl books`

### Enjoy!
