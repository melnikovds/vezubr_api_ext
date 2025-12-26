import allure
import pytest
import requests
import time
from config.settings import BASE_URL
from pages.mass_shipment_task_page import *

CLEAN_UP_AFTER_TEST = True  # если True - запускается блок удаления

@allure.story("Smoke test")
@allure.feature("Задание")
@allure.description("Массовое создание Заданий с рандомизированными данными")
@pytest.mark.parametrize("role", ["lkz"])
def test_create_list_tasks(role, get_auth_token):
    count = 10 # количество Заданий для создания

    # Авторизация
    token = get_auth_token(role)["token"]
    headers = {"Authorization": token, "Content-Type": "application/json"}

    # Генерация данных: создаём `count` заданий
    tasks_data = [generate_random_task_item() for _ in range(count)]

    payload = {"data": tasks_data}
    # print(payload)
    created_id = [] # список для хранения созданных заданий

    with allure.step(f"Массовое создание {count} Заданий"):
        start_time = time.time()  # фиксируем время до запроса
        response = requests.post(
            f"{BASE_URL}/shipment/tasks/create-list",
            headers=headers,
            json=payload
        )
        end_time = time.time() # фиксируем время после запроса
        duration_ms = round((end_time - start_time) * 1000, 2)

        with allure.step(f"Запрос выполнен за {duration_ms} мс"):
            pass

        assert response.status_code == 200, f"Ошибка массового создания: {response.text}"

    # Проверка ответа
    with allure.step("Проверка структуры и содержимого ответа"):
        json_response = response.json()
        # print(json_response)

        # Проверяем общую структуру
        assert isinstance(json_response, dict), "Ответ должен быть объектом"
        assert "data" in json_response, "В ответе отсутствует поле 'data'"
        assert "status" in json_response, "В ответе отсутствует поле 'status'"
        assert json_response["status"] == "ok", f"Ожидался общий статус 'ok', получен: {json_response['status']}"

        data = json_response["data"]
        assert isinstance(data, list), "Поле 'data' должно быть списком"
        assert len(data) == count, f"Ожидалось {count} элементов в 'data', получено: {len(data)}"

        # Проверяем каждый элемент в data
        for i, item in enumerate(data):
            with allure.step(f"Проверка элемента {i + 1} из {count} в массиве 'data'"):
                assert "id" in item, f"В элементе {i} отсутствует поле 'id'"
                assert isinstance(item["id"], str), f"ID должно быть строкой, получено: {type(item['id']).__name__}"
                assert is_valid_uuid(item["id"]), f"Некорректный UUID в id: {item['id']}"

                assert "errors" in item, f"В элементе {i} отсутствует поле 'errors'"
                assert isinstance(item["errors"], list), f"Поле 'errors' должно быть списком"
                assert len(item["errors"]) == 0, f"Ожидался пустой массив 'errors', но есть ошибки: {item['errors']}"

                assert "status" in item, f"В элементе {i} отсутствует поле 'status'"
                assert item["status"] == "ok", f"Ожидался статус 'ok', получен: {item['status']}"

    # Опциональное удаление
    if CLEAN_UP_AFTER_TEST and created_id:
        with allure.step("Удаление всех созданных Заданий"):
            deleted_count = 0
            failed_deletions = []

            for task_id in created_id:
                delete_url = f"{BASE_URL}/shipment/tasks/{task_id}/delete"
                try:
                    delete_response = requests.delete(delete_url, headers=headers)
                    if delete_response.status_code == 200:
                        deleted_count += 1
                    else:
                        failed_deletions.append({
                            "id": task_id,
                            "status": delete_response.status_code,
                            "body": delete_response.text
                        })
                except Exception as e:
                    failed_deletions.append({
                        "id": task_id,
                        "error": str(e)
                    })

            # результаты удаления
            if not failed_deletions:
                with allure.step("✅ Все созданные Задания успешно удалены"):
                    pass
            else:
                with allure.step(f"⚠️ Не удалось удалить {len(failed_deletions)} из {len(created_id)} заданий"):
                    allure.attach(
                        "\n".join([f"ID: {fail['id']}, ошибка: {fail.get('status', '')} {fail.get('error', '')}" for fail in failed_deletions]),
                        name="Ошибки удаления",
                        attachment_type=allure.attachment_type.TEXT
                    )