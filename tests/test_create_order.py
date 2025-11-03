import allure
import pytest
import requests
import json
import uuid

from pages.create_cargo_page import CargoPlaceClient
from pages.create_order_page import TransportRequestClient
from config.settings import BASE_URL


@allure.story("Smoke test")
@allure.feature("Транспортные заявки")
@allure.description("Создание транспортной заявки (рейса) с адресами и ГМ")
@pytest.mark.parametrize("role", ["lke"])
def test_create_transport_request(role, get_auth_token, client_id, producer_id):
    # 1. Авторизация
    token = get_auth_token(role)["token"]
    headers = {"Authorization": token}

    # 2. Получим список адресов
    response = requests.post(
        f"{BASE_URL}/contractor-point/list-info",
        headers=headers,
        json={"itemsPerPage": 100}
    )
    response.raise_for_status()
    points = response.json()["points"]

    # 3. Ищем два адреса
    departure_ext = "Izhevsk 81-870"
    delivery_ext = "Izhevsk 71-130"

    departure_addr = next((p for p in points if p.get("externalId") == departure_ext), None)
    delivery_addr = next((p for p in points if p.get("externalId") == delivery_ext), None)

    assert departure_addr is not None, f"Не найден адрес отправки: {departure_ext}"
    assert delivery_addr is not None, f"Не найден адрес доставки: {delivery_ext}"

    addresses = [departure_addr, delivery_addr]

    # 4. Создаем одно грузоместо
    cargo_client = CargoPlaceClient(BASE_URL, token)
    cp_external_id = f"CP-SMOKE-{uuid.uuid4().hex[:8].upper()}"
    cargo_resp = cargo_client.create_cargo_place(
        departure_external_id=departure_ext,
        delivery_external_id=delivery_ext,
        title="Smoke Test Cargo",
        external_id=cp_external_id,
        weight_kg=5,
        volume_m3=0.1
    )

    # 5. Спецификация грузоместа: из точки 1 в точку 2
    cargo_specs = [{
        "cargoPlaceId": cargo_resp["id"],
        "externalId": cargo_resp.get("externalId") or cp_external_id,
        "departurePointPosition": 1,
        "arrivalPointPosition": 2
    }]

    # 6. Создадим уникальный orderIdentifier
    order_id = f"API-ORDER-{uuid.uuid4().hex[:8].upper()}"

    # 7. Создание заявки
    client = TransportRequestClient(BASE_URL, token)
    response_data = client.create_transport_request(
        addresses=addresses,
        cargo_place_specs=cargo_specs,
        client_id=client_id,
        producer_id=producer_id,
        contract_id=17142,
        order_identifier=order_id
    )

    # 8. Проверка
    with allure.step("Проверка ответа"):
        assert "id" in response_data
        request_id = response_data["id"]
        assert isinstance(request_id, int) and request_id > 0

    print(f"\n✅ Создана заявка ID={request_id}, orderIdentifier={order_id}")

    with allure.step(f"✅ Заявка создана: ID={request_id}"):
        allure.attach(
            json.dumps(response_data, indent=2),
            name="Ответ API",
            attachment_type=allure.attachment_type.JSON
        )
