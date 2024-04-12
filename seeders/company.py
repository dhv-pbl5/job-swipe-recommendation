from faker import Faker

from models.account import Account
from models.company import Company
from models.constant import Constant
from utils import fake_phone_numbers, get_instance

_, db = get_instance()


def company_seeder(repeat_times=1000, reset=False):
    log_prefix = "seeders.company.company_seeder"
    fake = Faker()
    if reset:
        Company.query.delete()
        Account.query.delete()
        db.session.commit()

    COMPANY_ROLE = Constant.query.filter_by(constant_name="Company").first()
    if not COMPANY_ROLE:
        raise Exception(log_prefix)

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
