# git commit -m "PBL-847 set up base"

import jwt
import numpy as np
import pandas as pd
from flask import Blueprint, request
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import MinMaxScaler

from data import (
    calc_awards,
    calc_cpa,
    calc_exp,
    calc_year,
    compare_language,
    compare_need,
)
from models.account import Account
from models.application_position import ApplicationPosition
from models.company import Company
from models.constant import Constant
from models.match import Match
from models.user import User
from utils import get_instance
from utils.environment import Env
from utils.response import response_with_error, response_with_meta

_, db = get_instance()
recommend_bp = Blueprint("recommend", __name__, url_prefix="/api/v1/recommend")


def train_data(df: pd.DataFrame):
    df = df.dropna()
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]

    scaler = MinMaxScaler()
    scaler.fit(X.values)
    X = scaler.transform(X.values)

    model = LinearRegression()
    model.fit(X, y)

    return model, scaler


def get_salary(account_id: str):
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
            calc_year(user.date_of_birth),
            1 if user.gender else 0,
            calc_exp(user.account_id),
            calc_cpa(user.account_id),
            calc_awards(user.account_id),
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
            need = compare_need(user.account_id, company.account_id)
            row.extend(
                [
                    compare_language(user.account_id, company.account_id),
                    need[0],
                    round(need[1], 2),
                    calc_year(company.established_date),
                    1,
                ]
            )
            df.loc[len(df)] = row

        # Train user model
        model, scaler = train_data(df)
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
            need = compare_need(user.account_id, company[0].account_id)
            data.extend(
                [
                    compare_language(user.account_id, company[0].account_id),
                    need[0],
                    round(need[1], 2),
                    calc_year(company[1].established_date),
                ]
            )
            data = scaler.transform(np.asarray(data).reshape(1, -1))
            predict_result = model.predict(data)
            if predict_result[0] >= 0.5:
                suggest_companies.append(
                    {
                        "predict": round(predict_result[0], 3),
                        "account_id": company[0].account_id,
                        "email": company[0].email,
                        "account_status": company[0].account_status,
                        "address": company[0].address,
                        "avatar": company[0].avatar,
                        "phone_number": company[0].phone_number,
                        "application_positions": get_salary(company[0].account_id),
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
                        "description": company[1].description,
                    }
                )
        # Response list companies
        page = request.args.get("page", 1, type=int)
        paging = request.args.get("paging", 10, type=int)
        total_page = (
            len(suggest_companies) // paging
            if len(suggest_companies) % paging == 0
            else len(suggest_companies) // paging + 1
        )
        idx_from = max((page - 1) * paging, 0)
        idx_to = min(page * paging, len(suggest_companies) - 1)
        suggest_companies = sorted(
            suggest_companies, key=lambda x: x["predict"], reverse=True
        )
        return response_with_meta(
            data=[suggest_companies[idx] for idx in range(idx_from, idx_to)],
            meta={
                "current_page": page,
                "next_page": min(page + 1, total_page),
                "previous_page": max(page - 1, 1),
                "total_page": total_page,
                "total_count": len(suggest_companies),
            },
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
        matches = Match.query.filter(Match.company_id == company.account_id).all()
        for match in matches:
            user = User.query.filter(User.account_id == match.user_id).first()  # type: ignore
            if not user:
                continue
            # Collect basic user data
            need = compare_need(user.account_id, company.account_id)
            df.loc[len(df)] = [
                calc_year(user.date_of_birth) / 100,
                1 if user.gender else 0,
                calc_exp(user.account_id),
                calc_cpa(user.account_id),
                calc_awards(user.account_id),
                compare_language(user.account_id, company.account_id),
                need[0],
                round(need[1], 2),
                calc_year(company.established_date),
                1 if match.company_matched else 0,
            ]

        # Train company model
        model, scaler = train_data(df)
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
            need = compare_need(user[0].account_id, company.account_id)
            data = np.asarray(
                [
                    calc_year(user[1].date_of_birth),
                    1 if user[1].gender else 0,
                    calc_exp(user[1].account_id),
                    calc_cpa(user[1].account_id),
                    calc_awards(user[1].account_id),
                    compare_language(user[1].account_id, company.account_id),
                    need[0],
                    round(need[1], 2),
                    calc_year(company.established_date),
                ]
            ).reshape(1, -1)
            predict_result = model.predict(scaler.transform(data))

            if predict_result[0] >= 0.5:
                suggest_users.append(
                    {
                        "predict": round(predict_result[0], 3),
                        "account_id": user[0].account_id,
                        "email": user[0].email,
                        "account_status": user[0].account_status,
                        "address": user[0].address,
                        "avatar": user[0].avatar,
                        "phone_number": user[0].phone_number,
                        "application_positions": get_salary(user[0].account_id),
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
        page = request.args.get("page", 1, type=int)
        paging = request.args.get("paging", 10, type=int)
        total_page = (
            len(suggest_users) // paging
            if len(suggest_users) % paging == 0
            else len(suggest_users) // paging + 1
        )
        idx_from = max((page - 1) * paging, 0)
        idx_to = min(page * paging, len(suggest_users) - 1)
        suggest_users = sorted(suggest_users, key=lambda x: x["predict"], reverse=True)
        return response_with_meta(
            data=[suggest_users[idx] for idx in range(idx_from, idx_to)],
            meta={
                "current_page": page,
                "next_page": min(page + 1, total_page),
                "previous_page": max(page - 1, 1),
                "total_page": total_page,
                "total_count": len(suggest_users),
            },
        )
    except Exception as error:
        return response_with_error(__file__, error=error)
