import random

from faker import Faker
from tqdm import trange

from models.UserEducations import UserEducations
from models.Users import Users
from utils import get_instance

_, db = get_instance()


def user_educations_seeder(repeat_times=1000, reset=False):
    fake = Faker()

    if reset:
        db.session.query(UserEducations).delete()
        db.session.commit()

    query = Users.query.order_by(Users.created_at.desc())
    for i in trange(repeat_times):
        account_id = query.offset(i).first().account_id

        user_education = UserEducations(
            account_id=account_id,
            cpa=round(random.uniform(0, 4), 2),
            study_place=fake.city(),
            study_start_time=fake.date_this_decade(),
            study_end_time=(fake.date_this_decade() if random.randint(0, 1) else None),
        )
        db.session.add(user_education)
        db.session.commit()

    print("UserEducations seeded successfully")
