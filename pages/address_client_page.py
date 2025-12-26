import requests
from typing import Dict, Any, List, Optional


class AddressClient:
    """
    Простой клиент для работы с адресами
    """

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.headers = {"Authorization": token}

    def get_my_addresses(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Получение адресов текущего пользователя
        """
        try:
            response = requests.get(
                f"{self.base_url}/addresses",
                headers=self.headers,
                params={"limit": limit},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                return data.get("items", [])
            else:
                print(f"⚠️  Ошибка получения адресов: {response.status_code}")
                return []

        except Exception as e:
            print(f"⚠️  Исключение при получении адресов: {e}")
            return []