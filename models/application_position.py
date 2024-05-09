from datetime import datetime
from uuid import uuid4

from sqlalchemy import TIMESTAMP, UUID, Boolean, Column, ForeignKey, String

from utils import get_instance

_, db = get_instance()


class ApplicationPosition(db.Model):
    __tablename__ = "application_positions"

    id = Column(UUID(as_uuid=True), nullable=False, primary_key=True)
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
    apply_position = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "constants.constant_id",
            match="FULL",
            onupdate="NO ACTION",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    salary_range = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "constants.constant_id",
            match="FULL",
            onupdate="NO ACTION",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    status = Column(Boolean, nullable=False, default=True)
    note = Column(String(10000), nullable=True)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=True)

    def __repr__(self) -> str:
        return f"<ApplicationPosition {self.id}>"

    def __init__(self, account_id, apply_position, salary_range, note=""):
        self.id = uuid4()
        self.account_id = account_id
        self.apply_position = apply_position
        self.salary_range = salary_range
        self.note = note
        self.created_at = datetime.now()
