# Build a reusable HTTP client.

import logging
import time
from typing import Any

import requests

logger = logging.getLogger(__name__)


class APIClient:
    def __init__(
        self,
        base_url: str,
        timeout: int = 30,
        max_attempts: int = 3,
        retry_backoff_seconds: float = 1.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_attempts = max_attempts
        self.retry_backoff_seconds = retry_backoff_seconds

    def get(
        self,
        endpoint: str = "",
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any] | list[Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        for attempt in range(1, self.max_attempts + 1):
            try:
                response = requests.get(
                    url,
                    params=params,
                    timeout=self.timeout,
                )

                if response.status_code == 429 or response.status_code >= 500:
                    response.raise_for_status()

                response.raise_for_status()
                return response.json()
            except (requests.ConnectionError, requests.Timeout):
                if attempt == self.max_attempts:
                    raise
            except requests.HTTPError as error:
                status_code = error.response.status_code if error.response else None
                if (
                    attempt == self.max_attempts
                    or status_code not in {429, 500, 502, 503, 504}
                ):
                    raise

            delay = self.retry_backoff_seconds * (2 ** (attempt - 1))
            logger.warning(
                "Request to %s failed; retrying in %.1f seconds (%d/%d)",
                url,
                delay,
                attempt + 1,
                self.max_attempts,
            )
            time.sleep(delay)

        raise RuntimeError("HTTP request exhausted retry attempts.")
