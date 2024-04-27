from datetime import datetime

from flask import Blueprint

from models.languages import Language
from models.user import User
from models.user_award import UserAward
from models.user_education import UserEducation
from models.user_experience import UserExperience
from utils.response import response_with_error, response_with_message

suggestions_bp = Blueprint("suggestions", __name__, url_prefix="/api/v1/suggestions")


def calculate_year(start_time, end_time=None):
    if not end_time:
        end_time = datetime.today()

    age = (
        end_time.year
        - start_time.year
        - ((end_time.month, end_time.day) < (start_time.month, start_time.day))
    )
    return age


@suggestions_bp.route("/prepare-data", methods=["GET"])
def prepare_data():
    try:
        user_query = User.query.order_by(User.created_at.desc())  # type: ignore
        for idx in range(user_query.count()):
            user = user_query.offset(idx).first()  # type: ignore
            if not user:
                continue

            educations = UserEducation.query.filter_by(account_id=user.account_id).all()
            experiences = UserExperience.query.filter_by(
                account_id=user.account_id
            ).all()
            awards = UserAward.query.filter_by(account_id=user.account_id).all()
            languages = Language.query.filter_by(account_id=user.account_id).all()

            # return response_with_data(
            #     data={
            #         "age": calculate_year(user.date_of_birth) / 100,
            #         "gender": 1 if user.gender else 0,
            #         "experiences": sum(
            #             calculate_year(
            #                 experience.experience_start_time, experience.experience_end_time
            #             )
            #             for experience in user_experience
            #         ),
            #         "gpa": [
            #             round(float(education.cpa / 10), 3) for education in user_education
            #         ],
            #         "awards": len(user_awards),
            #         "languages": [
            #             user_languages.language_score for user_languages in user_languages
            #         ],
            #     }
            # )
        return response_with_message(message="Data prepared successfully!")
    except Exception as error:
        return response_with_error(file=__file__, error=error)
