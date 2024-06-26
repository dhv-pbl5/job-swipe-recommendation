import os

from faker import Faker

from models.account import Account
from models.company import Company
from models.constant import Constant
from utils import fake_phone_numbers, get_instance, setup_logger
from utils.environment import Env

_, db = get_instance()


def company_seeder(repeat_times=1000):
    logger = setup_logger()
    try:
        logger.info("Start seeding Companies...")
        image_urls_file = os.path.join(os.getcwd(), "seed/images/company_avatar.txt")
        image_urls = []
        try:
            with open(image_urls_file, "r") as file:
                image_urls = file.readlines()
            image_urls = [url.strip() for url in image_urls]
        except:
            pass

        fake = Faker()
        COMPANY_ROLE = Constant.query.filter_by(constant_name="Company").first()
        if not COMPANY_ROLE:
            raise Exception("Company role not found")

        for _ in range(repeat_times):
            account = Account(
                address=fake.address(),
                email=fake.email(),
                password=Env.DEFAULT_PASSWORD,
                phone_number=fake_phone_numbers(),
                refresh_token=fake.password(),
                system_role=COMPANY_ROLE.constant_id,
                avatar=image_urls[_ % len(image_urls)] if image_urls else "",
            )
            db.session.add(account)

            company = Company(
                account_id=account.account_id,
                company_name=fake.company(),
                company_url=fake.domain_name(),
                established_date=fake.date(),
                description=fake.text(),
            )
            db.session.add(company)

        db.session.commit()
        logger.info("Finished seeding Companies...")
    except Exception as error:
        db.session.rollback()
        logger.error(error)
