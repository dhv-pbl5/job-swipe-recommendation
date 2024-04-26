from random import randint

from tqdm import trange

from models.account import Account
from models.application_position import ApplicationPosition
from models.constant import Constant
from seeders.define_constants import POSITIONS_PREFIX
from utils import get_instance, log_prefix

_, db = get_instance()


def application_position_seeder():
    try:
        total_users = Account.query.count()
        query = Account.query.order_by(Account.created_at.desc())  # type: ignore
        positions = Constant.query.filter(
            Constant.constant_type.like(f"{POSITIONS_PREFIX}%")  # type: ignore
        ).all()

        for idx in trange(total_users):
            user = query.offset(idx).first()
            if not user:
                continue

            for _ in range(randint(1, len(positions))):
                application_position = ApplicationPosition(
                    account_id=user.account_id,
                    apply_position=positions[
                        randint(0, len(positions) - 1)
                    ].constant_id,
                )
                db.session.add(application_position)

        db.session.commit()
    except Exception as error:
        db.session.rollback()
        log_prefix(__file__, error, type="error")
