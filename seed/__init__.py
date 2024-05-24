import os
import re
from urllib import request as ulreq

import requests
from bs4 import BeautifulSoup
from flask import Blueprint, request
from PIL import ImageFile

from models.account import Account
from models.application_position import ApplicationPosition
from models.application_skill import ApplicationSkill
from models.company import Company
from models.constant import Constant
from models.languages import Language
from models.match import Match
from models.user import User
from models.user_award import UserAward
from models.user_education import UserEducation
from models.user_experience import UserExperience
from seed.application_position import application_position_seeder
from seed.application_skill import application_skill_seeder
from seed.company import company_seeder
from seed.constant import constant_seeder
from seed.language import language_seeder
from seed.match import match_seeder
from seed.user import user_seeder
from seed.user_award import user_award_seeder
from seed.user_education import user_education_seeder
from seed.user_experience import user_experience_seeder
from utils import get_instance, setup_logging
from utils.environment import Env
from utils.response import AppResponse

seed_bp = Blueprint("seed", __name__, url_prefix="/api/v1/seed")

_, db = get_instance()


@seed_bp.route("", methods=["POST"])
def database_seeder():
    body = request.get_json()

    reset = body.get("reset", False, type=bool)
    repeat_times = body.get("repeat_times", 1000, type=int)
    flask_key = body.get("key", "", type=str)
    if flask_key != Env.FLASK_PASSWORD:
        return AppResponse.bad_request(message="Forbidden", status_code=403)

    try:
        if reset:
            UserAward.query.delete()
            UserEducation.query.delete()
            UserExperience.query.delete()
            ApplicationPosition.query.delete()
            ApplicationSkill.query.delete()
            Company.query.delete()
            User.query.delete()
            Language.query.delete()
            Account.query.delete()
            Constant.query.delete()
            Match.query.delete()
            db.session.commit()

        constant_seeder()
        user_seeder(repeat_times)
        user_award_seeder(repeat_times)
        user_education_seeder(repeat_times)
        user_experience_seeder(repeat_times)
        company_seeder(repeat_times)
        language_seeder()
        application_position_seeder()
        application_skill_seeder()
        match_seeder()

        return AppResponse.success_with_message(message="Database seeded successfully!")
    except Exception as error:
        return AppResponse.server_error(error=error)


@seed_bp.route("/company/crawl-image", methods=["POST"])
def crawl_company_image():
    body = request.get_json()

    url = body.get("url", "", type=str)
    reset = body.get("reset", False, type=bool)
    limit = body.get("limit", 100, type=int)
    flask_key = body.get("key", "", type=str)
    if flask_key != Env.FLASK_PASSWORD:
        return AppResponse.bad_request(message="Forbidden", status_code=403)

    try:
        logger = setup_logging()
        logger.info("Starting to crawl company images...")
        image_urls_file = os.path.join(os.getcwd(), "seed/images/company_avatar.txt")
        if reset and os.path.exists(image_urls_file):
            os.remove(image_urls_file)

        urls = crawl(url, limit)
        for url in urls:
            with open(image_urls_file, "a", encoding="UTF8") as file:
                file.write(url + "\n")

        logger.info("Company images crawled successfully!")
        return AppResponse.success_with_message(
            message="Company images crawled successfully!"
        )
    except Exception as error:
        return AppResponse.server_error(error=error)


@seed_bp.route("/user/crawl-image", methods=["POST"])
def crawl_user_image():
    body = request.get_json()

    url = body.get("url", "", type=str)
    reset = body.get("reset", False, type=bool)
    limit = body.get("limit", 100, type=int)
    flask_key = body.get("key", "")
    if flask_key != Env.FLASK_PASSWORD:
        return AppResponse.bad_request(message="Forbidden", status_code=403)

    try:
        logger = setup_logging()
        logger.info("Starting to crawl user images...")
        image_urls_file = os.path.join(os.getcwd(), "seed/images/user_avatar.txt")
        if reset and os.path.exists(image_urls_file):
            os.remove(image_urls_file)

        urls = crawl(url, limit)
        for url in urls:
            with open(image_urls_file, "a", encoding="UTF8") as file:
                file.write(url + "\n")

        logger.info("User images crawled successfully!")
        return AppResponse.success_with_message(
            message="User images crawled successfully!"
        )
    except Exception as error:
        return AppResponse.server_error(error=error)


def crawl(web_url: str, limit) -> list:
    try:
        response = requests.get(web_url)
        soup = BeautifulSoup(response.content, "html.parser")
        image_tags = soup.find_all("img")
        urls = [img["src"] for img in image_tags if "src" in img.attrs]
        count = 0
        result = []
        for url in urls:
            if count >= limit:
                break
            if validate_image(url):
                result.append(url)
                count += 1

        return result
    except Exception as e:
        raise e


def validate_image(url: str) -> bool:
    if not re.search(
        r"((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)", url
    ):
        return False

    bytes, size = get_size(url)
    if bytes < 1024:
        return False

    if size and (size[0] < 240 or size[1] < 320):
        return False

    return True


def get_size(uri):
    file = ulreq.urlopen(uri)
    size = file.headers.get("content-length")
    if size:
        size = int(size)

    p = ImageFile.Parser()
    while True:
        data = file.read(1024)
        if not data:
            break
        p.feed(data)
        if p.image:
            return size, p.image.size

    file.close()
    return size, None
