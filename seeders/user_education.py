import random

from faker import Faker

from models.user import User
from models.user_education import UserEducation
from utils import get_instance

_, db = get_instance()


def user_education_seeder(repeat_times=1000, reset=False):
    fake = Faker()
    if reset:
        UserEducation.query.delete()
        db.session.commit()

    query = User.query.order_by(User.created_at.desc())  # type: ignore
    for i in range(repeat_times):
        account_id = query.offset(i).first()
        if not account_id:
            raise Exception
        else:
            account_id = account_id.account_id

        user_education = UserEducation(
            account_id,
            cpa=round(random.uniform(0, 4), 2),
            study_place=fake.city(),
            study_start_time=fake.date_this_decade(),
            study_end_time=(fake.date_this_decade() if random.randint(0, 1) else None),
        )
        db.session.add(user_education)
        db.session.commit()
