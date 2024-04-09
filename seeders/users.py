import random
from uuid import uuid4

from faker import Faker

from models.Accounts import Accounts
from models.Constants import Constants
from models.Users import Users
from utils import get_instance

_, db = get_instance()


def users_seeder(repeat_time=1000, reset=False):
    fake = Faker()

    if reset:
        db.session.query(Accounts).delete()
        db.session.commit()

    USER_ROLE = Constants.query.filter_by(constant_name="User").first()
    if not USER_ROLE:
        raise Exception("Please seed constants first!")

    for _ in range(repeat_time):
        account_id = uuid4()

        account = Accounts(
            account_id=account_id,
            address=fake.address(),
            email=fake.email(),
            password=fake.password(),
            phone_number="0" + "".join(str(random.randint(0, 9)) for _ in range(9)),
            refresh_token=fake.password(),
            system_role=USER_ROLE.constant_id,
        )
        db.session.add(account)

        user = Users(
            account_id=account_id,
            date_of_birth=fake.date_of_birth(),
            first_name=fake.first_name(),
            gender=fake.boolean(),
            last_name=fake.last_name(),
            social_media_link=[
                fake.domain_name() for _ in range(random.randint(0, 10))
            ],
            summary_introduction=fake.text(),
        )
        db.session.add(user)
        db.session.commit()

    print("Users seeded successfully")
