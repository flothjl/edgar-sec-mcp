from functools import partial
from typing import Dict, List

import httpx

from . import models, util
from .sec_forms import FormFetcher


class InitializationError(Exception): ...


def form_4_url_builder(cik, submission: models.Submission):
    return f"https://www.sec.gov/Archives/edgar/data/{cik}/{submission.accession.replace('-', '')}/{submission.primary_document.split('/')[-1]}"


class CompanyFilings:
    def __init__(self, app_name: str, email: str, ticker: str):
        self.app_name = app_name
        self.email = email
        self._headers = {
            "User-Agent": f"{self.app_name} ({self.email})",
        }
        try:
            self.cik_map = util.CikLookupByTicker(self._headers).cik_map
            self.cik = str(self.cik_map[ticker.lower()])
        except KeyError as e:
            raise InitializationError("Unable to find ticker") from e
        self.submissions = self._get_submissions()
        self.form4 = FormFetcher(
            url_builder=partial(form_4_url_builder, self.cik),
            form_codes=["4"],
            submissions=self.submissions,
            headers=self._headers,
        )

    @property
    def padded_cik(self) -> str:
        return self.cik.zfill(10)

    def _get_submissions(self) -> List[models.Submission]:
        BASE_URL = "https://data.sec.gov/submissions/"
        data = self._request_submissions(f"{BASE_URL}CIK{self.padded_cik}.json")

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
