import requests
import json
from typing import Dict, Any, List, Optional


class ReplacePlannedPairsClient:
    """Клиент для работы с эндпоинтом /cargo-place/replace-planned-pairs"""

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url
        self.headers = {"Authorization": token}

    def replace_planned_pairs(
            self,
            items: List[Dict[str, Any]],
            is_strict: bool = False
    ) -> List[Any]:
        """
        Замена плановых ГМ на фактические парами

        :param items: Список пар для замены
        :param is_strict: Флаг строгой проверки ошибок
        :return: Ответ API (обычно пустой список при успехе)
        """
        payload = {
            "items": items,
            "isStrict": is_strict
        }

        print(f"📤 Запрос к /cargo-place/replace-planned-pairs:")
        print(f"   URL: {self.base_url}/cargo-place/replace-planned-pairs")
        print(f"   Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")

        response = requests.post(
            f"{self.base_url}/cargo-place/replace-planned-pairs",
            headers=self.headers,
            json=payload,
            timeout=10
        )

        print(f"📥 Ответ: {response.status_code}")
        print(f"   Тело: {response.text}")

        response.raise_for_status()
        return response.json()

    def replace_by_ids(
            self,
            planned_id: int,
            cargo_place_id: int,
            is_strict: bool = False
    ) -> List[Any]:
        """
        Замена по ID Везубр (плановый ID -> фактический ID)
        """
        items = [{
            "plannedId": planned_id,
            "cargoPlaceId": cargo_place_id
        }]

        return self.replace_planned_pairs(items, is_strict)

    def replace_by_external_ids(
            self,
            planned_external_id: str,
            cargo_place_external_id: str,
            is_strict: bool = False
    ) -> List[Any]:
        """
        Замена по externalId (плановый externalId -> фактический externalId)
        """
        items = [{
            "plannedExternalId": planned_external_id,
            "cargoPlaceExternalId": cargo_place_external_id
        }]

        return self.replace_planned_pairs(items, is_strict)

    def replace_multiple_pairs(
            self,
            pairs: List[tuple],
            use_external_ids: bool = False,
            is_strict: bool = False
    ) -> List[Any]:
        """
        Замена нескольких пар ГМ

        :param pairs: Список кортежей (planned, actual)
        :param use_external_ids: Использовать externalId вместо ID
        :param is_strict: Флаг строгой проверки
        """
        items = []

        for planned, actual in pairs:
            if use_external_ids:
                items.append({
                    "plannedExternalId": planned,
                    "cargoPlaceExternalId": actual
                })
            else:
                items.append({
                    "plannedId": planned,
                    "cargoPlaceId": actual
                })

        return self.replace_planned_pairs(items, is_strict)

    def check_endpoint_availability(self) -> Dict[str, Any]:
        """
        Проверка доступности эндпоинта
        """
        result = {
            "available": False,
            "status_code": None,
            "error": None
        }

        try:
            print("🔍 Проверяем доступность /cargo-place/replace-planned-pairs...")

            # Пробуем вызвать эндпоинт с тестовыми данными
            test_payload = {
                "items": [{
                    "plannedId": 999999,  # Несуществующий ID
                    "cargoPlaceId": 999999
                }],
                "isStrict": False
            }

            response = requests.post(
                f"{self.base_url}/cargo-place/replace-planned-pairs",
                headers=self.headers,
                json=test_payload,
                timeout=10
            )

            result["status_code"] = response.status_code
            result["available"] = True
            print(f"✅ Эндпоинт доступен, статус: {response.status_code}")

        except requests.exceptions.HTTPError as e:
            result["status_code"] = e.response.status_code
            result["error"] = str(e)
            result["available"] = True  # Эндпоинт доступен, но вернул ошибку
            print(f"✅ Эндпоинт доступен (HTTP ошибка {e.response.status_code})")

        except Exception as e:
            result["error"] = str(e)
            print(f"❌ Эндпоинт недоступен: {e}")

        return result