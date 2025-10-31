import random
import requests
from datetime import datetime


class AddressPage:
    @staticmethod
    def list_addresses(base_url: str, token: str, items_per_page: int = 100) -> list:
        """Получить список всех адресов."""
        headers = {"Authorization": token}
        response = requests.post(
            f"{base_url}/contractor-point/list-info",
            headers=headers,
            json={"itemsPerPage": items_per_page}
        )
        response.raise_for_status()
        return response.json()["points"]

    @staticmethod
    def find_by_external_id(base_url: str, token: str, external_id: str) -> dict | None:
        """Найти адрес по externalId."""
        addresses = AddressPage.list_addresses(base_url, token, items_per_page=1000)
        return next((a for a in addresses if a.get("externalId") == external_id), None)

    @staticmethod
    def create_or_update_address(base_url: str, token: str, payload: dict) -> int:
        """Создать или обновить адрес. Возвращает id."""
        headers = {"Authorization": token}
        response = requests.post(
            f"{base_url}/contractor-point/update",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json().get("id", 0)
    def create_address_payload(**overrides) -> dict:
        # Генерация уникального externalId
        external_id = f"Izhevsk {random.randint(1, 100)}-{random.randint(1, 1000)}"

        # Генерация времени для title
        current_time = datetime.now().strftime("%H:%M:%S")
        default_title = f"Авто. API Ижевск {current_time}"

        payload = {
            "addressString": overrides.get("addressString", "Россия, г Ижевск, ул Дзержинского, д 61"),
            "title": overrides.get("title", default_title),
            "timezone": overrides.get("timezone", "Europe/Samara"),
            "externalId": overrides.get("externalId", external_id),  # ← рандомный ID
            "status": overrides.get("status", True),
            "latitude": overrides.get("latitude", 56.883786581427415),
            "longitude": overrides.get("longitude", 53.24970983252293),
            "cityName": overrides.get("cityName", "Ижевск"),
            "addressType": overrides.get("addressType", 2),
            "loadingType": overrides.get("loadingType", 1),
            "liftingCapacityMax": overrides.get("liftingCapacityMax", random.randint(2000, 5000)),
            "vicinityRadius": overrides.get("vicinityRadius", random.randint(2000, 40000)),
            "maxHeightFromGroundInCm": overrides.get("maxHeightFromGroundInCm", 300),
            "comment": overrides.get("comment", "что то привезли/увезли"),
            "necessaryPass": overrides.get("necessaryPass", 0),
            "statusFlowType": overrides.get("statusFlowType", "fullFlow"),
            "cart": overrides.get("cart", 0),
            "elevator": overrides.get("elevator", 0),
            "isFavorite": overrides.get("isFavorite", 0),
            "pointOwnerInn": None,
            "pointOwnerKpp": None,
            "pointArrivalDuration": None,
            "pointDepartureDuration": None,
            "contacts": overrides.get("contacts", [{"contact": None, "email": None, "phone": None}]),
            "attachedFiles": overrides.get("attachedFiles", []),
            "averageOperationTime": overrides.get("averageOperationTime", [0]),
            "openingHours": overrides.get("openingHours", []),
            "group": overrides.get("group", ""),
        }
        payload.update(overrides)
        return payload