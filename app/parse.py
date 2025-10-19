import csv
from dataclasses import astuple, dataclass, fields
from typing import Generator
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup, Tag
from tqdm import tqdm

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


PRODUCT_FIELDS = [field.name for field in fields(Quote)]


def fetch_page(page_url: str) -> bytes | None:
    response = requests.get(page_url)
    if response.status_code == 200:
        return response.content


def page_generator() -> Generator[BeautifulSoup, None, None]:
    page_number = 0
    while True:
        page_number += 1
        page_url = urljoin(BASE_URL, f"page/{page_number}/")
        content = fetch_page(page_url)
        if not content:
            break
        soup = BeautifulSoup(content, "html.parser")
        if not soup.select(".quote"):
            break
        yield soup


def parse_single_page(product: Tag) -> Quote:
    return Quote(
        text=product.select_one(".text").text,
        author=product.select_one(".author").text,
        tags=[tag.text.strip() for tag in product.select(".tag")],
    )


def get_home_product(page: BeautifulSoup) -> list[Quote]:
    quote_element = page.select(".quote")
    return [parse_single_page(product) for product in quote_element]


def get_product() -> list[Quote]:
    products = []
    for page in tqdm(page_generator()):
        products.extend(get_home_product(page))
    return products


def write_to_csv(products: list[Quote]) -> None:
    with open("result.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(PRODUCT_FIELDS)
        writer.writerows(
            [
                astuple(product) for product in products if product.author
            ]
        )


def main(output_csv_path: str) -> None:
    products = get_product()
    write_to_csv(products)


if __name__ == "__main__":
    main("quotes.csv")
