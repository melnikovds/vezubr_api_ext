import random
import string
from datetime import datetime


class VehiclePage:
    """
    Класс для работы с эндпоинтами, связанными с ТС (Transport Vehicle).
    Содержит методы для генерации данных и отправки запросов.
    """

    @staticmethod
    def generate_random_plate_number(prefix: str = "AUTO") -> str:
        """
        Генерирует короткий уникальный гос. номер ТС.
        Пример: AUTO_A3K9X
        """
        chars = string.ascii_uppercase + string.digits  # A-Z + 0-9
        suffix = ''.join(random.choices(chars, k=5))
        return f"{prefix}_{suffix}"

    @staticmethod
    def generate_random_mark_and_model() -> str:
        """Генерирует случайную марку и модель ТС в стиле Warhammer 40,000."""
        models = [
            "Бейнблейд Mk.IX",
            "Ленд Рейдер «Прометей»",
            "Бронетранспортёр «Химера»",
            "Боевой танк «Леман Русс»",
            "Разведывательный шагоход «Сентинел»",
            "Разведмашина «Хеллхаунд»",
            "Таурокс Прайм",
            "Истребитель танков «Вальдор»",
            "Штурмовой бронетранспортёр «Крассус»",
            "Тяжёлый танк «Малкадор»",
            "Экзекутор «Репулсор»",
            "Тяжёлый штурмовой авианосец «Штормлорд»",
            "Тягач Астра Милитарум",
            "Тяжёлый тягач кадийского образца",
            "Серв-грузовик марса-паттерна",
            "Благословение Омниссии из Миров-Кузниц",
            "Гравитационный логистический бегемот",
            "Транспортёр поддержки Скитариев",
            "Ржавый фургон техножреца",
            "Топливно-боевой муловоз Имперской Гвардии"
        ]
        return random.choice(models)

    @classmethod
    def create_vehicle_payload(cls, **overrides) -> dict:
        payload = {
            "createVehicle": True,
            "plateNumber": overrides.get("plateNumber") or cls.generate_random_plate_number(),
            "markAndModel": overrides.get("markAndModel") or cls.generate_random_mark_and_model(),
            "yearOfManufacture": overrides.get("yearOfManufacture") or 2020,
            "ownerType": overrides.get("ownerType", 1),
            "category": overrides.get("category") or [1],
            "bodyType": overrides.get("bodyType", 3),

            "liftingCapacityInKg": str(overrides.get("liftingCapacityInKg") or 100000),
            "liftingCapacityMin": str(overrides.get("liftingCapacityMin", 100)),
            "liftingCapacityMax": str(overrides.get("liftingCapacityMax", 100000)),

            "volume": overrides.get("volume") or 120,
            "palletsCapacity": overrides.get("palletsCapacity") or 35,
            "hasSanitaryPassport": True,
            "sanitaryPassportExpiresAtDate": "2031-10-24",
            "vin": None,
            "geozonePasses": [],
            "photoFiles": [],
        }
        payload.update(overrides)
        return payload
