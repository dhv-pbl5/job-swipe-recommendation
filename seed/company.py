from faker import Faker

from models.account import Account
from models.company import Company
from models.constant import Constant
from utils import fake_phone_numbers, get_instance, log_prefix

_, db = get_instance()


def company_seeder(repeat_times=1000):
    try:
        log_prefix(__file__, "Start seeding Companies...")

        fake = Faker()
        COMPANY_ROLE = Constant.query.filter_by(constant_name="Company").first()
        if not COMPANY_ROLE:
            raise Exception("Company role not found")

        for _ in range(repeat_times):
            account = Account(
                address=fake.address(),
                email=fake.email(),
                password=fake.password(),
                phone_number=fake_phone_numbers(),
                refresh_token=fake.password(),
                system_role=COMPANY_ROLE.constant_id,
            )
            db.session.add(account)

            company = Company(
                account_id=account.account_id,
                company_name=fake.company(),
                company_url=fake.domain_name(),
                established_date=fake.date(),
            )
            db.session.add(company)

        db.session.commit()
        log_prefix(__file__, "Finished seeding Companies...")
    except Exception as error:
        db.session.rollback()
        log_prefix(__file__, error, type="error")
