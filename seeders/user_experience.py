from random import randint

from faker import Faker

from models.constant import Constant
from models.user import User
from models.user_experience import UserExperience
from utils import get_instance

_, db = get_instance()


def user_experience_seeder(repeat_times=1000, reset=False):
    log_prefix = "seeders.user_experiences.user_experiences_seeder"
    fake = Faker()
    if reset:
        UserExperience.query.delete()
        db.session.commit()

    experiences_types = Constant.query.filter(Constant.constant_type.like("04%")).all()  # type: ignore

    query = User.query.order_by(User.created_at.desc())  # type: ignore
    for i in range(repeat_times):
        account_id = query.offset(i).first()
        if not account_id:
            raise Exception(log_prefix + "Data of Users is not enough")
        else:
            account_id = account_id.account_id

        user_experience = UserExperience(
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
