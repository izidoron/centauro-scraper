import logging
import re
import time
from typing import Any

from curl_cffi import requests
from curl_cffi.requests.exceptions import RequestException

from settings import Settings

logger = logging.getLogger(__name__)


class CentauroClient:
    def __init__(self) -> None:
        self._session = requests.Session()
        self._session.headers.update({"x-nextjs-data": "1"})
        self._build_id: str | None = None

    @property
    def build_id(self) -> str:
        if not self._build_id:
            self._build_id = self._fetch_build_id()
        return self._build_id

    def refresh_build_id(self) -> str:
        self._build_id = self._fetch_build_id()
        return self._build_id

    def _fetch_build_id(self) -> str:
        response = self._request("GET", Settings.SITE_URL)
        match = re.search(r'"buildId":"([^"]+)"', response.text)
        if not match:
            raise RuntimeError("buildId não encontrado na página da Centauro")
        return match.group(1)

    def get_search_page(self, slug: str, page: int) -> dict[str, Any]:
        url = f"{Settings.SITE_URL}/_next/data/{self.build_id}/busca/{slug}.json"
        params: dict[str, str | int] = {"searchSlug": slug}
        if page > 1:
            params["page"] = page

        response = self._request("GET", url, params=params)
        if not response.text.strip():
            raise ValueError(f"Resposta vazia para o termo '{slug}' (página {page})")

        payload = response.json()
        page_props = payload.get("pageProps")
        if not isinstance(page_props, dict):
            raise ValueError(f"Estrutura inesperada na resposta para '{slug}' (página {page})")

        if page_props.get("__N_REDIRECT"):
            raise ValueError(f"Redirecionamento inesperado para '{slug}' (página {page})")

        fallback = page_props.get("fallback")
        if not isinstance(fallback, dict):
            raise ValueError(f"Fallback ausente para '{slug}' (página {page})")

        for key, value in fallback.items():
            if "term" in key and isinstance(value, dict):
                return value

        raise ValueError(f"Dados de produtos não encontrados para '{slug}' (página {page})")

    def _request(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        last_error: Exception | None = None

        for attempt in range(1, Settings.MAX_RETRIES + 1):
            try:
                response = self._session.request(
                    method,
                    url,
                    impersonate=Settings.BROWSER_IMPERSONATE,
                    timeout=Settings.REQUEST_TIMEOUT,
                    **kwargs,
                )

                if response.status_code >= 400:
                    raise RequestException(
                        f"HTTP {response.status_code} em {url}",
                        response=response,
                    )

                return response
            except (RequestException, TimeoutError, ValueError) as error:
                last_error = error
                logger.warning(
                    "Falha na requisição (tentativa %s/%s): %s",
                    attempt,
                    Settings.MAX_RETRIES,
                    error,
                )
                if attempt < Settings.MAX_RETRIES:
                    time.sleep(Settings.RETRY_BACKOFF_SECONDS * attempt)

        raise RuntimeError(f"Requisição falhou após {Settings.MAX_RETRIES} tentativas") from last_error
