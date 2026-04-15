from __future__ import annotations

import logging

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
}


def scrape_product(url: str, timeout: int = 15) -> dict:
    """Scrape basic product metadata from a URL.

    Returns a dict with keys: title, description, price, images, url.
    Gracefully falls back to partial data on failure.
    """
    result: dict = {
        "url": url,
        "title": "",
        "description": "",
        "price": "",
        "images": [],
        "raw_text": "",
    }

    try:
        resp = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
        resp.raise_for_status()
    except Exception as exc:
        logger.warning("Failed to fetch %s: %s", url, exc)
        return result

    soup = BeautifulSoup(resp.text, "html.parser")

    og_title = soup.find("meta", property="og:title")
    title_tag = soup.find("title")
    result["title"] = (
        (og_title["content"] if og_title and og_title.get("content") else None)
        or (title_tag.get_text(strip=True) if title_tag else "")
    )

    og_desc = soup.find("meta", property="og:description")
    meta_desc = soup.find("meta", attrs={"name": "description"})
    result["description"] = (
        (og_desc["content"] if og_desc and og_desc.get("content") else None)
        or (meta_desc["content"] if meta_desc and meta_desc.get("content") else "")
    )

    og_image = soup.find("meta", property="og:image")
    if og_image and og_image.get("content"):
        result["images"].append(og_image["content"])

    for img in soup.find_all("img", src=True):
        src = img["src"]
        if src.startswith("http") and src not in result["images"]:
            result["images"].append(src)
        if len(result["images"]) >= 10:
            break

    price_selectors = [
        {"class_": "price"},
        {"class_": "product-price"},
        {"attrs": {"data-price": True}},
    ]
    for selector in price_selectors:
        el = soup.find(**selector)
        if el:
            result["price"] = el.get_text(strip=True)
            break

    body = soup.find("body")
    if body:
        result["raw_text"] = body.get_text(separator=" ", strip=True)[:2000]

    return result
