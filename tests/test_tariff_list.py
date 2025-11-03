import allure
import pytest
import requests
from config.settings import BASE_URL


@allure.story("Smoke test")
@allure.feature("Тарифы")
@allure.description("Получение списка тарифов и фильтров по ним")
@pytest.mark.parametrize("role", ["lke"])
def test_get_tariff_list(role, get_auth_token):
    # авторизация
    token = get_auth_token(role)["token"]
    headers = {"Authorization": token}

    # первый запрос списка тарифов
    with allure.step(f"Получение списка активных тарифов для роли '{role}'"):
        payload = {"itemsPerPage": 100,
                   "status": 1,
                   }
        response = requests.post(
            f"{BASE_URL}/tariffs/list",
            headers=headers,
            json=payload,
        )
        assert response.status_code == 200, f"Ошибка получения списка: {response.text}"

        data = response.json()

    with allure.step("Проверка структуры ответа"):
        assert isinstance(data, dict), "ответ должен быть JSON-объектом"
        assert "itemsCount" in data, "поле itemsCount отсутствует в ответе"
        assert isinstance(data["itemsCount"], int), "itemsCount должно быть числом"

        items_count = data["itemsCount"]

        with allure.step(f"всего активных тарифов найдено: {items_count}"):
            pass

        assert items_count > 350, f"Ожидалось более 350 активных тарифов, получено: {items_count}"

    with allure.step("Проверка пагинации: ожидается 100 тарифов"):
        assert "tariffs" in data, "Поле 'tariffs' отсутствует в ответе"
        tariffs = data["tariffs"]
        assert isinstance(tariffs, list), "Поле 'tariffs' должно быть списком"
        assert len(tariffs) == 100, f"Ожидалось 100 тарифов, получено: {len(tariffs)}"

    with allure.step("Проверка наличия и типа поля 'id' у всех тарифов"):
        missing_id = [i for i, tariff in enumerate(tariffs) if "id" not in tariff]
        invalid_id_type = [t["id"] for t in tariffs if "id" in t and not isinstance(t["id"], int)]

        error_messages = []
        if missing_id:
            error_messages.append(f"У {len(missing_id)} тарифов отсутствует поле 'id'")
        if invalid_id_type:
            error_messages.append(f"У следующих id тип не int: {invalid_id_type}")

        assert not error_messages, "Найдены ошибки в полях 'id':\n" + "\n".join(error_messages)

    # второй запрос списка тарифов
    with allure.step(f"Получение списка неактивных тарифов для роли '{role}'"):
        payload = {"itemsPerPage": 100,
                   "status": 0,
                   }
        response = requests.post(
            f"{BASE_URL}/tariffs/list",
            headers=headers,
            json=payload,
        )
        assert response.status_code == 200, f"Ошибка получения списка: {response.text}"

        data = response.json()

        with allure.step("Проверка структуры ответа"):
            assert isinstance(data, dict), "Ответ должен быть JSON-объектом"
            assert "itemsCount" in data, "поле itemsCount отсутствует в ответе"
            assert isinstance(data["itemsCount"], int), "itemsCount должно быть числом"

            items_count = data[["itemsCount"]]

            with allure.step(f"всего неактивных тарифов найдено: {items_count}"):
                pass

            assert items_count > 35, f"Ожидалось более 35 активных тарифов, получено: {items_count}"

    # третий запрос списка тарифов
    with allure.step(f"Получение всего списка активных тарифов для роли '{role}'"):
        payload = {"itemsPerPage": None,
                   "status": 1,
                   }
        response = requests.post(
            f"{BASE_URL}/tariffs/list",
            headers=headers,
            json=payload,
        )
        assert response.status_code == 200, f"Ошибка получения списка: {response.text}"

        data = response.json()

    with allure.step("Проверка структуры ответа"):
        assert isinstance(data, dict), "Ответ должен быть JSON-объектом"
        assert "itemsCount" in data, "поле itemsCount отсутствует в ответе"
        assert isinstance(data["itemsCount"], int), "itemsCount должно быть числом"

        items_count = data["itemsCount"]
        tariffs = data.get("tariffs", [])

        assert isinstance(tariffs, list), "поле 'tariffs' должно быть списком"

        assert items_count == len(tariffs), (
            f"Количество тарифов не совпадает: itemsCount={items_count}, "
            f"но в массиве 'tariffs' — {len(tariffs)} элементов"
        )

        message = f"Всего найдено {items_count} активных тарифов"
        print(message)

        with allure.step(message):
            pass

    # поиск тарифа по названию
    with allure.step(f"Поиск тарифа по названию для роли '{role}'"):
        payload = {"itemsPerPage": 100,
                   "status": 1,
                   "filterTitle": "45907832"
                   }
        response = requests.post(
            f"{BASE_URL}/tariffs/list",
            headers=headers,
            json=payload,
        )
        assert response.status_code == 200, f"Ошибка получения списка: {response.text}"

        data = response.json()

    with allure.step("Проверка результатов поиска по названию тарифа"):
        # 1. Проверяем что найден только один тариф
        assert "itemsCount" in data, "Поле itemsCount отсутствует в ответе"
        assert isinstance(data["itemsCount"], int), "itemsCount должно быть числом"
        assert data["itemsCount"] == 1, f"Ожидалось 1 найденное значение, получено: {data['itemsCount']}"

        # 2. Проверяем массив tariffs
        assert "tariffs" in data, "Поле 'tariffs' отсутствует в ответе"
        tariffs = data["tariffs"]
        assert isinstance(tariffs, list), "Поле 'tariffs' должно быть списком"
        assert len(tariffs) == 1, f"Ожидался один тариф, получено: {len(tariffs)}"

        # 3. Проверяем характеристики тарифа
        tariff = tariffs[0]
        assert "id" in tariff, "У тарифа отсутствует поле 'id'"
        assert isinstance(tariff["id"], int), "id тарифа должно быть целым числом"
        assert tariff["id"] == 23760, f"Ожидался тариф 23760, получен: {tariff['id']}"
        assert "title" in tariff, "У тарифа отсутствует поле 'title'"
        assert tariff["title"] == "все допы 45907832", "Неожиданное название тарифа"


