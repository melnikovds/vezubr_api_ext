import requests
import json
from typing import Dict, Any


class TruckDeliveriesTransportAppointClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {"Authorization": token}

    def appoint_transport(self, truck_delivery_id: str, driver_id: int, vehicle_id: int) -> Dict[str, Any]:
        """
        Назначение водителя и ТС на рейс
        Эндпоинт: POST /v1/api-ext/truck-deliveries/{id}/transport/appoint
        """
        url = f"{self.base_url}/truck-deliveries/{truck_delivery_id}/transport/appoint"


        payload = {
            "driver": driver_id,
            "vehicle": vehicle_id,
            "isLiftingValidationRequired": False,
            "isAgreeWithAdditionalRequirements": False
        }

        print(f"👨‍✈️ [TruckDeliveriesAppoint] Назначение транспорта на рейс {truck_delivery_id}")
        print(f"   Водитель: {driver_id}, ТС: {vehicle_id}")
        # Полезно выводить и payload для отладки
        print(f"   Payload (isLiftingValidationRequired=False): {payload}")

        response = requests.post(url, json=payload, headers=self.headers, timeout=30)

        if response.status_code != 200:
            print(f"❌ Ошибка назначения транспорта: {response.status_code}")
            print(f"Ответ: {response.text}")
            print(f"Запрос: {json.dumps(payload, indent=2, ensure_ascii=False)}")
            response.raise_for_status()

        result = response.json()
        print(f"✅ Транспорт назначен")
        return result