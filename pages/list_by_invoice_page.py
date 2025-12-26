import requests
from typing import Dict, Any


class ListByInvoiceClient:
    """Клиент для работы с эндпоинтом /cargo-place/list-by-invoice"""



    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {"Authorization": token}

    def list_by_invoice(self, invoice_number: str) -> Dict[str, Any]:
        """
        Запрос статусов грузомест по номеру заявки (invoiceNumber).
        :param invoice_number: Номер заявки
        :return: Ответ API (dict)
        """
        payload = {"invoiceNumber": invoice_number}
        response = requests.post(
            f"{self.base_url}/cargo-place/list-by-invoice",
            headers=self.headers,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    def get_cargo_place_by_id(self, invoice_number: str, cargo_place_id: int):
        """
        Возвращает одно грузоместо из ответа по cargoPlaceId.
        Выбрасывает AssertionError, если не найдено.
        """
        resp = self.list_by_invoice(invoice_number)

        print(f"🔍 Поиск грузоместа по cargoPlaceId={cargo_place_id} в invoice='{invoice_number}'")
        print(f"   Найдено грузомест: {len(resp.get('cargoPlaces', []))}")

        for cp in resp.get("cargoPlaces", []):
            if cp.get("cargoPlaceId") == cargo_place_id:
                print(f"✅ Найдено грузоместо: cargoPlaceId={cp.get('cargoPlaceId')}, barcode={cp.get('barcode')}")
                return cp

        raise AssertionError(
            f"Грузоместо с cargoPlaceId='{cargo_place_id}' не найдено в ответе для invoice='{invoice_number}'. "
            f"Найдены cargoPlaceIds: {[cp.get('cargoPlaceId') for cp in resp.get('cargoPlaces', [])]}"
        )

    # Старый метод оставляем, но в тесте использовать не будем
    def get_cargo_place_by_barcode(self, invoice_number: str, barcode: str):
        """
        Возвращает одно грузоместо из ответа по barcode (== externalId).
        Выбрасывает AssertionError, если не найдено.
        """
        resp = self.list_by_invoice(invoice_number)

        print(f"🔍 Полный ответ от /list-by-invoice для invoice '{invoice_number}':")
        print(f"   Статус ответа: {resp.get('status', 'N/A')}")
        print(f"   Найдено грузомест: {len(resp.get('cargoPlaces', []))}")
        print(f"   Ищем barcode: '{barcode}'")

        for i, cp in enumerate(resp.get("cargoPlaces", [])):
            found_barcode = cp.get('barcode')
            found_id = cp.get('cargoPlaceId')
            found_status = cp.get('status')
            print(f"   [{i}] barcode: '{found_barcode}', cargoPlaceId: {found_id}, status: {found_status}")

        for cp in resp.get("cargoPlaces", []):
            if cp.get("barcode") == barcode:
                return cp

        raise AssertionError(
            f"Грузоместо с barcode='{barcode}' не найдено в ответе для invoice='{invoice_number}'. "
            f"Найдены barcodes: {[cp.get('barcode') for cp in resp.get('cargoPlaces', [])]}"
        )

