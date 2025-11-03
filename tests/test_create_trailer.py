import allure
import pytest
import requests
from config.settings import BASE_URL
from pages.trailer_page import TrailerCreate


@allure.story("Smoke test")
@allure.feature("Транспортные средства")
@allure.description("Создание прицепа с рандомизированными данными под ролью ЛКЭ и ЛКП")
@pytest.mark.parametrize("role", ["lke", "lkp"])
def test_create_trailer(role, get_auth_token):
    # получаем токен
    token = get_auth_token(role)["token"]

    # генерируем данные для прицепа
    trailer_payload = TrailerCreate.create_trailer_payload()

    #  отправляем запрос
    with allure.step("Создание прицепа"):
        response = requests.post(
            url=f"{BASE_URL}/trailer/create",
            # headers={"Authorization": f"Bearer {token}"},
            headers={"Authorization": token},
            json=trailer_payload
        )
        assert response.status_code == 200, f"Ошибка создания прицепа: {response.text}"

    # проверяем ответ
    created_trailer = response.json()
    with allure.step("Проверка ключевых полей в ответе"):
        assert created_trailer["plateNumber"] == trailer_payload["plateNumber"]
        assert created_trailer["status"] == "active"
        assert "id" in created_trailer
        assert created_trailer["liftingCapacityInKg"] == trailer_payload["liftingCapacityInKg"]
        assert created_trailer["topLoadingAvailable"] == trailer_payload["isTopLoadingAvailable"]
        assert created_trailer["sideLoadingAvailable"] == trailer_payload["isSideLoadingAvailable"]
        assert created_trailer["rearLoadingAvailable"] == trailer_payload["isRearLoadingAvailable"]

    # выводим информацию о созданном прицепе
    plate = created_trailer["plateNumber"]
    mark = created_trailer["markAndModel"]

    print(f"\n Создан прицеп: {mark} | госномер: {plate}")
    with allure.step(f"создан прицеп: {mark} | госномер: {plate}"):
        pass



