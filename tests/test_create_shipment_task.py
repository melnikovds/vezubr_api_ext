import allure
import pytest
import requests
from config.settings import BASE_URL
from pages.shipment_task_page import TaskCreate


@allure.story("Smoke test")
@allure.feature("Задание")
@allure.description("Создание Задания с рандомизированными данными")
@pytest.mark.parametrize("role", ["lkz"])
def test_create_task(role, get_auth_token):
    # Авторизация
    token = get_auth_token(role)["token"]
    headers = {"Authorization": token}

    # Генерация данных
    task_payload = TaskCreate.create_task_payload()

    # Отправляем запрос
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

    original_data = test_create_task
    task_id = original_data["task_id"]
    create_payload = original_data["payload"]

    # Запрос деталки
    with allure.step(f"Получение деталки созданного Задания {task_id}"):
        response = requests.get(
            f"{BASE_URL}/v1/api-ext/shipment/tasks/{task_id}",
            headers=headers
        )
        assert response.status_code == 200, f"Ошибка получения деталки: {response.text}"

    detail_data = response.json()

    # Проверяем ключевые поля
    with allure.step("Сравнение полей из запроса на создание и деталки"):
        assert "status" in detail_data, "В ответе отсутствует поле 'status'"
        assert detail_data["status"] == "created"

        assert "createdAt" in detail_data, "В ответе отсутствует поле 'createdAt'"
        created_at = detail_data["createdAt"]
        assert isinstance(created_at,
                          str), f"Поле 'createdAt' должно быть строкой, получено: {type(created_at).__name__}"
        assert len(created_at) > 0, "Поле 'createdAt' пустое"

        assert "cargoPlaces" in detail_data, "Поле cargoPlaces отсутствует в ответе"
        cargo_places = detail_data["cargoPlaces"]
        assert isinstance(cargo_places, list), "cargoPlaces должен быть списком"
        assert len(cargo_places) > 0, "cargoPlaces пустой — ожидается хотя бы одно грузоместо"
        # Проверяем, что у каждого элемента есть 'id'
        for i, place in enumerate(cargo_places):
            assert "id" in place, f"В cargoPlaces[{i}] отсутствует поле 'id'"
            assert isinstance(place["id"], (int, str)), f"cargoPlaces[{i}].id должно быть строкой или числом"

        assert "shipBy" in detail_data, "Поле shipBy отсутствует в деталке"
        assert detail_data["shipBy"] == create_payload["shipBy"], \
            f"Ожидалось shipBy={create_payload['shipBy']}, получено {detail_data['shipBy']}"

        assert detail_data["title"] == create_payload["title"], "Несоответствие title"
        assert detail_data["number"] == create_payload["number"], "Несоответствие number"

        if "arrivalPoint" in create_payload and "arrivalPoint" in detail_data:
            assert detail_data["arrivalPoint"]["id"] == create_payload["arrivalPoint"]["id"]

        if "departurePoint" in create_payload and "departurePoint" in detail_data:
            assert detail_data["departurePoint"]["id"] == create_payload["departurePoint"]["id"]

        assert detail_data["volume"] == create_payload["volume"]
        assert detail_data["weight"] == create_payload["weight"]
        assert detail_data["quantity"] == create_payload["quantity"]
        assert detail_data["cost"] == create_payload["cost"]

    with allure.step(f"Поля созданного Задания {task_id} проверены"):
        pass



