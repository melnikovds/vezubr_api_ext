import requests
from typing import Dict, Any, List


class TruckDeliveriesDetailsClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }

    def get_truck_delivery_details(self, truck_delivery_id: str) -> Dict[str, Any]:
        """
        Получение деталей рейса (TD)
        Эндпоинт: GET /v1/api-ext/truck-deliveries/{id}/details
        Доступно только для LKP
        """
        url = f"{self.base_url}/truck-deliveries/{truck_delivery_id}/details"

        response = requests.get(url, headers=self.headers, timeout=30)

        if response.status_code != 200:
            print(f"❌ Ошибка получения деталей рейса {truck_delivery_id}: {response.status_code}")
            print(f"Ответ: {response.text[:200]}")
            response.raise_for_status()

        result = response.json()
        print(f"✅ Получены детали рейса {truck_delivery_id}")
        return result

    def get_points_info(self, truck_delivery_id: str) -> List[Dict[str, Any]]:
        """Получение информации о точках маршрута рейса"""
        details = self.get_truck_delivery_details(truck_delivery_id)
        return details.get("points", [])