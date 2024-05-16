import re
from flask import Blueprint, request
import requests
from bs4 import BeautifulSoup
from urllib import request as ulreq
from PIL import ImageFile

from models.account import Account
from models.application_position import ApplicationPosition
from models.application_skill import ApplicationSkill
from models.company import Company
from models.constant import Constant
from models.languages import Language
from models.user import User
from models.user_award import UserAward
from models.user_education import UserEducation
from models.user_experience import UserExperience
from models.match import Match
from seed.application_position import application_position_seeder
from seed.application_skill import application_skill_seeder
from seed.company import company_seeder
from seed.constant import constant_seeder
from seed.language import language_seeder
from seed.user import user_seeder
from seed.user_award import user_award_seeder
from seed.user_education import user_education_seeder
from seed.user_experience import user_experience_seeder
from seed.match import match_seeder
from utils import get_instance, log_prefix
from utils.environment import Env
from utils.response import response_with_error, response_with_message
import os

seed_bp = Blueprint("seed", __name__, url_prefix="/api/v1/seed")

_, db = get_instance()


@seed_bp.route("", methods=["POST"])
def database_seeder():
    body = request.get_json()

    reset = body.get("reset", False)
    repeat_times = body.get("repeat_times", 1000)
    flask_key = body.get("key", "")
    if flask_key != Env.FLASK_PASSWORD:
        return response_with_error(__file__, "403 Forbidden", 403)

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

        return response_with_message(message="Database seeded successfully!")
    except Exception as error:
        return response_with_error(file=__file__, error=error)


@seed_bp.route("/crawl-image", methods=["POST"])
def crawl_image():
    body = request.get_json()

    url = body.get("url", "")
    reset = body.get("reset", False)
    limit = body.get("limit", 100)
    flask_key = body.get("key", "")
    if flask_key != Env.FLASK_PASSWORD:
        return response_with_error(__file__, "403 Forbidden", 403)

    try:
        log_prefix(__file__, "Starting to crawl images...")
        image_urls_file = os.path.join(os.getcwd(), "seed/image_urls.txt")
        if reset and os.path.exists(image_urls_file):
            os.remove(image_urls_file)

        urls = crawl(url, limit)
        for idx, url in enumerate(urls):
            with open(image_urls_file, "a", encoding="UTF8") as file:
                file.write(url + "\n")
        log_prefix(__file__, "Images crawled successfully!")
        return response_with_message(message="Images crawled successfully!")
    except Exception as error:
        return response_with_error(file=__file__, error=error)


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
        print(f"Image {url} is too small")
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
