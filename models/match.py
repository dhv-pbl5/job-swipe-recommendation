# git commit -m "PBL-847 set up base"

from datetime import datetime
from uuid import uuid4

from sqlalchemy import TIMESTAMP, UUID, Boolean, Column, ForeignKey

from utils import get_instance

_, db = get_instance()


class Match(db.Model):
    __tablename__ = "matches"

    id = Column(UUID(as_uuid=True), primary_key=True, nullable=False)
    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "companies.account_id",
            match="FULL",
            onupdate="NO ACTION",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    company_matched = Column(Boolean)
    matched_time = Column(TIMESTAMP, nullable=False)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.account_id",
            match="FULL",
            onupdate="NO ACTION",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    user_matched = Column(Boolean)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=True)

    def __repr__(self) -> str:
        return f"<Match {self.id}>"

    def __init__(
        self, company_id: str, company_matched: bool, user_id: str, user_matched: bool
    ):
        self.id = uuid4()
        self.company_id = company_id
        self.company_matched = company_matched
        self.matched_time = datetime.now()
        self.user_id = user_id
        self.user_matched = user_matched
        self.created_at = datetime.now()
