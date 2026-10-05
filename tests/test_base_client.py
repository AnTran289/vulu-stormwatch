from unittest.mock import Mock, patch

import pytest
import requests

from stormwatch.clients.base_client import APIClient


@patch("stormwatch.clients.base_client.time.sleep")
@patch("stormwatch.clients.base_client.requests.get")
def test_retries_transient_connection_error(mock_get, mock_sleep):
    successful_response = Mock(status_code=200)
    successful_response.json.return_value = {"ok": True}
    successful_response.raise_for_status.return_value = None
    mock_get.side_effect = [requests.ConnectionError("reset"), successful_response]

    client = APIClient("https://example.test", retry_backoff_seconds=0.1)

    assert client.get() == {"ok": True}
    assert mock_get.call_count == 2
    mock_sleep.assert_called_once_with(0.1)


@patch("stormwatch.clients.base_client.time.sleep")
@patch("stormwatch.clients.base_client.requests.get")
def test_does_not_retry_permanent_http_error(mock_get, mock_sleep):
    response = Mock(status_code=404)
    error = requests.HTTPError("not found", response=response)
    response.raise_for_status.side_effect = error
    mock_get.return_value = response

    client = APIClient("https://example.test")

    with pytest.raises(requests.HTTPError):
        client.get()

    assert mock_get.call_count == 1
    mock_sleep.assert_not_called()
