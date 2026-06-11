from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st

from settings import OUTPUT_DIR

st.set_page_config(page_title="Volix -Centauro Scraper", page_icon="📊", layout="wide")


@st.cache_data
def load_products_from_path(path: Path) -> pd.DataFrame:
    if path.suffix == ".parquet":
        return pd.read_parquet(path)
    return pd.read_json(path)


def load_products_from_upload(uploaded_file) -> pd.DataFrame:
    content = uploaded_file.getvalue()
    if uploaded_file.name.endswith(".parquet"):
        return pd.read_parquet(BytesIO(content))
    return pd.read_json(BytesIO(content))


def prepare_dataframe(dataframe: pd.DataFrame) -> pd.DataFrame:
    prepared = dataframe.copy()
    prepared["price_numeric"] = pd.to_numeric(prepared["price"], errors="coerce")
    return prepared


def render_metrics(dataframe: pd.DataFrame) -> None:
    priced = dataframe.dropna(subset=["price_numeric"])
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Produtos coletados", len(dataframe))
    col2.metric("Termos de busca", dataframe["search_term"].nunique())
    col3.metric("Preço médio", f"R$ {priced['price_numeric'].mean():.2f}" if not priced.empty else "—")
    col4.metric("Preço mínimo", f"R$ {priced['price_numeric'].min():.2f}" if not priced.empty else "—")
    col5.metric("Preço máximo", f"R$ {priced['price_numeric'].max():.2f}" if not priced.empty else "—")


def main() -> None:
    st.title("Dashboard de Preços — Centauro")
    st.caption("Métricas sobre os produtos coletados pelo scraper")

    default_parquet = OUTPUT_DIR / "products.parquet"
    default_json = OUTPUT_DIR / "products.json"

    with st.sidebar:
        st.header("Fonte de dados")
        uploaded = st.file_uploader("Carregar arquivo", type=["json", "parquet"])
        use_default = st.checkbox("Usar saída padrão do scraper", value=not uploaded)

    if uploaded is not None:
        dataframe = load_products_from_upload(uploaded)
    elif use_default and default_parquet.exists():
        dataframe = load_products_from_path(default_parquet)
    elif use_default and default_json.exists():
        dataframe = load_products_from_path(default_json)
    else:
        st.warning("Execute o scraper primeiro ou envie um arquivo JSON/Parquet.")
        st.code("python src/main.py --stdout")
        return

    dataframe = prepare_dataframe(dataframe)
    render_metrics(dataframe)

    st.subheader("Distribuição de preços")
    priced = dataframe.dropna(subset=["price_numeric"])
    if priced.empty:
        st.info("Nenhum preço numérico disponível para exibir gráficos.")
    else:
        st.bar_chart(priced.groupby("search_term")["price_numeric"].mean())

    st.subheader("Resumo por termo de busca")
    summary = (
        priced.groupby("search_term")["price_numeric"]
        .agg(["count", "mean", "median", "min", "max"])
        .round(2)
        .rename(
            columns={
                "count": "produtos",
                "mean": "média",
                "median": "mediana",
                "min": "mínimo",
                "max": "máximo",
            }
        )
    )
    st.dataframe(summary, use_container_width=True)

    st.subheader("Produtos coletados")
    st.dataframe(dataframe, use_container_width=True, hide_index=True)


if __name__ == "__main__":
    main()
