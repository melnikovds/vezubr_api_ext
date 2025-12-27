import requests
import json
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List


class CargoDeliveryUpdateActiveClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }

    def update_active_request(
            self,
            request_id: int,
            delivery_type: str,
            delivery_sub_type: str,
            client_identifier: str,
            comment: str,
            inner_comment: str = None,
            body_types: List[int] = None,
            vehicle_type_id: int = None,
            route: List[Dict] = None,
            to_start_at_from: str = None,
            to_start_at_till: str = None
    ) -> Dict[str, Any]:
        """
        Редактирование активной заявки
        Эндпоинт: POST /v1/api-ext/cargo-delivery-requests/{id}/update/active
        """
        url = f"{self.base_url}/cargo-delivery-requests/{request_id}/update/active"

        # СОЗДАЕМ ПРАВИЛЬНЫЙ PAYLOAD (как в Postman)
        payload = {
            "comment": comment,
            "clientIdentifier": client_identifier,
            "deliveryType": delivery_type,
            "deliverySubType": delivery_sub_type,
        }

        if to_start_at_from:
            payload["toStartAtFrom"] = to_start_at_from
        else:
            # Генерируем время, если не передано
            from datetime import datetime, timedelta
            future_time = (datetime.now() + timedelta(days=1)).replace(microsecond=0).isoformat() + "Z"
            payload["toStartAtFrom"] = future_time

        if to_start_at_till:
            payload["toStartAtTill"] = to_start_at_till
        else:
            # Генерируем время, если не передано
            from datetime import datetime, timedelta
            future_time = (datetime.now() + timedelta(days=1, hours=2)).replace(microsecond=0).isoformat() + "Z"
            payload["toStartAtTill"] = future_time

        if inner_comment:
            payload["innerComment"] = inner_comment

        if body_types:
            payload["bodyTypes"] = body_types

        if vehicle_type_id:
            payload["vehicleTypeId"] = vehicle_type_id

        if route:
            payload["route"] = route

        # Остальные поля как в Postman
        payload["cargoPlaces"] = []
        payload["shipmentTasks"] = []

        print(f"✏️ [UpdateActive] Редактирование активной заявки {request_id}")
        print(f"   Метод: POST")
        print(f"   Комментарий к заявке: {comment}")
        print(f"   toStartAtFrom: {payload.get('toStartAtFrom')}")
        print(f"   toStartAtTill: {payload.get('toStartAtTill')}")
        print(f"   BodyTypes: {payload.get('bodyTypes')}")
        print(f"🔍 Отладочная информация:")
        print(f"   URL: {url}")
        print(f"   Полный payload:")
        print(json.dumps(payload, indent=2, ensure_ascii=False))

        response = requests.post(url, json=payload, headers=self.headers, timeout=30)

        print(f"🔍 Ответ сервера: status={response.status_code}")
        print(f"   Текст ответа: {response.text[:500]}...")

        if response.status_code != 200:
            print(f"❌ Ошибка редактирования заявки: {response.status_code}")
            print(f"Ответ: {response.text}")
            print(f"Запрос: {json.dumps(payload, indent=2, ensure_ascii=False)}")
            response.raise_for_status()

        result = response.json()
        print(f"✅ Заявка отредактирована. Ответ: {result}")
        return result

    def create_ftl_parameters(
            self,
            route: List[Dict],
            body_types: List[int] = None,
            vehicle_type_id: int = 1,
            order_type: int = 1,
            point_change_type: int = 2
    ) -> Dict:
        """Создание parameters для FTL заявки для /update/active"""
        return {
            "orderCategory": 1,
            "bodyTypes": body_types or [3, 4, 7, 8],
            "isDangerousGoods": False,
            "vehicleTypeId": vehicle_type_id,
            "orderType": order_type,
            "pointChangeType": point_change_type,
            "route": route
        }

    def get_warhammer_comment(self) -> str:
        """Генерация случайного комментария в стиле Warhammer 40k"""
        comments = [
            "Перемещение во имя Императора!",
            "Груз для Адептус Механикус",
            "Снабжение для Астра Милитарум",
            "Доставка священных реликвий",
            "Транспортировка для Инквизиции",
            "Поставка для космодесанта",
            "Для Войны с еретиками",
            "Во славу Золотого Трона!",
            "Экспресс-доставка в Ультрамар",
            "Для крестового похода",
            "Срочная доставка для Гвардии Смерти",
            "Для защиты Империума",
            "Перемещение через варп-пространство",
            "Для нужд Адептус Сороритас",
            "По приказу Лорда-командира"
        ]
        return random.choice(comments)

    def create_route_point(
            self,
            point_id: int,
            position: int,
            is_loading_work: bool,
            is_unloading_work: bool,
            required_arrive_at_from: str = None,
            required_arrive_at_till: str = None,
            with_warhammer_comment: bool = False
    ) -> Dict:
        """Создание точки маршрута с возможностью Warhammer комментария"""
        point = {
            "position": position,
            "point": point_id,
            "isLoadingWork": is_loading_work,
            "isUnloadingWork": is_unloading_work
        }

        if required_arrive_at_from:
            point["requiredArriveAtFrom"] = required_arrive_at_from
        if required_arrive_at_till:
            point["requiredArriveAtTill"] = required_arrive_at_till
        if with_warhammer_comment:
            point["comment"] = self.get_warhammer_comment()
            print(f"    Точка {position}: {point['comment']}")

        return point

    def update_route_with_comments(
            self,
            route: List[Dict],
            add_comments: bool = True
    ) -> List[Dict]:
        """Обновление маршрута с добавлением/изменением комментариев"""
        updated_route = []
        for point in route:
            updated_point = point.copy()
            if add_comments:
                updated_point["comment"] = self.get_warhammer_comment()
            else:
                updated_point.pop("comment", None)
            updated_route.append(updated_point)
        return updated_route

    def generate_future_iso_time(self, days_ahead: int = 1, hours_ahead: int = 0) -> str:
        """Генерация времени в будущем для requiredArriveAtFrom"""
        future_time = datetime.now() + timedelta(days=days_ahead, hours=hours_ahead)
        return future_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    def create_route_point_for_update(
            self,
            point_id: int,
            position: int,
            loading_type: int = 1
    ) -> Dict:
        """
        Создание точки маршрута для /update/active
        Соответствует документации: {"point": 27648, "position": 1, "loadingType": 1}
        """
        return {
            "point": point_id,
            "position": position,
            "loadingType": loading_type
        }
