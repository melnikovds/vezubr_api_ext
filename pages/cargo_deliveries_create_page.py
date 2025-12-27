import requests
import json
from typing import Dict, Any


class CargoDeliveriesCreateClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {"Authorization": token}

    def create_cargo_delivery(self, request_id: str, producer_id: int) -> str:
        """
        Создание рейса (Truck Delivery) внутри заявки
        Эндпоинт: POST /v1/api-ext/cargo-deliveries/create

        Args:
            request_id: UUID FTL заявки
            producer_id: ID подрядчика (LKP)

        Returns:
            truck_delivery_id: ID созданного рейса (для дальнейших операций)
        """
        url = f"{self.base_url}/cargo-deliveries/create"

        payload = {
            "requests": [request_id],
            "type": "truck",
            "producer": producer_id
        }

        print(f"🚚 [CargoDeliveriesCreate] Создание рейса для заявки {request_id}")
        print(f"   Подрядчик (producer): {producer_id}")

        response = requests.post(url, json=payload, headers=self.headers, timeout=30)

        if response.status_code != 200:
            print(f"❌ Ошибка создания рейса: {response.status_code}")
            print(f"Ответ: {response.text}")
            print(f"Запрос: {json.dumps(payload, indent=2, ensure_ascii=False)}")
            response.raise_for_status()

        result = response.json()
        truck_delivery_id = result.get("id")

        if not truck_delivery_id:
            raise ValueError(f"Ответ не содержит ID рейса. Полный ответ: {result}")

        print(f"✅ Рейс создан: truck_delivery_id={truck_delivery_id}")
        return truck_delivery_id