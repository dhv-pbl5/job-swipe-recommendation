from random import randint

from faker import Faker
from tqdm import trange

from models.account import Account
from models.constant import Constant
from models.user import User
from utils import get_instance, log_prefix

_, db = get_instance()


def user_seeder(repeat_times=1000, reset=False):
    try:
        fake = Faker()
        USER_ROLE = Constant.query.filter_by(constant_name="User").first()
        if not USER_ROLE:
            raise Exception("User role not found")

        for _ in trange(repeat_times, desc="Users"):
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
                date_of_birth=fake.date_of_birth(maximum_age=40, minimum_age=18),
                first_name=fake.first_name(),
                gender=fake.boolean(),
                last_name=fake.last_name(),
                social_media_link=[fake.domain_name() for _ in range(randint(0, 10))],
                summary_introduction=fake.text(),
            )
            db.session.add(user)

        db.session.commit()
    except Exception as error:
        db.session.rollback()
        log_prefix(__file__, error, type="error")
