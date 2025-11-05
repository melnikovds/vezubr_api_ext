import allure
import pytest
import requests
from config.settings import BASE_URL

@allure.story("Smoke test")
@allure.feature("Задание")
@allure.description("проверка деталки Задания")
@pytest.mark.dependency()
@pytest.mark.parametrize("role", ["lkz"])
def test_get_task(role, get_auth_token):
    # авторизация
    token = get_auth_token(role)["token"]
    headers = {"Authorization": token}

    # запрос деталки
    with allure.step(f"Получение деталки Задания"):
        response = requests.get(
            f"{BASE_URL}/shipment/tasks/b676f327-baff-4f5c-96d1-077a86f6dc55",
            headers=headers
        )
        assert response.status_code == 200, f"Ошибка получения деталки: {response.text}"

    detail_data = response.json()

    with allure.step("Проверяем ключевые поля Задания"):
        assert "status" in detail_data, "В ответе отсутствует поле 'status'"
        assert "id" in detail_data, "В ответе отсутствует поле 'id'"
        assert "externalTaskNumber" in detail_data, "В ответе отсутствует поле 'externalTaskNumber'"
        assert "requiredSentAtFrom" in detail_data, "В ответе отсутствует поле 'requiredSentAtFrom'"
        assert "requiredSentAtTill" in detail_data, "В ответе отсутствует поле 'requiredSentAtTill'"
        assert "requiredDeliveredAtFrom" in detail_data, "В ответе отсутствует поле 'requiredDeliveredAtFrom'"
        assert "requiredDeliveredAtTill" in detail_data, "В ответе отсутствует поле 'requiredDeliveredAtTill'"
        assert "cargoPlacesSummary" in detail_data, "В ответе отсутствует объект 'cargoPlacesSummary'"
        assert "shipper" in detail_data, "В ответе отсутствует объект 'shipper'"
        assert "consignee" in detail_data, "В ответе отсутствует объект 'consignee'"

        assert detail_data["status"] == "pick_pending"
        assert detail_data["title"] == "хлебобулочные изделия"
        assert detail_data["isCargoPlacesEnabled"] is True
        assert detail_data["number"] == "булочки"
        assert detail_data["shipBy"] == "fm_logistic"
        assert detail_data["volume"] == 5000000
        assert detail_data["weight"] == 300000
        assert detail_data["quantity"] == 55
        assert detail_data["cost"] == 11230000
        assert detail_data["createdAt"] == "2025-11-01T08:25:10+00:00"

        assert "cargoPlaces" in detail_data, "cargoPlaces отсутствует в ответе"
        cargo_places = detail_data["cargoPlaces"]
        assert isinstance(cargo_places, list), "cargoPlaces должен быть списком"
        assert len(cargo_places) > 0, "cargoPlaces пустой — ожидается хотя бы одно грузоместо"
        first_place = cargo_places[0]
        assert "id" in first_place, "Первое грузоместо не содержит поле 'id'"
        assert isinstance(first_place["id"], int), "ID грузоместа должно быть числом"

        with allure.step("Проверка departurePoint и arrivalPoint"):
            # Проверка departurePoint
            assert "departurePoint" in detail_data, "Поле departurePoint отсутствует в ответе"
            dep_point = detail_data["departurePoint"]
            assert isinstance(dep_point, dict), "departurePoint должен быть объектом"
            assert dep_point["id"] == 19162, f"Ожидался id=19162 для departurePoint, получено: {dep_point['id']}"

            # Проверка arrivalPoint
            assert "arrivalPoint" in detail_data, "Поле arrivalPoint отсутствует в ответе"
            arr_point = detail_data["arrivalPoint"]
            assert isinstance(arr_point, dict), "arrivalPoint должен быть объектом"
            assert arr_point["id"] == 27114, f"Ожидался id=27114 для arrivalPoint, получено: {arr_point['id']}"

            # Проверка что externalId — null
            assert dep_point["externalId"] is None, "externalId в departurePoint должен быть null"
            assert arr_point["externalId"] is None, "externalId в arrivalPoint должен быть null"

            # Проверка что address — строка и не пустой
            assert isinstance(dep_point.get("address"), str) and len(
                dep_point["address"]) > 0, "Некорректный address в departurePoint"
            assert isinstance(arr_point.get("address"), str) and len(
                arr_point["address"]) > 0, "Некорректный address в arrivalPoint"

        with allure.step("Проверка массива cargoDeliveryRequests"):
            assert "cargoDeliveryRequests" in detail_data, "Поле cargoDeliveryRequests отсутствует в ответе"

            requests_list = detail_data["cargoDeliveryRequests"]
            assert isinstance(requests_list, list), "cargoDeliveryRequests должен быть списком"
            assert len(requests_list) == 3, f"Ожидалось 3 заявки, получено: {len(requests_list)}"

            # Проверяем первую заявку
            req1 = requests_list[0]
            cargo_req1 = req1["cargoDeliveryRequest"]
            exec_info1 = req1["executorInfo"]

            assert cargo_req1["requestNr"] == "25-VZ-493", \
                f"Ожидался requestNr='25-VZ-493', получено: {cargo_req1['requestNr']}"

            assert exec_info1 is not None, "executorInfo в первой заявке должен быть заполнен"
            assert exec_info1["driverId"] == 4534, \
                f"Ожидался driverId=4534, получено: {exec_info1['driverId']}"

            # Проверяем вторую заявку
            req2 = requests_list[1]
            cargo_req2 = req2["cargoDeliveryRequest"]
            exec_info2 = req2["executorInfo"]

            assert cargo_req2["requestNr"] == "25-VZ-494", \
                f"Ожидался requestNr='25-VZ-494', получено: {cargo_req2['requestNr']}"

            assert exec_info2 is None, "executorInfo во второй заявке должен быть null"
















