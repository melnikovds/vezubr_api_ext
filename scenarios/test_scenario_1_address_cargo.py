from datetime import datetime

import pytest
from pages.address_page import AddressPage
from pages.create_cargo_page import CargoPlaceClient
from config.settings import BASE_URL

# Используем ТОЛЬКО существующие externalId
EXISTING_EXTERNAL_IDS = [
    "Izhevsk 81-870",
    "Izhevsk - Pastuhova - 37",
    "Izhevsk - Udmurtskaya - 12",
    "Izhevsk - Telegina - 47",
    "Izhevsk - Shkolnaya - 27"
]


def test_scenario_1(get_auth_token):
    token = get_auth_token("lke")["token"]

    # Создаём НОВЫЙ адрес отправки
    departure_ext = "Izhevsk-SCENARIO-1"

    # Выбираем СУЩЕСТВУЮЩИЙ адрес доставки
    delivery_ext = EXISTING_EXTERNAL_IDS[1]  # например, "Izhevsk - Pastuhova - 37"

    # 1. Найти или создать адрес отправки
    address = AddressPage.find_by_external_id(BASE_URL, token, departure_ext)
    if address:
        address["title"] = f"Обновлён {datetime.now().isoformat()}"
        AddressPage.create_or_update_address(BASE_URL, token, address)
    else:
        payload = AddressPage.create_address_payload(externalId=departure_ext)
        AddressPage.create_or_update_address(BASE_URL, token, payload)

    # 2. Создать грузоместо
    cargo_client = CargoPlaceClient(BASE_URL, token)
    cargo_resp = cargo_client.create_cargo_place(
        departure_external_id=departure_ext,
        delivery_external_id=delivery_ext  # ← теперь СУЩЕСТВУЮЩИЙ
    )
    assert cargo_resp["id"] > 0
    print(f"\n✅ Сценарий 1: грузоместо создано, ID={cargo_resp['id']}")