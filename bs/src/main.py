import asyncio
import re
import json
import time
import os

from bs4 import BeautifulSoup, Tag
from httpx import AsyncClient


BASE_URL = "https://books.toscrape.com"


async def scrape_catalogue(client: AsyncClient, url: str) -> dict:
    """
    scrape the catalogue and organise by categories

    :param client: AsyncClient
    :param url: str
    :return: dict
    """

    try:
        resp = await client.get(url)
        soup = BeautifulSoup(resp.text, "lxml")
        aside_div = soup.aside.find("div", class_="side_categories")
        aside_menu_list: list[Tag] = aside_div.ul.ul.find_all("li")

        catalogue = {}
        for link in aside_menu_list:
            item = link.a
            category, path = item.string.strip(), item["href"].strip()
            catalogue[category] = f"{BASE_URL}/{path}"

        return catalogue
    except Exception as err:
        raise err
        # print(err)


async def scrape_category_books(
    client: AsyncClient, url: str | None, book_urls: list | None = None
) -> list[dict]:
    """
    scrape all books from a given category

    :param client: AsyncClient
    :param url: str
    :return: list[dict]
    """

    if book_urls is None:
        book_urls = []

    try:
        resp = await client.get(url)
        soup = BeautifulSoup(resp.text, "lxml")

        articles = soup.find_all("article", class_="product_pod")
        for article in articles:
            pattern = re.compile(r"../../../([\w\W]*)")
            book_url = pattern.findall(article.h3.a["href"])[0]
            book_urls.append(f"{BASE_URL}/catalogue/{book_url}")

        next_btn = soup.find("li", class_="next")
        if next_btn is None:
            return book_urls

        last_slash = url.rindex("/")
        next_url = f"{url[:last_slash]}/{next_btn.a['href']}"

        return await scrape_category_books(client, next_url, book_urls)

    except Exception as err:
        raise err


async def scrape_book(client: AsyncClient, url: str) -> dict:
    """ "
    scrape a book page

    :param client: AsyncClient
    :param url: str
    :return: dict
    """

    try:
        resp = await client.get(url)
        soup = BeautifulSoup(resp.text, "lxml")

        div = soup.find("div", class_="product_main")
        name = div.h1.string
        price = div.find("p", class_="price_color").string
        rating = div.find("p", class_="star-rating")["class"][-1]
        available = True if div.find(class_="instock") else False
        image_url = soup.find(id="product_gallery").img["src"]

        return {
            "name": name,
            "price": price,
            "rating": rating,
            "available": available,
            "url": url,
            "image_url": f"{BASE_URL}/{image_url[6:]}",
        }
    except Exception as err:
        raise err


async def main():
    """Entry point"""

    client = AsyncClient()
    os.makedirs("data", exist_ok=True)

    start = time.time()
    catalogue = await scrape_catalogue(client, BASE_URL)
    with open("data/catalogue.json", "w") as f:
        json.dump(catalogue, f, indent=4)

    all_book_urls: dict[str, list[str]] = {}
    all_books: dict[str, list[dict]] = {}
    res = await asyncio.gather(
        *[scrape_category_books(client, url) for url in catalogue.values()]
    )

    for category, books in zip(catalogue.keys(), res):
        all_book_urls[category] = books

    with open("data/book_urls.json", "w") as f:
        json.dump(all_book_urls, f, indent=4)

    for category, book_urls in all_book_urls.items():
        tasks = [scrape_book(client, url) for url in book_urls]
        all_books[category] = await asyncio.gather(*tasks)

    with open("data/books.json", "w") as f:
        json.dump(all_books, f, indent=4)

    stop = time.time()
    print(f"Scraping took: {stop - start}s")


if __name__ == "__main__":
    asyncio.run(main())
