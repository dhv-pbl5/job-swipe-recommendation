from faker import Faker

from models.Accounts import Accounts
from models.Companies import Companies
from models.Constants import Constants
from utils import fake_phone_numbers, get_instance

_, db = get_instance()


def companies_seeder(repeat_times=1000, reset=False):
    fake = Faker()
    if reset:
        db.session.query(Companies).delete()
        db.session.query(Accounts).delete()
        db.session.commit()

    COMPANY_ROLE = Constants.query.filter_by(constant_name="Company").first()
    if not COMPANY_ROLE:
        raise Exception(
            "seeders.companies.companies_seeder: COMPANY_ROLE not found in Constants table."
        )

    for _ in range(repeat_times):
        account = Accounts(
            address=fake.address(),
            email=fake.email(),
            password=fake.password(),
            phone_number=fake_phone_numbers(),
            refresh_token=fake.password(),
            system_role=COMPANY_ROLE.constant_id,
        )
        db.session.add(account)

        company = Companies(
            account_id=account.account_id,
            company_name=fake.company(),
            company_url=fake.domain_name(),
            established_date=fake.date(),
        )
        db.session.add(company)
        db.session.commit()

    print("Companies seeded successfully")
