import time
import pytest
import requests
from pages.create_cargo_page import CargoPlaceClient
from pages.create_order_page import TransportRequestClient
from config.settings import BASE_URL


@pytest.mark.parametrize("role", ["lke"], indirect=True)
def test_scenario_2_quick(get_auth_token, role, client_id, producer_id, contract_id):
    """Быстрый работающий тест"""

    token = get_auth_token(role)["token"]
    headers = {"Authorization": token}

    print(f"\n=== Быстрый тест scenario_2 ===")

    # 1. Создаем 2 простых адреса
    addresses = []

    for i in range(2):
        ext_id = f"QUICK-ADDR-{i}-{int(time.time())}"

        payload = {
            "addressString": f"г Ижевск, Быстрая улица {i + 1}, д {i + 10}",
            "title": f"Быстрый адрес {i + 1}",
            "timezone": "Europe/Samara",
            "externalId": ext_id,
            "status": True,
            "latitude": 56.85 + (i * 0.01),
            "longitude": 53.20 + (i * 0.01),
            "cityName": "Ижевск",
            "addressType": 2,
            "loadingType": 1,
            "liftingCapacityMax": 3000,
            "vicinityRadius": 10000,
            "comment": "Адрес для быстрого теста",
            "statusFlowType": "fullFlow",
            # Минимальный набор обязательных полей
            "contacts": [{"contact": None, "email": None, "phone": None}],
            "attachedFiles": [],
        }

        response = requests.post(
            f"{BASE_URL}/contractor-point/update",
            headers=headers,
            json=payload
        )

        if response.status_code == 200:
            address_id = response.json().get("id")
            print(f"✅ Создан адрес {i + 1}: ID={address_id}")

            addresses.append({
                "id": address_id,
                "externalId": ext_id,
                "addressString": payload["addressString"],
                "latitude": payload["latitude"],
                "longitude": payload["longitude"],
                "cityName": payload["cityName"],
                "timezone": payload["timezone"],
                "addressType": payload["addressType"],
                "loadingType": payload["loadingType"],
                "statusFlowType": payload["statusFlowType"],
                "title": payload["title"]
            })

    # Ждем
    time.sleep(3)

    # 2. Создаем 1 грузоместо
    cargo_client = CargoPlaceClient(BASE_URL, token)

    try:
        resp = cargo_client.create_cargo_place(
            departure_external_id=addresses[0]["externalId"],
            delivery_external_id=addresses[1]["externalId"],
            title="Тестовый груз",
            external_id=f"CP-QUICK-{int(time.time())}",
            weight_kg=10,
            volume_m3=0.1
        )

        print(f"✅ Создано грузоместо: ID={resp['id']}")

        # 3. Создаем рейс
        order_client = TransportRequestClient(BASE_URL, token)

        cargo_specs = [{
            "cargoPlaceId": resp["id"],
            "externalId": resp.get("externalId"),
            "departurePointPosition": 1,
            "arrivalPointPosition": 2
        }]

        order_id = order_client.create_transport_request(
            addresses=addresses,
            cargo_place_specs=cargo_specs,
            client_id=client_id,
            producer_id=producer_id,
            contract_id=contract_id,
            order_identifier=f"QUICK-TEST-{int(time.time())}"
        )["id"]

        print(f"✅ Рейс создан: ID={order_id}")

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

    print(f"\n✅ Тест завершен!")