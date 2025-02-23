from typing import Callable, Dict, Generic, List, TypeVar

import httpx

from .models import Submission

R = TypeVar("R")


def _default_parse_fn(data: str) -> str:
    return data


class FormFetcher(Generic[R]):
    """
    Fetches and analyzes forms based on the provided parameters.

    Args:
        url_builder (Callable[[...], str]): The URL builder function to construct the form URL.
        form_codes (List[str]): The list of form codes to filter the submissions.
    """

    def __init__(
        self,
        url_builder: Callable[..., str],
        form_codes: List[str],
        submissions: List[Submission],
        parse_fn: Callable[..., R] = _default_parse_fn,
        headers: Dict[str, str] | None = None,
    ):
        self.url_builder = url_builder
        self.form_codes = form_codes
        self.parse_fn = parse_fn
        self.headers = headers
        self.submissions = submissions

    def get(self, limit: int = 10) -> List[R]:
        """
        Executes the filing analysis.

        Args:
            submissions (List[Submission]): The list of submissions to analyze.
            cik (str): The CIK (Central Index Key) of the company.
            limit (int | None, optional): The maximum number of results to return. Defaults to None.
            headers (Dict[str, str] | None, optional): The headers to include in the HTTP request. Defaults to None.

        Returns:
            List[R]: A list of objects of type T resulting from the analysis.
        """
        output = []
        for submission in self.submissions:
            if limit is not None and len(output) >= limit:
                break
            if submission.form in self.form_codes:
                url = self.url_builder(submission)
                response = httpx.get(url, headers=self.headers)
                response.raise_for_status()
                output.append(self.parse_fn(response.text))

        return output
