TYPE_DIGITS = 7

SYSTEM_ROLES = [("Admin", "0110"), ("User", "0111"), ("Company", "0111")]

POSITIONS_PREFIX = "02"
POSITIONS = ["Developer", "Designer", "Project Manager", "Tester", "Accountant"]

SKILLS_PREFIX = "03"
SKILLS = ["Python", "Java", "C++", "JavaScript", "SQL", "HTML", "CSS", "React", "Vue"]

EXPERIENCE_TYPES_PREFIX = "04"
EXPERIENCE_TYPES = ["Work", "Hobbies & Activities"]

NOTIFICATIONS_PREFIX = "05"
NOTIFICATIONS = [
    "Test {sender} {receiver}",
    "Matching {sender} {receiver}",
    "Request matching {sender} {receiver}",
    "Reject matching {sender} {receiver}",
    "New conversation {sender} {receiver}",
    "New message {sender} {receiver}",
    "Read message {sender} {receiver}",
    "Admin deactivate account",
    "Admin activate account",
]

LANGUAGES_PREFIX = "06"
LANGUAGES = [
    {
        "name": "IELTS",
        "note": {
            "values": None,
            "validate": {
                "required_points": True,
                "divisible": 0.5,
                "min": 2.5,
                "max": 9,
            },
        },
    },
    {
        "name": "TOEIC",
        "note": {
            "values": None,
            "validate": {
                "required_points": True,
                "divisible": 5,
                "min": 100,
                "max": 990,
            },
        },
    },
    {
        "name": "JLPT",
        "note": {
            "values": ["N1", "N2", "N3", "N4", "N5"],
            "validate": {
                "required_points": None,
                "divisible": None,
                "min": None,
                "max": None,
            },
        },
    },
]
