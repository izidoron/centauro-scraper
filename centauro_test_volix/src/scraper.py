import logging
from typing import Any

from client import CentauroClient
from parser import parse_search_page, slugify
from settings import Settings

logger = logging.getLogger(__name__)


def has_next_page(page_data: dict[str, Any], current_page: int) -> bool:
    pagination = page_data.get("pagination")
    if not isinstance(pagination, dict):
        return False

    current = pagination.get("current", "")
    if isinstance(current, str) and f"page={current_page}" in current:
        next_page = pagination.get("next")
        if isinstance(next_page, str):
            return f"page={current_page + 1}" in next_page
    return False


def scrape_term(client: CentauroClient, term: str) -> list[dict[str, Any]]:
    slug = slugify(term)
    collected: list[dict[str, Any]] = []

    for page in range(1, Settings.PAGES_PER_TERM + 1):
        try:
            page_data = client.get_search_page(slug, page)
            products = parse_search_page(term, page_data)
            collected.extend(products)
            logger.info(
                "Termo '%s' página %s: %s produto(s) coletado(s)",
                term,
                page,
                len(products),
            )

            if page == 1 and not has_next_page(page_data, page):
                logger.info("Termo '%s' possui apenas uma página de resultados", term)
                break
        except Exception as error:
            logger.error(
                "Falha ao coletar termo '%s' na página %s: %s",
                term,
                page,
                error,
            )
            if page == 1:
                break

    if not collected:
        logger.warning("Nenhum produto encontrado para o termo '%s'", term)

    return collected


def scrape_terms(terms: list[str]) -> list[dict[str, Any]]:
    client = CentauroClient()
    results: list[dict[str, Any]] = []

    for term in terms:
        try:
            results.extend(scrape_term(client, term))
        except Exception as error:
            logger.error("Falha ao processar termo '%s': %s", term, error)

    return results
