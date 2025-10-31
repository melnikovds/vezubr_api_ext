import random
from typing import Optional, Dict, Any
import requests


class CargoPlaceClient:
    CARGO_TYPES = ["pallet", "box", "bag"]
    _counter = 0  # классовый счётчик

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {"Authorization": token}

    def create_cargo_place(
        self,
        departure_external_id: str,
        delivery_external_id: str,
        title: str = None,
        external_id: str = None,
        cargo_type: Optional[str] = None,
        weight_kg: Optional[int] = None,
        volume_m3: Optional[int] = None,
        comment: str = "Тестирование внешнего API"
    ) -> Dict[str, Any]:
        # Генерация title, если не задан
        if title is None:
            CargoPlaceClient._counter += 1
            title = f"API-{CargoPlaceClient._counter:05d}"

        actual_type = cargo_type or random.choice(self.CARGO_TYPES)
        weight_kg = weight_kg or random.randint(100, 1000)
        volume_m3 = volume_m3 or random.randint(1, 3)

        volume = int(volume_m3 * 1_000_000)  # ← int, а не float
        weight = int(weight_kg * 1000)

        payload = {
            "type": actual_type,
            "title": title,
            "externalId": external_id,
            "volume": volume,
            "weight": weight,
            "reverseCargoType": "other",
            "reverseCargoReason": "",
            "comment": comment,
            "status": "new",
            "departureAddressExternalId": departure_external_id,
            "deliveryAddressExternalId": delivery_external_id,
        }

        response = requests.post(
            f"{self.base_url}/cargo-place/create-or-update",
            headers=self.headers,
            json=payload
        )

        # Отладочный вывод при ошибке
        if response.status_code != 200:
            print(f"\n❌ Ошибка создания грузоместа: {response.status_code}")
            print(f"URL: {response.url}")
            print(f"Тело запроса: {payload}")
            print(f"Ответ сервера: {response.text}")
            assert False, f"Сервер вернул ошибку: {response.status_code}"

        result = response.json()
        print(f"✅ Грузоместо создано: ID={result.get('id')}, title={result.get('title')}")
        return result