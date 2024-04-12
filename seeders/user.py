from random import randint

from faker import Faker

from models.account import Account
from models.constant import Constant
from models.user import User
from models.user_award import UserAward
from models.user_education import UserEducation
from models.user_experience import UserExperience
from utils import get_instance

_, db = get_instance()


def user_seeder(repeat_times=1000, reset=False):
    log_prefix = "seeders.users.users_seeder"
    fake = Faker()

    if reset:
        UserExperience.query.delete()
        UserEducation.query.delete()
        UserAward.query.delete()
        User.query.delete()
        Account.query.delete()
        db.session.commit()

    USER_ROLE = Constant.query.filter_by(constant_name="User").first()
    if not USER_ROLE:
        raise Exception(log_prefix + "Please seed constants first!")

    for _ in range(repeat_times):
        account = Account(
            address=fake.address(),
            email=fake.email(),
            password=fake.password(),
            phone_number="0" + "".join(str(randint(0, 9)) for _ in range(9)),
            refresh_token=fake.password(),
            system_role=USER_ROLE.constant_id,
        )
        db.session.add(account)

        user = User(
            account_id=account.account_id,
            date_of_birth=fake.date_of_birth(),
            first_name=fake.first_name(),
            gender=fake.boolean(),
            last_name=fake.last_name(),
            social_media_link=[fake.domain_name() for _ in range(randint(0, 10))],
            summary_introduction=fake.text(),
        )
        db.session.add(user)
        db.session.commit()
