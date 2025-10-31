import allure
import pytest
import requests

from config.settings import BASE_URL


@allure.story("Smoke test")
@allure.feature("Адресные точки")
@allure.description("Получение списка адресных точек")
@pytest.mark.parametrize("role", ["lke", "lkz"])
def test_get_address_list(role, get_auth_token):
    # 1. Авторизация
    token = get_auth_token(role)["token"]
    headers = {"Authorization": token}

    # 2. Запрос списка адресов
    with allure.step(f"Получение списка адресных точек для роли '{role}'"):
        response = requests.post(
            f"{BASE_URL}/contractor-point/list-info",
            headers=headers
        )
        assert response.status_code == 200, f"Ошибка получения списка: {response.text}"

    # 3. Проверка структуры ответа
    response_data = response.json()
    with allure.step("Проверка структуры ответа"):
        assert isinstance(response_data, dict), "Ожидался объект с данными"
        assert "points" in response_data, "В ответе отсутствует поле 'points'"
        assert isinstance(response_data["points"], list), "Поле 'points' должно быть списком"

        address_list = response_data["points"]
        assert len(address_list) > 0, "Список адресов пуст"

    # 4. Вывод информации
    count = len(address_list)
    print(f"\n✅ Получено адресов: {count} для роли {role}")

    with allure.step(f"✅ Получено адресов: {count}"):
        pass
