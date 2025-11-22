import allure
import pytest
import requests
from pages.tractor_page import TractorPage
from config.settings import BASE_URL


@allure.story("Smoke test")
@allure.feature("Тягач")
@allure.description("Создание Тягача и проверка его данных")
@pytest.mark.parametrize("role", ["lke", "lkp"])
def test_create_tractor(role, get_auth_token):
    # 1. Авторизация
    token = get_auth_token(role)["token"]
    headers = {"Authorization": token}

    # 2. Генерация данных
    tractor_payload = TractorPage.create_tractor_payload()

    # 3. Создание трактора
    with allure.step(f"Создание Тягача под ролью '{role}'"):
        create_response = requests.post(
            f"{BASE_URL}/tractor/create",
            headers=headers,
            json=tractor_payload
        )
        assert create_response.status_code == 200, f"Ошибка создания: {create_response.text}"

        created = create_response.json()
        tractor_data = created.get("tractor")
        assert tractor_data is not None, f"В ответе отсутствует объект 'tractor'. Ответ: {created}"

        tractor_id = tractor_data.get("id")
        assert tractor_id, f"В объекте 'tractor' отсутствует ID. Данные: {tractor_data}"

    # 4. Проверка данных сразу из ответа
    with allure.step("Проверка ключевых полей"):
        assert tractor_data["plateNumber"] == tractor_payload["plateNumber"]
        assert tractor_data["markAndModel"] == tractor_payload["markAndModel"]
        assert tractor_data["status"] == "active"

    # 5. Вывод информации
    plate = tractor_data["plateNumber"]
    mark = tractor_data["markAndModel"]
    print(f"\n✅ Создан Тягач: {mark} | Госномер: {plate}")

    with allure.step(f"✅ Создан Тягач: {mark} | Госномер: {plate}"):
        pass