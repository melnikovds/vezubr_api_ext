import allure
import pytest
import requests
from config.settings import BASE_URL
from pages.tariff_page import *

@allure.story("Smoke test")
@allure.feature("Тарифы")
@allure.description("Получение деталки тарифа и проверка ключевых полей")
@pytest.mark.parametrize("role", ["lke"])
def test_get_tariff(role, get_auth_token):
    # авторизация
    token = get_auth_token(role)["token"]
    # headers = {"Authorization": f"Bearer {token}"}
    headers = {"Authorization": token}

    # запрос тарифа
    with allure.step(f"Получение тарифа для роли '{role}'"):
        response = requests.get(
            f"{BASE_URL}/tariffs/23762",
            headers=headers
        )
        assert response.status_code == 200, f"Ошибка получения тарифа: {response.text}"

    # проверка ответа
    with allure.step("Проверка содержимого ответа"):
        assert response.headers["Content-Type"].startswith("application/json"), "Ответ не JSON"
        data = response.json()
        assert isinstance(data, dict), "Ответ должен быть объектом"
        assert len(data) > 0, "Тариф пустой"

        assert "title" in data, "у тарифа отсутствует название"
        assert data["title"] == "почасовой тариф для автотестов", "Неожиданное название тарифа"

        assert "id" in data, "отсутствует id тарифа"
        assert isinstance(data["id"], int), "id должен быть числом"
        assert data["id"] == 23762, "неправильный id тарифа"

        assert "isActive" in data, "отсутствует поле со статусом тарифа"
        assert data["isActive"] is True, "неправильный статус тарифа"

        with allure.step(f"Получен тариф: '{data['title']}' (ID: {data['id']})"):
            pass

        # проверка params
        assert "params" in data, "Отсутвует поле params"
        assert isinstance(data["params"], dict), "params должно быть объектом"

        expected_tariff_params(data["params"])



