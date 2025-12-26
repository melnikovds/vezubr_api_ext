import requests
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional


class CargoDeliveryDraftClient:
    """
    Клиент для работы с эндпоинтом /api-ext/cargo-delivery-requests/create
    для создания заявок в черновик (без публикации)
    """

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }

    def create_draft_delivery_request(
            self,
            client_identifier: str,
            delivery_sub_type: str,  # "ltl" или "ftl"
            departure_point: int,
            arrival_point: int,
            cargo_places: Optional[List[Dict]] = None,
            shipment_tasks: Optional[List[Dict]] = None,
            responsible_employees: Optional[List[int]] = None,
            comment: str = "Тестовая заявка в черновик",
            inner_comment: Optional[str] = None,
            to_start_at_from: Optional[str] = None,
            to_start_at_till: Optional[str] = None,
            delivery_type: str = "auto",
            additional_services: Optional[List[Dict]] = None,
            new_cargo_places: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """
        Создание заявки на доставку груза в черновик (без публикации)
        Структура согласно примеру LTL запроса
        """
        # Устанавливаем значения по умолчанию как ПУСТЫЕ МАССИВЫ, а не None
        if shipment_tasks is None:
            shipment_tasks = []

        if responsible_employees is None:
            responsible_employees = []

        if additional_services is None:
            additional_services = []

        if new_cargo_places is None:
            new_cargo_places = []

        if cargo_places is None:
            cargo_places = []

        if to_start_at_from is None:
            to_start_at_from = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")

        if to_start_at_till is None:
            to_start_at_till = (datetime.now(timezone.utc) + timedelta(days=1, hours=2)).strftime("%Y-%m-%dT%H:%M:%SZ")

        # ОСНОВНАЯ СТРУКТУРА СОГЛАСНО ПРИМЕРУ LTL
        payload = {
            "deliveryType": delivery_type,
            "deliverySubType": delivery_sub_type,
            "shipmentTasks": shipment_tasks,  # Пустой массив, не null!
            "cargoPlaces": cargo_places,
            "responsibleEmployees": responsible_employees,  # Пустой массив, не null!
            "comment": comment,
            "innerComment": inner_comment,
            "toStartAtFrom": to_start_at_from,
            "toStartAtTill": to_start_at_till,
            "additionalServices": additional_services,  # Пустой массив, не null!
            "departurePoint": departure_point,  # В КОРНЕ ЗАПРОСА (для LTL)
            "arrivalPoint": arrival_point,  # В КОРНЕ ЗАПРОСА (для LTL)
            "newCargoPlaces": new_cargo_places  # Пустой массив, не null!
        }

        # Для FTL добавляем parameters с route
        if delivery_sub_type.lower() == "ftl":
            payload["parameters"] = {
                "orderCategory": 1,
                "bodyTypes": [3, 4, 7, 8],
                "isDangerousGoods": False,
                "vehicleTypeId": 1,
                "orderType": 1,  # 1-городская, 3-междугородняя
                "pointChangeType": 2,
                "route": [
                    {
                        "requiredArriveAtFrom": to_start_at_from,
                        "requiredArriveAtTill": None,
                        "position": 1,
                        "point": departure_point,
                        "isLoadingWork": True,
                        "isUnloadingWork": False
                    },
                    {
                        "requiredArriveAtFrom": None,
                        "requiredArriveAtTill": None,
                        "position": 2,
                        "point": arrival_point,
                        "isLoadingWork": False,
                        "isUnloadingWork": True
                    }
                ]
            }

        print(f"   Создание {delivery_sub_type.upper()} заявки в черновик:")
        print(f"   clientIdentifier: {client_identifier}")
        print(f"   Тип: {delivery_sub_type}")

        if delivery_sub_type.lower() == "ltl":
            print(f"   Адреса в корне: {departure_point} → {arrival_point}")
            print(f"   cargoPlaces: {len(cargo_places)} шт (только ID)")
        else:  # FTL
            print(f"   Маршрут в parameters.route: {departure_point} → {arrival_point}")
            print(f"   cargoPlaces: {len(cargo_places)} шт")

        print(f"   Статус: draft (черновик)")

        url = f"{self.base_url}/cargo-delivery-requests/create"
        print(f"   URL: {url}")

        response = requests.post(
            url,
            headers=self.headers,
            json=payload,
            timeout=30
        )

        print(f"📥 Ответ сервера: {response.status_code}")

        if response.status_code != 200:
            print(f"❌ Ошибка создания заявки в черновик:")
            print(f"   Запрос: {json.dumps(payload, indent=2, ensure_ascii=False)}")
            print(f"   Ответ: {response.text}")
            response.raise_for_status()

        result = response.json()
        request_id = result.get("id")
        status = result.get("status")

        print(f"✅ {delivery_sub_type.upper()} заявка создана в черновик:")
        print(f"   ID заявки: {request_id}")
        print(f"   Номер заявки: {result.get('requestNr', 'N/A')}")
        print(f"   Статус: {status}")

        return result

    def create_ltl_draft_request(
            self,
            client_identifier: str,
            departure_point: int,
            arrival_point: int,
            cargo_place_ids: List[int],  # ID грузомест
            **kwargs
    ) -> Dict[str, Any]:
        """
        Создание LTL заявки в черновик
        Для LTL: адреса в корне запроса, в cargoPlaces только ID
        """
        # Для LTL в cargoPlaces указываем только ID (без адресов)
        cargo_places = []
        for cargo_id in cargo_place_ids:
            cargo_place_obj = {
                "id": cargo_id
                # НЕ указываем departurePoint и arrivalPoint здесь!
                # Они будут в корне запроса
            }
            cargo_places.append(cargo_place_obj)

        return self.create_draft_delivery_request(
            client_identifier=client_identifier,
            delivery_sub_type="ltl",
            departure_point=departure_point,
            arrival_point=arrival_point,
            cargo_places=cargo_places,
            **kwargs
        )

    def create_ftl_draft_request(
            self,
            client_identifier: str,
            departure_point: int,
            arrival_point: int,
            **kwargs
    ) -> Dict[str, Any]:
        """
        Создание FTL заявки в черновик
        Для FTL: адреса в parameters.route, cargo_places пустой массив
        """
        return self.create_draft_delivery_request(
            client_identifier=client_identifier,
            delivery_sub_type="ftl",
            departure_point=departure_point,
            arrival_point=arrival_point,
            cargo_places=[],  # Пустой массив для FTL
            **kwargs
        )
