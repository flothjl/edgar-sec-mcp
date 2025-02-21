from typing import Callable, Dict, List

import httpx

from .models import Submission


class FormFetcher[T]:
    """
    Fetches and analyzes forms based on the provided parameters.

    Args:
        url_builder (Callable[[...], str]): The URL builder function to construct the form URL.
        form_codes (List[str]): The list of form codes to filter the submissions.
    """

    def __init__(
        self,
        parse_fn: Callable[..., T],
        url_builder: Callable[..., str],
        form_codes: List[str],
        headers: Dict[str, str] | None = None,
    ):
        self.url_builder = url_builder
        self.form_codes = form_codes
        self.parse_fn = parse_fn
        self.headers = headers

    def execute(
        self,
        submissions: List[Submission],
        cik: str,
        limit: int | None = None,
    ) -> List[T]:
        """
        Executes the filing analysis.

        Args:
            submissions (List[Submission]): The list of submissions to analyze.
            cik (str): The CIK (Central Index Key) of the company.
            limit (int | None, optional): The maximum number of results to return. Defaults to None.
            headers (Dict[str, str] | None, optional): The headers to include in the HTTP request. Defaults to None.

        Returns:
            List[T]: A list of objects of type T resulting from the analysis.
        """
        output = []
        for submission in submissions:
            if limit is not None and len(output) >= limit:
                break
            if submission.form in self.form_codes:
                url = self.url_builder(
                    cik,
                    submission.accession,
                    submission.primary_document,
                )
                response = httpx.get(url, headers=self.headers)
                response.raise_for_status()
                output.append(self.parse_fn(response.text))

        return output
