import requests
import json
from typing import Dict, Any


class TruckDeliveriesTransportReplaceClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {"Authorization": token}

    def replace_transport(self, truck_delivery_id: str, driver_id: int, vehicle_id: int) -> Dict[str, Any]:
        """
        Замена водителя и ТС на рейсе
        Эндпоинт: POST /v1/api-ext/truck-deliveries/{id}/transport/replace

        Args:
            truck_delivery_id: ID рейса
            driver_id: ID нового водителя
            vehicle_id: ID нового ТС

        Returns:
            Ответ от API
        """
        url = f"{self.base_url}/truck-deliveries/{truck_delivery_id}/transport/replace"

        payload = {
            "driver": driver_id,
            "vehicle": vehicle_id,
            "isLiftingValidationRequired": False,
            "isAgreeWithAdditionalRequirements": False
        }

        print(f"🔄 [TruckDeliveriesReplace] Замена транспорта на рейсе {truck_delivery_id}")
        print(f"   Новый водитель: {driver_id}, Новое ТС: {vehicle_id}")

        response = requests.post(url, json=payload, headers=self.headers, timeout=30)

        if response.status_code != 200:
            print(f"❌ Ошибка замены транспорта: {response.status_code}")
            print(f"Ответ: {response.text}")
            print(f"Запрос: {json.dumps(payload, indent=2, ensure_ascii=False)}")
            response.raise_for_status()

        result = response.json()
        print(f"✅ Транспорт заменен")
        return result