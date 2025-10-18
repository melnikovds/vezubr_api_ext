import allure
import pytest
import requests

from config.settings import BASE_URL
from pages.address_page import AddressPage


@allure.story("Smoke test")
@allure.feature("Адресные точки")
@allure.description("Создание/обновление адресной точки с рандомизированными данными")
@pytest.mark.parametrize("role", ["lke", "lkz"])
def test_create_address(role, get_auth_token):
    # 1. Авторизация
    token = get_auth_token(role)["token"]
    headers = {"Authorization": token}

    # 2. Генерация данных
    address_payload = AddressPage.create_address_payload()

    # 3. Отправка запроса
    with allure.step(f"Создание адресной точки под ролью '{role}'"):
        response = requests.post(
            f"{BASE_URL}/contractor-point/update",
            headers=headers,
            json=address_payload
        )
        assert response.status_code == 200, f"Ошибка создания адреса: {response.text}"

    # 4. Проверка ответа
    created = response.json()
    with allure.step("Проверка наличия ID и его типа"):
        assert "id" in created, f"В ответе отсутствует поле 'id'. Ответ: {created}"
        assert isinstance(created["id"], int), f"ID должен быть целым числом, получено: {type(created['id'])}"

    # 5. Вывод информации
    addr_id = created["id"]
    title = address_payload["title"]
    print(f"\n✅ Создана адресная точка: {title} | ID: {addr_id}")

    with allure.step(f"✅ Создана адресная точка: {title} | ID: {addr_id}"):
        pass
