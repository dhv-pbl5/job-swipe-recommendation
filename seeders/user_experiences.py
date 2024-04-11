from random import randint

from faker import Faker
from tqdm import trange

from models.Constants import Constants
from models.UserExperiences import UserExperiences
from models.Users import Users
from utils import get_instance

_, db = get_instance()


def user_experiences_seeder(repeat_times=1000, reset=False):
    fake = Faker()

    if reset:
        db.session.query(UserExperiences).delete()
        db.session.commit()

    experiences_types = Constants.query.filter(
        Constants.constant_type.like("04%")
    ).all()

    query = Users.query.order_by(Users.created_at.desc())
    for i in trange(repeat_times):
        account_id = query.offset(i).first().account_id

        user_experience = UserExperiences(
            account_id=account_id,
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

    print("UserExperiences seeded successfully")
