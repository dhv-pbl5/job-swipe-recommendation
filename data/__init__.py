import csv
import os
import random
from datetime import datetime
from time import time

from flask import Blueprint, request

from models.account import Account
from models.application_position import ApplicationPosition
from models.company import Company
from models.constant import Constant
from models.languages import Language
from models.user import User
from models.user_award import UserAward
from models.user_education import UserEducation
from models.user_experience import UserExperience
from utils import get_instance, log_prefix
from utils.environment import Env
from utils.response import response_with_error, response_with_message

_, db = get_instance()
data_bp = Blueprint("data", __name__, url_prefix="/api/v1/data")


def calc_year(start_time, end_time=None) -> int:
    if not end_time:
        end_time = datetime.today()

    age = (
        end_time.year
        - start_time.year
        - ((end_time.month, end_time.day) < (start_time.month, start_time.day))
    )
    return age


def calc_cpa(user_id: str) -> float:
    educations = UserEducation.query.filter_by(account_id=user_id).all()
    cpa = 0.0
    for education in educations:
        cpa += (
            float(education.cpa) * 0.4
            if education.is_university
            else float(education.cpa) * 2
        )

    return round(cpa, 2)


def calc_exp(user_id: str) -> int:
    experiences = UserExperience.query.filter(
        UserExperience.account_id == user_id  # type: ignore
    ).all()
    years = 0
    for experience in experiences:
        years += calc_year(
            experience.experience_start_time, experience.experience_end_time
        )

    return years


def calc_awards(user_id: str) -> int:
    return UserAward.query.filter(UserAward.account_id == user_id).count()  # type: ignore


def compare_need(usr_id: str, cpn_id: str):
    usr_apps = ApplicationPosition.query.filter(
        ApplicationPosition.account_id == usr_id  # type: ignore
    ).all()

    res = (0, 0)
    for usr_app in usr_apps:
        query = ApplicationPosition.query.filter(
            ApplicationPosition.account_id == cpn_id,  # type: ignore
            ApplicationPosition.apply_position == usr_app.apply_position,  # type: ignore
        ).first()
        if query:
            usr_need = Constant.query.filter(
                Constant.constant_id == usr_app.salary_range
            ).first()
            cpn_paid = Constant.query.filter(
                Constant.constant_id == query.salary_range
            ).first()
            if not (usr_need and cpn_paid):
                continue

            if usr_need.constant_type >= cpn_paid.constant_type:
                return (1, 1)
            else:
                res = (
                    1,
                    max(
                        res[1],
                        (int(usr_need.constant_type[-2:]) + 1)
                        / (int(cpn_paid.constant_type[-2:]) + 1),
                    ),
                )

    return res


def compare_language(compare_id: str, is_compared_id: str) -> float:
    query = (
        db.session.query(Account, Language, Constant)
        .filter(Account.account_status == True)
        .filter(Account.deleted_at == None)
        .join(Language, Account.account_id == Language.account_id)  # type: ignore
        .join(Constant, Language.language_id == Constant.constant_id)  # type: ignore
        .order_by(Language.language_id.asc())  # type: ignore
    )
    compare_languages = query.filter(Account.account_id == compare_id).all()  # type: ignore
    is_compared_languages = query.filter(Account.account_id == is_compared_id).all()  # type: ignore

    for compare_language in compare_languages:
        for is_compared_language in is_compared_languages:
            if compare_language[1].language_id != is_compared_language[1].language_id:
                continue

            if not compare_language[2].note["values"]:
                compare_value = compare_language[1].language_score
                is_compared_value = is_compared_language[1].language_score

                if compare_value >= is_compared_value:
                    return 1
                else:
                    return float(compare_value) / float(is_compared_value)
            else:
                compare_value = (
                    compare_language[2]
                    .note["values"]
                    .index(compare_language[1].language_score)
                )
                is_compared_value = (
                    compare_language[2]
                    .note["values"]
                    .index(is_compared_language[1].language_score)
                )

                if compare_value <= is_compared_value:
                    return 1
                else:
                    return (compare_value + 1) / (is_compared_value + 1)

    return 0


@data_bp.route("", methods=["POST"])
def prepare():
    try:
        body = request.get_json()
        if body.get("key", "") != Env.FLASK_PASSWORD:
            return response_with_error(__file__, "403 Forbidden", 403)

        limit = int(body.get("limit", 50))

        start_time = time()
        log_prefix(__file__, "Start preparing data...")
        csv_path = os.path.join(os.getcwd(), "data.csv")
        if os.path.exists(csv_path):
            os.remove(csv_path)

        header = [
            "age",
            "gender",
            "experiences_years",
            "cpa",
            "has_awards",
            "languages",
            "has_position",
            "salary",
            "company_age",
            "result",
        ]
        user_query = (
            db.session.query(Account, User)
            .filter(Account.account_status == True)
            .filter(Account.deleted_at == None)
            .join(User, Account.account_id == User.account_id)  # type: ignore
            .order_by(Account.created_at.desc())  # type: ignore
            .limit(limit)
        )
        company_query = (
            db.session.query(Account, Company)
            .filter(Account.account_status == True)
            .filter(Account.deleted_at == None)
            .join(Company, Account.account_id == Company.account_id)  # type: ignore
            .order_by(Account.created_at.desc())  # type: ignore
            .limit(limit)
        )

        with open(csv_path, "w", encoding="UTF8", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(header)

            for user_idx in range(user_query.count()):
                log_prefix(__file__, f"Processing user {user_idx}...")
                user = user_query.offset(user_idx).first()  # type: ignore
                if not user:
                    continue

                # Basic row data
                awards = calc_awards(user[0].account_id)
                basic_row_data = [
                    calc_year(user[1].date_of_birth),
                    1 if user[1].gender else 0,
                    calc_exp(user[0].account_id),
                    calc_cpa(user[0].account_id),
                    awards,
                ]

                # Normalize languages data
                for company_idx in range(company_query.count()):
                    row = basic_row_data.copy()
                    company = company_query.offset(company_idx).first()
                    if not company:
                        continue

                    language_score = compare_language(
                        user[0].account_id, company[0].account_id
                    )
                    company_age = calc_year(company[1].established_date)
                    need = compare_need(user[0].account_id, company[0].account_id)
                    result = 0.0
                    if need[0]:
                        result = (
                            (
                                random.uniform(0.4, 1)
                                if company_age >= 3
                                else random.uniform(0.2, 0.6)
                            )
                            + (
                                random.uniform(0.5, 1)
                                if awards
                                else random.uniform(0.1, 0.2)
                            )
                            + language_score * 3
                            + need[1] * 3
                        ) / 8

                    row.extend(
                        [
                            round(language_score, 2),
                            need[0],
                            round(need[1], 2),
                            company_age,
                            round(result, 2),
                        ]
                    )
                    writer.writerow(row)

        log_prefix(
            __file__,
            f"Finished preparing data in {round(time() - start_time, 1)} seconds.",
        )
        return response_with_message("Data prepared successfully!")
    except Exception as error:
        return response_with_error(file=__file__, error=error)
