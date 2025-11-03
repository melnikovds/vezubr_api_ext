import allure
import pytest
import requests
from config.settings import BASE_URL
from pages.dictionaries_page import *

@allure.story("Smoke test")
@allure.feature("Справочники")
@allure.description("Получение справочников и проверка полного перевода всех полей")
@pytest.mark.parametrize("role", ["lke"])
def test_get_dictionaries(role, get_auth_token):
    # авторизация
    token = get_auth_token(role)["token"]
    headers = {"Authorization": token}

    # запрос справочника
    with allure.step(f"Получение справочников для роли '{role}'"):
        response = requests.get(
            f"{BASE_URL}/dictionaries",
            headers=headers
        )
        assert response.status_code == 200, f"Ошибка получения справочника: {response.text}"

    # проверка ответа
    with allure.step("Проверка содержимого ответа"):
        assert response.headers["Content-Type"].startswith("application/json"), "Ответ не JSON"
        data = response.json()
        assert isinstance(data, dict), "Ответ должен быть объектом"
        assert len(data) > 0, "Справочник пустой"
        assert "cargoPlaceSegmentStatuses" in data
        assert "cargoPlaceStatuses" in data
        assert "orderUiState" in data
        assert "truckDeliveryStatus" in data
        assert "userRoles" in data
        assert "tariffTypes" in data

        validate_russian_titles_in_response(response)
