from random import randint

from faker import Faker
from tqdm import trange

from models.constant import Constant
from models.user import User
from models.user_experience import UserExperience
from seeders.define_constants import EXPERIENCE_TYPES_PREFIX
from utils import get_instance, log_prefix

_, db = get_instance()


def user_experience_seeder(repeat_times=1000):
    try:
        fake = Faker()
        experiences_types = Constant.query.filter(
            Constant.constant_type.like(f"{EXPERIENCE_TYPES_PREFIX}%")  # type: ignore
        ).all()

        query = User.query.order_by(User.created_at.desc())  # type: ignore
        for i in trange(repeat_times):
            account = query.offset(i).first()
            if not account:
                continue

            for _ in range(randint(1, 5)):
                user_experience = UserExperience(
                    account_id=account.account_id,
                    experience_end_time=fake.date_this_decade(),
                    experience_start_time=fake.date_this_decade(),
                    experience_type=experiences_types[
                        randint(0, len(experiences_types) - 1)
                    ].constant_id,
                    position=fake.job(),
                    work_place=fake.company(),
                )
                db.session.add(user_experience)

        db.session.commit()
    except Exception as error:
        db.session.rollback()
        log_prefix(__file__, error, type="error")
