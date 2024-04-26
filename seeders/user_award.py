from faker import Faker
from tqdm import trange

from models.user import User
from models.user_award import UserAward
from utils import get_instance, log_prefix

_, db = get_instance()


def user_award_seeder(repeat_times=1000):
    try:
        fake = Faker()

        query = User.query.order_by(User.created_at.desc())  # type: ignore
        for i in trange(repeat_times):
            account = query.offset(i).first()
            if not account:
                continue

            for _ in range(1, 30):
                user_award = UserAward(
                    account_id=account.account_id,
                    certificate_name=fake.name(),
                    certificate_time=fake.date(),
                )
                db.session.add(user_award)

        db.session.commit()
    except Exception as error:
        db.session.rollback()
        log_prefix(__file__, error, type="error")
