import allure
import requests
import random
import string
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
from config.settings import TIMEOUT
from utils.inn_fetcher import INNFetcher


class ContractorDataGenerator:
    """Генератор тестовых данных для контрагентов с реалистичными ИНН"""

    def __init__(self):
        self.inn_cache = []  # Кэш полученных ИНН
        self.used_inns = set()  # Уже использованные ИНН в этой сессии

        # Реальные коды регионов РФ
        self.REAL_REGIONS = [
            1, 2, 3, 4, 5, 7, 10, 11, 12, 13, 14, 15,
            16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27,
            28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39,
            40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51,
            52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63,
            64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75,
            76, 77, 78, 79, 82, 86, 87, 89
        ]

        # Наиболее распространённые коды налоговых инспекций
        self.REAL_IFNS = [
            1, 2, 3, 4, 5, 6, 7, 8, 9,
            10, 11, 12, 13, 14, 15, 16, 17, 18, 19,
            20, 21, 22, 23, 24, 25
        ]

    def generate_realistic_inn(self, entity_type: str = "entity") -> str:
        """
        Генерирует реалистичный ИНН с реальными кодами регионов и ИФНС

        Parameters:
        -----------
        entity_type : str
            Тип сущности: 'entity' (юрлицо, 10 цифр) или 'individual' (физлицо, 12 цифр)

        Returns:
        --------
        str
            Сгенерированный ИНН
        """

        def calc(nums, coeffs):
            return sum(a * b for a, b in zip(nums, coeffs)) % 11 % 10

        # Формируем реальные первые 4 цифры
        region = random.choice(self.REAL_REGIONS)
        ifns = random.choice(self.REAL_IFNS)

        prefix = [
            region // 10, region % 10,
            ifns // 10, ifns % 10
        ]

        if entity_type == "entity":
            body = prefix + [random.randint(0, 9) for _ in range(5)]
            coeffs = [2, 4, 10, 3, 5, 9, 4, 6, 8]
            control = calc(body, coeffs)
            inn = ''.join(map(str, body)) + str(control)

            # Проверка валидности
            if len(inn) != 10 or not inn.isdigit():
                raise ValueError(f"Некорректный ИНН сгенерирован: {inn}")

            print(f"📝 Сгенерирован реалистичный ИНН: {inn} (регион: {region})")
            return inn

        elif entity_type == "individual":
            body = prefix + [random.randint(0, 9) for _ in range(6)]
            coeffs1 = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
            coeffs2 = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8, 5]
            d11 = calc(body, coeffs1)
            d12 = calc(body + [d11], coeffs2)
            inn = ''.join(map(str, body)) + str(d11) + str(d12)

            if len(inn) != 12 or not inn.isdigit():
                raise ValueError(f"Некорректный ИНН сгенерирован: {inn}")

            print(f"📝 Сгенерирован ИНН физлица: {inn} (регион: {region})")
            return inn

        else:
            raise ValueError("Тип должен быть 'individual' или 'entity'")

    def get_fresh_inn(self, source: str = "realistic") -> str:
        """
        Получение свежего ИНН из различных источников

        Parameters:
        -----------
        source : str
            Источник: "radar", "star", "generated", "mixed", "realistic"

            "realistic" - использует метод generate_realistic_inn с реальными кодами регионов

        Returns:
        --------
        str
            Свежий ИНН
        """
        if source == "realistic":
            # Используем новый метод генерации реалистичных ИНН
            inn = self.generate_realistic_inn("entity")
            self.used_inns.add(inn)
            return inn

        # Старая логика для других источников
        if not self.inn_cache:
            print(f"📥 Получение свежих ИНН из источника: {source}")
            self.inn_cache = INNFetcher.get_fresh_inns(10, source)

        # Берем ИНН из кэша, пропуская уже использованные
        for inn in self.inn_cache[:]:
            if inn not in self.used_inns:
                self.used_inns.add(inn)
                self.inn_cache.remove(inn)
                print(f"🎯 Используем ИНН: {inn}")
                return inn

        # Если все ИНН использованы, получаем новые
        print("🔄 Все ИНН использованы, получаем новые...")
        self.inn_cache = INNFetcher.get_fresh_inns(10, source)

        if self.inn_cache:
            inn = self.inn_cache.pop(0)
            self.used_inns.add(inn)
            return inn

        # Если не получилось, генерируем реалистичный
        print("⚠️  Не удалось получить ИНН, генерируем реалистичный...")
        return self.generate_realistic_inn("entity")

    @staticmethod
    def generate_random_email() -> str:
        """Генерация случайного email"""
        domains = ['gmail.com', 'yandex.ru', 'mail.ru', 'company.com']
        username = ''.join(random.choices(string.ascii_lowercase, k=8))
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"test_{username}_{timestamp}@{random.choice(domains)}"

    @staticmethod
    def generate_phone() -> str:
        """Генерация российского номера телефона"""
        return f"+7{random.randint(900, 999)}{random.randint(100, 999)}{random.randint(10, 99)}{random.randint(10, 99)}"

    @staticmethod
    def generate_simple_name() -> Dict[str, str]:
        """Генерация простого ФИО на русском (только имя и фамилия)"""
        surnames = ["Иванов", "Петров", "Сидоров", "Кузнецов", "Смирнов"]
        names = ["Иван", "Петр", "Алексей", "Дмитрий", "Сергей"]

        return {
            "surname": random.choice(surnames),
            "name": random.choice(names)
        }

    @staticmethod
    def generate_simple_company_name(contractor_type: str = None) -> str:
        """
        Генерация простого названия компании

        Parameters:
        -----------
        contractor_type : str, optional
            Тип контрагента: 'customer' или 'contractor'
        """
        prefixes = ["ООО", "АО", "ЗАО", "ПАО"]
        timestamp = datetime.now().strftime("%H%M%S")

        if contractor_type == "customer":
            base_name = "Заказчик"
        elif contractor_type == "contractor":
            base_name = "Подрядчик"
        else:
            base_name = "Контрагент"

        return f"{random.choice(prefixes)} '{base_name} {timestamp}'"


