from random import randint, randrange

from faker import Faker
from tqdm import trange

from models.account import Account
from models.constant import Constant
from models.languages import Language
from seeders.define_constants import LANGUAGES_PREFIX
from utils import get_instance, log_prefix

_, db = get_instance()


def language_seeder(repeat_times=1000):
    try:
        fake = Faker()
        query = Account.query.order_by(Account.created_at.desc())  # type: ignore

        languages = Constant.query.filter(
            Constant.constant_type.like(f"{LANGUAGES_PREFIX}%")  # type: ignore
        )
        total_languages = languages.count()
        languages = languages.all()

        for i in trange(repeat_times):
            account = query.offset(i).first()
            if not account:
                continue

            for _ in range(randint(0, total_languages)):
                language = languages[randint(0, len(languages) - 1)]
                score = 0
                if language.constant_name == "IELTS":
                    score = randrange(25, 90, 5) / 10
                elif language.constant_name == "TOEIC":
                    score = randrange(100, 990, 10)
                elif language.constant_name == "JLPT":
                    score = language.note["values"][randint(0, 4)]

                model = Language(
                    account_id=account.account_id,
                    language_id=language.constant_id,
                    language_score=str(score),
                    language_certificate_date=fake.date_this_decade(),
                )
                db.session.add(model)

            db.session.commit()
    except Exception as error:
        db.session.rollback()
        log_prefix(__file__, error, type="error")
