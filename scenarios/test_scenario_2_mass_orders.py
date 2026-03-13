import time
import pytest
from pages.address_page import AddressPage
from pages.create_cargo_page import CargoPlaceClient
from pages.create_order_page import TransportRequestClient
from config.settings import BASE_URL

DEPARTURE_POINT = 1
DESTINATION_POINTS = [2, 3, 4, 5]

# Шаблоны для адресов
ADDRESS_TEMPLATES = {
    "Izhevsk 81-870": {
        "addressString": "г Ижевск, ул Дзержинского, д 61",
        "latitude": 56.883786581427,
        "longitude": 53.249709832523,
        "title": "Авто. API Ижевск"
    },
    "Izhevsk - Pastuhova - 37": {
        "addressString": "г Ижевск, ул Пастухова, д 37",
        "latitude": 56.842033,
        "longitude": 53.2083981,
        "title": "Izhevsk - Pastuhova - 37"
    },
    "Izhevsk - Udmurtskaya - 12": {
        "addressString": "г Ижевск, ул Удмуртская, д 100",
        "latitude": 56.8521404,
        "longitude": 53.2242347,
        "title": "Izhevsk - Udmurtskaya - 12"
    },
    "Izhevsk - Telegina - 47": {
        "addressString": "Россия, г Ижевск, ул Телегина, зд 47",
        "latitude": 56.832214666145,
        "longitude": 53.161456986964,
        "title": "Izhevsk - Telegina - 47"
    },
    "Izhevsk - Shkolnaya - 27": {
        "addressString": "Россия, г Ижевск, ул Школьная, д 27",
        "latitude": 56.869681186854,
        "longitude": 53.18402530275,
        "title": "Izhevsk - Shkolnaya - 27"
    }
}


def ensure_address_exists(base_url: str, token: str, external_id: str) -> dict:
    """Убедиться, что адрес существует, если нет - создать."""
    address_client = AddressPage()

    # Ищем существующий адрес
    addr = address_client.find_by_external_id(base_url, token, external_id)

    if addr:
        return addr

    # Создаем новый адрес
    template = ADDRESS_TEMPLATES.get(external_id, {})

    payload = address_client.create_address_payload(
        title=template.get("title", external_id),
        externalId=external_id,
        addressString=template.get("addressString", "г Ижевск, ул Тестовая, д 1"),
        latitude=template.get("latitude", 56.85),
        longitude=template.get("longitude", 53.20),
        addressType=2,
        loadingType=1,
        statusFlowType="fullFlow"
    )

    address_id = address_client.create_or_update_address(base_url, token, payload)

    # Получаем созданный адрес
    return address_client.find_by_external_id(base_url, token, external_id)


def get_status_text(status_code: int) -> str:
    """Получить текстовое описание статуса."""
    if status_code == 12:
        return "Успешно создан"
    else:
        return f"Статус {status_code}"


@pytest.mark.parametrize("role", ["lke"], indirect=True)
def test_scenario_2_mass_orders(get_auth_token, role, client_id, producer_id, contract_id):
    """
    Тест массового создания заказов:
    1. Создание/получение 5 адресов
    2. Создание 20 грузомест
    3. Создание 5 рейсов по 4 грузоместа
    4. Мониторинг статусов рейсов в течение 10 минут
    """
    token = get_auth_token(role)["token"]

    # 1. Получить или создать 5 адресов
    external_ids = [
        "Izhevsk 81-870",
        "Izhevsk - Pastuhova - 37",
        "Izhevsk - Udmurtskaya - 12",
        "Izhevsk - Telegina - 47",
        "Izhevsk - Shkolnaya - 27"
    ]

    addresses = []
    for ext_id in external_ids:
        addr = ensure_address_exists(BASE_URL, token, ext_id)
        assert addr, f"Не удалось получить или создать адрес: {ext_id}"
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
            weight_kg=50,
            volume_m3=0.5
        )

        cargo_list.append({
            "id": resp["id"],
            "externalId": resp.get("externalId") or external_id_cp
        })

    # 3. Создать 5 рейсов по 4 грузоместа
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

    print(f"\n✅ Все рейсы успешно созданы!")
    print(f"Создано рейсов: {len(order_ids)}")
    print(f"ID рейсов: {order_ids}")

    # 4. Мониторинг деталей рейсов каждую минуту в течение 10 минут
    print(f"\n🔍 Начинаем мониторинг статусов рейсов...")

    for minute in range(1, 11):
        time.sleep(60)

        print(f"\n🔍 Минута {minute}/10:")

        for oid in order_ids:
            details = order_client.get_order_details(oid)
            status_code = details.get("state")
            status_text = get_status_text(status_code)
            cargo_places = details.get("transportOrder", {}).get("cargoPlaces", [])

            print(f"  Рейс {oid}: {status_text}, грузомест = {len(cargo_places)}")

    # Итоговый отчет
    print(f"\n" + "=" * 50)
    print(f"✅ ТЕСТ ЗАВЕРШЕН УСПЕШНО!")
    print(f"=" * 50)
    print(f"\n📊 ИТОГОВАЯ СТАТИСТИКА:")
    print(f"  - Создано адресов: {len(addresses)}")
    print(f"  - Создано грузомест: {len(cargo_list)}")
    print(f"  - Создано рейсов: {len(order_ids)}")
    print(f"  - ID созданных рейсов: {order_ids}")