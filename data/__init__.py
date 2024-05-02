import csv
import os
import random
from datetime import datetime
from time import time

from flask import Blueprint
from tqdm import trange

from models.account import Account
from models.company import Company
from models.constant import Constant
from models.languages import Language
from models.user import User
from models.user_award import UserAward
from models.user_education import UserEducation
from models.user_experience import UserExperience
from utils import get_instance
from utils.response import response_with_error, response_with_message

_, db = get_instance()
data_bp = Blueprint("data", __name__, url_prefix="/api/v1/data")


def calculate_year(start_time, end_time=None) -> int:
    if not end_time:
        end_time = datetime.today()

    age = (
        end_time.year
        - start_time.year
        - ((end_time.month, end_time.day) < (start_time.month, start_time.day))
    )
    return age


def calculate_cpa(account_id: str) -> float:
    educations = UserEducation.query.filter_by(account_id=account_id).all()
    cpa = 0.0
    for education in educations:
        cpa += (
            float(education.cpa) * 0.4 if education.cpa else float(education.cpa) * 3
        ) / 100

    return round(cpa, 3)


def calculate_experience_year(account_id: str) -> int:
    experiences = UserExperience.query.filter(
        UserExperience.account_id == account_id  # type: ignore
    ).all()
    years = 0

    for experience in experiences:
        years += calculate_year(
            experience.experience_start_time, experience.experience_end_time
        )

    return years


def calculate_awards(account_id: str) -> int:
    awards = UserAward.query.filter(UserAward.account_id == account_id).all()  # type: ignore
    return 1 if len(awards) > 0 else 0


def compare_language(compare_id: str, is_compared_id: str) -> int:
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
                if (
                    compare_language[1].language_score
                    >= is_compared_language[1].language_score
                ):
                    return 1
            elif compare_language[2].note["values"].index(
                compare_language[1].language_score
            ) <= compare_language[2].note["values"].index(
                is_compared_language[1].language_score
            ):
                return 1

    return 0


@data_bp.route("", methods=["POST"])
def prepare():
    try:
        start_time = time()
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
            "company_age",
            "result",
        ]
        user_query = (
            db.session.query(Account, User)
            .filter(Account.account_status == True)
            .filter(Account.deleted_at == None)
            .join(User, Account.account_id == User.account_id)  # type: ignore
            .order_by(Account.created_at.desc())  # type: ignore
            .limit(50)
        )
        company_query = (
            db.session.query(Account, Company)
            .filter(Account.account_status == True)
            .filter(Account.deleted_at == None)
            .join(Company, Account.account_id == Company.account_id)  # type: ignore
            .order_by(Account.created_at.desc())  # type: ignore
            .limit(50)
        )

        with open(csv_path, "w", encoding="UTF8", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(header)

            for user_idx in trange(user_query.count()):
                user = user_query.offset(user_idx).first()  # type: ignore
                if not user:
                    continue

                # Basic row data
                awards = calculate_awards(user[0].account_id)
                basic_row_data = [
                    calculate_year(user[1].date_of_birth) / 100,
                    1 if user[1].gender else 0,
                    calculate_experience_year(user[0].account_id),
                    calculate_cpa(user[0].account_id),
                    calculate_awards(user[0].account_id),
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
                    company_age = min(
                        calculate_year(company[1].established_date) / 100, 1
                    )
                    result = (
                        random.choice([0, 1, 1])
                        if (company_age > 0.03 and awards)
                        else random.choice([0, 0, 1])
                    )
                    if not language_score:
                        result = 0

                    row.extend([language_score, company_age, result])
                    writer.writerow(row)

        return response_with_message(
            message=f"Data prepared successfully! Execution time: {round(time() - start_time, 3)} seconds."
        )
    except Exception as error:
        return response_with_error(file=__file__, error=error)
