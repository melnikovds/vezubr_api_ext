import allure
import pytest
import json
from pages.create_cargo_page import CargoPlaceClient
from config.settings import BASE_URL

# Внешние ID из предыдущего теста
EXTERNAL_IDS = ["Izhevsk 81-870", "Izhevsk 71-130", "Izhevsk 64-649"]


@allure.story("Smoke test")
@allure.feature("Грузоместа")
@allure.description("Создание грузоместа с рандомизированными параметрами")
@pytest.mark.parametrize("role", ["lke"])
def test_create_cargo_place(role, get_auth_token):
    # 1. Авторизация
    token = get_auth_token(role)["token"]

    # 2. Инициализация клиента
    client = CargoPlaceClient(BASE_URL, token)

    # 3. Создание грузоместа
    with allure.step(f"Создание грузоместа для роли '{role}'"):
        response_data = client.create_cargo_place(
            departure_external_id=EXTERNAL_IDS[0],
            delivery_external_id=EXTERNAL_IDS[1]
        )

    # 4. Проверка ответа
    with allure.step("Проверка корректности ответа"):
        assert "id" in response_data, "Ответ должен содержать 'id'"
        cargo_id = response_data["id"]
        assert isinstance(cargo_id, int) and cargo_id > 0, f"Некорректный ID: {cargo_id}"

    print(f"\n✅ Создано грузоместо ID={cargo_id} для роли {role}")

    # 5. Прикрепляем данные в Allure
    with allure.step("Детали запроса и ответа"):
        # Чтобы показать, какие параметры были сгенерированы, можно расширить клиент,
        # но для простоты — просто покажем ответ
        allure.attach(
            json.dumps(response_data, indent=2),
            name="Ответ API (cargo-place)",
            attachment_type=allure.attachment_type.JSON
        )