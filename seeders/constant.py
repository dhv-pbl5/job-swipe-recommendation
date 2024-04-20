from models.constant import Constant
from utils import get_instance, get_tqdm

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
    # NOTIFICATIONS
    [
        "Test {sender} {receiver}",
        "Matching {sender} {receiver}",
        "Request matching {sender} {receiver}",
        "Reject matching {sender} {receiver}",
        "New conversation {sender} {receiver}",
        "New message {sender} {receiver}",
        "Read message {sender} {receiver}",
        "Admin deactivate account",
        "Admin activate account",
    ],
]


def generate_random_type(prefix, index):
    missing_digits = MAX_TYPE_DIGITS - len(str(index)) - len(prefix)
    return "".join("0" for _ in range(missing_digits)) + str(index)


def constant_seeder(reset=False):
    if reset:
        Constant.query.delete()
        db.session.commit()

    for index in get_tqdm(loop=len(SYSTEM_ROLES), desc="System Roles"):
        (name, prefix) = SYSTEM_ROLES[index]
        constant = Constant(name, prefix + generate_random_type(prefix, index))
        db.session.add(constant)
        db.session.commit()

    for index in get_tqdm(loop=len(OTHERS), desc="Others constants"):
        constant_type = OTHERS[index]
        prefix = "0" + str(index + 2)
        for idx, name in enumerate(constant_type):
            constant = Constant(
                name, prefix + generate_random_type(prefix, idx))
            db.session.add(constant)
            db.session.commit()

    db.session.commit()
