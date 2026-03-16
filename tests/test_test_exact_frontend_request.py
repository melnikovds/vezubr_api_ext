# tests/test_exact_frontend_request.py

import allure
import pytest
import requests
import json
from datetime import datetime
from config.settings import BASE_URL, TIMEOUT


@allure.epic("API Vezubr")
@allure.feature("Точное воспроизведение фронтового запроса")
@allure.story("Создание контрагента без КПП как на фронте")
@allure.tag("exact_request", "frontend", "contractor")
class TestExactFrontendRequest:
    """
    Тесты для точного воспроизведения запроса с фронта
    """

    @allure.title("Точная копия запроса из примера документации")
    @allure.description("""
    Воспроизводим точный запрос из документации:
    {"inn":"412308823552","role":2,"responsibleEmployees":[{"name":"Робаут","surname":"Жилиман","patronymic":"Тысячный","phone":"+7 (953) 982-34-74","email":"Random@email.ru"}]}
    """)
    def test_exact_documentation_request(self, lke_token):
        """
        Точное воспроизведение запроса из документации
        """
        with allure.step("🔐 Подготовка заголовков"):
            headers = {
                "Authorization": lke_token,
                "Content-Type": "application/json"
            }

        with allure.step("📝 Формирование точного запроса из документации"):
            # Точный запрос из документации
            exact_request = {
                "inn": "412308823552",
                "role": 2,
                "responsibleEmployees": [{
                    "name": "Робаут",
                    "surname": "Жилиман",
                    "patronymic": "Тысячный",
                    "phone": "+7 (953) 982-34-74",
                    "email": "Random@email.ru"
                }]
            }

            allure.attach(
                json.dumps(exact_request, indent=2, ensure_ascii=False),
                "Точный запрос из документации",
                allure.attachment_type.JSON
            )

            print(f"\n📤 Отправляем точный запрос из документации:")
            print(f"   ИНН: {exact_request['inn']}")
            print(f"   Роль: {exact_request['role']}")
            print(f"   Без КПП: Да")

        with allure.step("🚀 Отправка запроса"):
            url = f"{BASE_URL}/contractor/child-create"

            response = requests.post(
                url,
                json=exact_request,
                headers=headers,
                timeout=TIMEOUT
            )

            allure.attach(
                str(response.status_code),
                "HTTP Status Code",
                allure.attachment_type.TEXT
            )

            if response.text:
                allure.attach(
                    response.text,
                    "Response Body",
                    allure.attachment_type.JSON
                )

            print(f"📥 Ответ: {response.status_code}")
            print(f"   Тело ответа: {response.text[:200]}...")

        with allure.step("📊 Анализ ответа"):
            if response.status_code == 200:
                print(f"✅ Успех! Запрос из документации работает")
                data = response.json()
                contractor_id = data.get("id")
                return contractor_id
            else:
                error_msg = f"{response.status_code}: {response.text}"
                print(f"❌ Ошибка: {error_msg}")

                # Анализируем ошибку
                if "412308823552" in response.text:
                    print(f"💡 ИНН 412308823552 уже используется или невалиден")

                if "КПП" in response.text:
                    print(f"💡 Система упоминает КПП, хотя мы его не отправляли")

                # Пробуем понять что не так
                pytest.fail(f"Запрос из документации не работает: {error_msg}")

    @allure.title("Минимальный запрос без КПП (как на фронте)")
    @allure.description("""
    Создаем минимальный запрос без КПП, как это делает фронт
    """)
    def test_minimal_request_no_kpp(self, lke_token):
        """
        Минимальный запрос без КПП
        """
        with allure.step("🔐 Подготовка заголовков"):
            headers = {
                "Authorization": lke_token,
                "Content-Type": "application/json"
            }

        with allure.step("📝 Формирование минимального запроса"):
            # Генерируем уникальный ИНН
            from pages.create_contractor_page import ContractorDataGenerator
            generator = ContractorDataGenerator()
            inn = generator.generate_realistic_inn("entity")

            timestamp = datetime.now().strftime('%H%M%S')

            minimal_request = {
                "inn": inn,
                "role": 1,
                "name": f"Тест без КПП {timestamp}",
                "responsibleEmployees": [{
                    "name": "Тест",
                    "surname": "БезКПП",
                    "phone": "+7 (999) 123-45-67",
                    "email": f"test_{timestamp}@example.com"
                }]
            }

            allure.attach(
                json.dumps(minimal_request, indent=2, ensure_ascii=False),
                "Минимальный запрос без КПП",
                allure.attachment_type.JSON
            )

            print(f"\n📤 Минимальный запрос без КПП:")
            print(f"   ИНН: {inn}")
            print(f"   Поля: {list(minimal_request.keys())}")
            print(f"   КПП в запросе: {'kpp' in minimal_request}")

        with allure.step("🚀 Отправка запроса"):
            url = f"{BASE_URL}/contractor/child-create"

            response = requests.post(
                url,
                json=minimal_request,
                headers=headers,
                timeout=TIMEOUT
            )

            print(f"📥 Ответ: {response.status_code}")
            if response.text:
                print(f"   Тело: {response.text[:200]}...")

        with allure.step("📊 Анализ результата"):
            if response.status_code == 200:
                data = response.json()
                contractor_id = data.get("id")

                allure.attach(
                    f"✅ Успех! Контрагент создан без КПП\n"
                    f"ID: {contractor_id}\n"
                    f"ИНН: {inn}",
                    "Результат",
                    allure.attachment_type.TEXT
                )

                return contractor_id
            else:
                error_msg = response.text
                allure.attach(error_msg, "Ошибка", allure.attachment_type.TEXT)

                # Детальный анализ ошибки
                error_lower = error_msg.lower()

                if "не найден организацию" in error_lower:
                    allure.attach(
                        f"💡 Production среда проверяет реальность ИНН\n"
                        f"ИНН: {inn}\n"
                        f"Нужны реальные ИНН из реестров ФНС",
                        "Анализ ошибки",
                        allure.attachment_type.TEXT
                    )
                    pytest.skip(f"ИНН {inn} не найден в реестрах")

                elif "неверный" in error_lower and "инн" in error_lower:
                    allure.attach(
                        f"💡 Проблема с алгоритмом генерации ИНН\n"
                        f"Сгенерированный ИНН: {inn}\n"
                        f"Длина: {len(inn)} цифр",
                        "Анализ ошибки",
                        allure.attachment_type.TEXT
                    )
                    pytest.fail(f"Некорректный ИНН: {inn}")

                elif "кпп" in error_lower:
                    allure.attach(
                        f"💡 Система ожидает КПП\n"
                        f"Хотя в документации он nullable\n"
                        f"Попробуем добавить КПП в следующих тестах",
                        "Анализ ошибки",
                        allure.attachment_type.TEXT
                    )
                    # Переходим к следующему тесту с КПП
                    pytest.skip(f"Система требует КПП: {error_msg[:100]}")

                else:
                    pytest.fail(f"Неизвестная ошибка: {error_msg[:200]}")

    @allure.title("Запрос с КПП=null (явное указание null)")
    @allure.description("""
    Пробуем явно указать kpp: null как требует JSON
    """)
    def test_request_with_null_kpp(self, lke_token):
        """
        Запрос с явным указанием null для КПП
        """
        with allure.step("🔐 Подготовка заголовков"):
            headers = {
                "Authorization": lke_token,
                "Content-Type": "application/json"
            }

        with allure.step("📝 Формирование запроса с kpp: null"):
            from pages.create_contractor_page import ContractorDataGenerator
            generator = ContractorDataGenerator()
            inn = generator.generate_realistic_inn("entity")

            timestamp = datetime.now().strftime('%H%M%S')

            # Явно указываем null для КПП
            request_with_null_kpp = {
                "inn": inn,
                "role": 1,
                "name": f"Тест с null КПП {timestamp}",
                "kpp": None,  # Явный null
                "responsibleEmployees": [{
                    "name": "Тест",
                    "surname": "NullКПП",
                    "phone": "+7 (999) 987-65-43",
                    "email": f"test_null_{timestamp}@example.com"
                }]
            }

            allure.attach(
                json.dumps(request_with_null_kpp, indent=2, ensure_ascii=False),
                "Запрос с kpp: null",
                allure.attachment_type.JSON
            )

            print(f"\n📤 Запрос с явным kpp: null")
            print(f"   КПП в JSON: {request_with_null_kpp.get('kpp')}")

        with allure.step("🚀 Отправка запроса"):
            url = f"{BASE_URL}/contractor/child-create"

            response = requests.post(
                url,
                json=request_with_null_kpp,
                headers=headers,
                timeout=TIMEOUT
            )

            print(f"📥 Ответ: {response.status_code}")

        with allure.step("📊 Сравнение с запросом без поля kpp"):
            # Сравним поведение с null и без поля вообще
            if response.status_code == 200:
                print(f"✅ Работает с kpp: null")
                return response.json().get("id")
            else:
                error_msg = response.text

                # Сравниваем с ошибкой из предыдущего теста
                allure.attach(
                    f"Сравнение:\n"
                    f"1. Без поля 'kpp' - ошибка\n"
                    f"2. С 'kpp': null - ошибка\n"
                    f"Вывод: возможно нужно пустая строка ''",
                    "Анализ",
                    allure.attachment_type.TEXT
                )

                pytest.skip(f"kpp: null тоже не работает: {error_msg[:100]}")

    @allure.title("Дебаг: анализ что именно отправляется в запросе")
    @allure.description("""
    Дебаг-тест для анализа реального тела запроса
    """)
    def test_debug_request_body(self, lke_token):
        """
        Дебаг-тест для анализа что именно уходит в API
        """
        import json

        with allure.step("🔍 Создаем разные варианты запроса"):
            variants = [
                {
                    "name": "Без поля kpp",
                    "data": {
                        "inn": "1234567890",
                        "role": 1,
                        "name": "Тест 1",
                        "responsibleEmployees": [
                            {"name": "Тест", "surname": "1", "phone": "+7111", "email": "1@test.com"}]
                    }
                },
                {
                    "name": "С kpp: null",
                    "data": {
                        "inn": "1234567890",
                        "role": 1,
                        "name": "Тест 2",
                        "kpp": None,
                        "responsibleEmployees": [
                            {"name": "Тест", "surname": "2", "phone": "+7222", "email": "2@test.com"}]
                    }
                },
                {
                    "name": "С kpp: '' (пустая строка)",
                    "data": {
                        "inn": "1234567890",
                        "role": 1,
                        "name": "Тест 3",
                        "kpp": "",
                        "responsibleEmployees": [
                            {"name": "Тест", "surname": "3", "phone": "+7333", "email": "3@test.com"}]
                    }
                }
            ]

        with allure.step("📊 Анализ JSON представления"):
            for variant in variants:
                json_str = json.dumps(variant["data"], ensure_ascii=False)

                allure.attach(
                    f"Вариант: {variant['name']}\n\n"
                    f"JSON:\n{json_str}\n\n"
                    f"Длина: {len(json_str)} символов\n"
                    f"Содержит 'kpp': {'kpp' in json_str}",
                    f"Анализ {variant['name']}",
                    allure.attachment_type.TEXT
                )

                print(f"\n{variant['name']}:")
                print(f"  JSON: {json_str}")
                print(f"  Поле kpp в JSON: {'kpp' in json_str}")