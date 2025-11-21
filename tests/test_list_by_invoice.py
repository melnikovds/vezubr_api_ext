import allure
import pytest
import json
import uuid
import random
import requests

from pages.create_cargo_page import CargoPlaceClient
from pages.create_order_page import TransportRequestClient
from pages.list_by_invoice_page import ListByInvoiceClient
from config.settings import BASE_URL


CARGO_STATUSES = [
    "new", "waiting_for_sending", "sent", "handed", "handover",
    "not_accepted", "accepted", "received", "not_delivered", "lost"
]


@allure.story("Smoke test")
@allure.feature("Грузоместа")
@allure.description(
    "Создание ГМ со случайным статусом → создание заявки с invoiceNumber "
    "→ проверка статуса через /cargo-place/list-by-invoice"
)
@pytest.mark.parametrize("role", ["lkz"])
def test_list_cargo_place_by_invoice(role, valid_addresses, client_id, producer_id, contract_id):
    import time

    # === Извлекаем данные из фикстуры ===
    role = valid_addresses["role"]
    token = valid_addresses["token"]
    dep_addr = valid_addresses["departure"]
    del_addr = valid_addresses["delivery"]

    dep_ext = dep_addr["externalId"]
    del_ext = del_addr["externalId"]

    # === Клиенты ===
    cargo_client = CargoPlaceClient(BASE_URL, token)
    order_client = TransportRequestClient(BASE_URL, token)
    checker = ListByInvoiceClient(BASE_URL, token)

    # === Подготовка данных ===
    # После создания заявки статус будет waiting_for_sending
    cargo_status = "waiting_for_sending"
    external_id_cp = f"CP-TEST-{uuid.uuid4().hex[:8].upper()}"
    invoice_number = f"INV-{uuid.uuid4().hex[:8].upper()}"

    print(f"🔧 Настройки теста:")
    print(f"   role: {role}")
    print(f"   client_id: {client_id}")
    print(f"   producer_id: {producer_id}")
    print(f"   contract_id: {contract_id}")
    print(f"   external_id_cp: {external_id_cp}")
    print(f"   invoice_number: {invoice_number}")

    # === Шаг 1: Создание грузоместа ===
    with allure.step(f"Создание грузоместа"):
        cargo_resp = cargo_client.create_cargo_place(
            departure_external_id=dep_ext,
            delivery_external_id=del_ext,
            title=f"Test {cargo_status}",
            external_id=external_id_cp,
            weight_kg=50,
            volume_m3=0.5,
            invoice_number=invoice_number
        )

        print(f"🔍 Полный ответ создания грузоместа: {cargo_resp}")

        cargo_id = cargo_resp["id"]
        actual_external_id = cargo_resp.get("externalId") or external_id_cp
        print(f"✅ Создано грузоместо: ID={cargo_id}, externalId={actual_external_id}")

    # === Шаг 2: Создание заявки ===
    with allure.step("Формирование спецификации грузоместа"):
        cargo_spec = {
            "cargoPlaceId": cargo_id,
            "externalId": actual_external_id,
            "departurePointPosition": 1,
            "arrivalPointPosition": 2,
        }

    with allure.step("Создание транспортной заявки"):
        print(f"🔍 Создание заявки с order_identifier: {invoice_number}")

        order_response = order_client.create_transport_request(
            addresses=[dep_addr, del_addr],
            cargo_place_specs=[cargo_spec],
            client_id=client_id,
            producer_id=producer_id,
            contract_id=contract_id,
            order_identifier=invoice_number,
            inner_comment=f"Тест статуса (роль {role})",
        )

        assert "id" in order_response, f"Заявка не создана: {order_response}"
        order_id = order_response.get('id')
        print(f"✅ Создана заявка: ID={order_id}, invoice={invoice_number}")

    # === Шаг 3: Проверка через list-by-invoice ===
    with allure.step(f"Запрос /list-by-invoice для invoice={invoice_number}"):
        time.sleep(5)

        try:
            response_data = checker.list_by_invoice(invoice_number)
            print(f"🔍 Ответ /list-by-invoice:")
            print(f"   invoiceNumber: {response_data.get('invoiceNumber')}")
            print(f"   cargoPlaces count: {len(response_data.get('cargoPlaces', []))}")

            if response_data.get('cargoPlaces'):
                for cp in response_data['cargoPlaces']:
                    print(f"   - cargoPlaceId: {cp.get('cargoPlaceId')}, barcode: {cp.get('barcode')}, status: {cp.get('status')}")

            # Ищем по cargoPlaceId
            cargo_place = checker.get_cargo_place_by_id(invoice_number, cargo_id)
            print(f"✅ УСПЕХ: Найдено грузоместо в ответе!")

        except AssertionError as e:
            print(f"❌ Грузоместо не найдено в ответе: {e}")
            raise

    # === Assert ===
    with allure.step("Проверка статуса и метаданных"):
        assert cargo_place["cargoPlaceId"] == cargo_id
        assert cargo_place["status"] == cargo_status, \
            f"Ожидался статус '{cargo_status}', получен '{cargo_place['status']}'"
        assert "statusAddress" in cargo_place
        assert "statusUpdateAt" in cargo_place

    # === Allure Attachments ===
    with allure.step("Детали запроса и ответа"):
        allure.attach(
            json.dumps({
                "role": role,
                "client_id": client_id,
                "producer_id": producer_id,
                "contract_id": contract_id,
                "invoiceNumber": invoice_number,
                "cargoPlaceId": cargo_id,
                "externalId": actual_external_id,
                "departureExternalId": dep_ext,
                "deliveryExternalId": del_ext,
                "cargo_status": cargo_status,
                "actual_status": cargo_place["status"]
            }, indent=2, ensure_ascii=False),
            name="Контекст теста",
            attachment_type=allure.attachment_type.JSON
        )

        allure.attach(
            json.dumps(cargo_place, indent=2, ensure_ascii=False),
            name="Результат /list-by-invoice",
            attachment_type=allure.attachment_type.JSON
        )