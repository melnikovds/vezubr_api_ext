import allure
import pytest
import requests
import json
import uuid
import random

from pages.create_cargo_page import CargoPlaceClient
from pages.create_order_page import TransportRequestClient
from pages.address_page import AddressPage
from config.settings import BASE_URL


@allure.story("Smoke test")
@allure.feature("Транспортные заявки")
@allure.description("Создание транспортной заявки (рейса) с адресами и ГМ")
@pytest.mark.parametrize("role", ["lke"])
def test_create_transport_request(role, get_auth_token, client_id, producer_id):
    # 1. Авторизация
    token = get_auth_token(role)["token"]
    headers = {"Authorization": token}

    # 2. СОЗДАЕМ НОВЫЕ АДРЕСА ДЛЯ ТЕСТА
    # Генерируем уникальные externalId для теста
    departure_ext = f"Izhevsk-TEST-{uuid.uuid4().hex[:8].upper()}"
    delivery_ext = f"Izhevsk-TEST-{uuid.uuid4().hex[:8].upper()}"

    with allure.step("Создание тестовых адресов"):
        # ИСПРАВЛЕНИЕ: Используем класс напрямую, а не создаем экземпляр
        # Создаем адрес отправки
        departure_payload = AddressPage.create_address_payload(  # ← УБИРАЕМ address_client.
            externalId=departure_ext,
            title=f"Тестовый адрес отправки {departure_ext}",
            addressString="г Ижевск, ул Дзержинского, д 61"
        )
        departure_id = AddressPage.create_or_update_address(BASE_URL, token, departure_payload)
        print(f"✅ Создан адрес отправки: externalId={departure_ext}, id={departure_id}")

        # Создаем адрес доставки
        delivery_payload = AddressPage.create_address_payload(  # ← УБИРАЕМ address_client.
            externalId=delivery_ext,
            title=f"Тестовый адрес доставки {delivery_ext}",
            addressString="г Ижевск, ул 9 Января, д 191"
        )
        delivery_id = AddressPage.create_or_update_address(BASE_URL, token, delivery_payload)
        print(f"✅ Создан адрес доставки: externalId={delivery_ext}, id={delivery_id}")

    # 3. Получаем созданные адреса для использования в заявке
    response = requests.post(
        f"{BASE_URL}/contractor-point/list-info",
        headers=headers,
        json={"itemsPerPage": 100}
    )
    response.raise_for_status()
    points = response.json()["points"]

    departure_addr = next((p for p in points if p.get("externalId") == departure_ext), None)
    delivery_addr = next((p for p in points if p.get("externalId") == delivery_ext), None)

    assert departure_addr is not None, f"Не найден созданный адрес отправки: {departure_ext}"
    assert delivery_addr is not None, f"Не найден созданный адрес доставки: {delivery_ext}"

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
