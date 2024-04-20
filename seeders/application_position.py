from random import randint

from models.account import Account
from models.application_position import ApplicationPosition
from models.constant import Constant
from utils import get_instance, get_tqdm

_, db = get_instance()


def application_position_seeder(reset=False):
    if reset:
        ApplicationPosition.query.delete()
        db.session.commit()

    total_users = Account.query.count()
    query = Account.query.order_by(Account.created_at.desc())  # type: ignore
    positions = Constant.query.filter(
        Constant.constant_type.like("03%")).all()  # type: ignore
    for idx in get_tqdm(loop=total_users, desc="Application Positions"):
        user = query.offset(idx).first()
        if not user:
            continue

        application_position = ApplicationPosition(
            account_id=user.account_id,
            apply_position=positions[randint(
                0, len(positions) - 1)].constant_id,
        )
        db.session.add(application_position)
        db.session.commit()
