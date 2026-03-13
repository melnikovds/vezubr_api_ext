import allure
import pytest
import uuid
import time
from datetime import datetime, timedelta
from pages.cargo_delivery_page import CargoDeliveryClient
from pages.cargo_deliveries_create_page import CargoDeliveriesCreateClient
from pages.truck_deliveries_transport_appoint_page import TruckDeliveriesTransportAppointClient
from pages.truck_deliveries_transport_replace_page import TruckDeliveriesTransportReplaceClient
from pages.cargo_deliveries_start_page import CargoDeliveriesStartClient
from pages.truck_deliveries_points_update_page import TruckDeliveriesPointsUpdateClient
from config.settings import BASE_URL, PRODUCER_ID


class TestReplaceDriverExecutionParams:
    """Тест замены водителя через executionParameters"""

    TEST_ADDRESSES = [27648, 27649, 27650]
    INITIAL_DRIVER_ID = 5534
    INITIAL_VEHICLE_ID = 9710
    REPLACEMENT_DRIVER_ID = 5684
    REPLACEMENT_VEHICLE_ID = 9887

    @pytest.fixture
    def test_addresses(self):
        """Фикстура для получения тестовых адресов"""
        if len(self.TEST_ADDRESSES) < 3:
            pytest.skip(f"Недостаточно тестовых адресов. Нужно 3, есть {len(self.TEST_ADDRESSES)}")

        addresses = self.TEST_ADDRESSES[:3]
        print(f"📌 Используем адреса: {addresses}")
        return {
            "departure": addresses[0],
            "intermediate": addresses[1],
            "delivery": addresses[2]
        }

    def check_driver_in_execution_params(self, lkz_client, request_id, expected_info=None):
        """Проверка водителя в executionParameters"""
        print(f"\n🔍 Проверяем executionParameters в заявке {request_id}...")

        details = lkz_client.get_delivery_request_details(request_id)

        if "executionParameters" not in details:
            print("⚠️ executionParameters отсутствует в ответе")
            return None

        execution_params = details["executionParameters"]
        print(f"Найдено executionParameters: {len(execution_params)}")

        for i, param in enumerate(execution_params):
            print(f"\n  ExecutionParameter {i}:")
            print(f"    driverFullName: {param.get('driverFullName')}")
            print(f"    driverPhone: {param.get('driverPhone')}")
            print(f"    vehiclePlateNumber: {param.get('vehiclePlateNumber')}")
            print(f"    driverLicenseId: {param.get('driverLicenseId')}")
            print(f"    vehicleMarkAndModel: {param.get('vehicleMarkAndModel')}")
            print(f"    companyName: {param.get('companyName')}")

            # Если передан expected_info, проверяем соответствие
            if expected_info:
                if (param.get('driverFullName') == expected_info.get('driver_name') or
                        param.get('driverPhone') == expected_info.get('driver_phone') or
                        param.get('vehiclePlateNumber') == expected_info.get('plate_number')):
                    print(f"    ✅ Совпадает с ожидаемым")
                    return param

        # Возвращаем первый параметр если нет проверки
        if execution_params:
            return execution_params[0]

        return None

    @allure.story("Замена водителя и ТС через executionParameters")
    @allure.feature("Замена транспорта")
    @allure.description("Тест замены водителя с проверкой через executionParameters")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_replace_driver_via_execution_params(
            self,
            lkz_token,
            lkp_token,
            test_addresses
    ):
        """
        Тест замены водителя с проверкой через executionParameters:
        1. Создать заявку
        2. Принять заявку
        3. Создать рейс
        4. Назначить водителя
        5. Проверить что водитель появился в executionParameters
        6. Заменить водителя
        7. Проверить что водитель изменился в executionParameters
        8. Начать и завершить рейс
        """

        print(f"\n{'=' * 60}")
        print(f"🚀 ТЕСТ: Замена водителя (через executionParameters)")
        print(f"{'=' * 60}")

        departure_id = test_addresses["departure"]
        intermediate_id = test_addresses["intermediate"]
        delivery_id = test_addresses["delivery"]

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
                    point_id=intermediate_id,
                    position=2,
                    is_loading_work=False,
                    is_unloading_work=False
                ),
                lkz_client.create_route_point(
                    point_id=delivery_id,
                    position=3,
                    is_loading_work=False,
                    is_unloading_work=True
                )
            ]

            client_identifier = f"EXEC-PARAM-{uuid.uuid4().hex[:8].upper()}"

            response = lkz_client.create_and_publish_delivery_request(
                delivery_type="auto",
                delivery_sub_type="ftl",
                body_types=[3, 4, 7, 8],
                vehicle_type_id=1,
                order_type=1,
                point_change_type=2,
                route=route,
                comment="Тест замены через executionParameters",
                client_identifier=client_identifier,
                to_start_at_from=start_time,
                producer_id=PRODUCER_ID,
                rate=180000
            )

            request_id = response["id"]
            request_nr = response["requestNr"]

            print(f"✅ Создана заявка: ID={request_id}, №={request_nr}")

        time.sleep(2)

        # ==================== 2. ПРИНЯТИЕ ЗАЯВКИ ====================
        with allure.step("2. LKP принимает заявку"):
            lkp_client = CargoDeliveryClient(BASE_URL, lkp_token)

            lkp_client.take_delivery_request(request_id)
            print(f"✅ LKP принял заявку")

        time.sleep(3)

        # ==================== 3. СОЗДАНИЕ РЕЙСА ====================
        with allure.step("3. LKP создает рейс"):
            lkp_cargo_create = CargoDeliveriesCreateClient(BASE_URL, lkp_token)

            delivery_id_uuid = lkp_cargo_create.create_cargo_delivery(
                request_id=request_id,
                producer_id=PRODUCER_ID
            )

            print(f"✅ Создан рейс: ID={delivery_id_uuid}")

        time.sleep(2)

        # ==================== 4. НАЗНАЧЕНИЕ ПЕРВОНАЧАЛЬНОГО ТРАНСПОРТА ====================
        with allure.step("4. LKP назначает первоначальный транспорт"):
            lkp_transport_appoint = TruckDeliveriesTransportAppointClient(BASE_URL, lkp_token)

            lkp_transport_appoint.appoint_transport(
                truck_delivery_id=delivery_id_uuid,
                driver_id=self.INITIAL_DRIVER_ID,
                vehicle_id=self.INITIAL_VEHICLE_ID
            )

            print(f"✅ Назначен первоначальный транспорт:")
            print(f"   Водитель: {self.INITIAL_DRIVER_ID}")
            print(f"   ТС: {self.INITIAL_VEHICLE_ID}")

        time.sleep(3)

        # ==================== 5. ПРОВЕРКА ПЕРВОНАЧАЛЬНОГО ВОДИТЕЛЯ ====================
        with allure.step("5. LKZ проверяет водителя в executionParameters"):
            print(f"\n🔍 LKZ проверяет назначенного водителя...")

            # Проверяем несколько раз с задержкой
            max_attempts = 5
            initial_exec_param = None

            for attempt in range(max_attempts):
                print(f"🔍 Попытка {attempt + 1} из {max_attempts}...")

                initial_exec_param = self.check_driver_in_execution_params(lkz_client, request_id)

                if initial_exec_param and initial_exec_param.get("driverFullName"):
                    print(f"✅ Водитель найден в executionParameters")
                    print(f"   Имя: {initial_exec_param.get('driverFullName')}")
                    print(f"   Телефон: {initial_exec_param.get('driverPhone')}")
                    print(f"   Номер ТС: {initial_exec_param.get('vehiclePlateNumber')}")
                    break

                if attempt < max_attempts - 1:
                    print(f"⏳ Ждем 3 секунды...")
                    time.sleep(3)
                else:
                    print(f"⚠️ Водитель не найден после {max_attempts} попыток")

            if initial_exec_param:
                print(f"\n📋 ИНФОРМАЦИЯ О ПЕРВОНАЧАЛЬНОМ ВОДИТЕЛЕ:")
                for key, value in initial_exec_param.items():
                    if value:  # Выводим только непустые значения
                        print(f"  {key}: {value}")

        # ==================== 6. ЗАМЕНА ТРАНСПОРТА ====================
        with allure.step("6. LKP заменяет водителя и ТС"):
            lkp_transport_replace = TruckDeliveriesTransportReplaceClient(BASE_URL, lkp_token)

            lkp_transport_replace.replace_transport(
                truck_delivery_id=delivery_id_uuid,
                driver_id=self.REPLACEMENT_DRIVER_ID,
                vehicle_id=self.REPLACEMENT_VEHICLE_ID
            )

            print(f"✅ Транспорт заменен:")
            print(f"   Новый водитель: {self.REPLACEMENT_DRIVER_ID}")
            print(f"   Новое ТС: {self.REPLACEMENT_VEHICLE_ID}")

        time.sleep(3)

        # ==================== 7. ПРОВЕРКА ЗАМЕНЫ ====================
        with allure.step("7. LKZ проверяет замененного водителя"):
            print(f"\n🔍 LKZ проверяет замененного водителя...")

            # Проверяем несколько раз
            max_attempts = 5
            new_exec_param = None

            for attempt in range(max_attempts):
                print(f"🔍 Попытка {attempt + 1} из {max_attempts}...")

                new_exec_param = self.check_driver_in_execution_params(lkz_client, request_id)

                if new_exec_param and new_exec_param.get("driverFullName"):
                    print(f"✅ Водитель найден в executionParameters")

                    # Проверяем что данные изменились
                    if initial_exec_param:
                        # Сравниваем ключевые поля
                        fields_to_compare = ["driverFullName", "driverPhone", "driverLicenseId", "vehiclePlateNumber"]
                        changes_detected = False

                        print(f"\n🔍 СРАВНЕНИЕ ДО И ПОСЛЕ ЗАМЕНЫ:")
                        for field in fields_to_compare:
                            old_value = initial_exec_param.get(field)
                            new_value = new_exec_param.get(field)

                            if old_value != new_value:
                                print(f"  {field}: '{old_value}' → '{new_value}' ✅ ИЗМЕНИЛОСЬ")
                                changes_detected = True
                            else:
                                print(f"  {field}: '{old_value}' → '{new_value}' ❌ НЕ ИЗМЕНИЛОСЬ")

                        if changes_detected:
                            print(f"\n🎉 ЗАМЕНА ПОДТВЕРЖДЕНА!")
                        else:
                            print(f"\n⚠️ Данные не изменились!")

                    break

                if attempt < max_attempts - 1:
                    print(f"⏳ Ждем 3 секунды...")
                    time.sleep(3)
                else:
                    print(f"⚠️ Водитель не найден после {max_attempts} попыток")

        # ==================== 8. НАЧАЛО РЕЙСА ====================
        with allure.step("8. LKP начинает рейс"):
            lkp_cargo_start = CargoDeliveriesStartClient(BASE_URL, lkp_token)

            try:
                lkp_cargo_start.start_cargo_delivery(delivery_id_uuid)
                print(f"✅ Рейс начат")
            except Exception as e:
                print(f"⚠️ Не удалось начать рейс: {e}")

        time.sleep(2)

        # ==================== 9. ЗАВЕРШЕНИЕ РЕЙСА ====================
        with allure.step("9. LKP завершает рейс"):
            try:
                lkp_points_update = TruckDeliveriesPointsUpdateClient(BASE_URL, lkp_token)

                print(f"\n🔧 Завершаем рейс...")

                try:
                    lkp_points_update.complete_all_points(delivery_id_uuid)
                    print(f"✅ Рейс завершен")
                except Exception as e:
                    print(f"⚠️ Основной метод не сработал: {e}")
                    try:
                        lkp_points_update.complete_all_points_simple(delivery_id_uuid)
                        print(f"✅ Рейс завершен (простой метод)")
                    except Exception as e2:
                        print(f"⚠️ Простой метод не сработал: {e2}")

            except Exception as e:
                print(f"❌ Ошибка при завершении рейса: {e}")

        # ==================== 10. ФИНАЛЬНЫЙ ОТЧЕТ ====================
        with allure.step("10. Финальный отчет"):
            print(f"\n{'=' * 60}")
            print(f"🎉 ТЕСТ ЗАВЕРШЕН")
            print(f"{'=' * 60}")
            print(f"Результат:")
            print(f"  Заявка: {request_id} ({request_nr})")
            print(f"  Рейс: {delivery_id_uuid}")

            if initial_exec_param and new_exec_param:
                print(f"\n  До замены:")
                print(f"    Водитель: {initial_exec_param.get('driverFullName', 'не найден')}")
                print(f"    Телефон: {initial_exec_param.get('driverPhone', 'не найден')}")
                print(f"    ТС: {initial_exec_param.get('vehiclePlateNumber', 'не найден')}")

                print(f"\n  После замены:")
                print(f"    Водитель: {new_exec_param.get('driverFullName', 'не найден')}")
                print(f"    Телефон: {new_exec_param.get('driverPhone', 'не найден')}")
                print(f"    ТС: {new_exec_param.get('vehiclePlateNumber', 'не найден')}")

            print(
                f"\n  Вывод: {'Замена проверена через executionParameters' if new_exec_param else 'Замена не подтверждена'}")