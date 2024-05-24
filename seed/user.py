import os
from random import randint

from faker import Faker

from models.account import Account
from models.constant import Constant
from models.user import User
from utils import fake_phone_numbers, get_instance, setup_logging
from utils.environment import Env

_, db = get_instance()


def user_seeder(repeat_times=1000, reset=False):
    logger = setup_logging()
    try:
        logger.info("Start seeding Users...")

        image_urls_file = os.path.join(os.getcwd(), "seed/images/user_avatar.txt")
        with open(image_urls_file, "r") as file:
            image_urls = file.readlines()
        image_urls = [url.strip() for url in image_urls]

        fake = Faker()
        USER_ROLE = Constant.query.filter_by(constant_name="User").first()
        if not USER_ROLE:
            raise Exception("User role not found")

        for _ in range(repeat_times):
            account = Account(
                address=fake.address(),
                email=fake.email(),
                password=Env.DEFAULT_PASSWORD,
                phone_number=fake_phone_numbers(),
                refresh_token=fake.password(),
                system_role=USER_ROLE.constant_id,
                avatar=image_urls[_ % len(image_urls)],
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
        logger.info("Finished seeding Users...")
    except Exception as error:
        db.session.rollback()
        logger.error(error)
