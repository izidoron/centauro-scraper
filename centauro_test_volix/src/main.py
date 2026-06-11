import argparse
import json
import logging
import sys
from pathlib import Path

from exporters import export_products
from loaders import load_search_terms
from scraper import scrape_terms
from settings import BASE_DIR, OUTPUT_DIR


def configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Coletor de produtos da Centauro")
    parser.add_argument(
        "--input",
        type=Path,
        default=BASE_DIR / "input.json",
        help="Arquivo de entrada (.json, .txt ou .csv)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help="Diretório de saída para JSON e Parquet",
    )
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Também imprime o resultado no terminal",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Ativa logs detalhados",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    configure_logging(args.verbose)
    logger = logging.getLogger(__name__)

    try:
        terms = load_search_terms(args.input)
        if not terms:
            logger.error("Nenhum termo de busca encontrado em %s", args.input)
            return 1

        logger.info("Iniciando coleta para %s termo(s)", len(terms))
        products = scrape_terms(terms)
        exported = export_products(products, args.output_dir)

        logger.info("Coleta finalizada com %s produto(s)", len(products))
        logger.info("JSON salvo em %s", exported["json"])
        logger.info("Parquet salvo em %s", exported["parquet"])

        if args.stdout:
            print(json.dumps(products, ensure_ascii=False, indent=2))

        return 0
    except Exception as error:
        logger.error("Execução interrompida: %s", error, exc_info=args.verbose)
        return 1


if __name__ == "__main__":
    sys.exit(main())
