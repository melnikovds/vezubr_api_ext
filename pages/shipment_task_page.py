import random
import string
from faker import Faker
from datetime import datetime, timezone, timedelta

class TaskCreate:
    """
    Класс для работы с эндпоинтами, связанными с Заданиями.
    Содержит методы для генерации данных и отправки запросов.
    """
    fake = Faker('ru_RU')

    @staticmethod
    def generate_product_name():
        products = [
            "Бумага офисная", "Картон", "Электроника", "Одежда", "Мебель",
            "Строительные материалы", "Фармацевтика", "Продукты питания"
        ]
        return random.choice(products)

    @staticmethod
    def generate_random_number():
        part1 = f"{random.randint(10, 99):02d}"
        part2 = f"{random.randint(0, 999):03d}"
        part3 = f"{random.randint(1000, 9999)}"

        return f"{part1}-{part2}-{part3}"

    @staticmethod
    def generate_dates() -> tuple[str, str, str, str]:

        now = datetime.now(timezone.utc)

        def format_z(dt: datetime) -> str:
            return dt.strftime("%Y-%m-%dT%H:%M:%S") + f".{int(dt.microsecond / 1000):03d}Z"

        date_plus_1_day = now + timedelta(days=1)
        date_plus_2_days = now + timedelta(days=2)
        date_plus_3_days = now + timedelta(days=3)
        date_plus_4_days = now + timedelta(days=4)

        return (
            format_z(date_plus_1_day),
            format_z(date_plus_2_days),
            format_z(date_plus_3_days),
            format_z(date_plus_4_days)
        )

    @staticmethod
    def generate_update_dates() -> tuple[str, str, str, str]:

        now = datetime.now(timezone.utc)

        def format_z(dt: datetime) -> str:
            return dt.strftime("%Y-%m-%dT%H:%M:%S") + f".{int(dt.microsecond / 1000):03d}Z"

        date_plus_1_day = now + timedelta(days=11)
        date_plus_2_days = now + timedelta(days=12)
        date_plus_3_days = now + timedelta(days=13)
        date_plus_4_days = now + timedelta(days=14)

        return (
            format_z(date_plus_1_day),
            format_z(date_plus_2_days),
            format_z(date_plus_3_days),
            format_z(date_plus_4_days)
        )

    @staticmethod
    def generate_type_package():
        package = [
            "box", "pallet", "container", "bag", "RP", "vehicleBody"
        ]
        return [random.choice(package)]

    @staticmethod
    def choice_ship_by():
        options = [
            "fm_logistic", "vezubr", "pochta"
        ]
        return random.choice(options)

    @staticmethod
    def generate_external_task_number():
        while True:
            word = TaskCreate.fake.word().lower()
            if 6 <= len(word) <= 8 and word.isalpha():
                return word

    @classmethod
    def create_task_payload(cls, **overrides):
        date_1, date_2, date_3, date_4 = TaskCreate.generate_dates()

        payload = {
            "number": overrides.get("number") or cls.generate_random_number(),
            "title": overrides.get("title") or cls.generate_product_name(),
            "shipBy": overrides.get("shipBy") or cls.choice_ship_by(),
            "types": overrides.get("types") or cls.generate_type_package(),
            "isCargoPlacesEnabled": overrides.get("isCargoPlacesEnabled") or True,

            "arrivalPoint": overrides.get("arrivalPoint", {"id": 18647}),
            "departurePoint": overrides.get("departurePoint", {"id": 19162}),

            "consignee": overrides.get(
                "consignee",
                {
                    "inn": "7724656304",
                    "kpp": "771501001"
                }
            ),
            "shipper": overrides.get(
                "shipper",
                {
                    "inn": "5321162475",
                    "kpp": "532101001"
                }
            ),

            "requiredSentAtFrom": overrides.get("requiredSentAtFrom") or date_1,
            "requiredSentAtTill": overrides.get("requiredSentAtTill") or date_2,
            "requiredDeliveredAtFrom": overrides.get("requiredDeliveredAtTill") or date_3,
            "requiredDeliveredAtTill": overrides.get("requiredDeliveredAtFrom") or date_4,

            "volume": overrides.get("volume", random.randint(1, 10) * 1_000_000),
            "weight": overrides.get("weight", random.randint(1, 10) * 1_000),
            "cost": overrides.get("cost", random.randint(10_000, 1_000_000_000)),
            "quantity": overrides.get("quantity", random.randint(1, 100))
        }
        payload.update(overrides)
        return payload

    @classmethod
    def update_task_payload(cls, **overrides):
        date_1, date_2, date_3, date_4 = TaskCreate.generate_update_dates()

        payload = {
                "shipBy": overrides.get("shipBy") or cls.choice_ship_by(),
                "number": overrides.get("number") or cls.generate_random_number(),
                "externalTaskNumber": overrides.get("externalTaskNumber", cls.generate_external_task_number()),
                "title": overrides.get("title") or cls.generate_product_name(),
                # "shipper": overrides.get("shipper") or None,
                # "consignee": overrides.get("consignee") or None,
                "departurePoint": overrides.get("departurePoint", {"id": 17974}),
                "arrivalPoint": overrides.get("arrivalPoint", {"id": 18528}),
                # "cargoPlaces": [],
                "volume": overrides.get("volume", random.randint(1, 10) * 1_000_000),
                "weight": overrides.get("weight", random.randint(1, 10) * 1_000),
                "cost": overrides.get("cost", random.randint(10_000, 1_000_000_000)),
                "quantity": overrides.get("quantity", random.randint(1, 100)),
                "types": overrides.get("types") or cls.generate_type_package(),
                "requiredSentAtFrom": date_1,
                "requiredSentAtTill": date_2,
                "requiredDeliveredAtFrom": date_3,
                "requiredDeliveredAtTill": date_4
                # "isCargoPlacesEnabled": true
            }
        payload.update(overrides)
        return payload










