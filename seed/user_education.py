import random

from faker import Faker
from tqdm import trange

from models.user import User
from models.user_education import UserEducation
from utils import get_instance, log_prefix

_, db = get_instance()


def user_education_seeder(repeat_times=1000):
    try:
        fake = Faker()

        query = User.query.order_by(User.created_at.desc())  # type: ignore
        for i in trange(repeat_times, desc="User Educations"):
            account = query.offset(i).first()
            if not account:
                continue

            for _ in range(random.randint(1, 5)):
                is_university = bool(random.randint(0, 1))
                start_date = fake.date_this_decade()

                user_education = UserEducation(
                    account_id=account.account_id,
                    cpa=(
                        round(random.uniform(2, 4), 2)
                        if is_university
                        else round(random.uniform(6, 10), 2)
                    ),
                    study_place=fake.city(),
                    study_start_time=start_date,
                    study_end_time=(
                        fake.date_between(start_date) if random.randint(0, 1) else None
                    ),
                    is_university=is_university,
                )
                db.session.add(user_education)

        db.session.commit()
    except Exception as error:
        db.session.rollback()
        log_prefix(__file__, error, type="error")
