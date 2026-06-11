import logging
from typing import Any

from settings import Settings

logger = logging.getLogger(__name__)


def slugify(term: str) -> str:
    return term.strip().lower().replace(" ", "-")


def to_product_schema(search_term: str, product: dict[str, Any]) -> dict[str, Any] | None:
    try:
        name = product.get("name")
        price = product.get("price")
        url = product.get("url")

        product_url = None
        if isinstance(url, str) and url:
            product_path = url.split("?")[0]
            product_url = f"{Settings.SITE_URL}{product_path}"

        price_value = None
        if price is not None:
            price_value = str(price)

        if not name and price_value is None and not product_url:
            logger.warning("Produto ignorado por não conter dados úteis: %s", product.get("id"))
            return None

        return {
            "search_term": search_term,
            "product_name": name,
            "price": price_value,
            "product_url": product_url,
        }
    except Exception as error:
        logger.error("Erro ao parsear produto: %s", error, exc_info=True)
        return None


def parse_search_page(search_term: str, page_data: dict[str, Any]) -> list[dict[str, Any]]:
    products = page_data.get("products")
    if not isinstance(products, list):
        logger.warning("Lista de produtos ausente para o termo '%s'", search_term)
        return []

    parsed_products: list[dict[str, Any]] = []
    for product in products:
        if not isinstance(product, dict):
            logger.warning("Item de produto inválido para o termo '%s'", search_term)
            continue

        parsed = to_product_schema(search_term, product)
        if parsed:
            parsed_products.append(parsed)

    return parsed_products
