import allure
import pytest
import requests
from config.settings import BASE_URL
from pages.shipment_task_page import TaskCreate
from pprint import pprint


@allure.story("Smoke test")
@allure.feature("Задание")
@allure.description("Обновление Задания")
@pytest.mark.parametrize("role", ["lkz"])
def test_update_task(role, get_auth_token):
    # Авторизация
    token = get_auth_token(role)["token"]
    headers = {"Authorization": token}

    # Создаём Задание
    task_payload = TaskCreate.create_task_payload()

    with allure.step("Создание Задания"):
        response = requests.post(
            f"{BASE_URL}/shipment/tasks/create",
            headers=headers,
            json=task_payload
        )
        assert response.status_code == 200, f"Ошибка создания Задания: {response.text}"

    created = response.json()
    task_id = created["id"]

    # Обновляем Задание
    task_update = TaskCreate.update_task_payload()
    pprint(task_update)

    with allure.step("Обновление Задания"):
        response = requests.post(
            f"{BASE_URL}/shipment/tasks/{task_id}/update",
            headers=headers,
            json=task_update
        )
        assert response.status_code == 200, f"Ошибка обновления Задания: {response.text}"

    # Проверка обновления Задания
    # updated = response.json()

    with allure.step("Запрос деталки Задания"):
        response = requests.get(
            f"{BASE_URL}/shipment/tasks/{task_id}",
            headers=headers
        )
        assert response.status_code == 200, f"Ошибка получения деталки: {response.text}"

    # Деталка Задания
    detail_data = response.json()
    pprint(detail_data)

    # правим UTC время на местное время Адреса
    expected_local_one = TaskCreate.to_local_hour(task_update["requiredSentAtFrom"], tz_offset_hours=3)
    expected_local_two = TaskCreate.to_local_hour(task_update["requiredSentAtTill"], tz_offset_hours=3)
    expected_local_three = TaskCreate.to_local_hour(task_update["requiredDeliveredAtFrom"], tz_offset_hours=3)
    expected_local_four = TaskCreate.to_local_hour(task_update["requiredDeliveredAtTill"], tz_offset_hours=3)

    with allure.step("Проверяем значения обновлённого Задания"):
        assert detail_data["shipBy"] == task_update["shipBy"]
        assert detail_data["number"] == task_update["number"]
        assert detail_data["externalTaskNumber"] == task_update["externalTaskNumber"]
        assert detail_data["title"] == task_update["title"]
        assert detail_data["departurePoint"]["id"] == task_update["departurePoint"]["id"]
        assert detail_data["arrivalPoint"]["id"] == task_update["arrivalPoint"]["id"]
        assert detail_data["volume"] == task_update["volume"]
        assert detail_data["weight"] == task_update["weight"]
        assert detail_data["cost"] == task_update["cost"]
        assert detail_data["quantity"] == task_update["quantity"]
        assert detail_data["types"] == task_update["types"]
        # assert detail_data["requiredSentAtFrom"][:13] == task_update["requiredSentAtFrom"][:13]
        # assert detail_data["requiredSentAtTill"][:13] == task_update["requiredSentAtTill"][:13]
        # assert detail_data["requiredDeliveredAtFrom"][:13] == task_update["requiredDeliveredAtFrom"][:13]
        # assert detail_data["requiredDeliveredAtTill"] == task_update["requiredDeliveredAtTill"][:13]
        assert detail_data["requiredSentAtFrom"][:13] == expected_local_one
        assert detail_data["requiredSentAtTill"][:13] == expected_local_two
        assert detail_data["requiredDeliveredAtFrom"][:13] == expected_local_three
        assert detail_data["requiredDeliveredAtTill"][:13] == expected_local_four

