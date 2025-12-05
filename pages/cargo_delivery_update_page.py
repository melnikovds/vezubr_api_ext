import requests
import json
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, List


class CargoDeliveryUpdateClient:
    """
    Клиент для работы с эндпоинтом /cargo-delivery-requests/{id}/update
    для редактирования заявок в статусе draft
    """

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }

    def update_draft_request(
            self,
            request_id: int,
            # Обязательные поля из структуры создания:
            delivery_type: str = "auto",
            delivery_sub_type: str = "ltl",  # "ltl" или "ftl"
            # Для LTL: адреса в корне (обязательные!)
            departure_point: Optional[int] = None,
            arrival_point: Optional[int] = None,
            # Для FTL: параметры маршрута
            route: Optional[List[Dict]] = None,
            # Поля которые хотим изменить:
            to_start_at_from: Optional[str] = None,
            to_start_at_till: Optional[str] = None,
            client_identifier: Optional[str] = None,
            inner_comment: Optional[str] = None,
            comment: Optional[str] = None,
            # Другие поля из структуры создания:
            cargo_places: Optional[List[Dict]] = None,
            shipment_tasks: Optional[List[Dict]] = None,
            responsible_employees: Optional[List[int]] = None,
            additional_services: Optional[List[Dict]] = None,
            new_cargo_places: Optional[List[Dict]] = None,
            # Для FTL заявок
            parameters: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Обновление заявки в статусе draft
        Структура должна соответствовать структуре создания заявки!
        """
        # БАЗОВАЯ СТРУКТУРА КАК ПРИ СОЗДАНИИ
        payload = {
            "deliveryType": delivery_type,
            "deliverySubType": delivery_sub_type,
        }

        # Обязательные поля в зависимости от типа заявки
        if departure_point is not None:
            payload["departurePoint"] = departure_point
        if arrival_point is not None:
            payload["arrivalPoint"] = arrival_point

        # Остальные поля
        if shipment_tasks is not None:
            payload["shipmentTasks"] = shipment_tasks
        if cargo_places is not None:
            payload["cargoPlaces"] = cargo_places
        if responsible_employees is not None:
            payload["responsibleEmployees"] = responsible_employees
        if additional_services is not None:
            payload["additionalServices"] = additional_services
        if new_cargo_places is not None:
            payload["newCargoPlaces"] = new_cargo_places

        # Поля которые можно изменить (если переданы)
        if to_start_at_from is not None:
            payload["toStartAtFrom"] = to_start_at_from
        if to_start_at_till is not None:
            payload["toStartAtTill"] = to_start_at_till
        if client_identifier is not None:
            payload["clientIdentifier"] = client_identifier
        if inner_comment is not None:
            payload["innerComment"] = inner_comment
        if comment is not None:
            payload["comment"] = comment

        # Для FTL добавляем parameters
        if delivery_sub_type.lower() == "ftl":
            if parameters is not None:
                payload["parameters"] = parameters
            elif route is not None:
                payload["parameters"] = {
                    "orderCategory": 1,
                    "bodyTypes": [3, 4, 7, 8],
                    "isDangerousGoods": False,
                    "vehicleTypeId": 1,
                    "orderType": 1,
                    "pointChangeType": 2,
                    "route": route
                }

        url = f"{self.base_url}/cargo-delivery-requests/{request_id}/update"

        print(f"Редактирование заявки в черновике:")
        print(f"   URL: {url}")
        print(f"   ID заявки: {request_id}")
        print(f"   Тип заявки: {delivery_sub_type.upper()}")
        print(f"   DeliveryType: {delivery_type}")
        print(f"   DeliverySubType: {delivery_sub_type}")

        if departure_point and arrival_point:
            print(f"   Адреса: {departure_point} → {arrival_point}")

        # Показываем какие поля обновляем
        update_fields = []
        for key in ["toStartAtFrom", "toStartAtTill", "clientIdentifier", "innerComment", "comment"]:
            if key in payload:
                value = payload[key]
                if key in ["toStartAtFrom", "toStartAtTill"] and value:
                    update_fields.append(f"{key}: {value[:19]}...")
                else:
                    update_fields.append(f"{key}: {value}")

        if update_fields:
            print(f"   Обновляемые поля:")
            for field in update_fields:
                print(f"   - {field}")

        print(f"   Payload: {json.dumps(payload, ensure_ascii=False)}")

        # Используем POST
        response = requests.post(
            url,
            headers=self.headers,
            json=payload,
            timeout=30
        )

        print(f"   Ответ сервера: {response.status_code}")

        if response.status_code != 200:
            print(f"   Ошибка редактирования заявки:")
            print(f"   Ответ: {response.text}")
            response.raise_for_status()

        result = response.json()
        print(f"✅ Заявка успешно отредактирована")
        print(f"   Ответ: {result}")

        return result

    def generate_future_iso_time(self, days_ahead: int = 2, hours_ahead: int = 1) -> str:
        """Генерация времени в ISO формате"""
        future_time = datetime.now(timezone.utc) + timedelta(days=days_ahead, hours=hours_ahead)
        return future_time.strftime("%Y-%m-%dT%H:%M:%SZ")
