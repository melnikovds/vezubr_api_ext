import random
import string


class TractorPage:
    """Класс для генерации данных для создания тягача."""

    @staticmethod
    def generate_random_plate_number(prefix: str = "TRACTOR") -> str:
        """Генерирует короткий уникальный гос. номер, например: TRACTOR_A3K9X"""
        chars = string.ascii_uppercase + string.digits
        return f"{prefix}_{''.join(random.choices(chars, k=5))}"

    @staticmethod
    def generate_random_mark_and_model() -> str:
        """Генерирует случайную марку тягача"""
        models = [
            "Malcador Prime",
            "Banehammer Heavy Tractor",
            "Mars-Pattern Crawler",
            "Forge World Titan-Tug",
            "Omnissiah's Iron Mule",
            "Skitarii Heavy Hauler",
            "Astra Militarum Prime Mover",
            "Cadian Logistics Behemoth",
            "Graviton Tractor Mk.IV",
            "Tech-Priest Blessed Tow-Beast"
        ]
        return random.choice(models)

    @classmethod
    def create_tractor_payload(cls, **overrides) -> dict:
        """
        Генерирует минимально необходимый payload для создания тягача.
        Все необязательные поля (vin, category и т.д.) опущены — API использует значения по умолчанию.
        """
        payload = {
            "createVehicle": True,
            "plateNumber": overrides.get("plateNumber") or cls.generate_random_plate_number(),
            "markAndModel": overrides.get("markAndModel") or cls.generate_random_mark_and_model(),
            "yearOfManufacture": overrides.get("yearOfManufacture") or random.randint(2010, 2024),
            "ownerType": overrides.get("ownerType", 1),
            "isCarTransporterCovered": overrides.get("isCarTransporterCovered", False),

        }
        payload.update(overrides)
        return payload
