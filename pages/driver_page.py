import random
from faker import Faker
from datetime import timedelta, timezone, datetime

class DriverCreate:
    """
    Класс для работы с эндпоинтами, связанными с Водителями.
    Содержит методы для генерации данных и отправки запросов.
    """
    fake = Faker('ru_RU')

    @staticmethod
    def generate_last_name():
        return DriverCreate.fake.last_name_male()

    @staticmethod
    def generate_first_name():
        return DriverCreate.fake.first_name_male()

    @staticmethod
    def generate_middle_name():
        return DriverCreate.fake.middle_name_male()

    @staticmethod
    def generate_phone_number():
        area_code = random.choice(['909', '908', '907', '906', '905', '904'])
        phone = Faker().numerify(text=f"+7 ({area_code}) ###-##-##")
        return phone

    @staticmethod
    def generate_date_of_birth() -> str:
        now = datetime.now(timezone.utc)
        dob = now - timedelta(days=30*365 + 7)
        return dob.strftime("%Y-%m-%dT%H:%M:%S") + f".{int(dob.microsecond / 1000):03d}Z"

    @staticmethod
    def generate_license_expires() -> str:
        now = datetime.now(timezone.utc)
        expires = now + timedelta(days=20*365 + 5)
        return expires.strftime("%Y-%m-%dT%H:%M:%S") + f".{int(expires.microsecond / 1000):03d}Z"

    @staticmethod
    def generate_passport_issued() -> str:
        now = datetime.now(timezone.utc)
        issued = now - timedelta(days=5*365 + 1)
        return issued.strftime("%Y-%m-%dT%H:%M:%S") + f".{int(issued.microsecond / 1000):03d}Z"

    @staticmethod
    def generate_sanitary_book_expires() -> str:
        now = datetime.now(timezone.utc)
        expires = now + timedelta(days=10*365 + 2)
        return expires.strftime("%Y-%m-%dT%H:%M:%S") + f".{int(expires.microsecond / 1000):03d}Z"

    @staticmethod
    def generate_registration_address() -> str:
        house_number = random.randint(1, 15)
        building_number = random.randint(1 , 5)
        apartment_number = random.randint(1, 150)
        return f"ул. Белы Куна д. {house_number} к. {building_number} кв. {apartment_number}"

    @classmethod
    def create_driver_payload(cls, **overrides):
        # генерируем ФИО, если они не переданы явно
        base_surname = (
                overrides.get("driverLicenseSurname") or
                overrides.get("surname") or
                cls.generate_last_name()
        )
        base_name = (
                overrides.get("driverLicenseName") or
                overrides.get("name") or
                cls.generate_first_name()
        )
        base_patronymic = (
                overrides.get("driverLicensePatronymic") or
                overrides.get("patronymic") or
                cls.generate_middle_name()
        )

        payload = {
            "driverLicenseSurname": overrides.get("driverLicenseSurname", base_surname),
            "surname": overrides.get("surname", base_surname),
            "driverLicenseName": overrides.get("driverLicenseName", base_name),
            "name": overrides.get("name", base_name),
            "driverLicensePatronymic": overrides.get("driverLicensePatronymic", base_patronymic),
            "patronymic": overrides.get("patronymic", base_patronymic),

            "applicationPhone": overrides.get("applicationPhone") or cls.generate_phone_number(),
            "registrationAddress": overrides.get("registrationAddress") or cls.generate_registration_address(),
            "driverLicenseId": overrides.get("driverLicenseId") or str(random.randint(1_000_000_000, 9_999_999_999)),
            "passportId": overrides.get("passportId") or str(random.randint(1_000_000_000, 9_999_999_999)),
            "passportIssuedBy": "МВД России по Ростовской области",
            
            "canWorkAsLoader": False,
            "dlRusResident": True,
            "hasSanitaryBook": True,
            "neverDelegate": False,
            "passportRusResident": True,
            "passportUnitCode": "111-333",
            "factAddress": "",
            "contactPhone": "",
            "inn": "",

            "dateOfBirth": overrides.get("dateOfBirth") or cls.generate_date_of_birth(),
            "driverLicenseDateOfBirth": overrides.get("driverLicenseDateOfBirth") or cls.generate_date_of_birth(),
            "driverLicenseExpiresAtDate": overrides.get("driverLicenseExpiresAtDate") or cls.generate_license_expires(),
            "passportIssuedAtDate": overrides.get("passportIssuedAtDate") or cls.generate_passport_issued(),
            "sanitaryBookExpiresAtDate": overrides.get("sanitaryBookExpiresAtDate") or cls.generate_sanitary_book_expires(),
        }
        payload.update(overrides)
        return payload

