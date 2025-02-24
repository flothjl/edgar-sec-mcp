import csv
import io
import json
from functools import partial
from typing import Dict, List

import httpx
from bs4 import BeautifulSoup, Tag
from ixbrlparse import IXBRL

from . import models, util
from .sec_forms import FormFetcher


class InitializationError(Exception): ...


def _base_url_builder(cik, submission: models.Submission):
    return f"https://www.sec.gov/Archives/edgar/data/{cik}/{submission.accession.replace('-', '')}/{submission.primary_document.split('/')[-1]}"


def ixbrl_proxy_parser(data: str) -> str:
    parsed = IXBRL(io.StringIO(data))
    print(parsed)
    with open("ixbrl_parsed.json", "w+") as f:
        json.dump(parsed.to_json(), f)
    return parsed.contexts


def proxy_parser(data: str) -> List[str]:
    """
    Cleans a DEF 14A HTML document by:
    - Removing <script> and <style> tags.
    - Stripping all attributes from elements.
    - Preserving structural tags and textual content.
    """
    soup = BeautifulSoup(data, "html.parser")

    tables = soup.find_all("table")
    csv_list = []

    for table in tables:
        if not isinstance(table, Tag):
            continue
        output = io.StringIO()
        writer = csv.writer(output)

        for row in table.find_all("tr"):
            if not isinstance(row, Tag):
                continue
            cells = [cell.get_text(strip=True) for cell in row.find_all(["td", "th"])]
            writer.writerow(cells)

        csv_list.append(output.getvalue())

    return csv_list


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
            url_builder=self.base_url_builder,
            form_codes=["4"],
            submissions=self.submissions,
            headers=self._headers,
        )
        self.form10k = FormFetcher(
            url_builder=self.base_url_builder,
            form_codes=["10-K"],
            submissions=self.submissions,
            headers=self._headers,
        )
        self.proxy_statements = FormFetcher(
            url_builder=self.base_url_builder,
            form_codes=["DEF 14A"],
            submissions=self.submissions,
            headers=self._headers,
            parse_fn=proxy_parser,
        )

    @property
    def base_url_builder(self):
        return partial(_base_url_builder, self.cik)

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
