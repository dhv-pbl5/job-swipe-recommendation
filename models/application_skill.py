# git commit -m "PBL-847 set up base"

from datetime import datetime
from uuid import uuid4

from sqlalchemy import TIMESTAMP, UUID, Column, ForeignKey, String

from utils import get_instance

_, db = get_instance()


class ApplicationSkill(db.Model):
    __tablename__ = "application_skills"

    id = Column(UUID(as_uuid=True), nullable=False, primary_key=True)
    application_position_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "application_positions.id",
            match="FULL",
            onupdate="NO ACTION",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    skill_id = Column(
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
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=True)

    def __repr__(self) -> str:
        return f"<ApplicationSkill {self.id}>"

    def __init__(self, application_position_id, skill_id):
        self.id = uuid4()
        self.application_position_id = application_position_id
        self.skill_id = skill_id
        self.created_at = datetime.now()
