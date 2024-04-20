from faker import Faker

from models.user import User
from models.user_award import UserAward
from utils import get_instance, get_tqdm

_, db = get_instance()


def user_award_seeder(repeat_times=1000, reset=False):
    log_prefix = "seeders.user_awards.user_awards_seeder"
    fake = Faker()
    if reset:
        UserAward.query.delete()
        db.session.commit()

    query = User.query.order_by(User.created_at.desc())  # type: ignore
    for i in get_tqdm(loop=repeat_times, desc="User Awards"):
        account_id = query.offset(i).first()
        if not account_id:
            raise Exception(log_prefix + "Data of Users is not enough")
        else:
            account_id = account_id.account_id

        user_award = UserAward(
            account_id=account_id,
            certificate_name=fake.name(),
            certificate_time=fake.date(),
        )
        db.session.add(user_award)
        db.session.commit()
