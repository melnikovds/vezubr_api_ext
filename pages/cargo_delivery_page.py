import requests
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional


class CargoDeliveryClient:
    """
    Клиент для работы с эндпоинтом /cargo-delivery-requests/create-and-publish
    """

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {"Authorization": token}

    # ==================== ОСНОВНЫЕ МЕТОДЫ ДЛЯ СОЗДАНИЯ ЗАЯВОК ====================

    def create_and_publish_delivery_request(
            self,
            delivery_type: str = "auto",
            delivery_sub_type: str = "ftl",
            body_types: List[int] = None,
            vehicle_type_id: int = 1,
            order_type: int = 1,
            point_change_type: int = 2,
            route: List[Dict] = None,
            comment: str = "Тестовая заявка API",
            client_identifier: str = None,
            to_start_at_from: str = None,
            producer_id: int = None,
            rate: int = 100000,
            selecting_strategy: str = "rate",
            cargo_places: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Создание и публикация заявки на доставку груза
        """
        if body_types is None:
            body_types = [3, 4, 7, 8]

        if route is None:
            route = []

        if to_start_at_from is None:
            to_start_at_from = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        if client_identifier is None:
            client_identifier = f"API-TEST-{datetime.now().strftime('%d%m%Y-%H%M%S')}"

        payload = {
            "deliveryType": delivery_type,
            "deliverySubType": delivery_sub_type,
            "parameters": {
                "bodyTypes": body_types,
                "vehicleTypeId": vehicle_type_id,
                "orderType": order_type,
                "pointChangeType": point_change_type,
                "route": route
            },
            "comment": comment,
            "clientIdentifier": client_identifier,
            "toStartAtFrom": to_start_at_from,
            "parametersForProducers": {
                "shares": [
                    {
                        "producer": producer_id,
                        "rate": rate
                    }
                ],
                "selectingStrategy": selecting_strategy
            }
        }

        if cargo_places:
            payload["parameters"]["cargoPlaces"] = cargo_places

        print(f" Payload для создания заявки на доставку:")
        print(f"   clientIdentifier: {client_identifier}")
        print(f"   deliverySubType: {delivery_sub_type}")
        print(f"   route points: {len(route)}")
        if cargo_places:
            print(f"   cargoPlaces: {len(cargo_places)}")

        response = requests.post(
            f"{self.base_url}/cargo-delivery-requests/create-and-publish",
            headers=self.headers,
            json=payload,
            timeout=30
        )

        if response.status_code != 200:
            print(f"❌ Ошибка создания заявки: {response.status_code}")
            print(f"Ответ: {response.text}")
            print(f"Запрос: {json.dumps(payload, indent=2, ensure_ascii=False)}")
            response.raise_for_status()

        result = response.json()
        print(f"✅ Заявка создана: ID={result.get('id')}, requestNr={result.get('requestNr')}")
        return result

    def create_and_publish_delivery_request_with_tasks(
            self,
            delivery_type: str = "auto",
            delivery_sub_type: str = "ftl",
            body_types: List[int] = None,
            vehicle_type_id: int = 1,
            order_type: int = 1,
            point_change_type: int = 2,
            route: List[Dict] = None,
            comment: str = "Тестовая заявка API",
            client_identifier: str = None,
            to_start_at_from: str = None,
            producer_id: int = None,
            rate: int = 100000,
            selecting_strategy: str = "rate",
            cargo_places: List[Dict] = None,
            shipment_tasks: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        Создание и публикация заявки на доставку груза с поддержкой shipmentTasks
        """
        if body_types is None:
            body_types = [3, 4, 7, 8]

        if route is None:
            route = []

        if to_start_at_from is None:
            to_start_at_from = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        if client_identifier is None:
            client_identifier = f"API-TEST-{datetime.now().strftime('%d%m%Y-%H%M%S')}"

        payload = {
            "deliveryType": delivery_type,
            "deliverySubType": delivery_sub_type,
            "parameters": {
                "bodyTypes": body_types,
                "vehicleTypeId": vehicle_type_id,
                "orderType": order_type,
                "pointChangeType": point_change_type,
                "route": route
            },
            "comment": comment,
            "clientIdentifier": client_identifier,
            "toStartAtFrom": to_start_at_from,
            "parametersForProducers": {
                "shares": [
                    {
                        "producer": producer_id,
                        "rate": rate
                    }
                ],
                "selectingStrategy": selecting_strategy
            }
        }

        if cargo_places:
            payload["cargoPlaces"] = cargo_places

        if shipment_tasks:
            payload["shipmentTasks"] = shipment_tasks

        print(f" Payload для создания заявки на доставку:")
        print(f"   clientIdentifier: {client_identifier}")
        print(f"   deliverySubType: {delivery_sub_type}")
        print(f"   route points: {len(route)}")
        if cargo_places:
            print(f"   cargoPlaces: {len(cargo_places)}")
        if shipment_tasks:
            print(f"   shipmentTasks: {len(shipment_tasks)}")

        response = requests.post(
            f"{self.base_url}/cargo-delivery-requests/create-and-publish",
            headers=self.headers,
            json=payload,
            timeout=30
        )

        if response.status_code != 200:
            print(f"❌ Ошибка создания заявки: {response.status_code}")
            print(f"Ответ: {response.text}")
            print(f"Запрос: {json.dumps(payload, indent=2, ensure_ascii=False)}")
            response.raise_for_status()

        result = response.json()
        print(f"✅ Заявка создана: ID={result.get('id')}, requestNr={result.get('requestNr')}")
        return result

    def create_route_point(
            self,
            point_id: int,
            position: int,
            is_loading_work: bool = False,
            is_unloading_work: bool = False,
            required_arrive_at: str = None
    ) -> Dict[str, Any]:
        """
        Создание точки маршрута
        """
        point = {
            "position": position,
            "point": point_id,
            "isLoadingWork": is_loading_work,
            "isUnloadingWork": is_unloading_work
        }

        if required_arrive_at:
            point["requiredArriveAt"] = required_arrive_at

        return point

    def create_cargo_place_spec(
            self,
            cargo_place_id: int,
            external_id: str,
            departure_point_position: int,
            arrival_point_position: int
    ) -> Dict[str, Any]:
        """
        Создание спецификации грузоместа для LTL заявки
        """
        return {
            "cargoPlaceId": cargo_place_id,
            "externalId": external_id,
            "departurePointPosition": departure_point_position,
            "arrivalPointPosition": arrival_point_position
        }

    # ==================== МЕТОДЫ ДЛЯ РАБОТЫ С ЗАЯВКАМИ ====================

    def get_delivery_request_details(self, request_id):
        """
        Получение детальной информации по FTL заявке

        Args:
            request_id (str): ID заявки

        Returns:
            dict: Детальная информация о заявке
        """
        url = f"{self.base_url}/cargo-delivery-requests/{request_id}/details"

        response = requests.get(
            url=url,
            headers=self.headers
        )

        if response.status_code != 200:
            raise Exception(f"Ошибка получения деталей заявки {request_id}: {response.status_code} - {response.text}")

        return response.json()

    def check_delivery_status_in_request_details(self, details: dict, delivery_id_uuid: str,
                                                 expected_status: str = "canceled") -> bool:
        """
        Проверка статуса рейса в outgoingEntities деталей заявки

        Args:
            details: детальная информация о заявке
            delivery_id_uuid: ID рейса для проверки
            expected_status: ожидаемый статус (по умолчанию "canceled")

        Returns:
            bool: True если статус соответствует ожидаемому
        """
        print(f"🔍 Проверяем outgoingEntities в деталях заявки...")
        print(f"ID заявки: {details.get('id')}")

        # Проверяем наличие outgoingEntities
        if "outgoingEntities" not in details:
            print("⚠️ outgoingEntities отсутствует в деталях заявки")
            return False

        outgoing_entities = details["outgoingEntities"]

        # Проверяем что это список
        if not isinstance(outgoing_entities, list):
            print(f"⚠️ outgoingEntities не является списком: {type(outgoing_entities)}")
            return False

        print(f"✅ outgoingEntities найден, количество элементов: {len(outgoing_entities)}")

        # Если список пустой, выводим отладочную информацию
        if len(outgoing_entities) == 0:
            print("⚠️ outgoingEntities пустой список")
            # Выводим ключи деталей для отладки
            print(f"Ключи в details: {list(details.keys())}")
            return False

        # Проверяем каждый элемент
        for i, entity in enumerate(outgoing_entities):
            print(f"\n🔍 Проверяем entity {i}:")
            print(f"  id: {entity.get('id')}")
            print(f"  type: {entity.get('type')}")
            print(f"  status: {entity.get('status')}")

            # Проверяем по ID рейса и типу
            if (entity.get("id") == delivery_id_uuid and
                    entity.get("type") == "delivery"):

                actual_status = entity.get("status")
                if actual_status == expected_status:
                    print(f"✅ Найден рейс со статусом {expected_status}: id={entity.get('id')}")
                    return True
                else:
                    print(f"⚠️ Рейс найден, но статус: '{actual_status}' (ожидается '{expected_status}')")
                    return False

        print(f"⚠️ Рейс {delivery_id_uuid} не найден в outgoingEntities")
        return False

    def find_delivery_in_outgoing_entities(self, details: dict) -> dict:
        """
        Поиск рейса в outgoingEntities

        Args:
            details: детальная информация о заявке

        Returns:
            dict: информация о найденном рейсе или пустой dict
        """
        if "outgoingEntities" not in details:
            return {}

        outgoing_entities = details.get("outgoingEntities", [])

        for entity in outgoing_entities:
            if entity.get("type") == "delivery":
                print(f"✅ Найден delivery в outgoingEntities:")
                print(f"   id: {entity.get('id')}")
                print(f"   type: {entity.get('type')}")
                print(f"   status: {entity.get('status')}")
                return entity

        print("⚠️ Не найден delivery в outgoingEntities")
        return {}

    def wait_for_delivery_status(self, request_id: str, delivery_id_uuid: str, expected_status: str = "canceled",
                                 max_attempts: int = 5, delay: int = 3) -> bool:
        """
        Ожидание и проверка статуса рейса в деталях заявки

        Args:
            request_id: ID заявки
            delivery_id_uuid: ID рейса
            expected_status: ожидаемый статус
            max_attempts: максимальное количество попыток
            delay: задержка между попытками в секундах

        Returns:
            bool: True если статус соответствует ожидаемому
        """
        print(f"\n Ожидание статуса '{expected_status}' для рейса {delivery_id_uuid}...")

        for attempt in range(max_attempts):
            print(f" Попытка {attempt + 1} из {max_attempts}...")

            try:
                details = self.get_delivery_request_details(request_id)

                if self.check_delivery_status_in_request_details(details, delivery_id_uuid, expected_status):
                    print(f"✅ Статус '{expected_status}' подтвержден")
                    return True
                else:
                    # Выводим что нашлось для отладки
                    delivery_entity = self.find_delivery_in_outgoing_entities(details)
                    if delivery_entity:
                        print(
                            f"⚠️ Статус найденного delivery: {delivery_entity.get('status')} (ожидается '{expected_status}')")
                    else:
                        print(f"⚠️ Delivery не найден в outgoingEntities")

            except Exception as e:
                print(f"❌ Ошибка при получении деталей заявки: {str(e)}")

            if attempt < max_attempts - 1:
                print(f"⏳ Ждем {delay} секунды...")
                time.sleep(delay)

        print(f"❌ Не удалось дождаться статуса '{expected_status}' после {max_attempts} попыток")
        return False

    def take_delivery_request(self, request_id):
        """
        Принятие FTL заявки исполнителем

        Args:
            request_id (str): ID заявки

        Returns:
            dict: Результат принятия заявки
        """
        url = f"{self.base_url}/cargo-delivery-requests/{request_id}/take"

        response = requests.get(
            url=url,
            headers=self.headers
        )

        if response.status_code != 200:
            raise Exception(f"Ошибка принятия заявки {request_id}: {response.status_code} - {response.text}")

        return response.json()

    # ==================== МЕТОДЫ ДЛЯ РАБОТЫ С ВОДИТЕЛЕМ В EXECUTION PARAMETERS ====================

    def get_driver_info_from_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """
        Получение информации о водителе из детализации заявки
        Ищем в executionParameters

        Args:
            request_id: ID заявки

        Returns:
            dict или None: Информация о водителе и ТС из executionParameters
        """
        details = self.get_delivery_request_details(request_id)

        print(f"\n🔍 Анализируем структуру заявки {request_id}...")
        print(f"Статус заявки: {details.get('status')}")

        # Ищем executionParameters
        execution_param = self._find_execution_param(details)

        if execution_param:
            print(f"✅ Найден водитель в executionParameters")
            return self._extract_driver_from_execution_param(execution_param)

        print("⚠️ Не удалось найти информацию о водителе в заявке")
        return None

    def _find_execution_param(self, details: Dict) -> Optional[Dict]:
        """Поиск executionParameters в структуре заявки"""
        # 1. Проверяем на верхнем уровне
        if "executionParameters" in details:
            execution_params = details["executionParameters"]
            if isinstance(execution_params, list) and execution_params:
                # Проверяем первый элемент
                first_param = execution_params[0]
                if first_param.get("driverFullName") or first_param.get("driverPhone"):
                    return first_param

        # 2. Проверяем в outgoingEntities
        if "outgoingEntities" in details:
            entities = details["outgoingEntities"]
            for entity in entities:
                if "executionParameters" in entity:
                    execution_params = entity["executionParameters"]
                    if isinstance(execution_params, list) and execution_params:
                        first_param = execution_params[0]
                        if first_param.get("driverFullName") or first_param.get("driverPhone"):
                            return first_param

        return None

    def _extract_driver_from_execution_param(self, param: Dict) -> Dict[str, Any]:
        """Извлечение информации о водителе из executionParameters"""
        return {
            "driver_full_name": param.get("driverFullName", ""),
            "driver_phone": param.get("driverPhone", ""),
            "driver_passport": param.get("driverPassportId", ""),
            "driver_license": param.get("driverLicenseId", ""),
            "plate_number": param.get("vehiclePlateNumber", ""),
            "vehicle_mark_model": param.get("vehicleMarkAndModel", ""),
            "company_name": param.get("companyName", ""),
            "company_inn": param.get("companyInn", ""),
            "is_loading_work": param.get("isLoadingWork", False),
            "is_unloading_work": param.get("isUnloadingWork", False)
        }

    def verify_driver_change_in_request(
            self,
            request_id: str,
            max_attempts: int = 5,
            delay: int = 3
    ) -> Optional[Dict[str, Any]]:
        """
        Проверка наличия информации о водителе в заявке с повторными попытками

        Args:
            request_id: ID заявки
            max_attempts: Максимальное количество попыток
            delay: Задержка между попытками

        Returns:
            dict или None: Информация о водителе из executionParameters
        """
        print(f"\n🔍 Проверка водителя в заявке {request_id}")

        for attempt in range(max_attempts):
            print(f"\n🔍 Попытка {attempt + 1} из {max_attempts}...")

            try:
                driver_info = self.get_driver_info_from_request(request_id)

                if driver_info and driver_info.get("driver_full_name"):
                    print(f"✅ Водитель найден:")
                    print(f"   ФИО: {driver_info['driver_full_name']}")
                    print(f"   Телефон: {driver_info['driver_phone']}")
                    print(f"   Номер ТС: {driver_info['plate_number']}")
                    return driver_info
                else:
                    print(f"⚠ Информация о водителе не найдена")

                    if attempt < max_attempts - 1:
                        print(f"⏳ Ждем {delay} секунды...")
                        time.sleep(delay)
                    else:
                        print(f"❌ Водитель не найден после {max_attempts} попыток")
                        return None

            except Exception as e:
                print(f"❌ Ошибка при проверке: {str(e)}")
                if attempt < max_attempts - 1:
                    print(f"⏳ Ждем {delay} секунды и пробуем снова...")
                    time.sleep(delay)
                else:
                    print(f"❌ Все попытки завершились ошибкой")
                    raise

        return None

    def compare_drivers_in_request(
            self,
            request_id: str,
            initial_driver_info: Dict,
            max_attempts: int = 5,
            delay: int = 3
    ) -> Dict[str, Any]:
        """
        Сравнение водителя с первоначальным (для проверки замены)

        Args:
            request_id: ID заявки
            initial_driver_info: Информация о первоначальном водителе
            max_attempts: Максимальное количество попыток
            delay: Задержка между попытками

        Returns:
            dict: Результаты сравнения
        """
        print(f"\n🔍 Сравнение водителей в заявке {request_id}")

        for attempt in range(max_attempts):
            print(f"\n🔍 Попытка {attempt + 1} из {max_attempts}...")

            try:
                current_driver_info = self.get_driver_info_from_request(request_id)

                if not current_driver_info or not current_driver_info.get("driver_full_name"):
                    print(f"⚠️ Текущий водитель не найден")
                    if attempt < max_attempts - 1:
                        print(f" Ждем {delay} секунды...")
                        time.sleep(delay)
                    continue

                # Сравниваем ключевые поля
                comparison = self._compare_execution_params(initial_driver_info, current_driver_info)

                if comparison["driver_changed"] or comparison["vehicle_changed"]:
                    print(f"✅ Изменения обнаружены!")
                    return {
                        "current_driver_info": current_driver_info,
                        "comparison": comparison,
                        "success": True
                    }
                else:
                    print(f"⚠️ Изменений не обнаружено")

                    if attempt < max_attempts - 1:
                        print(f" Ждем {delay} секунды...")
                        time.sleep(delay)
                    else:
                        print(f"❌ Изменения не обнаружены после {max_attempts} попыток")
                        return {
                            "current_driver_info": current_driver_info,
                            "comparison": comparison,
                            "success": False
                        }

            except Exception as e:
                print(f"❌ Ошибка при сравнении: {str(e)}")
                if attempt < max_attempts - 1:
                    print(f" Ждем {delay} секунды и пробуем снова...")
                    time.sleep(delay)
                else:
                    print(f"❌ Все попытки завершились ошибкой")
                    raise

        return {
            "current_driver_info": None,
            "comparison": None,
            "success": False
        }

    def _compare_execution_params(self, param1: Dict, param2: Dict) -> Dict[str, bool]:
        """Сравнение двух executionParameters"""
        fields_to_compare = [
            ("driver_full_name", "driverFullName"),
            ("driver_phone", "driverPhone"),
            ("driver_license", "driverLicenseId"),
            ("plate_number", "vehiclePlateNumber")
        ]

        results = {}
        driver_changed = False
        vehicle_changed = False

        print(f"\n🔍 Сравнение полей:")
        for field_name, field_key in fields_to_compare:
            value1 = param1.get(field_name, "")
            value2 = param2.get(field_name, "")

            changed = value1 != value2
            results[field_name] = changed

            if field_name in ["driver_full_name", "driver_phone", "driver_license"]:
                driver_changed = driver_changed or changed
            elif field_name == "plate_number":
                vehicle_changed = vehicle_changed or changed

            status = "✅ ИЗМЕНИЛОСЬ" if changed else "❌ НЕ ИЗМЕНИЛОСЬ"
            print(f"  {field_name}: '{value1}' → '{value2}' {status}")

        return {
            **results,
            "driver_changed": driver_changed,
            "vehicle_changed": vehicle_changed,
            "any_changed": driver_changed or vehicle_changed
        }

    def print_driver_info_from_execution(self, driver_info: Dict):
        """
        Вывод информации о водителе из executionParameters

        Args:
            driver_info: Информация о водителе
        """
        print("\n" + "=" * 60)
        print("👨‍✈️ ИНФОРМАЦИЯ О ВОДИТЕЛЕ И ТС (из executionParameters):")
        print("=" * 60)
        print(f"Водитель:")
        print(f"  ФИО: {driver_info.get('driver_full_name')}")
        print(f"  Телефон: {driver_info.get('driver_phone')}")
        print(f"  Паспорт: {driver_info.get('driver_passport')}")
        print(f"  В/у: {driver_info.get('driver_license')}")

        print(f"\nТранспортное средство:")
        print(f"  Гос. номер: {driver_info.get('plate_number')}")
        print(f"  Марка/модель: {driver_info.get('vehicle_mark_model')}")

        print(f"\nКомпания:")
        print(f"  Название: {driver_info.get('company_name')}")
        print(f"  ИНН: {driver_info.get('company_inn')}")

        print(f"\nРаботы:")
        print(f"  Погрузка: {'Да' if driver_info.get('is_loading_work') else 'Нет'}")
        print(f"  Разгрузка: {'Да' if driver_info.get('is_unloading_work') else 'Нет'}")
        print("=" * 60 + "\n")
