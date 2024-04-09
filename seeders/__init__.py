from flask import Blueprint

from seeders.constants import constants_seeder
from seeders.users import users_seeder
from utils.response import response_with_data, response_with_error

seeders_bp = Blueprint("seeders", __name__, url_prefix="/api/v1/seeders")


@seeders_bp.route("", methods=["POST"])
def DatabaseSeeder():
    try:
        constants_seeder(reset=True)
        users_seeder(repeat_time=1000, reset=True)

        return response_with_data("Database seeded successfully!")
    except Exception as error:
        return response_with_error(error=error)
