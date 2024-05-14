# git commit -m "PBL-847 set up base"

from datetime import datetime
from uuid import uuid4

from sqlalchemy import TIMESTAMP, UUID, Column, ForeignKey, String

from utils import get_instance

_, db = get_instance()


class UserExperience(db.Model):
    __tablename__ = "user_experiences"

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
    experience_end_time = Column(TIMESTAMP, nullable=True)
    experience_start_time = Column(TIMESTAMP, nullable=False)
    experience_type = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "constants.constant_id",
            match="FULL",
            onupdate="NO ACTION",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    note = Column(String(1000), nullable=True)
    position = Column(String(1000), nullable=False)
    work_place = Column(String(1000), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=True)

    def __repr__(self) -> str:
        return f"<UserExperience {self.id}>"

    def __init__(
        self,
        account_id,
        experience_end_time,
        experience_start_time,
        experience_type,
        position,
        work_place,
    ):
        self.id = uuid4()
        self.account_id = account_id
        self.experience_end_time = experience_end_time
        self.experience_start_time = experience_start_time
        self.experience_type = experience_type
        self.position = position
        self.work_place = work_place
        self.created_at = datetime.now()
