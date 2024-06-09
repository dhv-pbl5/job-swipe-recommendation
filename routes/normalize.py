from flask import Blueprint

from models.company import Company
from models.user import User
from utils import get_instance, setup_logger
from utils.common import (
    calculate_awards,
    calculate_cpa,
    calculate_experiences,
    calculate_time,
)
from utils.response import AppResponse

_, db = get_instance()

normalize_bp = Blueprint("normalize", __name__, url_prefix="/api/v1/normalize")


@normalize_bp.route("/user/<user_id>", methods=["POST"])
def user_normalize(user_id):
    logger = setup_logger()
    try:
        user = User.query.filter_by(account_id=user_id).first()
        if not user:
            return AppResponse.bad_request(f"User with id = {user_id} not found")

        data = [
            calculate_time(user.date_of_birth),
            1 if user.gender else 0,
            calculate_experiences(user_id),
            calculate_cpa(user_id),
            calculate_awards(user_id),
        ]
        user.normalize = data
        db.session.add(user)
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
            calculate_time(company.established_time),
        ]
        company.normalize = data
        db.session.add(company)
        db.session.commit()

        return AppResponse.success_with_message(
            f"Updated company with id = {company_id} successfully!"
        )
    except Exception as e:
        db.session.rollback()
        return AppResponse.server_error(e)