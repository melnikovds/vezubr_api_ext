import random
import string
from faker import Faker

class TrailerCreate:
    """
    Класс для работы с эндпоинтами, связанными с Прицепами.
    Содержит методы для генерации данных и отправки запросов.
    """
    fake = Faker()

    @staticmethod
    def generate_trailer_plate():
        letters = "АВЕКМНОРСТУХ"
        digits = "0123456789"
        return (random.choice(letters) +
                ''.join(random.choices(digits, k=3)) +
                ''.join(random.choices(letters, k=2)) +
                ''.join(random.choices(digits, k=2)))

    @staticmethod
    def name_trailer_brand_model():
        base_brands = ["Schmitz Cargobull", "Krone", "Wielton", "Fruehauf", "Ron Schlepper", "Bergkamp", "Cimolai", "Tabou", ]
        brand = random.choice(base_brands)
        # генерируем случайное название модели
        model = f"{TrailerCreate.fake.lexify('???')} {TrailerCreate.fake.numerify('##')}"
        return f"{brand} {model}"

    @classmethod
    def create_trailer_payload(cls, **overrides):
        payload = {
            "createVehicle": True,
            "plateNumber": overrides.get("plateNumber") or cls.generate_trailer_plate(),
            "markAndModel": overrides.get("markAndModel") or cls.name_trailer_brand_model(),
            "yearOfManufacture": overrides.get("yearOfManufacture") or random.randint(2000, 2020),
            "ownerType": overrides.get("ownerType", 1),
            "category": overrides.get("category") or [9],
            "bodyType": overrides.get("bodyType", 10),

            "liftingCapacityInKg": str(overrides.get("liftingCapacityInKg") or 20000),
            "liftingCapacityMin": str(overrides.get("liftingCapacityMin", 100)),
            "liftingCapacityMax": str(overrides.get("liftingCapacityMax", 25000)),

            "isRearLoadingAvailable": overrides.get("isRearLoadingAvailable", True),
            "isSideLoadingAvailable": None,
            "isTopLoadingAvailable" : None,

            "heightFromGroundInCm": overrides.get("heightFromGroundInCm") or 300,
            "platformHeight": overrides.get("platformHeight") or 150,
            "platformLength": overrides.get("platformLength") or 1000,
            "hasSanitaryPassport": True,
            "sanitaryPassportExpiresAtDate": "2030-10-01",
            "vin": None,
            "geozonePasses": [],
            "photoFiles": []
        }
        payload.update(overrides)
        return payload
