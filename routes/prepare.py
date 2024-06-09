import csv
import os
import random

import numpy as np
from flask import Blueprint, request

from models.account import Account
from models.company import Company
from models.user import User
from utils import get_instance, setup_logger
from utils.common import compare_language, compare_needs
from utils.environment import Env
from utils.response import AppResponse

_, db = get_instance()

prepare_bp = Blueprint("prepare", __name__, url_prefix="/api/v1/prepare")


@prepare_bp.route("", methods=["POST"])
def prepare_example_data():
    logger = setup_logger()
    body = request.get_json()

    try:
        if body.get("key", "") != Env.FLASK_PASSWORD:
            return AppResponse.bad_request(message="Forbidden", status_code=403)

        limit = body.get("limit", 50)
        logger.info("Starting to prepare data...")

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
        users_query = (
            db.session.query(Account, User)
            .filter(Account.account_status == True)
            .filter(Account.deleted_at == None)
            .join(User, Account.account_id == User.account_id)  # type: ignore
            .order_by(Account.created_at.desc())  # type: ignore
            .limit(limit)
        )
        companies_query = (
            db.session.query(Account, Company)
            .filter(Account.account_status == True)
            .filter(Account.deleted_at == None)
            .join(Company, Account.account_id == Company.account_id)  # type: ignore
            .order_by(Account.created_at.desc())  # type: ignore
            .limit(limit)
        )

        with open(csv_path, "w", encoding="UTF-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(header)

            for user_idx in limit:
                user = users_query.offset(user_idx).first()
                if not user:
                    continue

                for company_idx in limit:
                    company = companies_query.offset(company_idx).first()
                    if not company:
                        continue

                    language_score = compare_language(
                        user[0].account_id, company[0].account_id
                    )
                    needs = compare_needs(user[0].account_id, company[0].account_id)

                    result = 0.0
                    if needs[0]:
                        result = (
                            (
                                random.uniform(0.4, 1)
                                if company[0].normalize[0] >= 3
                                else random.uniform(0.2, 0.6)
                            )
                            + (
                                random.uniform(0.5, 1)
                                if user[0].normalize[4] >= 3
                                else random.uniform(0.1, 0.2)
                            )
                            + language_score * 3
                            + needs[1] * 3
                        ) / 8

                    writer.writerow(
                        np.concatenate(
                            (
                                np.array(user[0].normalize),
                                np.array(needs),
                                np.array(company[0].normalize),
                                np.array([round(result, 2)]),
                            ),
                            axis=1,
                        )
                    )

        return AppResponse.success_with_message("Data prepared successfully")
    except Exception as e:
        return AppResponse.server_error(e)
