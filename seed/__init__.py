# git commit -m "PBL-847 set up base"

from flask import Blueprint, request

from models.account import Account
from models.application_position import ApplicationPosition
from models.application_skill import ApplicationSkill
from models.company import Company
from models.constant import Constant
from models.languages import Language
from models.user import User
from models.user_award import UserAward
from models.user_education import UserEducation
from models.user_experience import UserExperience
from seed.application_position import application_position_seeder
from seed.application_skill import application_skill_seeder
from seed.company import company_seeder
from seed.constant import constant_seeder
from seed.language import language_seeder
from seed.user import user_seeder
from seed.user_award import user_award_seeder
from seed.user_education import user_education_seeder
from seed.user_experience import user_experience_seeder
from utils import get_instance
from utils.environment import Env
from utils.response import response_with_error, response_with_message

seed_bp = Blueprint("seed", __name__, url_prefix="/api/v1/seed")

_, db = get_instance()


@seed_bp.route("", methods=["POST"])
def database_seeder():
    body = request.get_json()

    reset = body.get("reset", False)
    repeat_times = body.get("repeat_times", 1000)
    flask_key = body.get("key", "")
    if flask_key != Env.FLASK_PASSWORD:
        return response_with_error(__file__, "403 Forbidden", 403)

    try:
        if reset:
            UserAward.query.delete()
            UserEducation.query.delete()
            UserExperience.query.delete()
            ApplicationPosition.query.delete()
            ApplicationSkill.query.delete()
            Company.query.delete()
            User.query.delete()
            Language.query.delete()
            Account.query.delete()
            Constant.query.delete()
            db.session.commit()

        constant_seeder()
        user_seeder(repeat_times)
        user_award_seeder(repeat_times)
        user_education_seeder(repeat_times)
        user_experience_seeder(repeat_times)
        company_seeder(repeat_times)
        language_seeder()
        application_position_seeder()
        application_skill_seeder()

        return response_with_message(message="Database seeded successfully!")
    except Exception as error:
        return response_with_error(file=__file__, error=error)
