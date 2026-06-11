import csv
import json
from pathlib import Path


def load_search_terms(path: Path) -> list[str]:
    suffix = path.suffix.lower()

    if suffix == ".json":
        return _load_from_json(path)
    if suffix == ".txt":
        return _load_from_txt(path)
    if suffix == ".csv":
        return _load_from_csv(path)

    raise ValueError(f"Formato de entrada não suportado: {path.suffix}")


def _load_from_json(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as file:
        payload = json.load(file)

    if isinstance(payload, list):
        return [str(term).strip() for term in payload if str(term).strip()]

    if isinstance(payload, dict):
        for key in ("input", "terms", "search_terms"):
            if key in payload and isinstance(payload[key], list):
                return [str(term).strip() for term in payload[key] if str(term).strip()]

    raise ValueError("JSON de entrada deve ser uma lista ou conter a chave 'input'")


def _load_from_txt(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as file:
        return [line.strip() for line in file if line.strip()]


def _load_from_csv(path: Path) -> list[str]:
    with path.open(encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        if not reader.fieldnames:
            raise ValueError("CSV de entrada está vazio")

        column = next(
            (
                name
                for name in reader.fieldnames
                if name and name.lower() in {"term", "terms", "search_term", "busca"}
            ),
            reader.fieldnames[0],
        )

        return [row[column].strip() for row in reader if row.get(column, "").strip()]
