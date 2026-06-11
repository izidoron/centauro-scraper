import json
from pathlib import Path
from typing import Any

import pandas as pd


def export_products(products: list[dict[str, Any]], output_dir: Path, stem: str = "products") -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / f"{stem}.json"
    parquet_path = output_dir / f"{stem}.parquet"

    with json_path.open("w", encoding="utf-8") as file:
        json.dump(products, file, ensure_ascii=False, indent=2)

    dataframe = pd.DataFrame(products)
    dataframe.to_parquet(parquet_path, index=False)

    return {"json": json_path, "parquet": parquet_path}
