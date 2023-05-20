import httpx
from selectolax.parser import HTMLParser
from urllib.parse import urljoin

from dataclasses import dataclass

from rich import print


@dataclass
class Product:
    """Легко расширяемый класс для хранения данных о товарах."""
    name: str
    price: str
    sku: str
    rating: str


@dataclass
class Response:
    """Удобный класс для хранения ответа от сервера."""
    body_html: HTMLParser
    next_page: dict


def get_page(client, url):
    """Получение отдельной страницы."""
    headers = {
        "User-Agent":
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0"
            "YaBrowser/23.3.3.721 Yowser/2.5 Safari/537.36"}
    response = client.get(url, headers=headers)
    html = HTMLParser(response.text)
    if html.css_first("a[data-id=pagination-test-link-next]"):
        next_page = html.css_first(
            "a[data-id=pagination-test-link-next]").attributes
    else:
        next_page = {"href": False}
    return Response(body_html=html, next_page=next_page)


def extract_text(html, selector, index):
    """Извлечение текста из HTML."""
    try:
        return html.css(selector)[index].text(strip=True)
    except IndexError:
        return "None"


def detail_page_loop(client, page):
    """Получение данных о товарах на странице."""
    base_url = "https://www.rei.com"
    product_link = parse_links(page.body_html)
    for link in product_link:
        detail_page = get_page(client, urljoin(base_url, link))
        parse_detail(detail_page.body_html)


def parse_detail(html):
    """Парсинг данных о товаре."""
    new_product = Product(
        name=extract_text(html, "h1#product-page-title", 0),
        price=extract_text(html, "span.item-number", 0),
        sku=extract_text(html, "span.price-value", 0),
        rating=extract_text(html, "span.cdr-rating__number_13-3-1", 0),
    )
    print(new_product)


def parse_links(html):
    """Парсинг ссылок на товары."""
    links = html.css("div#search-results > ul li > a")
    return [link.attrs["href"] for link in links]


def pagination_loop(client):
    """Получение данных со всех страниц."""
    url = "https://www.rei.com/c/backpacks"
    while True:
        page = get_page(client, url)
        detail_page_loop(client, page)
        if page.next_page["href"]:
            url = urljoin(url, page.next_page["href"])
            print(url)
        else:
            client.close()
            break


def main():
    client = httpx.Client()
    pagination_loop(client)


if __name__ == "__main__":
    main()
