from models.constant import Constant
from seed.define_constants import (
    EXPERIENCE_TYPES,
    EXPERIENCE_TYPES_PREFIX,
    LANGUAGES,
    LANGUAGES_PREFIX,
    NOTIFICATIONS,
    NOTIFICATIONS_PREFIX,
    POSITIONS,
    POSITIONS_PREFIX,
    SALARY_RANGES,
    SALARY_RANGES_PREFIX,
    SKILLS,
    SKILLS_PREFIX,
    SYSTEM_ROLES,
)
from utils import get_instance, setup_logger

_, db = get_instance()


def common_constants(type, prefix: str):
    for idx, name in enumerate(type):
        constant = Constant(constant_name=name, prefix=prefix, index=idx)
        db.session.add(constant)


def constant_seeder():
    logger = setup_logger()
    try:
        logger.info("Start seeding Constants...")
        for idx, (name, prefix) in enumerate(SYSTEM_ROLES):
            constant = Constant(constant_name=name, prefix=prefix, index=idx)
            db.session.add(constant)

        common_constants(EXPERIENCE_TYPES, EXPERIENCE_TYPES_PREFIX)
        common_constants(POSITIONS, POSITIONS_PREFIX)
        common_constants(SKILLS, SKILLS_PREFIX)
        common_constants(NOTIFICATIONS, NOTIFICATIONS_PREFIX)
        common_constants(SALARY_RANGES, SALARY_RANGES_PREFIX)

        for idx, language in enumerate(LANGUAGES):
            constant = Constant(
                constant_name=language["name"],
                prefix=LANGUAGES_PREFIX,
                index=idx,
                note=language["note"],
            )
            db.session.add(constant)

        db.session.commit()
        logger.info("Finished seeding Constants.")
    except Exception as error:
        db.session.rollback()
        logger.error(error)
