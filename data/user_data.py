from datetime import datetime

from flask import Blueprint

from models.company import Company
from models.user import User
from models.user_award import UserAward
from models.user_education import UserEducation
from models.user_experience import UserExperience
from utils import get_instance
from utils.response import AppResponse

_, db = get_instance()
normalize_bp = Blueprint("normalize", __name__, url_prefix="/api/v1/normalize")


def calc_cpa(user_id) -> float:
    educations = UserEducation.query.filter_by(account_id=user_id).all()
    cpa = float(0)
    for education in educations:
        cpa += (
            float(education.cpa) * 0.4
            if not education.is_university
            else float(education.cpa) * 2
        )

    return round(cpa, 2)


def calc_year(start_time, end_time=None) -> int:
    if not end_time:
        end_time = datetime.today()

    return (
        end_time.year
        - start_time.year
        - ((end_time.month, end_time.day) < (start_time.month, start_time.day))
    )


def calc_exp(user_id) -> int:
    experiences = UserExperience.query.filter_by(account_id=user_id).all()

    return sum(
        calc_year(experience.experience_start_time, experience.experience_end_time)
        for experience in experiences
    )


def calc_awards(user_id) -> int:
    return UserAward.query.filter_by(account_id=user_id).count()


@normalize_bp.route("/user/<user_id>", methods=["POST"])
def user_normalize(user_id):
    try:
        user = User.query.filter_by(account_id=user_id).first()
        if not user:
            return AppResponse.bad_request(f"User with id = {user_id} not found")

        data = [
            calc_year(user[0].date_of_birth),
            1 if user[0].gender else 0,
            calc_exp(user_id),
            calc_cpa(user_id),
            calc_awards(user_id),
        ]
        user.normalize = data
        db.session.commit()

        return AppResponse.success_with_message(
            f"Updated user with id = {user_id} successfully!"
        )
    except Exception as e:
        db.session.rollback()
        return AppResponse.server_error(e)


@normalize_bp.route("/company/<company_id>", methods=["POST"])
def company_normalize(company_id):
    try:
        company = Company.query.filter_by(account_id=company_id).first()
        if not company:
            return AppResponse.bad_request(f"Company with id = {company_id} not found")

        data = [
            calc_year(company[0].established_time),
        ]
        company.normalize = data
        db.session.commit()

        return AppResponse.success_with_message(
            f"Updated company with id = {company_id} successfully!"
        )
    except Exception as e:
        db.session.rollback()
        return AppResponse.server_error(e)
