from random import randint, randrange

from models.company import Company
from models.match import Match
from models.user import User
from utils import get_instance, setup_logging

_, db = get_instance()


def match_seeder():
    logger = setup_logging()
    try:
        logger.info("Start seeding match...")
        num_of_match = 50
        company_query = Company.query.order_by(Company.created_at.desc())  # type: ignore
        user_query = User.query.order_by(User.created_at.desc())  # type: ignore

        for i in range(num_of_match):
            company = company_query.offset(i).first()
            for i in range(randrange(1, min(num_of_match, user_query.count()))):
                user = user_query.offset(i).first()
                if not company or not user:
                    continue
                company_matched_status = randint(0, 2)
                user_matched_status = randint(0, 2)
                match = Match(
                    company_id=company.account_id,
                    company_matched=(False if company_matched_status == 2 else True),
                    user_id=user.account_id,
                    user_matched=(False if user_matched_status == 2 else True),
                )
                db.session.add(match)

        db.session.commit()
        logger.info("Finished seeding match...")
    except Exception as error:
        db.session.rollback()
        logger.error(error)
