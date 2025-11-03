import allure
import pytest
import requests
from config.settings import BASE_URL
from pages.vehicle_page import VehiclePage


@allure.story("Smoke test")
@allure.feature("Транспортные средства")
@allure.description("Создание ТС с рандомизированными данными под ролью ЛКП и ЛКЭ")
@pytest.mark.parametrize("role", ["lke", "lkp"])
def test_create_vehicle(role, get_auth_token):
    # 1. Получаем токен
    token = get_auth_token(role)["token"]

    # 2. Генерируем данные для ТС
    vehicle_payload = VehiclePage.create_vehicle_payload()

    # 3. Отправляем запрос
    with allure.step("Создание транспортного средства"):
        response = requests.post(
            f"{BASE_URL}/vehicle/create",
            headers={"Authorization": token},
            json=vehicle_payload
        )
        assert response.status_code == 200, f"Ошибка создания ТС: {response.text}"

    # 4. Проверяем ответ
    created_vehicle = response.json()
    with allure.step("Проверка ключевых полей в ответе"):
        assert created_vehicle["plateNumber"] == vehicle_payload["plateNumber"]
        assert created_vehicle["status"] == "active"
        assert "id" in created_vehicle
        assert created_vehicle["volume"] == vehicle_payload["volume"]

    # 5. Выводим информацию о созданном ТС
    plate = created_vehicle["plateNumber"]
    mark = created_vehicle["markAndModel"]


    print(f"\n Создано ТС: {mark} | Госномер: {plate}")

    # Шаг в Allure-отчёте
    with allure.step(f" Создано ТС: {mark} | Госномер: {plate}"):
        pass
