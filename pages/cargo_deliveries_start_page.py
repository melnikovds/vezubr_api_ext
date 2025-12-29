import requests
import json
from typing import Dict, Any


class CargoDeliveriesStartClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {"Authorization": token}

    def start_cargo_delivery(self, cargo_delivery_id: str) -> Dict[str, Any]:
        """
        Начало исполнения рейса
        Эндпоинт: POST /v1/api-ext/cargo-deliveries/{id}/start

        Args:
            cargo_delivery_id: ID рейса (тот же что и truck_delivery_id)

        Returns:
            Ответ от API
        """
        url = f"{self.base_url}/cargo-deliveries/{cargo_delivery_id}/start"

        print(f"🚀 [CargoDeliveriesStart] Начало исполнения рейса {cargo_delivery_id}")

        response = requests.post(url, headers=self.headers, timeout=30)

        if response.status_code != 200:
            print(f"❌ Ошибка начала рейса: {response.status_code}")
            print(f"Ответ: {response.text}")
            response.raise_for_status()

        result = response.json()
        print(f"✅ Рейс начат")
        return result
