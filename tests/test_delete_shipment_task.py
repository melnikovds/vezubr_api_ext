import allure
import pytest
import requests
from config.settings import BASE_URL
from pages.shipment_task_page import TaskCreate

@allure.story("Smoke test")
@allure.feature("Задание")
@allure.description("удаление Задания с рандомизированными данными")
@pytest.mark.parametrize("role", ["lkz"])
def test_delete_task(role, get_auth_token):
    # Авторизация
    token = get_auth_token(role)["token"]
    headers = {"Authorization": token}

    # Генерация данных
    task_payload = TaskCreate.create_task_payload()

    # создаём Задание
    with allure.step("Создание Задания"):
        response = requests.post(
            f"{BASE_URL}/shipment/tasks/create",
            headers=headers,
            json=task_payload
        )
        assert response.status_code == 200, f"Ошибка создания Задания: {response.text}"

    # Проверяем ответ
    created = response.json()
    with allure.step("Проверка наличия ID и его типа"):
        assert "id" in created, f"В ответе отсутствует поле 'id. Ответ: {created}"
        assert isinstance(created["id"], str), f"ID должен быть строкой, получено: {type(created['id'])} "

    #  Вывод информации
    task_id = created["id"]
    print(f"Создано Задание {task_id}")

    with allure.step(f"Создано Задание {task_id}"):
        pass

    # Удаление Задания
    with allure.step(f"Удаление созданного Задания {task_id}"):
        response = requests.delete(
            f"{BASE_URL}/shipment/tasks/{task_id}/delete",
            headers=headers
        )
        assert response.status_code == 200, f"Ошибка удаления Задания: {response.text}"

    # Проверка удаления Задания
    with allure.step(f"Получение деталки удалённого Задания {task_id}"):
        response = requests.get(
            f"{BASE_URL}/shipment/tasks/{task_id}",
            headers=headers
        )
        assert response.status_code == 404, f"Ошибка получения деталки: {response.text}"

        response_json = response.json()
        assert response_json.get("message") == "Задание не найдено", \
            f"Ожидалось сообщение 'Задание не найдено', но получено: {response_json.get('message')}"

        assert response_json.get("status") is False, \
            f"Ожидалось status: false, но получено: {response_json.get('status')}"



