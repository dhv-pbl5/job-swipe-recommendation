from datetime import datetime
from uuid import uuid4

from sqlalchemy import TIMESTAMP, UUID, Boolean, Column, ForeignKey, String

from utils import get_instance

_, db = get_instance()


class Account(db.Model):
    __tablename__ = "accounts"

    account_id = Column(UUID(as_uuid=True), nullable=False, primary_key=True)
    account_status = Column(Boolean, nullable=False, default=True)
    address = Column(String(1000), nullable=False)
    avatar = Column(String(1000), nullable=True)
    email = Column(String(1000), nullable=False)
    password = Column(String(1000), nullable=False)
    phone_number = Column(String(1000), nullable=False)
    refresh_token = Column(String(1000), nullable=False)
    system_role = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "constants.constant_id",
            match="FULL",
            onupdate="NO ACTION",
            ondelete="CASCADE",
        ),
        nullable=False,
    )
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP, nullable=True)
    deleted_at = Column(TIMESTAMP, nullable=True)

    def __repr__(self) -> str:
        return f"<Account {self.account_id}>"

    def __init__(
        self,
        address: str,
        email: str,
        password: str,
        phone_number: str,
        refresh_token: str,
        system_role: str,
        avatar: str = "",
    ):
        self.account_id = uuid4()
        self.address = address
        self.email = email
        self.password = password
        self.phone_number = phone_number
        self.refresh_token = refresh_token
        self.system_role = system_role
        self.created_at = datetime.now()
        self.avatar = avatar
