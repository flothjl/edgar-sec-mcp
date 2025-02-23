import unittest
from unittest.mock import patch

import httpx

from edgar_sec_mcp.edgar.util import CikLookupByTicker


class TestCikLookupByTicker(unittest.TestCase):
    @patch("httpx.get")
    def test_get_sec_cik_list_success(self, mock_get):
        # Mock a successful response
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = "AAPL\t0000320193\nGOOGL\t0001652044"

        cik_lookup = CikLookupByTicker()
        result = cik_lookup.get_sec_cik_list(None)

        self.assertEqual(result, {"AAPL": "0000320193", "GOOGL": "0001652044"})

    @patch("httpx.get")
    def test_get_sec_cik_list_http_error(self, mock_get):
        # Mock an HTTP error
        mock_get.side_effect = httpx.HTTPStatusError(
            "Not Found",
            request=httpx.Request("GET", "localhost"),
            response=mock_get.return_value,
        )

        cik_lookup = CikLookupByTicker()

        with self.assertRaises(httpx.HTTPStatusError):
            cik_lookup.get_sec_cik_list(None)


if __name__ == "__main__":
    unittest.main()
