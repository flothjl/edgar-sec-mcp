from typing import Dict

import httpx


class CikLookupByTicker:
    """
    A class for looking up CIK numbers by ticker symbols, with caching support.

    Methods:
        cik_map(self): Returns the CIK map.
        get_sec_cik_list(headers: Dict | None = None) -> Dict: Retrieves the SEC CIK list.
    """

    __CIK_MAP = None

    def __init__(self, headers: Dict | None = None):
        self._headers = headers

    @property
    def cik_map(self):
        return self._get_cik_map(self._headers)

    @classmethod
    def _get_cik_map(cls, headers: Dict | None = None):
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
        response = httpx.get(URL, headers=headers)
        response.raise_for_status()
        data = response.text
        lines = data.strip().split("\n")
        ticker_cik_dict = {line.split("\t")[0]: line.split("\t")[1] for line in lines}
        return ticker_cik_dict
