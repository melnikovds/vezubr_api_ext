# tests/test_create_transport_request_with_4_cargo.py
import allure
import pytest
import requests
import json
import uuid

from pages.create_cargo_page import CargoPlaceClient
from pages.create_order_page import TransportRequestClient
from config.settings import BASE_URL

# Конфигурация - РАЗНЫЕ АДРЕСА ДЛЯ КАЖДОЙ ВЫГРУЗКИ
DEPARTURE_ID = 27282
DELIVERY_IDS = [27287, 27288, 27125, 27374]  # 4 разных адреса для выгрузки
ALL_ADDRESS_IDS = [DEPARTURE_ID] + DELIVERY_IDS
CLIENT_ID = 1598
PRODUCER_ID = 1939
CONTRACT_ID = 21017


@allure.story("Smoke test")
@allure.feature("Транспортные заявки")
@allure.description("Создание рейса с 4 грузоместами по внутренним ID адресов")
@pytest.mark.parametrize("role", ["lkz"])
def test_create_transport_request_with_4_cargo(role, get_auth_token):
    token = get_auth_token(role)["token"]
    headers = {"Authorization": token}

    # 1. Получим все нужные адреса по ID
    resp = requests.post(
        f"{BASE_URL}/contractor-point/list-info",
        headers=headers,
        json={"itemsPerPage": 1000}
    )
    resp.raise_for_status()
    all_points = resp.json()["points"]

    # 2. Создаём словарь: {id: адрес}
    addresses_by_id = {p["id"]: p for p in all_points}

    # 3. Проверяем наличие всех нужных адресов
    missing = [aid for aid in ALL_ADDRESS_IDS if aid not in addresses_by_id]
    if missing:
        raise AssertionError(f"Не найдены адреса с ID: {missing}. Доступные ID: {list(addresses_by_id.keys())}")

    # 4. Формируем маршрут в нужном порядке
    route_addresses = [addresses_by_id[addr_id] for addr_id in ALL_ADDRESS_IDS]

    print(f"🔍 Маршрут: {[addr['id'] for addr in route_addresses]}")

    # 5. Создадим 4 грузоместа
    cargo_client = CargoPlaceClient(BASE_URL, token)
    cargo_places = []

    for i, delivery_id in enumerate(DELIVERY_IDS, start=1):
        title = f"Тестирование API {i}"
        external_id = f"API-TR-TEST-{role}-{i:02d}"
        cargo_resp = cargo_client.create_cargo_place_by_id(
            departure_address_id=DEPARTURE_ID,
            delivery_address_id=delivery_id,
            title=title,
            external_id=external_id,
            weight_kg=10,
            volume_m3=0.5
        )
        cargo_places.append(cargo_resp)

    # 6. Сопоставим ГМ с позициями выгрузки
    cargo_specs = []
    for i, cargo in enumerate(cargo_places):
        # Используем переданный external_id (который мы знаем)
        actual_external_id = f"API-TR-TEST-{role}-{i + 1:02d}"

        cargo_specs.append({
            "cargoPlaceId": cargo["id"],
            "externalId": actual_external_id,
            "departurePointPosition": 1,
            "arrivalPointPosition": i + 2
        })

        print(f"✅ Спецификация ГМ {i + 1}: ID={cargo['id']}, externalId={actual_external_id}")

    # 7. Создание заявки
    order_id = f"API-ORDER-4GM-{uuid.uuid4().hex[:8].upper()}"
    client = TransportRequestClient(BASE_URL, token)

    response_data = client.create_and_publish_transport_request(
        addresses=route_addresses,
        cargo_place_specs=cargo_specs,
        client_id=CLIENT_ID,
        producer_id=PRODUCER_ID,
        contract_id=CONTRACT_ID,
        order_identifier=order_id
    )

    # 8. Проверка
    with allure.step("Проверка ответа"):
        assert "id" in response_data, "Ответ не содержит 'id'"
        request_id = response_data["id"]
        assert isinstance(request_id, int) and request_id > 0

    print(f"\n✅ Рейс создан: ID={request_id}, orderIdentifier={order_id}")

    with allure.step(f"✅ Рейс создан: ID={request_id}"):
        allure.attach(
            json.dumps(response_data, indent=2, ensure_ascii=False),
            name="Ответ API (create-and-publish)",
            attachment_type=allure.attachment_type.JSON
        )