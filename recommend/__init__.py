from datetime import datetime

import jwt
import numpy as np
import pandas as pd
from flask import Blueprint, request
from sklearn.linear_model import LinearRegression

from data import (
    calculate_awards,
    calculate_cpa,
    calculate_experience_year,
    calculate_year,
    compare_language,
)
from models.account import Account
from models.company import Company
from models.constant import Constant
from models.match import Match
from models.user import User
from utils import get_instance
from utils.environment import Env
from utils.response import response_with_data, response_with_error

_, db = get_instance()
recommend_bp = Blueprint("recommend", __name__, url_prefix="/api/v1/recommend")


def train_data(df: pd.DataFrame):
    df = df.dropna()
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]

    model = LinearRegression()
    model.fit(X.values, y)

    return model


def decode_jwt_token(jwt_token: str | None) -> str | None:
    if not jwt_token:
        return None

    jwt_payload = jwt.decode(
        jwt_token.split(" ")[1],
        Env.JWT_SECRET_KEY,
        algorithms=["HS256"],
        options={
            "verify_signature": False,
            "require": ["sub", "exp", "iat"],
            "verify_exp": "verify_signature",
            "verify_iat": "verify_signature",
        },
    )
    return jwt_payload["sub"]


@recommend_bp.route("/user", methods=["GET"])
def user_predict():
    try:
        account_id = decode_jwt_token(request.headers.get("Authorization"))
        user = User.query.filter(User.account_id == account_id).first()  # type: ignore
        if not user:
            return response_with_error(__file__, message="401 Unauthorized")

        # Collect basic user data
        user_basic_row = [
            calculate_year(user.date_of_birth) / 100,
            1 if user.gender else 0,
            calculate_experience_year(user.account_id),
            calculate_cpa(user.account_id),
            calculate_awards(user.account_id),
        ]

        # Collect previous matched data
        df = pd.read_csv("data.csv")
        matches = Match.query.filter(
            Match.user_id == user.account_id,
            Match.user_matched == True,  # type: ignore
        ).all()
        for match in matches:
            company = Company.query.filter(
                Company.account_id == match.company_id  # type: ignore
            ).first()
            if not company:
                continue

            # Create new user row
            row = user_basic_row.copy()
            row.extend(
                [
                    compare_language(user.account_id, company.account_id),
                    min(calculate_year(company.established_date) / 100, 1),
                    1,
                ]
            )
            df.loc[len(df)] = row

        # Train user model
        model = train_data(df)
        suggest_companies = []
        companies = (
            db.session.query(Account, Company, Constant)
            .filter(Account.deleted_at == None)
            .filter(Account.account_status == True)
            .join(Company, Account.account_id == Company.account_id)  # type: ignore
            .join(Constant, Account.system_role == Constant.constant_id)  # type: ignore
            .all()
        )
        for company in companies:
            data = user_basic_row.copy()
            data.extend(
                [
                    compare_language(user.account_id, company[0].account_id),
                    min(calculate_year(company[1].established_date) / 100, 1),
                ]
            )
            data = np.asarray(data).reshape(1, -1)
            predict_result = model.predict(data)
            if predict_result[0] >= 0.7:
                suggest_companies.append(
                    {
                        "predict_result": round(predict_result[0], 3),
                        "account_id": company[0].account_id,
                        "email": company[0].email,
                        "account_status": company[0].account_status,
                        "address": company[0].address,
                        "avatar": company[0].avatar,
                        "phone_number": company[0].phone_number,
                        "system_role": {
                            "constant_id": company[0].system_role,
                            "constant_name": company[2].constant_name,
                            "constant_type": company[2].constant_type,
                        },
                        "created_at": company[0].created_at.strftime(
                            "%Y-%m-%dT%H:%M:%S"
                        ),
                        "updated_at": (
                            company[0].updated_at.strftime("%Y-%m-%dT%H:%M:%S")
                            if company[0].updated_at
                            else None
                        ),
                        "deleted_at": (
                            company[0].deleted_at.strftime("%Y-%m-%dT%H:%M:%S")
                            if company[0].deleted_at
                            else None
                        ),
                        "company_name": company[1].company_name,
                        "company_url": company[1].company_url,
                        "established_date": company[1].established_date.strftime(
                            "%Y-%m-%dT%H:%M:%S"
                        ),
                    }
                )

        # Response list companies
        return response_with_data(
            data={
                "companies": sorted(
                    suggest_companies, key=lambda x: x["predict_result"], reverse=True
                ),
                "length": len(suggest_companies),
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M"),
            }
        )
    except Exception as error:
        return response_with_error(__file__, error=error)


