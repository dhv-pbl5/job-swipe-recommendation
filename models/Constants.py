from datetime import datetime
from uuid import uuid4

from sqlalchemy import TIMESTAMP, UUID, Column, String

from utils import get_instance

_, db = get_instance()


class Constants(db.Model):
    __tablename__ = "constants"

    constant_id = Column(UUID, nullable=False, primary_key=True)
    constant_name = Column(String(1000), nullable=False)
    constant_type = Column(String(1000), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=True)

    def __repr__(self) -> str:
        return f"<Constant {self.constant_id}>"

    def __init__(self, constant_name: str, constant_type: str):
        self.constant_id = uuid4()
        self.constant_name = constant_name
        self.constant_type = constant_type
        self.created_at = datetime.now()
