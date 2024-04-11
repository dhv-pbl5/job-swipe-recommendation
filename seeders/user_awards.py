from faker import Faker
from tqdm import trange

from models.UserAwards import UserAwards
from models.Users import Users
from utils import get_instance

_, db = get_instance()


def user_awards_seeder(repeat_times=1000, reset=False):
    fake = Faker()

    if reset:
        db.session.query(UserAwards).delete()
        db.session.commit()

    query = Users.query.order_by(Users.created_at.desc())
    for i in trange(repeat_times):
        account_id = query.offset(i).first().account_id

        user_award = UserAwards(
            account_id=account_id,
            certificate_name=fake.name(),
            certificate_time=fake.date(),
        )
        db.session.add(user_award)
        db.session.commit()

    print("UserAwards seeded successfully")
