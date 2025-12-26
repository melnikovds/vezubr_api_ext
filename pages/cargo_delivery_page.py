import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional


class CargoDeliveryClient:
    """
    Клиент для работы с эндпоинтом /cargo-delivery-requests/create-and-publish
    """

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {"Authorization": token}

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

        :param delivery_type: Тип транспорта (auto)
        :param delivery_sub_type: Тип заявки (ftl/ltl)
        :param body_types: ID типов кузова
        :param vehicle_type_id: ID типа ТС
        :param order_type: Категория рейса (1-городская, 3-междугородняя)
        :param point_change_type: Тип изменения маршрута
        :param route: Маршрут с точками
        :param comment: Комментарий к заявке
        :param client_identifier: Идентификатор заявки
        :param to_start_at_from: Дата и время начала выполнения
        :param producer_id: ID перевозчика
        :param rate: Ставка в копейках
        :param selecting_strategy: Стратегия публикации
        :param cargo_places: Список грузомест (для LTL)
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

        # Добавляем грузоместа если указаны (для LTL)
        if cargo_places:
            payload["parameters"]["cargoPlaces"] = cargo_places

        print(f"📦 Payload для создания заявки на доставку:")
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

        # Добавляем грузоместа если указаны
        if cargo_places:
            payload["cargoPlaces"] = cargo_places

        # Добавляем shipmentTasks если указаны
        if shipment_tasks:
            payload["shipmentTasks"] = shipment_tasks

        print(f"📦 Payload для создания заявки на доставку:")
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