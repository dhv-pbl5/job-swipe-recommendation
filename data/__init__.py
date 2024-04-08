from faker import Faker


def format_phone_number(fake: Faker) -> str:
    return f"0{fake.msisdn()[3:]}"


if __name__ == "__main__":
    fake = Faker()

    json = {
        "email": fake.email(domain="gmail.com"),
        "password": fake.password(),
        "address": fake.city(),
        "phone_number": format_phone_number(fake),
        "system_role": {"constant_id": "7cca2e18-b460-43f7-9d1f-a8e6cbe99a50"},
        "gender": fake.boolean(),
        "last_name": fake.last_name(),
        "first_name": fake.first_name(),
        "date_of_birth": str(fake.unix_time()),
    }

    print(json)
