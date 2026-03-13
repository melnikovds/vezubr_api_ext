import requests
import json
from typing import Dict, Any


class CargoDeliveriesCancelClient:
    """
    Клиент для отмены рейса (Truck Delivery)
    Эндпоинт: POST /v1/api-ext/cargo-deliveries/{id}/cancel
    """

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {"Authorization": token}

    def cancel_cargo_delivery(self, truck_delivery_id: str) -> Dict[str, Any]:
        """
        Отмена рейса через ЭП

        Args:
            truck_delivery_id: ID рейса для отмены

        Returns:
            dict: ответ от API
        """
        url = f"{self.base_url}/cargo-deliveries/{truck_delivery_id}/cancel"

        print(f"🔄 [CargoDeliveriesCancel] Отмена рейса {truck_delivery_id}")

        response = requests.post(url, headers=self.headers, timeout=30)

        if response.status_code != 200:
            print(f"❌ Ошибка отмены рейса: {response.status_code}")
            print(f"Ответ: {response.text}")
            response.raise_for_status()

        result = response.json()
        print(f"✅ Рейс успешно отменен")
        return result