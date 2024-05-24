from random import randint

from faker import Faker

from models.user import User
from models.user_award import UserAward
from utils import get_instance, setup_logging

_, db = get_instance()


def user_award_seeder(repeat_times=1000):
    logger = setup_logging()
    try:
        logger.info("Start seeding User Awards...")
        fake = Faker()

        query = User.query.order_by(User.created_at.desc())  # type: ignore
        for i in range(repeat_times):
            account = query.offset(i).first()
            if not account:
                continue

            for _ in range(1, randint(1, 10)):
                user_award = UserAward(
                    account_id=account.account_id,
                    certificate_name=fake.name(),
                    certificate_time=fake.date(),
                )
                db.session.add(user_award)

        db.session.commit()
        logger.info("Finished seeding User Awards...")
    except Exception as error:
        db.session.rollback()
        logger.error(error)
