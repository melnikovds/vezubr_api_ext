import allure
import pytest
import json

from pages.create_cargo_page import CargoPlaceClient
from config.settings import BASE_URL


# Адреса по ID (внутренние ID системы Везубр)
DEPARTURE_ADDRESS_ID = 27282
DELIVERY_ADDRESS_IDS = [27287, 27288, 27125, 27125]  # 4 ГМ: два — в 27125


@allure.story("Smoke test")
@allure.feature("Грузоместа")
@allure.description("Создание грузомест с указанием внутренних ID адресов")
@pytest.mark.parametrize("role", ["lkz"])
def test_create_cargo_place_by_address_id(role, get_auth_token):
    token = get_auth_token(role)["token"]
    client = CargoPlaceClient(BASE_URL, token)

    created_cargos = []

    for i, delivery_id in enumerate(DELIVERY_ADDRESS_IDS, start=1):
        title = f"Тестирование API {i}"
        external_id = f"API-ID-TEST-{role}-{i:02d}"

        with allure.step(f"Создание грузоместа №{i}: {title}"):
            response_data = client.create_cargo_place_by_id(
                departure_address_id=DEPARTURE_ADDRESS_ID,
                delivery_address_id=delivery_id,
                title=title,
                external_id=external_id
            )

        # Проверка ответа
        assert "id" in response_data, f"ГМ №{i}: отсутствует 'id'"
        cargo_id = response_data["id"]
        assert isinstance(cargo_id, int) and cargo_id > 0, f"ГМ №{i}: некорректный ID: {cargo_id}"

        created_cargos.append(response_data)
        print(f"\n✅ ГМ №{i} создано: ID={cargo_id}, title='{title}'")

    # Прикрепление в Allure
    with allure.step("Детали всех созданных грузомест"):
        allure.attach(
            json.dumps(created_cargos, indent=2, ensure_ascii=False),
            name="Ответы API (cargo-place by ID)",
            attachment_type=allure.attachment_type.JSON
        )