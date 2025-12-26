import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List


class TransportRequestClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {"Authorization": token}

    def get_order_details(self, order_id: int) -> dict:
        response = requests.get(
            f"{self.base_url}/order/{order_id}/details",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json()

    def create_transport_request(
            self,
            addresses: List[Dict[str, Any]],  # весь маршрут (5 точек)
            cargo_place_specs: List[Dict[str, Any]],  # спецификации грузомест с позициями
            client_id: int,
            producer_id: int,
            contract_id: int,
            order_identifier: str,
            inner_comment: str = "Тестовое создание рейса"
    ) -> Dict[str, Any]:
        now = datetime.now()
        start_date = (now + timedelta(days=1)).strftime("%Y-%m-%d")
        start_time = "10:00"

        # Подготовка адресов с position
        route = []
        for i, addr in enumerate(addresses):
            route.append({
                "id": addr["id"],
                "externalId": addr["externalId"],
                "latitude": addr.get("latitude"),
                "longitude": addr.get("longitude"),
                "addressString": addr["addressString"],
                "cityName": addr.get("cityName") or "Ижевск",
                "cityFiasId": addr.get("cityFiasId"),
                "timeZoneId": addr.get("timezone") or "Europe/Samara",
                "contacts": addr.get("contacts") or [""],
                "phone": addr.get("phone") or "",
                "email": addr.get("email") or "",
                "title": addr.get("title") or "Адрес",
                "attachedFiles": [],
                "isLoadingWork": (i == 0),  # первая — загрузка
                "isUnloadingWork": (i == len(addresses) - 1),  # последняя — выгрузка
                "position": i + 1,  # ← обязательно!
                "loadingType": addr.get("loadingType", 1),
                "statusFlowType": "fullFlow"
            })

        payload = {
            "toStartAtDate": start_date,
            "toStartAtTime": start_time,
            "requiredProducers": [producer_id],
            "client": client_id,
            "orderIdentifier": order_identifier,
            "innerComment": inner_comment,
            "publicComment": "",
            "publishingType": "rate",
            "clientRate": 50000,
            "parametersForProducers": [{
                "producer": producer_id,
                "tariff": 0,
                "contract": contract_id
            }],
            "orderType": 1,
            "vehicleType": 1,
            "bodyTypes": [3, 4],
            "addresses": route,
            "cargoPlaces": cargo_place_specs
        }

        response = requests.post(
            f"{self.base_url}/order/transport-request/create",
            headers=self.headers,
            json=payload
        )
        if response.status_code != 200:
            print(f"\n❌ Ошибка: {response.status_code}")
            print(f"Ответ: {response.text}")
            print(f"Тело запроса: {json.dumps(payload, ensure_ascii=False, indent=2)}")
            assert False, f"Ошибка создания рейса: {response.status_code}"

        return response.json()

    def create_and_publish_transport_request(
            self,
            addresses: List[Dict[str, Any]],
            cargo_place_specs: List[Dict[str, Any]],
            client_id: int,
            producer_id: int,
            contract_id: int,
            order_identifier: str,
            inner_comment: str = "Тестовое создание рейса (с публикацией)"
    ) -> Dict[str, Any]:
        now = datetime.now()
        start_date = (now + timedelta(days=1)).strftime("%Y-%m-%d")
        start_time = "10:00"

        # Формируем маршрут с position
        route = []
        for i, addr in enumerate(addresses):
            route.append({
                "id": addr["id"],
                "externalId": addr.get("externalId", ""),
                "latitude": addr.get("latitude"),
                "longitude": addr.get("longitude"),
                "addressString": addr["addressString"],
                "cityName": addr.get("cityName") or "Ижевск",
                "cityFiasId": addr.get("cityFiasId"),
                "timeZoneId": addr.get("timezone") or "Europe/Samara",
                "contacts": addr.get("contacts") or [""],
                "phone": addr.get("phone") or "",
                "email": addr.get("email") or "",
                "title": addr.get("title") or "Адрес",
                "attachedFiles": [],
                "isLoadingWork": (i == 0),
                "isUnloadingWork": (i == len(addresses) - 1),
                "position": i + 1,
                "loadingType": addr.get("loadingType", 1),
                "statusFlowType": "fullFlow"
            })

        payload = {
            "toStartAtDate": start_date,
            "toStartAtTime": start_time,
            "requiredProducers": [producer_id],
            "client": client_id,
            "orderIdentifier": order_identifier,
            "innerComment": inner_comment,
            "publicComment": "",
            "publishingType": "rate",
            "clientRate": 50000,
            "parametersForProducers": [{
                "producer": producer_id,
                "tariff": 0,
                "contract": contract_id
            }],
            "orderType": 1,
            "vehicleType": 1,
            "bodyTypes": [3, 4],
            "addresses": route,
            "cargoPlaces": cargo_place_specs
        }

        # Используем /create-and-publish вместо /create
        response = requests.post(
            f"{self.base_url}/order/transport-request/create-and-publish",
            headers=self.headers,
            json=payload
        )

        if response.status_code != 200:
            print(f"\n❌ Ошибка создания и публикации рейса: {response.status_code}")
            print(f"URL: {response.url}")
            print(f"Ответ: {response.text}")
            print(f"Запрос: {json.dumps(payload, ensure_ascii=False, indent=2)}")
            response.raise_for_status()

        return response.json()