from models.Constants import Constants
from utils import get_instance

_, db = get_instance()

MAX_TYPE_DIGITS = 7

SYSTEM_ROLES = [("Admin", "0110"), ("User", "0111"), ("Company", "0111")]
OTHERS = [
    # EXPERIENCE_TYPES
    ["Work", "Hobbies & Activities"],
    # POSITIONS
    ["Developer", "Designer", "Project Manager", "Tester", "Accountant"],
    # SKILLS
    [
        "Python",
        "Java",
        "C++",
        "JavaScript",
        "SQL",
        "HTML",
        "CSS",
        "React",
        "Vue",
    ],
]


def generate_random_type(prefix, index):
    missing_digits = MAX_TYPE_DIGITS - len(str(index)) - len(prefix)
    return "".join("0" for _ in range(missing_digits)) + str(index)


def constants_seeder(reset=False):
    if reset:
        db.session.query(Constants).delete()
        db.session.commit()

    for index, (name, prefix) in enumerate(SYSTEM_ROLES):
        constant = Constants(name, prefix + generate_random_type(prefix, index))
        db.session.add(constant)
        db.session.commit()

    for index, constant_type in enumerate(OTHERS):
        prefix = "0" + str(index + 2)
        for idx, name in enumerate(constant_type):
            constant = Constants(name, prefix + generate_random_type(prefix, idx))
            db.session.add(constant)
            db.session.commit()

    db.session.commit()
