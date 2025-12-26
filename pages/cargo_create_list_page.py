import random
from typing import List, Dict, Any
import requests
from datetime import datetime, timedelta


class CargoPlaceListClient:
    CARGO_TYPES = ["free", "pallet", "box", "bag"]

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }

    def _generate_random_dimensions(self) -> Dict[str, int]:
        """Генерирует случайные, но валидные размеры и вес."""
        length = random.randint(10, 200)  # см
        width = random.randint(10, 150)
        height = random.randint(10, 150)
        volume = length * width * height  # см³
        weight = random.randint(500, 20000)  # граммы
        quantity = random.randint(1, 50)

        return {
            "length": length,
            "width": width,
            "height": height,
            "volume": volume,
            "weight": weight,
            "quantity": quantity
        }

    def _generate_random_datetime_window(self, base_days_offset: int = 0) -> Dict[str, str]:
        """Генерирует временные окна отправки/доставки."""
        base = datetime.now() + timedelta(days=base_days_offset)
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
            is_planned: bool = False,
            producer_id: int = None,
            contract_id: int = None,
            client_id: int = None,
    ) -> Dict[str, Any]:
        dims = self._generate_random_dimensions()
        time_windows = self._generate_random_datetime_window()

        cargo = {
            "status": "waiting_for_sending",
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
        }

        # Контекст — критично для валидации адресов
        if producer_id is not None:
            cargo["producerId"] = producer_id
        if contract_id is not None:
            cargo["contractId"] = contract_id
        if client_id is not None:
            cargo["clientId"] = client_id

        return cargo

    def create_cargo_places_list(self, cargo_places: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Отправляет POST-запрос на /create-list."""
        url = f"{self.base_url}/cargo-place/create-list"
        payload = {"data": cargo_places}

        response = requests.post(url, headers=self.headers, json=payload)

        if response.status_code != 200:
            print(f"\n❌ Ошибка создания списка грузомест: {response.status_code}")
            print(f"URL: {url}")
            print(f"Тело запроса: {payload}")
            print(f"Ответ сервера: {response.text}")
            response.raise_for_status()

        return response.json()
