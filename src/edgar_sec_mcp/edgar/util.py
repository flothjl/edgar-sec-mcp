import logging
import threading
from typing import Dict

import httpx


class CikLookupByTicker:
    """
    A class for looking up CIK numbers by ticker symbols, with caching support.

    Methods:
        cik_map(self): Returns the CIK map.
        get_sec_cik_list(headers: Dict) -> Dict: Retrieves the SEC CIK list.
    """

    __CIK_MAP = None
    __lock = threading.Lock()

    def __init__(self, headers: Dict | None = None):
        self._headers = headers

    @property
    def cik_map(self):
        return self._get_cik_map(self._headers)

    @classmethod
    def _get_cik_map(cls, headers: Dict | None = None):
        with cls.__lock:
            if cls.__CIK_MAP is None:
                cls.__CIK_MAP = cls.get_sec_cik_list(headers)
        return cls.__CIK_MAP

    @staticmethod
    def get_sec_cik_list(headers: Dict | None) -> Dict[str, str]:
        """
        Retrieve the SEC CIK list.

        Args:
            headers (Dict | None): Optional headers for making HTTP requests.

        Returns:
            Dict: A dictionary mapping ticker symbols to CIK numbers.
        """
        URL = "https://www.sec.gov/include/ticker.txt"
        CIK_DELIM = "\t"
        response = httpx.get(URL, headers=headers)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            logging.error(
                f"HTTP error occurred: {e.response.status_code} - {e.response.text}"
            )
            raise
        data = response.text
        lines = data.strip().split("\n")
        ticker_ciks = dict()
        for line in lines:
            try:
                ticker_ciks[line.split(CIK_DELIM)[0]] = line.split(CIK_DELIM)[1]
            except Exception:
                # Skip
                continue

        return ticker_ciks
