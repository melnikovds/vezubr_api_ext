import allure
import pytest
import requests
import json

from pages.address_page import AddressPage
from config.settings import BASE_URL


@allure.story("Smoke test")
@allure.feature("Адресные точки")
@allure.description("Создание/обновление адресной точки с рандомизированными данными")
@pytest.mark.parametrize("role", ["lke", "lkz"])
def test_create_address(role, get_auth_token):
    # 1. Авторизация
    token = get_auth_token(role)["token"]
    headers = {"Authorization": token}

    # 2. Генерация данных — через AddressPage
    address_payload = AddressPage.create_address_payload()

    # 3. Отправка запроса
    with allure.step(f"Создание адресной точки для роли '{role}'"):
        response = requests.post(
            f"{BASE_URL}/contractor-point/update",
            headers=headers,
            json=address_payload
        )
        assert response.status_code == 200, f"Ошибка создания адреса: {response.text}"

    # 4–5. Проверка и логирование — без изменений
    response_data = response.json()
    with allure.step("Проверка структуры ответа"):
        if "id" in response_data:
            assert isinstance(response_data["id"], int) and response_data["id"] > 0

    external_id = address_payload["externalId"]
    print(f"\n✅ Создана адресная точка с externalId: {external_id} для роли {role}")

    with allure.step(f"✅ Адрес создан: {external_id}"):
        allure.attach(
            json.dumps(address_payload, ensure_ascii=False, indent=2),
            name="Тело запроса",
            attachment_type=allure.attachment_type.JSON
        )
        allure.attach(
            json.dumps(response_data, indent=2),
            name="Ответ сервера",
            attachment_type=allure.attachment_type.JSON
        )