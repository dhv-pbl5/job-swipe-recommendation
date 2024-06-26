from random import randint

from models.application_position import ApplicationPosition
from models.application_skill import ApplicationSkill
from models.constant import Constant
from seed.define_constants import SKILLS_PREFIX
from utils import get_instance, setup_logger

_, db = get_instance()


def application_skill_seeder():
    logger = setup_logger()
    try:
        logger.info("Start seeding Application Skills...")
        total_positions = ApplicationPosition.query.count()
        skills = Constant.query.filter(
            Constant.constant_type.like(f"{SKILLS_PREFIX}%")  # type: ignore
        ).all()
        query = ApplicationPosition.query.order_by(
            ApplicationPosition.created_at.desc()  # type: ignore
        )

        for idx in range(total_positions):
            position = query.offset(idx).first()
            if not position:
                continue

            for _ in range(randint(0, len(skills))):
                application_skill = ApplicationSkill(
                    application_position_id=position.id,
                    skill_id=skills[randint(0, len(skills) - 1)].constant_id,
                )
                db.session.add(application_skill)

        db.session.commit()
        logger.info("Finished seeding Application Skills.")
    except Exception as error:
        db.session.rollback()
        logger.error(error)
