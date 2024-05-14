# git commit -m "PBL-847 set up base"

from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, TIMESTAMP, UUID, Column, String

from utils import get_instance

_, db = get_instance()

TYPE_DIGITS = 7


def generate_type(prefix: str, index: int) -> str:
    missing_digits = TYPE_DIGITS - len(str(index)) - len(prefix)
    return prefix + "".join("0" for _ in range(missing_digits)) + str(index)


class Constant(db.Model):
    __tablename__ = "constants"

    constant_id = Column(UUID(as_uuid=True), nullable=False, primary_key=True)
    constant_name = Column(String(1000), nullable=False)
    constant_type = Column(String(1000), nullable=False, unique=True)
    note = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=True)

    def __repr__(self) -> str:
        return f"<Constant {self.constant_id}>"

    def __init__(self, constant_name: str, prefix: str, index: int, note=None):
        self.constant_id = uuid4()
        self.constant_name = constant_name
        self.constant_type = generate_type(prefix, index)
        self.note = note
        self.created_at = datetime.now()
