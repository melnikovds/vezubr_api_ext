
import allure

import uuid
import time
from datetime import datetime, timedelta
from pages.cargo_delivery_page import CargoDeliveryClient
from pages.cargo_deliveries_create_page import CargoDeliveriesCreateClient
from pages.truck_deliveries_transport_appoint_page import TruckDeliveriesTransportAppointClient
from pages.cargo_deliveries_cancel_page import CargoDeliveriesCancelClient
from config.settings import BASE_URL, PRODUCER_ID


@allure.story("Отмена рейса после назначения водителя")
@allure.feature("Отмена рейса")
@allure.description("Тест отмены рейса после назначения водителя и проверки статуса canceled")
@allure.severity(allure.severity_level.CRITICAL)
def test_cancel_truck_delivery_after_driver_appointment(
        lkz_token,
        lkp_token,
        valid_addresses
):
    """
    Тест отмены рейса после назначения водителя:
    1. Создать заявку (LKZ)
    2. Принять заявку (LKP)
    3. Создать рейс (LKP)
    4. Назначить водителя (LKP)
    5. Отменить рейс (LKP)
    6. Проверить что рейс в статусе canceled через детали заявки
    """

    # Константы для теста
    INITIAL_DRIVER_ID = 5534
    INITIAL_VEHICLE_ID = 9710

    # Получаем адреса из фикстуры
    departure_point = valid_addresses["departure"]
    delivery_point = valid_addresses["delivery"]

    departure_id = departure_point["id"]
    delivery_id = delivery_point["id"]

    # ==================== 1. СОЗДАНИЕ ЗАЯВКИ ====================
    with allure.step("1. LKZ создает FTL заявку"):
        lkz_client = CargoDeliveryClient(BASE_URL, lkz_token)

        start_time = (datetime.now() + timedelta(days=1)).replace(microsecond=0).isoformat() + "Z"

        route = [
            lkz_client.create_route_point(
                point_id=departure_id,
                position=1,
                is_loading_work=True,
                is_unloading_work=False
            ),
            lkz_client.create_route_point(
                point_id=delivery_id,
                position=2,
                is_loading_work=False,
                is_unloading_work=True
            )
        ]

        client_identifier = f"CANCEL-TEST-{uuid.uuid4().hex[:8].upper()}"

        response = lkz_client.create_and_publish_delivery_request(
            delivery_type="auto",
            delivery_sub_type="ftl",
            body_types=[3, 4, 7, 8],
            vehicle_type_id=1,
            order_type=1,
            point_change_type=2,
            route=route,
            comment="Тест отмены рейса после назначения водителя",
            client_identifier=client_identifier,
            to_start_at_from=start_time,
            producer_id=PRODUCER_ID,
            rate=180000
        )

        request_id = response["id"]
        request_nr = response["requestNr"]

    time.sleep(1)

    # ==================== 2. ПРИНЯТИЕ ЗАЯВКИ ====================
    with allure.step("2. LKP принимает заявку"):
        lkp_client = CargoDeliveryClient(BASE_URL, lkp_token)
        lkp_client.take_delivery_request(request_id)

    time.sleep(1)

    # ==================== 3. СОЗДАНИЕ РЕЙСА ====================
    with allure.step("3. LKP создает рейс"):
        lkp_cargo_create = CargoDeliveriesCreateClient(BASE_URL, lkp_token)
        delivery_id_uuid = lkp_cargo_create.create_cargo_delivery(
            request_id=request_id,
            producer_id=PRODUCER_ID
        )

    time.sleep(1)

    # ==================== 4. НАЗНАЧЕНИЕ ВОДИТЕЛЯ ====================
    with allure.step("4. LKP назначает водителя"):
        lkp_transport_appoint = TruckDeliveriesTransportAppointClient(BASE_URL, lkp_token)
        lkp_transport_appoint.appoint_transport(
            truck_delivery_id=delivery_id_uuid,
            driver_id=INITIAL_DRIVER_ID,
            vehicle_id=INITIAL_VEHICLE_ID
        )

    time.sleep(1)

    # ==================== 5. ОТМЕНА РЕЙСА ====================
    with allure.step("5. LKP отменяет рейс"):
        lkp_cargo_cancel = CargoDeliveriesCancelClient(BASE_URL, lkp_token)
        lkp_cargo_cancel.cancel_cargo_delivery(delivery_id_uuid)

    time.sleep(2)

    # ==================== 6. ПРОВЕРКА СТАТУСА В ЗАЯВКЕ ====================
    with allure.step("6. Проверка статуса canceled в деталях заявки"):
        # Получаем детали заявки через LKP
        details = lkp_client.get_delivery_request_details(request_id)

        # Проверяем наличие outgoingEntities
        assert "outgoingEntities" in details

        outgoing_entities = details["outgoingEntities"]
        assert isinstance(outgoing_entities, list)
        assert len(outgoing_entities) > 0

        # Ищем наш рейс в outgoingEntities
        delivery_entity = None
        for entity in outgoing_entities:
            if entity.get("id") == delivery_id_uuid and entity.get("type") == "delivery":
                delivery_entity = entity
                break

        assert delivery_entity is not None, f"Рейс {delivery_id_uuid} не найден в outgoingEntities"

        # Проверяем статус
        actual_status = delivery_entity.get("status")
        expected_status = "canceled"

        assert actual_status == expected_status, \
            f"Рейс {delivery_id_uuid} имеет статус '{actual_status}', а ожидается '{expected_status}'"
