from datetime import datetime
from uuid import uuid4

from sqlalchemy import TIMESTAMP, UUID, Column, ForeignKey, Numeric, String

from utils import get_instance

_, db = get_instance()


class UserEducations(db.Model):
    __tablename__ = "user_educations"

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
    cpa = Column(Numeric(100, 10), nullable=False)
    majority = Column(String(1000), nullable=True)
    note = Column(String(1000), nullable=True)
    study_end_time = Column(TIMESTAMP, nullable=True)
    study_place = Column(String(1000), nullable=False)
    study_start_time = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=True)

    def __repr__(self) -> str:
        return f"<UserEducation {self.id}>"

    def __init__(
        self,
        account_id,
        cpa,
        study_place,
        study_start_time,
        majority="",
        study_end_time=None,
    ):
        self.id = uuid4()
        self.account_id = account_id
        self.cpa = cpa
        self.majority = majority
        self.study_end_time = study_end_time
        self.study_place = study_place
        self.study_start_time = study_start_time
        self.created_at = datetime.now()
