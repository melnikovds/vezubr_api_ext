import allure
import pytest
import uuid
import requests

from datetime import datetime, timedelta

from pages.cargo_delivery_page import CargoDeliveryClient
from pages.create_cargo_page import CargoPlaceClient
from pages.address_page import AddressPage
from pages.shipment_task_page import TaskCreate
from config.settings import BASE_URL


class TestCargoDeliveryWithTasks:
    """Тесты для создания FTL заявок с разными комбинациями ГМ и заданий"""

    @allure.story("Cargo Delivery Requests")
    @allure.feature("FTL заявки")
    @allure.description("Тест 1: FTL заявка с грузоместами (без заданий)")
    @pytest.mark.parametrize("role", ["lkz"])
    def test_1_ftl_with_cargo_places_only(self, role, valid_addresses, client_id, producer_id):
        """
        Тест 1: FTL заявка только с грузоместами (без shipment tasks)
        """
        token = valid_addresses["token"]

        # === Клиенты ===
        delivery_client = CargoDeliveryClient(BASE_URL, token)
        cargo_client = CargoPlaceClient(BASE_URL, token)

        # === 1. Создаем тестовые адреса ===
        with allure.step("Создание тестовых адресов"):
            departure_ext = f"CDR-TEST-{uuid.uuid4().hex[:8].upper()}"
            delivery_ext = f"CDR-TEST-{uuid.uuid4().hex[:8].upper()}"

            # Адрес отправки
            departure_payload = AddressPage.create_address_payload(
                externalId=departure_ext,
                title=f"Адрес отправки CDR {departure_ext}",
                addressString="г Ижевск, ул Дзержинского, д 61"
            )
            departure_id = AddressPage.create_or_update_address(BASE_URL, token, departure_payload)
            print(f"✅ Создан адрес отправки: ID={departure_id}, externalId={departure_ext}")

            # Адрес доставки
            delivery_payload = AddressPage.create_address_payload(
                externalId=delivery_ext,
                title=f"Адрес доставки CDR {delivery_ext}",
                addressString="г Ижевск, ул 9 Января, д 191"
            )
            delivery_id = AddressPage.create_or_update_address(BASE_URL, token, delivery_payload)
            print(f"✅ Создан адрес доставки: ID={delivery_id}, externalId={delivery_ext}")

        # === 2. Создаем грузоместо ===
        with allure.step("Создание грузоместа"):
            cp_external_id = f"CP-CDR-{uuid.uuid4().hex[:8].upper()}"
            cargo_resp = cargo_client.create_cargo_place(
                departure_external_id=departure_ext,
                delivery_external_id=delivery_ext,
                title="Груз для FTL заявки",
                external_id=cp_external_id,
                weight_kg=500,
                volume_m3=1.5
            )
            cargo_id = cargo_resp["id"]
            print(f"✅ Создано грузоместо: ID={cargo_id}")

        # === 3. Формируем маршрут ===
        with allure.step("Формирование маршрута"):
            route = [
                delivery_client.create_route_point(
                    point_id=departure_id,
                    position=1,
                    is_loading_work=True,
                    is_unloading_work=False,
                    required_arrive_at=(datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y %H:%M")
                ),
                delivery_client.create_route_point(
                    point_id=delivery_id,
                    position=2,
                    is_loading_work=False,
                    is_unloading_work=True
                )
            ]

        # === 4. Создаем cargoPlaces для payload ===
        with allure.step("Подготовка cargoPlaces"):
            cargo_places = [
                {
                    "id": cargo_id,
                    "departurePoint": departure_id,
                    "arrivalPoint": delivery_id
                }
            ]

        # === 5. Создаем и публикуем заявку с cargoPlaces ===
        with allure.step("Создание и публикация FTL заявки с грузоместами"):
            client_identifier = f"FTL-CARGO-ONLY-{uuid.uuid4().hex[:8].upper()}"

            response = delivery_client.create_and_publish_delivery_request_with_tasks(
                delivery_type="auto",
                delivery_sub_type="ftl",
                body_types=[3, 4, 7, 8],
                vehicle_type_id=1,
                order_type=1,
                point_change_type=2,
                route=route,
                comment="FTL заявка только с грузоместами (Тест 1)",
                client_identifier=client_identifier,
                producer_id=producer_id,
                rate=150000,
                cargo_places=cargo_places,
                shipment_tasks=None
            )

        # === 6. Проверки ===
        with allure.step("Проверка ответа"):
            assert "id" in response, "Ответ должен содержать 'id'"
            assert "requestNr" in response, "Ответ должен содержать 'requestNr'"

            request_id = response["id"]
            request_nr = response["requestNr"]

            print(f"✅ FTL заявка с грузоместами создана успешно:")
            print(f"   ID: {request_id}")
            print(f"   Номер: {request_nr}")

        # === 7. Allure attachments ===
        with allure.step("Детали теста"):
            allure.attach(
                f"""
                Тест 1: FTL с грузоместами (без заданий)
                - ID заявки: {request_id}
                - Номер заявки: {request_nr} 
                - clientIdentifier: {client_identifier}
                - Адрес отправки: {departure_id}
                - Адрес доставки: {delivery_id}
                - Грузоместо: {cargo_id}
                - Задания: НЕТ
                - Перевозчик: {producer_id}
                """,
                name="Детали теста 1",
                attachment_type=allure.attachment_type.TEXT
            )

    @allure.story("Cargo Delivery Requests")
    @allure.feature("FTL заявки")
    @allure.description("Тест 2: FTL заявка без грузомест и без заданий")
    @pytest.mark.parametrize("role", ["lkz"])
    def test_2_ftl_without_cargo_and_tasks(self, role, valid_addresses, client_id, producer_id):
        """
        Тест 2: FTL заявка без грузомест и без shipment tasks
        """
        token = valid_addresses["token"]

        # === Клиенты ===
        delivery_client = CargoDeliveryClient(BASE_URL, token)

        # === 1. Создаем тестовые адреса ===
        with allure.step("Создание тестовых адресов"):
            departure_ext = f"CDR-TEST-{uuid.uuid4().hex[:8].upper()}"
            delivery_ext = f"CDR-TEST-{uuid.uuid4().hex[:8].upper()}"

            # Адрес отправки
            departure_payload = AddressPage.create_address_payload(
                externalId=departure_ext,
                title=f"Адрес отправки CDR {departure_ext}",
                addressString="г Ижевск, ул Дзержинского, д 61"
            )
            departure_id = AddressPage.create_or_update_address(BASE_URL, token, departure_payload)
            print(f"✅ Создан адрес отправки: ID={departure_id}")

            # Адрес доставки
            delivery_payload = AddressPage.create_address_payload(
                externalId=delivery_ext,
                title=f"Адрес доставки CDR {delivery_ext}",
                addressString="г Ижевск, ул 9 Января, д 191"
            )
            delivery_id = AddressPage.create_or_update_address(BASE_URL, token, delivery_payload)
            print(f"✅ Создан адрес доставки: ID={delivery_id}")

        # === 2. Формируем маршрут ===
        with allure.step("Формирование маршрута"):
            route = [
                delivery_client.create_route_point(
                    point_id=departure_id,
                    position=1,
                    is_loading_work=True,
                    is_unloading_work=False,
                    required_arrive_at=(datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y %H:%M")
                ),
                delivery_client.create_route_point(
                    point_id=delivery_id,
                    position=2,
                    is_loading_work=False,
                    is_unloading_work=True
                )
            ]

        # === 3. Создаем заявку БЕЗ cargoPlaces и shipmentTasks ===
        with allure.step("Создание и публикация FTL заявки без грузомест"):
            client_identifier = f"FTL-NO-CARGO-{uuid.uuid4().hex[:8].upper()}"

            response = delivery_client.create_and_publish_delivery_request_with_tasks(
                delivery_type="auto",
                delivery_sub_type="ftl",
                body_types=[3, 4, 7, 8],
                vehicle_type_id=1,
                order_type=1,
                point_change_type=2,
                route=route,
                comment="FTL заявка без грузомест и заданий (Тест 2)",
                client_identifier=client_identifier,
                producer_id=producer_id,
                rate=120000,
                cargo_places=None,  # Без грузомест
                shipment_tasks=None  # Без заданий
            )

        # === 4. Проверки ===
        with allure.step("Проверка ответа"):
            assert "id" in response, "Ответ должен содержать 'id'"
            assert "requestNr" in response, "Ответ должен содержать 'requestNr'"

            request_id = response["id"]
            request_nr = response["requestNr"]

            print(f"✅ FTL заявка без грузомест создана успешно:")
            print(f"   ID: {request_id}")
            print(f"   Номер: {request_nr}")

        # === 5. Allure attachments ===
        with allure.step("Детали теста"):
            allure.attach(
                f"""
                Тест 2: FTL без грузомест и заданий
                - ID заявки: {request_id}
                - Номер заявки: {request_nr} 
                - clientIdentifier: {client_identifier}
                - Адрес отправки: {departure_id}
                - Адрес доставки: {delivery_id}
                - Грузоместа: НЕТ
                - Задания: НЕТ
                - Перевозчик: {producer_id}
                """,
                name="Детали теста 2",
                attachment_type=allure.attachment_type.TEXT
            )

    @allure.story("Cargo Delivery Requests")
    @allure.feature("FTL заявки")
    @allure.description("Тест 3: FTL заявка с заданием без грузомест")
    @pytest.mark.parametrize("role", ["lkz"])
    def test_3_ftl_with_task_without_cargo(self, role, valid_addresses, client_id, producer_id):
        """
        Тест 3: FTL заявка с shipment task но без грузомест
        """
        token = valid_addresses["token"]

        # === Клиенты ===
        delivery_client = CargoDeliveryClient(BASE_URL, token)

        # === 1. Создаем тестовые адреса ===
        with allure.step("Создание тестовых адресов"):
            departure_ext = f"CDR-TEST-{uuid.uuid4().hex[:8].upper()}"
            delivery_ext = f"CDR-TEST-{uuid.uuid4().hex[:8].upper()}"

            # Адрес отправки
            departure_payload = AddressPage.create_address_payload(
                externalId=departure_ext,
                title=f"Адрес отправки CDR {departure_ext}",
                addressString="г Ижевск, ул Дзержинского, д 61"
            )
            departure_id = AddressPage.create_or_update_address(BASE_URL, token, departure_payload)
            print(f"✅ Создан адрес отправки: ID={departure_id}")

            # Адрес доставки
            delivery_payload = AddressPage.create_address_payload(
                externalId=delivery_ext,
                title=f"Адрес доставки CDR {delivery_ext}",
                addressString="г Ижевск, ул 9 Января, д 191"
            )
            delivery_id = AddressPage.create_or_update_address(BASE_URL, token, delivery_payload)
            print(f"✅ Создан адрес доставки: ID={delivery_id}")

        # === 2. Создаем задание (shipment task) через API ===
        with allure.step("Создание задания через API"):
            task_payload = TaskCreate.create_task_payload(
                departurePoint={"id": departure_id},
                arrivalPoint={"id": delivery_id}
            )

            # Создаем задание
            headers = {"Authorization": token}
            task_response = requests.post(
                f"{BASE_URL}/shipment/tasks/create",
                headers=headers,
                json=task_payload
            )
            assert task_response.status_code == 200, f"Ошибка создания задания: {task_response.text}"

            created_task = task_response.json()
            shipment_task_id = created_task["id"]
            print(f"✅ Создано задание: ID={shipment_task_id}")

        # === 3. Формируем маршрут ===
        with allure.step("Формирование маршрута"):
            route = [
                delivery_client.create_route_point(
                    point_id=departure_id,
                    position=1,
                    is_loading_work=True,
                    is_unloading_work=False,
                    required_arrive_at=(datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y %H:%M")
                ),
                delivery_client.create_route_point(
                    point_id=delivery_id,
                    position=2,
                    is_loading_work=False,
                    is_unloading_work=True
                )
            ]

        # === 4. Создаем shipment tasks для payload ===
        with allure.step("Подготовка shipment tasks"):
            shipment_tasks = [
                {
                    "id": shipment_task_id,  # Используем ID созданного задания
                    "departurePoint": departure_id,
                    "arrivalPoint": delivery_id
                }
            ]

        # === 5. Создаем заявку с shipmentTasks но БЕЗ cargoPlaces ===
        with allure.step("Создание и публикация FTL заявки с заданием"):
            client_identifier = f"FTL-TASK-ONLY-{uuid.uuid4().hex[:8].upper()}"

            response = delivery_client.create_and_publish_delivery_request_with_tasks(
                delivery_type="auto",
                delivery_sub_type="ftl",
                body_types=[3, 4, 7, 8],
                vehicle_type_id=1,
                order_type=1,
                point_change_type=2,
                route=route,
                comment="FTL заявка с заданием без груза (Тест 3)",
                client_identifier=client_identifier,
                producer_id=producer_id,
                rate=130000,
                shipment_tasks=shipment_tasks,  # ТОЛЬКО задания
                cargo_places=None  # Без грузомест
            )

        # === 6. Проверки ===
        with allure.step("Проверка ответа"):
            assert "id" in response, "Ответ должен содержать 'id'"
            assert "requestNr" in response, "Ответ должен содержать 'requestNr'"

            request_id = response["id"]
            request_nr = response["requestNr"]

            print(f"✅ FTL заявка с заданием создана успешно:")
            print(f"   ID: {request_id}")
            print(f"   Номер: {request_nr}")
            print(f"   Task ID: {shipment_task_id}")

        # === 7. Allure attachments ===
        with allure.step("Детали теста"):
            allure.attach(
                f"""
                    Тест 3: FTL с заданием но без грузомест
                    - ID заявки: {request_id}
                    - Номер заявки: {request_nr} 
                    - clientIdentifier: {client_identifier}
                    - Адрес отправки: {departure_id}
                    - Адрес доставки: {delivery_id}
                    - Task ID: {shipment_task_id} (создано через API)
                    - Грузоместа: НЕТ
                    - Перевозчик: {producer_id}
                    """,
                name="Детали теста 3",
                attachment_type=allure.attachment_type.TEXT
            )

    @allure.story("Cargo Delivery Requests")
    @allure.feature("FTL заявки")
    @allure.description("Тест 4: FTL заявка с заданием и грузоместами")
    @pytest.mark.parametrize("role", ["lkz"])
    def test_4_ftl_with_task_and_cargo(self, role, valid_addresses, client_id, producer_id):
        """
     Тест 4: FTL заявка с shipment task и привязанными грузоместами
        """
        token = valid_addresses["token"]

        # === Клиенты ===
        delivery_client = CargoDeliveryClient(BASE_URL, token)
        cargo_client = CargoPlaceClient(BASE_URL, token)

        # === 1. Создаем тестовые адреса ===
        with allure.step("Создание тестовых адреса"):
            departure_ext = f"CDR-TEST-{uuid.uuid4().hex[:8].upper()}"
            delivery_ext = f"CDR-TEST-{uuid.uuid4().hex[:8].upper()}"

            # Адрес отправки
            departure_payload = AddressPage.create_address_payload(
                externalId=departure_ext,
                title=f"Адрес отправки CDR {departure_ext}",
                addressString="г Ижевск, ул Дзержинского, д 61"
            )
            departure_id = AddressPage.create_or_update_address(BASE_URL, token, departure_payload)
            print(f"✅ Создан адрес отправки: ID={departure_id}")

            # Адрес доставки
            delivery_payload = AddressPage.create_address_payload(
                externalId=delivery_ext,
                title=f"Адрес доставки CDR {delivery_ext}",
                addressString="г Ижевск, ул 9 Января, д 191"
            )
            delivery_id = AddressPage.create_or_update_address(BASE_URL, token, delivery_payload)
            print(f"✅ Создан адрес доставки: ID={delivery_id}")

        # === 2. Создаем задание (shipment task) через API ===
        with allure.step("Создание задания через API"):
            task_payload = TaskCreate.create_task_payload(
                departurePoint={"id": departure_id},
                arrivalPoint={"id": delivery_id}
            )

            # Создаем задание
            headers = {"Authorization": token}
            task_response = requests.post(
                f"{BASE_URL}/shipment/tasks/create",
                headers=headers,
                json=task_payload
            )
            assert task_response.status_code == 200, f"Ошибка создания задания: {task_response.text}"

            created_task = task_response.json()
            shipment_task_id = created_task["id"]
            print(f"✅ Создано задание: ID={shipment_task_id}")

        # === 3. Создаем грузоместо ===
        with allure.step("Создание грузоместа"):
            cp_external_id = f"CP-CDR-{uuid.uuid4().hex[:8].upper()}"
            cargo_resp = cargo_client.create_cargo_place(
                departure_external_id=departure_ext,
                delivery_external_id=delivery_ext,
                title="Груз для FTL заявки с заданием",
                external_id=cp_external_id,
                weight_kg=500,
                volume_m3=1.5
            )
            cargo_id = cargo_resp["id"]
            print(f"✅ Создано грузоместо: ID={cargo_id}")

        # === 4. Формируем маршрут ===
        with allure.step("Формирование маршрута"):
            route = [
                delivery_client.create_route_point(
                    point_id=departure_id,
                    position=1,
                    is_loading_work=True,
                    is_unloading_work=False,
                    required_arrive_at=(datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y %H:%M")
                ),
                delivery_client.create_route_point(
                    point_id=delivery_id,
                    position=2,
                    is_loading_work=False,
                    is_unloading_work=True
                )
            ]

        # === 5. Создаем shipment tasks для payload ===
        with allure.step("Подготовка shipment tasks"):
            shipment_tasks = [
                {
                    "id": shipment_task_id,  # Используем ID созданного задания
                    "departurePoint": departure_id,
                    "arrivalPoint": delivery_id
                }
            ]

        # === 6. Создаем cargoPlaces с привязкой к task ===
        with allure.step("Подготовка cargoPlaces с привязкой к заданию"):
            cargo_places = [
                {
                    "id": cargo_id,
                    "departurePoint": departure_id,
                    "arrivalPoint": delivery_id,
                    "shipmentTaskId": shipment_task_id  # Привязываем ГМ к созданному заданию
                }
            ]

        # === 7. Создаем заявку с shipmentTasks и cargoPlaces ===
        with allure.step("Создание и публикация FTL заявки с заданием и грузом"):
            client_identifier = f"FTL-TASK-CARGO-{uuid.uuid4().hex[:8].upper()}"

            response = delivery_client.create_and_publish_delivery_request_with_tasks(
                delivery_type="auto",
                delivery_sub_type="ftl",
                body_types=[3, 4, 7, 8],
                vehicle_type_id=1,
                order_type=1,
                point_change_type=2,
                route=route,
                comment="FTL заявка с заданием и грузом (Тест 4)",
                client_identifier=client_identifier,
                producer_id=producer_id,
                rate=160000,
                shipment_tasks=shipment_tasks,
                cargo_places=cargo_places
            )

        # === 8. Проверки ===
        with allure.step("Проверка ответа"):
            assert "id" in response, "Ответ должен содержать 'id'"
            assert "requestNr" in response, "Ответ должен содержать 'requestNr'"

            request_id = response["id"]
            request_nr = response["requestNr"]

            print(f"✅ FTL заявка с заданием и грузом создана успешно:")
            print(f"   ID: {request_id}")
            print(f"   Номер: {request_nr}")
            print(f"   Task ID: {shipment_task_id}")
            print(f"   Cargo ID: {cargo_id}")

        # === 9. Allure attachments ===
        with allure.step("Детали теста"):
            allure.attach(
                f"""
                    Тест 4: FTL с заданием и грузоместами
                    - ID заявки: {request_id}
                    - Номер заявки: {request_nr} 
                    - clientIdentifier: {client_identifier}
                    - Адрес отправки: {departure_id}
                    - Адрес доставки: {delivery_id}
                    - Task ID: {shipment_task_id} (создано через API)
                    - Cargo ID: {cargo_id} (привязан к task)
                    - Перевозчик: {producer_id}
                    """,
                name="Детали теста 4",
                attachment_type=allure.attachment_type.TEXT
            )
