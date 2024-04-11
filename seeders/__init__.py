from flask import Blueprint, request

from seeders.companies import companies_seeder
from seeders.constants import constants_seeder
from seeders.user_awards import user_awards_seeder
from seeders.user_educations import user_educations_seeder
from seeders.user_experiences import user_experiences_seeder
from seeders.users import users_seeder
from utils.response import response_with_data, response_with_error

seeders_bp = Blueprint("seeders", __name__, url_prefix="/api/v1/seeders")


@seeders_bp.route("", methods=["POST"])
def database_seeder():
    body = request.get_json()
    reset = body.get("reset", False)
    repeat_times = body.get("repeat_times", 1000)
    try:
        constants_seeder(reset)
        users_seeder(repeat_times, reset)
        user_awards_seeder(repeat_times, reset)
        user_educations_seeder(repeat_times, reset)
        user_experiences_seeder(repeat_times, reset)
        companies_seeder(repeat_times, reset)
        return response_with_data(message="Database seeded successfully!")
    except Exception:
        return response_with_error()
