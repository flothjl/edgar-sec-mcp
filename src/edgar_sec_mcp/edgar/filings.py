from typing import Dict, List

import httpx

from . import models, util
from .sec_forms import FormFetcher


class InitializationError(Exception): ...


def form_4_url_builder(cik, accession, filename):
    return f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession.replace('-', '')}/{filename.split('/')[-1]}"


class CompanyFilings:
    def __init__(self, app_name: str, email: str, ticker: str, **kwargs):
        self.app_name = app_name
        self.email = email
        self._headers = {
            "User-Agent": f"{self.app_name} ({self.email})",
        }
        try:
            if "cik_lookup" in kwargs:
                self.cik_map = kwargs["cik_lookup"].cik_map
            else:
                self.cik_map = util.CikLookupByTicker(self._headers).cik_map
            self.cik = str(self.cik_map[ticker.lower()])
        except KeyError as e:
            raise InitializationError("Unable to find ticker") from e
        self._submissions = None
        self._form_4_fetcher = FormFetcher(
            url_builder=form_4_url_builder, form_codes=["4"], headers=self._headers
        )

    @property
    def padded_cik(self) -> str:
        return self.cik.zfill(10)

    @property
    def submissions(self):
        if self._submissions is None:
            self._submissions = self._get_submissions()
        return self._submissions

    def get_form_4_filings(self, last: int = 10) -> List[str]:
        try:
            return self._form_4_fetcher.execute(self.submissions, self.cik, last)
        except Exception as e:
            raise ValueError("Error in retrieving Form 4 filings") from e

    def _get_submissions(self) -> List[models.Submission]:
        base_url = "https://data.sec.gov/submissions/"
        data = self._request_submissions(f"{base_url}CIK{self.padded_cik}.json")

        submissions = self._process_submissions_response(data)

        return submissions

    def _request_submissions(self, url: str) -> Dict:
        response = httpx.get(url, headers=self._headers)
        response.raise_for_status()
        return response.json()

    def _process_submissions_response(self, data: Dict) -> List[models.Submission]:
        submissions = []
        recents = data["filings"]["recent"]

        for record in zip(
            recents["form"],
            recents["filingDate"],
            recents["accessionNumber"],
            recents["primaryDocument"],
        ):
            submissions.append(models.Submission(*record))
        return submissions
