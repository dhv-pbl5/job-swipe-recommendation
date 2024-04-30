import csv
import os
from datetime import datetime
from random import randint
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
from seeder.define_constants import LANGUAGES_PREFIX
from utils import get_instance
from utils.response import response_with_error, response_with_message

_, db = get_instance()
data_bp = Blueprint("data", __name__, url_prefix="/api/v1/data")


def calculate_year(start_time, end_time=None):
    if not end_time:
        end_time = datetime.today()

    age = (
        end_time.year
        - start_time.year
        - ((end_time.month, end_time.day) < (start_time.month, start_time.day))
    )
    return age


def calculate_cpa(account_id: str):
    educations = UserEducation.query.filter_by(account_id=account_id).all()
    cpa = 0.0
    for education in educations:
        cpa += (
            float(education.cpa) * 0.4 if education.cpa else float(education.cpa) * 3
        ) / 100

    return round(cpa, 3)


def calculate_experience_year(experiences):
    experience_year = 0
    for experience in experiences:
        experience_year += calculate_year(
            experience.experience_start_time, experience.experience_end_time
        )

    return experience_year


def compare_language(compare_id: str, is_compared_id: str) -> int:
    query = (
        db.session.query(Account, Language)
        .filter(Account.account_status == True)
        .filter(Account.deleted_at == None)
        .join(Language, Account.account_id == Language.account_id)  # type: ignore
        .order_by(Language.language_id.asc())  # type: ignore
    )
    compare_languages = query.filter(Account.account_id == compare_id).all()  # type: ignore
    is_compared_languages = query.filter(Account.account_id == is_compared_id).all()  # type: ignore

    for compare_language in compare_languages:
        for is_compared_language in is_compared_languages:
            if compare_language[1].language_id != is_compared_language[1].language_id:
                continue

            language = (
                Constant.query.filter(
                    Constant.constant_type.like(f"{LANGUAGES_PREFIX}%")  # type: ignore
                )
                .filter(Constant.constant_id == compare_language[1].language_id)
                .first()
            )
            if not language:
                continue

            if not language.note["values"]:
                if (
                    compare_language[1].language_score
                    >= is_compared_language[1].language_score
                ):
                    return 1
            elif language.note["values"].index(
                compare_language[1].language_score
            ) <= language.note["values"].index(is_compared_language[1].language_score):
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
            # User
            "age",
            "gender",
            "experiences_years",
            "cpa",
            "has_awards",
            "languages",
            # Company
            "company_age",
            # Result
            "result",
        ]
        user_query = (
            db.session.query(Account, User)
            .filter(Account.account_status == True)
            .filter(Account.deleted_at == None)
            .join(User, Account.account_id == User.account_id)  # type: ignore
            .order_by(Account.created_at.desc())  # type: ignore
        )
        company_query = (
            db.session.query(Account, Company)
            .filter(Account.account_status == True)
            .filter(Account.deleted_at == None)
            .join(Company, Account.account_id == Company.account_id)  # type: ignore
            .order_by(Account.created_at.desc())  # type: ignore
        )

        with open(csv_path, "w", encoding="UTF8", newline="") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(header)

            for user_idx in trange(user_query.count()):
                user = user_query.offset(user_idx).first()  # type: ignore
                if not user:
                    continue

                # Normalize experience and awards data
                experiences = UserExperience.query.filter_by(
                    account_id=user[0].account_id
                ).all()
                awards = UserAward.query.filter_by(account_id=user[0].account_id).all()

                # Basic row data
                basic_row_data = [
                    calculate_year(user[1].date_of_birth) / 100,
                    1 if user[1].gender else 0,
                    calculate_experience_year(experiences),
                    calculate_cpa(user[0].account_id),
                    1 if len(awards) > 0 else 0,
                ]

                # Normalize languages data
                for company_idx in range(company_query.count()):
                    row = basic_row_data.copy()
                    company = company_query.offset(company_idx).first()
                    if not company:
                        continue

                    row.extend(
                        [
                            compare_language(user[0].account_id, company[0].account_id),
                            min(calculate_year(company[1].established_date) / 100, 1),
                            randint(0, 1),
                        ]
                    )

                    writer.writerow(row)

        return response_with_message(
            message=f"Data prepared successfully! Execution time: {round(time() - start_time, 3)} seconds."
        )
    except Exception as error:
        return response_with_error(file=__file__, error=error)
