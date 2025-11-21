import allure
import pytest
import uuid
import time
import json
import requests
from pages.create_cargo_page import CargoPlaceClient
from pages.create_order_page import TransportRequestClient
from pages.replace_planned_pairs_page import ReplacePlannedPairsClient
from config.settings import BASE_URL


@allure.story("Diagnostic test")
@allure.feature("Диагностика замены ГМ")
@allure.description("Диагностический тест для выявления проблем с заменой ГМ")
@pytest.mark.parametrize("role", ["lkz"])
def test_diagnostic_replace_issue(role, valid_addresses, client_id, producer_id, contract_id):
    """
    Диагностический тест для выявления проблемы с заменой ГМ
    """
    print("🔍 ЗАПУСК ДИАГНОСТИЧЕСКОГО ТЕСТА...")

    token = valid_addresses["token"]
    dep_addr = valid_addresses["departure"]
    del_addr = valid_addresses["delivery"]

    # Клиенты
    cargo_client = CargoPlaceClient(BASE_URL, token)
    order_client = TransportRequestClient(BASE_URL, token)
    replace_client = ReplacePlannedPairsClient(BASE_URL, token)

    # 1. Проверяем доступность эндпоинта
    print("1. Проверка эндпоинта...")
    availability = replace_client.check_endpoint_availability()
    assert availability["available"], "Эндпоинт недоступен"

    # 2. Создаем ОДНО плановое ГМ
    print("2. Создание тестовых данных...")
    planned_resp = cargo_client.create_cargo_place(
        departure_external_id=dep_addr["externalId"],
        delivery_external_id=del_addr["externalId"],
        title="Диагностическое плановое ГМ",
        external_id=f"DIAG-PLAN-{uuid.uuid4().hex[:6].upper()}",
        weight_kg=50,
        volume_m3=0.5
    )
    planned_id = planned_resp["id"]
    print(f"   ✅ Плановое ГМ: ID={planned_id}")

    # 3. Создаем ОДНО фактическое ГМ
    actual_resp = cargo_client.create_cargo_place(
        departure_external_id=dep_addr["externalId"],
        delivery_external_id=del_addr["externalId"],
        title="Диагностическое фактическое ГМ",
        external_id=f"DIAG-ACTUAL-{uuid.uuid4().hex[:6].upper()}",
        weight_kg=50,
        volume_m3=0.5,
        invoice_number=f"DIAG-INV-{uuid.uuid4().hex[:8].upper()}"
    )
    actual_id = actual_resp["id"]
    print(f"   ✅ Фактическое ГМ: ID={actual_id}")

    # 4. Проверяем что ГМ существуют через прямой запрос
    print("3. Проверка существования ГМ...")
    try:
        # Пробуем получить информацию о ГМ (если такой эндпоинт есть)
        response = requests.get(
            f"{BASE_URL}/cargo-place/{planned_id}",
            headers={"Authorization": token},
            timeout=5
        )
        if response.status_code == 200:
            print(f"   ✅ Плановое ГМ {planned_id} существует в системе")
        else:
            print(f"   ⚠️ Не удалось проверить плановое ГМ: {response.status_code}")
    except:
        print("   ℹ️ Эндпоинт проверки ГМ недоступен")

    # 5. Создаем максимально простую заявку
    print("4. Создание заявки...")
    order_response = order_client.create_transport_request(
        addresses=[dep_addr, del_addr],
        cargo_place_specs=[{
            "cargoPlaceId": planned_id,
            "externalId": planned_resp.get("externalId"),
            "departurePointPosition": 1,
            "arrivalPointPosition": 2,
        }],
        client_id=client_id,
        producer_id=producer_id,
        contract_id=contract_id,
        order_identifier=f"DIAG-ORDER-{uuid.uuid4().hex[:8].upper()}",
        inner_comment="Диагностическая заявка",
    )
    order_id = order_response.get('id')
    print(f"   ✅ Заявка создана: ID={order_id}")

    # 6. Детально анализируем заявку ДО замены
    print("5. Анализ заявки ДО замены...")
    time.sleep(3)
    order_details = order_client.get_order_details(order_id)

    print("   📊 Детали заявки:")
    print(f"      - ID заявки: {order_details.get('id')}")
    print(f"      - Статус: {order_details.get('state')}")
    print(f"      - OrderIdentifier: {order_details.get('transportOrder', {}).get('orderIdentifier')}")

    transport_order = order_details.get('transportOrder', {})
    cargo_places = transport_order.get('cargoPlaces', [])
    print(f"      - Грузомест в заявке: {len(cargo_places)}")

    for i, cp in enumerate(cargo_places):
        print(f"      ГМ #{i + 1}:")
        print(f"        - ID: {cp.get('id')}")
        print(f"        - externalId: {cp.get('externalId')}")
        print(f"        - status: {cp.get('status')}")
        print(f"        - cargoPlaceId: {cp.get('cargoPlaceId')}")  # Это ключевое поле!

    # 7. Пробуем замену
    print("6. Попытка замены...")
    try:
        result = replace_client.replace_by_ids(planned_id, actual_id, is_strict=False)
        print(f"   ✅ Замена выполнена: {result}")

        # 8. Проверяем заявку ПОСЛЕ замены
        print("7. Анализ заявки ПОСЛЕ замены...")
        time.sleep(3)
        order_details_after = order_client.get_order_details(order_id)
        cargo_places_after = order_details_after.get('transportOrder', {}).get('cargoPlaces', [])

        print(f"   📊 Грузомест после замены: {len(cargo_places_after)}")
        for i, cp in enumerate(cargo_places_after):
            print(f"      ГМ #{i + 1} после замены:")
            print(f"        - ID: {cp.get('id')}")
            print(f"        - externalId: {cp.get('externalId')}")
            print(f"        - status: {cp.get('status')}")
            print(f"        - cargoPlaceId: {cp.get('cargoPlaceId')}")

    except Exception as e:
        print(f"   ❌ Ошибка замены: {e}")

    # 9. Диагностика проблемы
    print("8. Диагностика проблемы...")
    if cargo_places and cargo_places[0].get('cargoPlaceId') is None:
        print("   🔴 ПРОБЛЕМА: cargoPlaceId = None")
        print("   💡 Возможные причины:")
        print("      - Грузоместа не привязываются к заявке при создании")
        print("      - Проблема в методе create_transport_request")
        print("      - Заявка создается без реальной привязки к ГМ")
    elif cargo_places and cargo_places[0].get('cargoPlaceId') == planned_id:
        print("   🟢 cargoPlaceId корректно привязан")
    else:
        print(f"   🟡 cargoPlaceId: {cargo_places[0].get('cargoPlaceId') if cargo_places else 'N/A'}")

    # 10. Сохраняем диагностическую информацию
    with allure.step("Диагностическая информация"):
        allure.attach(
            json.dumps({
                "planned_id": planned_id,
                "actual_id": actual_id,
                "order_id": order_id,
                "cargo_places_before": cargo_places,
                "cargo_places_after": cargo_places_after if 'cargo_places_after' in locals() else [],
                "problem_identified": "cargoPlaceId is None" if cargo_places and cargo_places[0].get(
                    'cargoPlaceId') is None else "unknown"
            }, indent=2, ensure_ascii=False),
            name="Диагностика проблемы замены",
            attachment_type=allure.attachment_type.JSON
        )

    print("🏁 ДИАГНОСТИКА ЗАВЕРШЕНА")


@allure.story("Quick test")
@allure.feature("Быстрая проверка замены")
@allure.description("Быстрая проверка на существующих данных")
@pytest.mark.parametrize("role", ["lkz"])
def test_quick_replace_check(role, valid_addresses):
    """
    Быстрая проверка на существующей заявке с реальными ГМ
    """
    token = valid_addresses["token"]
    replace_client = ReplacePlannedPairsClient(BASE_URL, token)

    # Используем существующие ID из предыдущих тестов
    existing_planned_id = 45843  # Из предыдущего теста
    existing_actual_id = 45845  # Из предыдущего теста

    print("🔍 Быстрая проверка на существующих данных...")

    try:
        result = replace_client.replace_by_ids(existing_planned_id, existing_actual_id, is_strict=False)
        print(f"✅ Замена выполнена: {result}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")