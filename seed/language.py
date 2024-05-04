from random import randint, randrange

from faker import Faker

from models.account import Account
from models.constant import Constant
from models.languages import Language
from seed.define_constants import LANGUAGES_PREFIX
from utils import get_instance, log_prefix

_, db = get_instance()


def language_seeder():
    try:
        log_prefix(__file__, "Start seeding Languages...")
        fake = Faker()
        query = Account.query.order_by(Account.created_at.desc())  # type: ignore
        total_account = query.count()

        languages = Constant.query.filter(
            Constant.constant_type.like(f"{LANGUAGES_PREFIX}%")  # type: ignore
        )
        total_languages = languages.count()
        languages = languages.all()

        for i in range(total_account):
            account = query.offset(i).first()
            if not account:
                continue

            for _ in range(randint(1, total_languages)):
                language = languages[randint(0, len(languages) - 1)]
                score = 0
                if language.note["values"]:
                    score = language.note["values"][
                        randint(0, len(language.note["values"]) - 1)
                    ]
                else:
                    score = (
                        randrange(
                            language.note["validate"]["min"] * 10,
                            language.note["validate"]["max"] * 10,
                            language.note["validate"]["divisible"] * 10,
                        )
                        / 10
                    )
                    if round(score, 0) == score:
                        score = int(score)

                model = Language(
                    account_id=account.account_id,
                    language_id=language.constant_id,
                    language_score=str(score),
                    language_certificate_date=fake.date_this_decade(),
                )
                db.session.add(model)

            db.session.commit()

        log_prefix(__file__, "Finished seeding Languages...")
    except Exception as error:
        db.session.rollback()
        log_prefix(__file__, error, type="error")
