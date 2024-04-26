from datetime import datetime
from uuid import uuid4

from sqlalchemy import TIMESTAMP, UUID, Column, ForeignKey, String

from utils import get_instance

_, db = get_instance()


class Language(db.Model):
    __tablename__ = "languages"

    id = Column(UUID, nullable=False, primary_key=True)
    account_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "accounts.account_id",
            match="FULL",
            onupdate="NO ACTION",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    language_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "constants.constant_id",
            match="FULL",
            onupdate="NO ACTION",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    language_score = Column(String(1000), nullable=False)
    language_certificate_date = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=True)

    def __repr__(self) -> str:
        return f"<Language {self.id}>"

    def __init__(
        self,
        account_id: str,
        language_id: str,
        language_score: str,
        language_certificate_date: str = "",
    ):
        self.id = uuid4()
        self.account_id = account_id
        self.language_id = language_id
        self.language_score = language_score
        self.language_certificate_date = language_certificate_date
        self.created_at = datetime.now()
