from tqdm import tqdm

from models.Constants import Constants
from utils import get_instance

_, db = get_instance()

SYSTEM_ROLE = [("Admin", "01100"), ("User", "01110"), ("Company", "01120")]
EXPERIENCE_TYPES = [("Work", "04100"), ("Hobbies & Activities", "04200")]


def constants_seeder(reset=False):
    if reset:
        db.session.query(Constants).delete()
        db.session.commit()

    for name, type in tqdm(SYSTEM_ROLE + EXPERIENCE_TYPES):
        constants = Constants(name, type)
        db.session.add(constants)

    db.session.commit()
    print("Constants seeded successfully")
