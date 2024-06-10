from datetime import datetime

import jwt

from models.account import Account
from models.application_position import ApplicationPosition
from models.constant import Constant
from models.languages import Language
from models.user_award import UserAward
from models.user_education import UserEducation
from models.user_experience import UserExperience
from utils import get_instance
from utils.environment import Env


def decode_jwt_token(token: str | None) -> str:
    if not token:
        return ""

    payload = jwt.decode(
        token.split(" ")[1],
        Env.JWT_SECRET_KEY,
        algorithms=["HS256"],
        options={
            "verify_signature": False,
            "require": ["sub", "exp", "iat"],
            "verify_exp": "verify_signature",
            "verify_iat": "verify_signature",
        },
    )
    return payload["sub"]


def compare_language(fid, sid) -> float:
    _, db = get_instance()

    query = (
        db.session.query(Account, Language, Constant)
        .filter_by(account_status=True, deleted_at=None)
        .join(Language, Account.account_id == Language.account_id)  # type: ignore
        .join(Constant, Language.language_id == Constant.constant_id)  # type: ignore
        .order_by(Language.language_id.asc())  # type: ignore
    )
    f_languages = query.filter_by(account_id=fid).all()
    s_languages = query.filter_by(account_id=sid).all()

    for f_language in f_languages:
        for s_language in s_languages:
            if f_language[1].language_id != s_language[1].language_id:
                continue

            if not f_language[2].note["values"]:
                f_value = f_language[1].language_score
                s_value = s_language[1].language_score

                return 1 if f_value >= s_value else f_value / s_value
            else:
                f_value = (
                    f_language[2].note["values"].index(f_language[1].language_score)
                )
                s_value = (
                    s_language[2].note["values"].index(s_language[1].language_score)
                )

                return 1 if f_value <= s_value else (f_value + 1) / (s_value + 1)

    return 0


def compare_needs(fid, sid):
    f_applications = ApplicationPosition.query.filter_by(account_id=fid).all()
    if not f_applications:
        return (0, 0)

    result = (0, 0)
    for f_application in f_applications:
        query = ApplicationPosition.query.filter_by(
            account_id=sid, apply_position=f_application.apply_position
        ).first()

        if query:
            f_needs = Constant.query.filter_by(
                constant_id=f_application.salary_range
            ).first()
            s_paid = Constant.query.filter_by(constant_id=query.salary_range).first()
            if not (f_needs and s_paid):
                continue

            if f_needs.constant_type >= s_paid.constant_type:
                return (1, 1)
            else:
                res = (
                    1,
                    max(
                        res[1],
                        (int(f_needs.constant_type[-2:]) + 1)
                        / (int(s_paid.constant_type[-2:]) + 1),
                    ),
                )

    return (result[0], round(result[1], 2))


def calculate_cpa(id) -> float:
    educations = UserEducation.query.filter_by(account_id=id).all()
    cpa = 0
    for education in educations:
        cpa += (
            float(education.cpa) * 0.4
            if not education.is_university
            else float(education.cpa) * 2
        )

    return round(cpa, 2)


def calculate_time(start_time, end_time=None) -> int:
    if not end_time:
        end_time = datetime.today()

    return (
        end_time.year
        - start_time.year
        - ((end_time.month, end_time.day) < (start_time.month, start_time.day))
    )


def calculate_experiences(id) -> int:
    experiences = UserExperience.query.filter_by(account_id=id).all()

    return sum(
        calculate_time(experience.experience_start_time, experience.experience_end_time)
        for experience in experiences
    )


def calculate_awards(id) -> int:
    return UserAward.query.filter_by(account_id=id).count()


def get_salary(account_id: str):
    _, db = get_instance()

    applications = (
        db.session.query(ApplicationPosition, Constant)
        .filter(ApplicationPosition.account_id == account_id)  # type: ignore
        .join(Constant, ApplicationPosition.salary_range == Constant.constant_id)  # type: ignore
        .all()
    )
    if not applications:
        return []

    result = []
    for application in applications:
        position = (
            db.session.query(ApplicationPosition, Constant)
            .filter(ApplicationPosition.id == application[0].id)  # type: ignore
            .join(Constant, ApplicationPosition.apply_position == Constant.constant_id)  # type: ignore
            .first()
        )
        if not position:
            continue

        result.append(
            {
                "apply_position": {
                    "constant_id": position[1].constant_id,
                    "constant_name": position[1].constant_name,
                    "constant_type": position[1].constant_type,
                },
                "salary_range": {
                    "constant_id": application[1].constant_id,
                    "constant_name": application[1].constant_name,
                    "constant_type": application[1].constant_type,
                },
            }
        )

    return result
