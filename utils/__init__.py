import logging
import sys
from datetime import datetime
from random import randint

import jwt
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from models.account import Account
from models.application_position import ApplicationPosition
from models.constant import Constant
from models.languages import Language
from models.user_award import UserAward
from models.user_education import UserEducation
from models.user_experience import UserExperience
from utils.environment import Env

app = None
db = None


def create_app() -> tuple[Flask, SQLAlchemy]:
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = Env.DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    CORS(app)
    db = SQLAlchemy(app)

    return app, db


def get_instance() -> tuple[Flask, SQLAlchemy]:
    global db, app
    if app and db:
        return app, db

    app, db = create_app()
    return app, db


def fake_phone_numbers():
    return "0" + "".join(str(randint(0, 9)) for _ in range(9))


def setup_logger() -> logging.Logger:
    logger = logging.getLogger()
    for handler in logger.handlers:
        logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(f"%(levelname)s - %(funcName)s | %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

    return logger


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
