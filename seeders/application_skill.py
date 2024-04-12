from random import randint

from models.application_position import ApplicationPosition
from models.application_skill import ApplicationSkill
from models.constant import Constant
from utils import get_instance

_, db = get_instance()


def application_skill_seeder(reset=False):
    if reset:
        ApplicationSkill.query.delete()
        db.session.commit()

    skills = Constant.query.filter(Constant.constant_type.like("04%")).all()  # type: ignore
    total_positions = ApplicationPosition.query.count()
    query = ApplicationPosition.query.order_by(ApplicationPosition.created_at.desc())  # type: ignore
    for idx in range(total_positions):
        position = query.offset(idx).first()
        if not position:
            continue

        application_skill = ApplicationSkill(
            application_position_id=position.id,
            skill_id=skills[randint(0, len(skills) - 1)].constant_id,
        )
        db.session.add(application_skill)
        db.session.commit()
