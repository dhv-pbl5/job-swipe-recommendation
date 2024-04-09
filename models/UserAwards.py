from datetime import datetime

from sqlalchemy import TIMESTAMP, UUID, Column, String

from utils import get_instance

_, db = get_instance()


class UserAwards(db.Model):
    __tablename__ = "user_awards"

    id = Column(UUID, nullable=False, primary_key=True)
    account_id = Column(UUID, nullable=False)
    certificate_name = Column(String(1000), nullable=False)
    certificate_time = Column(TIMESTAMP, nullable=False)
    note = Column(String(1000), nullable=True)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=True)

    def __repr__(self) -> str:
        return f"<UserAward {self.id}>"

    def __init__(self, id, account_id, certificate_name, certificate_time, note=""):
        self.id = id
        self.account_id = account_id
        self.certificate_name = certificate_name
        self.certificate_time = certificate_time
        self.note = note
        self.created_at = datetime.now()
