import numpy as np
import pandas as pd
from flask import Blueprint, request

from models.account import Account
from models.company import Company
from models.constant import Constant
from models.match import Match
from models.user import User
from utils import get_instance
from utils.common import compare_language, compare_needs, decode_jwt_token, get_salary
from utils.constant import AppConstant
from utils.learning import train_data
from utils.response import AppResponse

_, db = get_instance()

recommend_bp = Blueprint("recommend", __name__, url_prefix="/api/v1/recommend")


@recommend_bp.route("/user", methods=["GET"])
def user_predict():
    try:
        account_id = decode_jwt_token(request.headers.get("Authorization"))
        user = User.query.filter_by(account_id=account_id).first()
        if not user:
            return AppResponse.bad_request(message="Unauthorized")

        # Collect previous matched data
        df = pd.read_csv("data.csv")
        matches = Match.query.filter_by(
            user_id=user.account_id, user_matched=True
        ).all()
        for match in matches:
            company = Company.query.filter_by(account_id=match.company_id).first()
            if not company:
                continue

            need = compare_needs(user.account_id, company.account_id)
            df.loc[len(df)] = np.concatenate(
                (
                    np.array(user.normalize),
                    np.array(
                        [
                            compare_language(user.account_id, company.account_id),
                            need[0],
                            need[1],
                        ]
                    ),
                    np.array(company.normalize),
                    np.array([1]),
                ),
                axis=1,
            )

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
            need = compare_needs(user.account_id, company[0].account_id)
            data = np.concatenate(
                (
                    np.array(user.normalize),
                    np.array(
                        [
                            compare_language(user.account_id, company[0].account_id),
                            need[0],
                            need[1],
                        ]
                    ),
                    np.array(company.normalize),
                ),
                axis=1,
            ).reshape(1, -1)
            data = scaler.transform(data)

            predict_result = model.predict(data)
            if predict_result[0] >= AppConstant.ACCEPT_THRESHOLD:
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

        idx_from = max((page - 1) * paging, 0)
        idx_to = min(page * paging, len(suggest_companies) - 1)
        suggest_companies = sorted(
            suggest_companies, key=lambda x: x["predict"], reverse=True
        )

        return AppResponse.success_with_meta(
            data=[suggest_companies[idx] for idx in range(idx_from, idx_to)],
            page=page,
            page_size=paging,
            total_count=len(suggest_companies),
        )
    except Exception as error:
        return AppResponse.server_error(error=error)


@recommend_bp.route("/company", methods=["GET"])
def company_predict():
    try:
        account_id = decode_jwt_token(request.headers.get("Authorization"))
        company = Company.query.filter(Company.account_id == account_id).first()  # type: ignore
        if not company:
            return AppResponse.bad_request(message="Unauthorized")

        # Collect previous data
        df = pd.read_csv("data.csv")
        matches = Match.query.filter(Match.company_id == company.account_id).all()
        for match in matches:
            user = User.query.filter(User.account_id == match.user_id).first()  # type: ignore
            if not user:
                continue

            need = compare_needs(user.account_id, company.account_id)
            df.loc[len(df)] = np.concatenate(
                (
                    np.array(user.normalize),
                    np.array(
                        [
                            compare_language(user.account_id, company.account_id),
                            need[0],
                            round(need[1], 2),
                        ]
                    ),
                    np.array(company.normalize),
                    np.array([1 if match.user_matched else 0]),
                ),
                axis=1,
            )

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
            need = compare_needs(user[0].account_id, company.account_id)
            data = np.concatenate(
                (
                    np.array(user[1].normalize),
                    np.array(
                        [
                            compare_language(user[1].account_id, company.account_id),
                            need[0],
                            round(need[1], 2),
                        ]
                    ),
                    np.array(company.normalize),
                ),
                axis=1,
            ).reshape(1, -1)
            predict_result = model.predict(scaler.transform(data))

            if predict_result[0] >= AppConstant.ACCEPT_THRESHOLD:
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

        idx_from = max((page - 1) * paging, 0)
        idx_to = min(page * paging, len(suggest_users) - 1)
        suggest_users = sorted(suggest_users, key=lambda x: x["predict"], reverse=True)

        return AppResponse.success_with_meta(
            data=[suggest_users[idx] for idx in range(idx_from, idx_to)],
            page=page,
            page_size=paging,
            total_count=len(suggest_users),
        )
    except Exception as error:
        return AppResponse.server_error(error=error)
