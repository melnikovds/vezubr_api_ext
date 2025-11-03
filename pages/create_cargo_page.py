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
            cargo_type: Optional[str] = None,
            weight_kg: Optional[int] = None,
            volume_m3: Optional[int] = None,
            comment: str = "Тестирование внешнего API"
    ) -> Dict[str, Any]:
        # Увеличиваем счётчик и формируем title
        CargoPlaceClient._counter += 1
        title = f"API-{CargoPlaceClient._counter:05d}"  # например: API-00042

        # Рандомизация параметров
        actual_type = cargo_type or random.choice(self.CARGO_TYPES)
        weight_kg = weight_kg or random.randint(100, 1000)
        volume_m3 = volume_m3 or random.randint(1, 3)

        payload = {
            "type": actual_type,
            "title": title,  
            "volume": volume_m3 * 1_000_000,  # м³ → см³
            "weight": weight_kg * 1000,  # кг → г
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
        response.raise_for_status()
        return response.json()
