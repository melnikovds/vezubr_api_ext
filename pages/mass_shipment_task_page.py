from faker import Faker
import random
import re

fake = Faker('ru_RU')

def generate_random_task_item():
    """Генерирует один объект задания с рандомными данными."""
    point_id = [17978, 18535, 18534, 17980, 18294, 18293, 18529, 18785, 18527, 18290, 27606, 18520, 27607, 18532, 27883, 27317, 19203, 19206, 18499, 18481, 17984, 27318]
    arrival_id = random.choice(point_id)
    departure_id = random.choice([pid for pid in point_id if pid != arrival_id])
    type_package = ["free", "box", "pallet", "container", "bag", "RP"]

    return {
        "number": fake.numerify("###-###"),
        "title": fake.word().lower(),
        "shipBy": "vezubr",
        "requiredSentAtFrom": None,
        "requiredSentAtTill": None,
        "requiredDeliveredAtTill": None,
        "requiredDeliveredAtFrom": None,
        "consignee": None,
        "shipper": None,
        "arrivalPoint": {"id": arrival_id},
        "departurePoint": {"id": departure_id},
        "volume": random.randint(1, 10) * 1_000_000,
        "weight": random.randint(100_000, 500_000),
        "cost": random.randint(1_000_000, 5_000_000),
        "quantity": random.randint(1, 100),
        "types": [random.choice(type_package)],
        "isCargoPlacesEnabled": False
    }

def is_valid_uuid(uuid_string: str) -> bool:
    """Проверяет, является ли строка корректным UUID4."""
    uuid4_pattern = re.compile(
        r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$'
    )
    return bool(uuid4_pattern.match(uuid_string))

