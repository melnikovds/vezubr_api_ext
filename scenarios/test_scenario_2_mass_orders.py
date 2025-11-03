import time
import pytest
import time
from pages.address_page import AddressPage
from pages.create_cargo_page import CargoPlaceClient
from pages.create_order_page import TransportRequestClient
from config.settings import BASE_URL

DEPARTURE_POINT = 1
DESTINATION_POINTS = [2, 3, 4, 5]
# Только существующие externalId
EXISTING_EXTERNAL_IDS = [
    "Izhevsk 81-870",
    "Izhevsk - Pastuhova - 37",
    "Izhevsk - Udmurtskaya - 12",
    "Izhevsk - Telegina - 47",
    "Izhevsk - Shkolnaya - 27"
]

def test_scenario_2(get_auth_token, client_id, producer_id, contract_id):
    token = get_auth_token("lke")["token"]

    # 1. Получить 5 существующих адресов
    external_ids = [
        "Izhevsk 81-870",
        "Izhevsk - Pastuhova - 37",
        "Izhevsk - Udmurtskaya - 12",
        "Izhevsk - Telegina - 47",
        "Izhevsk - Shkolnaya - 27"
    ]
    addresses = []
    for ext_id in external_ids:
        addr = AddressPage.find_by_external_id(BASE_URL, token, ext_id)
        assert addr, f"Адрес {ext_id} не найден"
        addresses.append(addr)

    # 2. Создать 20 грузомест
    cargo_client = CargoPlaceClient(BASE_URL, token)
    cargo_list = []
    for i in range(20):
        dep = external_ids[i % len(external_ids)]
        arr = external_ids[(i + 1) % len(external_ids)]
        external_id_cp = f"CP-{45529 + i}"
        resp = cargo_client.create_cargo_place(
            departure_external_id=dep,
            delivery_external_id=arr,
            title=f"Груз-{i + 1}",
            external_id=external_id_cp,
            weight_kg = 50,
            volume_m3 = 0.5
        )
        cargo_list.append({
            "id": resp["id"],
            "externalId": resp.get("externalId") or external_id_cp
        })

    # 3. Создаем 5 рейсов по 4 грузоместа
    order_client = TransportRequestClient(BASE_URL, token)
    order_ids = []

    for i in range(5):
        batch = cargo_list[i * 4: (i + 1) * 4]
        cargo_specs = [
            {
                "cargoPlaceId": cp["id"],
                "externalId": cp["externalId"],
                "departurePointPosition": DEPARTURE_POINT,
                "arrivalPointPosition": DESTINATION_POINTS[idx]
            }
            for idx, cp in enumerate(batch)
        ]

        order_id = order_client.create_transport_request(
            addresses=addresses,
            cargo_place_specs=cargo_specs,
            client_id=client_id,
            producer_id=producer_id,
            contract_id=contract_id,
            order_identifier=f"SCENARIO2-{i}-{int(time.time())}"
        )["id"]
        order_ids.append(order_id)

    # ✅ Выводим ID созданных рейсов
    print(f"\n✅ Созданы рейсы с ID: {order_ids}")

    # 5. Мониторинг деталей рейсов 10 минут
    for minute in range(10):
        time.sleep(60)
        print(f"\n🔍 Минута {minute + 1}/10: проверка деталей рейсов...")
        for oid in order_ids:
            details = order_client.get_order_details(oid)
            status = details.get("state")
            cargo_places = details.get("transportOrder", {}).get("cargoPlaces", [])
            print(f"  Рейс {oid}: статус = {status}, грузомест = {len(cargo_places)}")