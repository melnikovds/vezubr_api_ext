import allure
import pytest
import requests
from config.settings import BASE_URL

@allure.story("Smoke test")
@allure.feature("Задание")
@allure.description("проверка списка Заданий в Заявке")
@pytest.mark.parametrize("role", ["lkz"])
def test_task_request_list(role, get_auth_token):
    # авторизация
    token = get_auth_token(role)["token"]
    headers = {"Authorization": token}

    # отправка запроса
    # body = {
    #         "id": "b676f327-baff-4f5c-96d1-077a86f6dc55",
    #         "number": "булочка"
    # }
    body = {
            "id": "b449ea13-6a32-4b72-af02-cc834c54f76a"
            # "number": "25-VZ-494"
    }

    with allure.step(f"отправка запроса по списку Заявок с Заданием"):
        response = requests.post(
            f"{BASE_URL}/shipment/tasks/cargo-delivery-request/list",
            headers=headers,
            json=body
        )
        print(response.text)
        assert response.status_code == 200, f"Ошибка отправки запроса: {response.text}"

    task_list = response.json()
    print(task_list)
