from flask import Blueprint, request

from seeders.constants import constants_seeder
from seeders.user_awards import user_awards_seeder
from seeders.user_educations import user_educations_seeder
from seeders.user_experiences import user_experiences_seeder
from seeders.users import users_seeder
from utils.response import response_with_data, response_with_error

seeders_bp = Blueprint("seeders", __name__, url_prefix="/api/v1/seeders")


@seeders_bp.route("", methods=["POST"])
def database_seeder():
    reset = request.json.get("reset", False)
    repeat_times = request.json.get("repeat_times", 1000)

    try:
        constants_seeder(reset)
        users_seeder(repeat_times, reset)
        user_awards_seeder(repeat_times, reset)
        user_educations_seeder(repeat_times, reset)
        user_experiences_seeder(repeat_times, reset)

        return response_with_data(message="Database seeded successfully!")
    except Exception as error:
        response_with_error(error)
