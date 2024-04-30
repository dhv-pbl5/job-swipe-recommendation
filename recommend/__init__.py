import numpy as np
import pandas as pd
from flask import Blueprint, request
from sklearn import svm
from sklearn.model_selection import train_test_split

from data import (
    calculate_cpa,
    calculate_experience_year,
    calculate_year,
    compare_language,
)
from models.account import Account
from models.company import Company
from models.user import User
from models.user_award import UserAward
from models.user_experience import UserExperience
from utils import get_instance
from utils.response import response_with_data, response_with_error

_, db = get_instance()
recommend_bp = Blueprint("recommend", __name__, url_prefix="/api/v1/recommend")


def train_data():
    data = pd.read_csv("data.csv")

    X = data.iloc[:, :-1]
    y = data.iloc[:, -1]
    X_train, X_test, y_train, y_test = train_test_split(
        X.values, y, test_size=0.2, random_state=42
    )

    # model = LinearRegression()
    model = svm.SVC(kernel="rbf")
    model.fit(X_train, y_train)
    return model


@recommend_bp.route("/predict", methods=["GET"])
def predict():
    try:
        user_id = request.args.get("user_id", type=str)
        user = (
            db.session.query(Account, User)
            .filter(Account.account_id == user_id)  # type: ignore
            .join(User, Account.account_id == User.account_id)  # type: ignore
            .first()
        )
        if not user:
            return response_with_error(__file__, message="User not found")

        experiences = UserExperience.query.filter(
            UserExperience.account_id == user_id  # type: ignore
        ).all()
        awards = UserAward.query.filter(UserAward.account_id == user_id).all()  # type: ignore

        user_basic_row = [
            calculate_year(user[1].date_of_birth) / 100,
            1 if user[1].gender else 0,
            calculate_experience_year(experiences),
            calculate_cpa(user[0].account_id),
            1 if len(awards) > 0 else 0,
        ]

        suggest_list = []
        companies = (
            db.session.query(Account, Company)
            .filter(Account.account_status == True)
            .filter(Account.deleted_at == None)
            .join(Company, Account.account_id == Company.account_id)  # type: ignore
            .all()
        )
        model = train_data()
        for company in companies:
            row = user_basic_row.copy()
            row.extend(
                [
                    compare_language(user[0].account_id, company[0].account_id),
                    min(calculate_year(company[1].established_date) / 100, 1),
                ]
            )
            if model.predict(np.asarray(row).reshape(1, -1)) >= 0.4:
                suggest_list.append(company[0].account_id)

        return response_with_data(data=suggest_list)
    except Exception as error:
        return response_with_error(__file__, error=error)