# @allure.story("Smoke test")
# @allure.feature("Задание")
# @allure.description("Создание Задания с рандомизированными данными")
# @pytest.mark.dependency()
# @pytest.mark.parametrize("role", ["lkz"])
# def test_create_task(role, get_auth_token):
#     # Авторизация
#     token = get_auth_token(role)["token"]
#     headers = {"Authorization": token}
#
#     # Генерация данных
#     task_payload = TaskCreate.create_task_payload()
#
#     # Отправляем запрос
#     with allure.step("Создание Задания"):
#         response = requests.post(
#             f"{BASE_URL}/shipment/tasks/create",
#             headers=headers,
#             json=task_payload
#         )
#         assert response.status_code == 200, f"Ошибка создания Задания: {response.text}"
#
#     # Проверяем ответ
#     created = response.json()
#     with allure.step("Проверка наличия ID и его типа"):
#         assert "id" in created, f"В ответе отсутствует поле 'id. Ответ: {created}"
#         assert isinstance(created["id"], str), f"ID должен быть строкой, получено: {type(created['id'])} "
#
#     #  Вывод информации
#     task_id = created["id"]
#     print(f"Создано Задание {task_id}")
#
#     with allure.step(f"Создано Задание {task_id}"):
#         pass
#
#     #  Берём данные для следующего теста
#     return {
#         "payload": task_payload,
#         "task_id": created["id"]
#     }
#
#
# @allure.story("Smoke test")
# @allure.feature("Задание")
# @allure.description("Проверка деталей Задания после создания")
# @pytest.mark.dependency(depends=["test_create_task"])
# @pytest.mark.parametrize("role", ["lkz"])
# def test_check_task_details(role, get_auth_token, test_create_task):
#     # Получаем данные из предыдущего теста
#     original_data = test_create_task
#     task_id = original_data["task_id"]
#     create_payload = original_data["payload"]
#
#     # Авторизация
#     token = get_auth_token(role)["token"]
#     headers = {"Authorization": f"Bearer {token}"}
#
#     # Запрос деталки
#     with allure.step(f"Получение деталки созданного Задания {task_id}"):
#         response = requests.get(
#             f"{BASE_URL}/v1/api-ext/shipment/tasks/{task_id}",
#             headers=headers
#         )
#         assert response.status_code == 200, f"Ошибка получения деталки: {response.text}"
#
#     detail_data = response.json()
#
#     # Проверяем ключевые поля
#     with allure.step("Сравнение полей из запроса на создание и деталки"):
#         assert "status" in detail_data, "В ответе отсутствует поле 'status'"
#         assert detail_data["status"] == "created"
#
#         assert "createdAt" in detail_data, "В ответе отсутствует поле 'createdAt'"
#         created_at = detail_data["createdAt"]
#         assert isinstance(created_at,
#                           str), f"Поле 'createdAt' должно быть строкой, получено: {type(created_at).__name__}"
#         assert len(created_at) > 0, "Поле 'createdAt' пустое"
#
#         assert "cargoPlaces" in detail_data, "Поле cargoPlaces отсутствует в ответе"
#         cargo_places = detail_data["cargoPlaces"]
#         assert isinstance(cargo_places, list), "cargoPlaces должен быть списком"
#         assert len(cargo_places) > 0, "cargoPlaces пустой — ожидается хотя бы одно грузоместо"
#         # Проверяем, что у каждого элемента есть 'id'
#         for i, place in enumerate(cargo_places):
#             assert "id" in place, f"В cargoPlaces[{i}] отсутствует поле 'id'"
#             assert isinstance(place["id"], (int, str)), f"cargoPlaces[{i}].id должно быть строкой или числом"
#
#         assert "shipBy" in detail_data, "Поле shipBy отсутствует в деталке"
#         assert detail_data["shipBy"] == create_payload["shipBy"], \
#             f"Ожидалось shipBy={create_payload['shipBy']}, получено {detail_data['shipBy']}"
#
#         assert detail_data["title"] == create_payload["title"], "Несоответствие title"
#         assert detail_data["number"] == create_payload["number"], "Несоответствие number"
#
#         if "arrivalPoint" in create_payload and "arrivalPoint" in detail_data:
#             assert detail_data["arrivalPoint"]["id"] == create_payload["arrivalPoint"]["id"]
#
#         if "departurePoint" in create_payload and "departurePoint" in detail_data:
#             assert detail_data["departurePoint"]["id"] == create_payload["departurePoint"]["id"]
#
#         assert detail_data["volume"] == create_payload["volume"]
#         assert detail_data["weight"] == create_payload["weight"]
#         assert detail_data["quantity"] == create_payload["quantity"]
#         assert detail_data["cost"] == create_payload["cost"]
#
#     with allure.step(f"Поля созданного Задания {task_id} проверены"):
#         pass









