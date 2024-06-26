from datetime import datetime

from sqlalchemy import JSON, TIMESTAMP, UUID, Column, ForeignKey, String, Text

from utils import get_instance

_, db = get_instance()


class Company(db.Model):
    __tablename__ = "companies"

    account_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "accounts.account_id",
            match="FULL",
            onupdate="NO ACTION",
            ondelete="CASCADE",
        ),
        nullable=False,
        primary_key=True,
    )
    company_name = Column(String(1000), nullable=False)
    company_url = Column(String(1000), nullable=False)
    established_date = Column(TIMESTAMP, nullable=False)
    description = Column(Text, nullable=True)
    others = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=True)
    normalize = Column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"<Company {self.account_id}>"

    def __init__(
        self, account_id, company_name, company_url, established_date, description=""
    ):
        self.account_id = account_id
        self.company_name = company_name
        self.company_url = company_url
        self.established_date = established_date
        self.description = description
        self.created_at = datetime.now()