class CreateContractorPage:
    """Page Object для работы с созданием контрагентов"""

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }
        self.generator = ContractorDataGenerator()
        self.created_contractors = []

        print(f"\n🔧 CreateContractorPage инициализирован:")
        print(f"   Base URL: {self.base_url}")
        print(f"   Token: {token[:20]}...")

    def prepare_simple_contractor_data(
            self,
            role: int = 1,
            name: Optional[str] = None,
            inn_source: str = "realistic",
            add_bank_details: bool = False,
            **kwargs
    ) -> Dict[str, Any]:
        """
        Подготовка простых данных для создания контрагента

        Parameters:
        -----------
        role : int
            Роль контрагента (1 - заказчик, 2 - подрядчик)
        name : str, optional
            Название компании
        inn_source : str
            Источник ИНН
        add_bank_details : bool
            Добавлять банковские реквизиты
        **kwargs : дополнительные параметры
        """
        # Получаем ИНН
        inn = kwargs.get("inn") or self.generator.get_fresh_inn(inn_source)

        # Генерируем название если не передано
        if not name:
            if role == 1:
                name = self.generator.generate_simple_company_name("customer")
            else:
                name = self.generator.generate_simple_company_name("contractor")

        # Базовые данные - только обязательные поля
        contractor_data = {
            "inn": inn,
            "role": role,
            "name": name
        }

        # ВНИМАНИЕ: Не добавляем поле "kpp" вообще, если оно не нужно
        # Это важно для nullable полей

        # Опционально: НДС и система налогообложения
        # Добавляем только если явно указаны
        if "vatRate" in kwargs:
            contractor_data["vatRate"] = kwargs["vatRate"]
        if "taxationSystem" in kwargs:
            contractor_data["taxationSystem"] = kwargs["taxationSystem"]

        # Банковские реквизиты
        if add_bank_details:
            contractor_data.update({
                "bankBik": "044525225",
                "checkingAccount": f"40702810{random.randint(1000000000, 9999999999)}",
                "bankName": "ПАО Сбербанк",
                "correspondentAccount": "30101810400000000225"
            })

        # Один ответственный сотрудник (обязательное поле по документации)
        name_data = self.generator.generate_simple_name()
        contractor_data["responsibleEmployees"] = [{
            "name": name_data["name"],
            "surname": name_data["surname"],
            "phone": self.generator.generate_phone(),
            "email": self.generator.generate_random_email(),
            "roles": [1]
        }]

        # Обновление данными из kwargs (кроме уже обработанных)
        for key, value in kwargs.items():
            if key not in ["inn", "name", "vatRate", "taxationSystem"]:
                contractor_data[key] = value

        print(f"📝 Подготовлены данные контрагента:")
        print(f"   Роль: {'Заказчик' if role == 1 else 'Подрядчик'} ({role})")
        print(f"   ИНН: {inn}")
        print(f"   Название: {name}")
        print(f"   Банковские реквизиты: {'Да' if add_bank_details else 'Нет'}")
        print(f"   Поля в запросе: {list(contractor_data.keys())}")

        return contractor_data

    def prepare_contractor_data(self,
                                role: int = 1,
                                inn_source: str = "mixed",
                                add_responsible_employee: bool = True,
                                **kwargs) -> Dict[str, Any]:
        """
        Подготовка полных данных для создания контрагента (старый метод для обратной совместимости)
        """
        # Получаем свежий ИНН из указанного источника
        inn = kwargs.get("inn") or self.generator.get_fresh_inn(inn_source)

        # Базовые данные
        contractor_data = {
            "inn": inn,
            "role": role,
            "name": kwargs.get("name") or self.generator.generate_simple_company_name(),
            "kpp": kwargs.get("kpp") or f"{random.randint(100000000, 999999999)}",
            "vatRate": kwargs.get("vatRate", random.choice([0, 5, 7, 22])),
            "taxationSystem": kwargs.get("taxationSystem", random.choice([1, 2, 3])),
            "responsibleEmployees": []
        }

        # Добавление банковских реквизитов
        if kwargs.get("add_bank_details", False):
            contractor_data.update({
                "bankBik": "044525225",
                "checkingAccount": f"40702810{random.randint(1000000000, 9999999999)}",
                "bankName": "ПАО Сбербанк",
                "correspondentAccount": "30101810400000000225"
            })

        # Добавление ответственного сотрудника
        if add_responsible_employee:
            name_data = self.generator.generate_simple_name()
            contractor_data["responsibleEmployees"] = [{
                "name": name_data["name"],
                "surname": name_data["surname"],
                "patronymic": kwargs.get("patronymic", ""),
                "phone": self.generator.generate_phone(),
                "email": self.generator.generate_random_email(),
                "roles": kwargs.get("roles", [1])  # По умолчанию минимальная роль
            }]

        # Обновление данными из kwargs
        contractor_data.update(kwargs)

        # Удаление None значений
        contractor_data = {k: v for k, v in contractor_data.items() if v is not None}

        return contractor_data

    def create_child_contractor(self, contractor_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создание контрагента"""
        if "/v1/api-ext" in self.base_url:
            url = f"{self.base_url}/contractor/child-create"
        else:
            url = f"{self.base_url}/v1/api-ext/contractor/child-create"

        print(f"\n📤 Отправка запроса:")
        print(f"   URL: {url}")
        print(f"   ИНН: {contractor_data.get('inn')}")
        print(f"   Название: {contractor_data.get('name')}")
        print(f"   Роль: {contractor_data.get('role')}")

        with allure.step(f"Отправка запроса на создание контрагента"):
            allure.attach(
                str(contractor_data),
                name="Request Body",
                attachment_type=allure.attachment_type.JSON
            )

            try:
                response = requests.post(
                    url,
                    json=contractor_data,
                    headers=self.headers,
                    timeout=TIMEOUT
                )

                print(f"📥 Получен ответ:")
                print(f"   Статус: {response.status_code}")

                allure.attach(
                    str(response.status_code),
                    name="Response Status Code",
                    attachment_type=allure.attachment_type.TEXT
                )

                if response.text:
                    print(f"   Ответ: {response.text[:200]}..." if len(
                        response.text) > 200 else f"   Ответ: {response.text}")
                    allure.attach(
                        response.text,
                        name="Response Body",
                        attachment_type=allure.attachment_type.JSON
                    )

                if response.status_code == 200:
                    response_data = response.json()

                    if "id" in response_data:
                        self.created_contractors.append({
                            "id": response_data["id"],
                            "data": contractor_data
                        })
                        print(f"✅ Контрагент создан, ID: {response_data['id']}")

                    return response_data
                else:
                    error_msg = f"{response.status_code} Error: {response.text}"
                    print(f"❌ {error_msg}")

                    # Если это дублирование ИНН, помечаем его как использованный
                    if "дублирован" in response.text.lower() or "duplicate" in response.text.lower():
                        inn = contractor_data.get("inn")
                        if inn:
                            self.generator.used_inns.add(inn)
                            print(f"🚫 ИНН {inn} помечен как дублированный")

                    # Если ИНН не найден в реестрах
                    if "не найден организацию" in error_msg.lower():
                        print(f"💡 ИНН {contractor_data.get('inn')} не найден в реестрах")

                    raise requests.exceptions.HTTPError(error_msg)

            except requests.exceptions.RequestException as e:
                print(f"❌ Ошибка при выполнении запроса: {e}")
                raise

    def get_contractor_profile(self, contractor_id: int) -> Dict[str, Any]:
        """
        Получение профиля контрагента через GET /v1/api-ext/contractor/profile/{id}

        Parameters:
        -----------
        contractor_id : int
            ID контрагента

        Returns:
        --------
        Dict[str, Any]
            Профиль контрагента
        """
        url = f"{self.base_url}/contractor/profile/{contractor_id}"

        print(f"\n📥 Получение профиля контрагента ID={contractor_id}")

        with allure.step(f"Получение профиля контрагента ID={contractor_id}"):
            try:
                response = requests.get(
                    url,
                    headers=self.headers,
                    timeout=TIMEOUT
                )

                response.raise_for_status()
                profile = response.json()

                print(f"✅ Профиль получен")
                allure.attach(
                    str(profile),
                    name="Contractor Profile",
                    attachment_type=allure.attachment_type.JSON
                )

                return profile

            except requests.exceptions.RequestException as e:
                print(f"❌ Ошибка получения профиля: {e}")
                raise

    def test_inn_generation(self, count: int = 5) -> List[str]:
        """
        Тестирование генерации ИНН

        Parameters:
        -----------
        count : int
            Количество ИНН для генерации

        Returns:
        --------
        List[str]
            Список сгенерированных ИНН
        """
        print(f"\n🧪 Тестирование генерации {count} ИНН:")

        inns = []
        for i in range(count):
            inn = self.generator.generate_realistic_inn("entity")
            inns.append(inn)

            # Проверка формата
            if len(inn) == 10 and inn.isdigit():
                region = int(inn[:2])
                print(f"  {i + 1}. {inn} (регион: {region}) ✓")
            else:
                print(f"  {i + 1}. {inn} ✗")

        return inns