from dataclasses import dataclass


@dataclass
class Submission:
    form: str
    filing_date: str
    accession: str
    primary_document: str
