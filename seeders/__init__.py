from flask import Blueprint, request

from seeders.application_position import application_position_seeder
from seeders.application_skill import application_skill_seeder
from seeders.company import company_seeder
from seeders.constant import constant_seeder
from seeders.user import user_seeder
from seeders.user_award import user_award_seeder
from seeders.user_education import user_education_seeder
from seeders.user_experience import user_experience_seeder
from utils.response import response_with_data, response_with_error

seeders_bp = Blueprint("seeders", __name__, url_prefix="/api/v1/seeders")


@seeders_bp.route("", methods=["POST"])
def database_seeder():
    body = request.get_json()
    reset = body.get("reset", False)
    repeat_times = body.get("repeat_times", 1000)
    try:
        constant_seeder(reset)
        user_seeder(repeat_times, reset)
        user_award_seeder(repeat_times, reset)
        user_education_seeder(repeat_times, reset)
        user_experience_seeder(repeat_times, reset)
        company_seeder(repeat_times, reset)
        application_position_seeder(reset)
        application_skill_seeder(reset)

        return response_with_data(message="Database seeded successfully!")
    except Exception as error:
        print(error)
        return response_with_error()
