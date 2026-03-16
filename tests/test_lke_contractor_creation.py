import allure
import pytest
import requests
from datetime import datetime
from config.settings import BASE_URL


@allure.epic("API Vezubr")
@allure.feature("Простое создание контрагентов")
@allure.story("Экспедитором (LKE) создаются внутренние контрагенты")
@allure.tag("contractor", "lke", "simple")
@allure.severity(allure.severity_level.CRITICAL)
class TestSimpleContractorCreate:
    """
    Простые тесты создания внутренних контрагентов
    Используется метод generate_realistic_inn с реальными кодами регионов
    """

    @allure.title("Создание внутреннего заказчика (LKZ)")
    @allure.description("""
    Экспедитор создает внутреннего заказчика с минимальными данными:
    - ИНН (сгенерированный с реальными кодами регионов)
    - Название компании
    - Роль = 1 (заказчик)
    - Один ответственный сотрудник
    """)
    def test_create_customer_lkz(self, lke_token, create_contractor_page):
        """
        Создание внутреннего заказчика экспедитором
        """
        with allure.step("🔐 Авторизация под LKE"):
            page = create_contractor_page(BASE_URL, lke_token)

        with allure.step("📝 Подготовка простых данных заказчика"):
            contractor_data = page.prepare_simple_contractor_data(
                role=1,  # Заказчик
                name=f"Внутренний заказчик LKZ {datetime.now().strftime('%H%M%S')}",
                inn_source="realistic",  # Используем реалистичные ИНН
                vatRate=22,
                taxationSystem=1
            )

            allure.attach(
                str(contractor_data),
                "Данные для создания заказчика",
                allure.attachment_type.JSON
            )

            # Проверяем что КПП не добавлен (необязательное поле)
            assert "kpp" not in contractor_data, "КПП не должен быть в минимальных данных"
            assert len(contractor_data["responsibleEmployees"]) == 1, "Должен быть один ответственный"

        with allure.step("🚀 Создание заказчика"):
            try:
                response = page.create_child_contractor(contractor_data)
                contractor_id = response.get("id")

                allure.dynamic.title(f"Создан заказчик ID={contractor_id}")

                allure.attach(
                    f"✅ Заказчик успешно создан\n"
                    f"ID: {contractor_id}\n"
                    f"ИНН: {contractor_data['inn']}\n"
                    f"Роль: Заказчик (1)",
                    "Результат создания",
                    allure.attachment_type.TEXT
                )

            except requests.exceptions.HTTPError as e:
                error_msg = str(e)
                allure.attach(error_msg, "Ошибка создания", allure.attachment_type.TEXT)

                # Обработка ожидаемых ошибок для production
                if "не найден организацию" in error_msg.lower():
                    pytest.skip(f"ИНН не найден в реестрах: {contractor_data['inn']}")
                elif "уже зарегистрирован" in error_msg.lower():
                    pytest.skip(f"ИНН уже используется: {contractor_data['inn']}")
                else:
                    raise

        with allure.step("✅ Проверка создания"):
            profile = page.get_contractor_profile(contractor_id)

            assert profile["id"] == contractor_id
            assert profile["inn"] == contractor_data["inn"]
            assert profile["role"] == 1, f"Роль должна быть 1, а не {profile['role']}"

            allure.attach(
                f"✅ Проверка пройдена\n"
                f"ID: {profile['id']}\n"
                f"ИНН: {profile['inn']}\n"
                f"Роль: {profile['role']}",
                "Результат проверки",
                allure.attachment_type.TEXT
            )

        return contractor_id

    @allure.title("Создание внутреннего подрядчика (LKP)")
    @allure.description("""
    Экспедитор создает внутреннего подрядчика:
    - ИНН (сгенерированный с реальными кодами регионов)
    - Название компании  
    - Роль = 2 (подрядчик)
    - Банковские реквизиты
    - Один ответственный сотрудник
    """)
    def test_create_contractor_lkp(self, lke_token, create_contractor_page):
        """
        Создание внутреннего подрядчика экспедитором
        """
        with allure.step("🔐 Авторизация под LKE"):
            page = create_contractor_page(BASE_URL, lke_token)

        with allure.step("📝 Подготовка данных подрядчика с банковскими реквизитами"):
            contractor_data = page.prepare_simple_contractor_data(
                role=2,  # Подрядчик
                name=f"Внутренний подрядчик LKP {datetime.now().strftime('%H%M%S')}",
                inn_source="realistic",
                add_bank_details=True,  # Для подрядчика добавляем банковские реквизиты
                vatRate=22,
                taxationSystem=1
            )

            allure.attach(
                str(contractor_data),
                "Данные для создания подрядчика",
                allure.attachment_type.JSON
            )

            # Проверяем что банковские реквизиты добавлены
            assert "bankBik" in contractor_data, "Для подрядчика должны быть банковские реквизиты"

        with allure.step("🚀 Создание подрядчика"):
            try:
                response = page.create_child_contractor(contractor_data)
                contractor_id = response.get("id")

                allure.dynamic.title(f"Создан подрядчик ID={contractor_id}")

                allure.attach(
                    f"✅ Подрядчик успешно создан\n"
                    f"ID: {contractor_id}\n"
                    f"ИНН: {contractor_data['inn']}\n"
                    f"Роль: Подрядчик (2)\n"
                    f"Банковские реквизиты: Да",
                    "Результат создания",
                    allure.attachment_type.TEXT
                )

            except requests.exceptions.HTTPError as e:
                error_msg = str(e)
                allure.attach(error_msg, "Ошибка создания", allure.attachment_type.TEXT)

                if "не найден организацию" in error_msg.lower():
                    pytest.skip(f"ИНН не найден в реестрах: {contractor_data['inn']}")
                elif "уже зарегистрирован" in error_msg.lower():
                    pytest.skip(f"ИНН уже используется: {contractor_data['inn']}")
                else:
                    raise

        with allure.step("✅ Проверка создания"):
            profile = page.get_contractor_profile(contractor_id)

            assert profile["role"] == 2, f"Роль должна быть 2, а не {profile['role']}"

        return contractor_id

    @allure.title("Быстрая проверка генерации ИНН")
    def test_inn_generation_check(self, create_contractor_page):
        """
        Проверка что метод generate_realistic_inn работает корректно
        """
        with allure.step("🧪 Генерация тестовых ИНН"):
            # Создаем временный page object без авторизации
            page = create_contractor_page(BASE_URL, "dummy_token")

            # Тестируем генерацию
            inns = page.test_inn_generation(3)

            allure.attach(
                str(inns),
                "Сгенерированные ИНН",
                allure.attachment_type.JSON
            )

        with allure.step("✅ Проверка формата ИНН"):
            for inn in inns:
                assert len(inn) == 10, f"ИНН должен быть 10 цифр: {inn}"
                assert inn.isdigit(), f"ИНН должен содержать только цифры: {inn}"

                # Проверка региона
                region_code = int(inn[:2])
                assert region_code in page.generator.REAL_REGIONS, \
                    f"Некорректный код региона: {region_code} в ИНН {inn}"

                allure.attach(
                    f"ИНН {inn}:\n"
                    f"• Длина: 10 ✓\n"
                    f"• Только цифры: ✓\n"
                    f"• Регион: {region_code} (валидный)",
                    "Проверка ИНН",
                    allure.attachment_type.TEXT
                )
