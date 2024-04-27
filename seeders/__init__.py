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
from seeders.application_position import application_position_seeder
from seeders.application_skill import application_skill_seeder
from seeders.company import company_seeder
from seeders.constant import constant_seeder
from seeders.language import language_seeder
from seeders.user import user_seeder
from seeders.user_award import user_award_seeder
from seeders.user_education import user_education_seeder
from seeders.user_experience import user_experience_seeder
from utils import get_instance
from utils.response import response_with_error, response_with_message

seeders_bp = Blueprint("seeders", __name__, url_prefix="/api/v1/seeders")

_, db = get_instance()


@seeders_bp.route("", methods=["POST"])
def database_seeder():
    body = request.get_json()
    reset = body.get("reset", False)
    repeat_times = body.get("repeat_times", 1000)
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
