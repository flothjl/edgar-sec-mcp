from dataclasses import asdict, dataclass


@dataclass
class BaseForm:
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Form4(BaseForm):
    reporting_owner: str
    reporting_owner_title: str
    reporting_owner_relationship: str
    security_title: str
    transaction_date: str
    transaction_code: str
    transaction_shares: str
    transaction_price: str
    shares_owned_following_transaction: str


@dataclass
class Submission:
    form: str
    filing_date: str
    accession: str
    primary_document: str
