from datetime import datetime
from uuid import uuid4

from sqlalchemy import TIMESTAMP, UUID, Column, ForeignKey, String

from utils import get_instance

_, db = get_instance()


class UserAward(db.Model):
    __tablename__ = "user_awards"

    id = Column(UUID, nullable=False, primary_key=True)
    account_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.account_id",
            match="FULL",
            onupdate="NO ACTION",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    certificate_name = Column(String(1000), nullable=False)
    certificate_time = Column(TIMESTAMP, nullable=False)
    note = Column(String(1000), nullable=True)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=True)

    def __repr__(self) -> str:
        return f"<UserAward {self.id}>"

    def __init__(self, account_id, certificate_name, certificate_time):
        self.id = uuid4()
        self.account_id = account_id
        self.certificate_name = certificate_name
        self.certificate_time = certificate_time
        self.created_at = datetime.now()
