import allure
import pytest
import requests
from config.settings import BASE_URL
from pages.driver_page import DriverCreate

@allure.story("Smoke test")
@allure.feature("Водители")
@allure.description("Создание водителя с рандомизированными данными под ролью ЛКЭ и ЛКП")
@pytest.mark.parametrize("role", ["lke", "lkp"])
def test_create_driver(role, get_auth_token):
    # получаем токен
    token = get_auth_token(role)["token"]

    # генерируем данные для водителя
    driver_payload = DriverCreate.create_driver_payload()

    # отправляем запрос
    with allure.step("Создание водителя"):
        response = requests.post(
            url=f"{BASE_URL}/driver/create",
            headers={"Authorization": token},
            json=driver_payload
        )
        assert response.status_code == 200, f"Ошибка создания водителя: {response.text}"

    # проверяем ответ
    created_driver = response.json()
    with allure.step("Проверка ключевых полей в ответе"):
        assert created_driver["applicationPhone"] == ''.join(
            c for c in driver_payload["applicationPhone"] if c.isdigit()), \
            "Номера телефонов не совпадают"
        assert created_driver["status"] == "active"
        assert "id" in created_driver
        assert created_driver["passportRusResident"] == driver_payload["passportRusResident"]
        assert created_driver["hasSanitaryBook"] == driver_payload["hasSanitaryBook"]
        assert created_driver["dlRusResident"] == driver_payload["dlRusResident"]
        assert created_driver["driverLicenseId"], "Поле driverLicenseId отсутствует или пустое"
        assert created_driver["surname"] == driver_payload["surname"]
        assert created_driver["driverLicenseSurname"] == driver_payload["driverLicenseSurname"]

        # выводим информацию о созданном водителе
        first_name = created_driver["driverLicenseName"]
        last_name = created_driver["driverLicenseSurname"]

        print(f"\n Создан водитель: {first_name} {last_name}")
        with allure.step(f"создан водитель: {first_name} {last_name}"):
            pass