@recommend_bp.route("/company", methods=["GET"])
def company_predict():
    try:
        account_id = decode_jwt_token(request.headers.get("Authorization"))
        company = Company.query.filter(Company.account_id == account_id).first()  # type: ignore
        if not company:
            return response_with_error(__file__, message="401 Unauthorized")

        # Collect previous data
        df = pd.read_csv("data.csv")
        matches = Match.query.filter(
            Match.company_id == company.account_id,
            Match.company_matched == True,  # type: ignore
        ).all()
        for match in matches:
            user = User.query.filter(User.account_id == match.user_id).first()  # type: ignore
            if not user:
                continue

            # Collect basic user data
            df.loc[len(df)] = [
                calculate_year(user.date_of_birth) / 100,
                1 if user.gender else 0,
                calculate_experience_year(user.account_id),
                calculate_cpa(user.account_id),
                calculate_awards(user.account_id),
                compare_language(user.account_id, company.account_id),
                min(calculate_year(company.established_date) / 100, 1),
                1,
            ]

        # Train company model
        model = train_data(df)
        suggest_users = []
        users = (
            db.session.query(Account, User, Constant)
            .filter(Account.deleted_at == None)
            .filter(Account.account_status == True)
            .join(User, Account.account_id == User.account_id)  # type: ignore
            .join(Constant, Account.system_role == Constant.constant_id)  # type: ignore
            .all()
        )
        for user in users:
            data = np.asarray(
                [
                    calculate_year(user.date_of_birth) / 100,
                    1 if user.gender else 0,
                    calculate_experience_year(user.account_id),
                    calculate_cpa(user.account_id),
                    calculate_awards(user.account_id),
                    compare_language(user.account_id, company.account_id),
                    min(calculate_year(company.established_date) / 100, 1),
                ]
            ).reshape(1, -1)
            predict_result = model.predict(data)
            if predict_result[0] >= 0.4:
                suggest_users.append(
                    {
                        "predict_result": round(predict_result[0], 3),
                        "account_id": user[0].account_id,
                        "email": user[0].email,
                        "account_status": user[0].account_status,
                        "address": user[0].address,
                        "avatar": user[0].avatar,
                        "phone_number": user[0].phone_number,
                        "system_role": {
                            "constant_id": user[0].system_role,
                            "constant_name": user[2].constant_name,
                            "constant_type": user[2].constant_type,
                        },
                        "created_at": user[0].created_at.strftime("%Y-%m-%dT%H:%M:%S"),
                        "updated_at": (
                            user[0].updated_at.strftime("%Y-%m-%dT%H:%M:%S")
                            if user[0].updated_at
                            else None
                        ),
                        "deleted_at": (
                            user[0].deleted_at.strftime("%Y-%m-%dT%H:%M:%S")
                            if user[0].deleted_at
                            else None
                        ),
                        "first_name": user[1].first_name,
                        "last_name": user[1].last_name,
                        "gender": user[1].gender,
                        "date_of_birth": user[1].date_of_birth.strftime(
                            "%Y-%m-%dT%H:%M:%S"
                        ),
                        "summary_introduction": user[1].summary_introduction,
                    }
                )

        # Response list users
        return response_with_data(
            data={
                "users": sorted(
                    suggest_users, key=lambda x: x["predict_result"], reverse=True
                ),
                "length": len(suggest_users),
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M"),
            }
        )
    except Exception as error:
        return response_with_error(__file__, error=error)
