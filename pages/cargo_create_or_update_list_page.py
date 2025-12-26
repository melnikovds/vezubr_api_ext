import random
from typing import List, Dict, Any
import requests
from datetime import datetime, timedelta


class CargoPlaceCreateOrUpdateListClient:
    CARGO_TYPES = ["free", "pallet", "box", "bag"]

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }

    def _generate_random_dimensions(self) -> Dict[str, int]:
        length = random.randint(10, 200)
        width = random.randint(10, 150)
        height = random.randint(10, 150)
        volume = length * width * height
        weight = random.randint(500, 20000)
        quantity = random.randint(1, 50)
        return {
            "length": length,
            "width": width,
            "height": height,
            "volume": volume,
            "weight": weight,
            "quantity": quantity
        }

    def _generate_random_datetime_window(self) -> Dict[str, str]:
        base = datetime.now()
        start = base.replace(hour=9, minute=0, second=0, microsecond=0)
        end = base.replace(hour=18, minute=0, second=0, microsecond=0)
        return {
            "requiredSendAtFrom": start.isoformat(),
            "requiredSendAtTill": end.isoformat(),
            "requiredDeliveredAtFrom": (start + timedelta(days=2)).isoformat(),
            "requiredDeliveredAtTill": (end + timedelta(days=2)).isoformat(),
        }

    def generate_cargo_place(
            self,
            departure_external_id: str,
            delivery_external_id: str,
            external_id: str,
            bar_code: str,
            invoice_number: str,
            is_planned: bool = False
    ) -> Dict[str, Any]:
        dims = self._generate_random_dimensions()
        time_windows = self._generate_random_datetime_window()

        return {
            "status": "waiting_for_sending",  # не требует statusAddress
            "barCode": bar_code,
            "type": random.choice(self.CARGO_TYPES),
            "departureAddressExternalId": departure_external_id,
            "deliveryAddressExternalId": delivery_external_id,
            "invoiceNumber": invoice_number,
            "invoiceNumbers": [invoice_number],
            "externalId": external_id,
            "isPlanned": is_planned,
            **dims,
            **time_windows,
            "wmsNumber": f"WMS-{external_id}",
            "invoiceDate": "2025-03-14",
            # ИНН/КПП НЕ указываем — не обязательны и могут вызвать ошибку
        }

    def create_or_update_cargo_places_list(self, cargo_places: List[Dict[str, Any]]) -> Dict[str, Any]:
        url = f"{self.base_url}/cargo-place/create-or-update-list"
        payload = {"data": cargo_places}

        response = requests.post(url, headers=self.headers, json=payload)

        if response.status_code != 200:
            print(f"\n❌ Ошибка create-or-update-list: {response.status_code}")
            print(f"URL: {url}")
            print(f"Тело запроса: {payload}")
            print(f"Ответ сервера: {response.text}")
            response.raise_for_status()

        return response.json()
