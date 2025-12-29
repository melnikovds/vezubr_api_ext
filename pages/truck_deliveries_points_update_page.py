import requests
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List


class TruckDeliveriesPointsUpdateClient:
    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": token,
            "Content-Type": "application/json"
        }

    def complete_all_points(self, truck_delivery_id: str) -> Dict[str, Any]:
        """
        Завершение рейса в правильном формате как на фронте
        """
        url = f"{self.base_url}/truck-deliveries/{truck_delivery_id}/points/update/statuses"

        # Текущее время в UTC
        from datetime import datetime, timezone, timedelta
        now = datetime.now(timezone.utc)

        # Базовое время: 20 секунд назад (чтобы все было в прошлом)
        base_time = now - timedelta(seconds=20)

        # Важно: форматируем как на фронте - "YYYY-MM-DDTHH:MM:SSZ" (без +00:00!)
        def format_frontend_time(dt):
            # Убираем микросекунды и timezone offset, добавляем Z
            return dt.replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%S") + "Z"

        # Создаем точки как на фронте:
        points = [
            {
                "position": 1,
                "startedAt": format_frontend_time(base_time + timedelta(seconds=0)),
                "completedAt": format_frontend_time(base_time + timedelta(seconds=4))
            },
            {
                "position": 2,
                "startedAt": format_frontend_time(base_time + timedelta(seconds=7)),
                "completedAt": format_frontend_time(base_time + timedelta(seconds=11))
            },
            {
                "position": 3,
                "startedAt": format_frontend_time(base_time + timedelta(seconds=15)),
                "completedAt": format_frontend_time(base_time + timedelta(seconds=20))
            }
        ]

        payload = {"points": points}

        print(f"🏁 [TruckDeliveriesPointsUpdate] Завершение рейса {truck_delivery_id}")
        print(f"   Формат как на фронте (без +00:00):")
        for i, point in enumerate(points, 1):
            print(f"   Точка {i}: startedAt={point['startedAt']}, completedAt={point['completedAt']}")
        print(f"   Все времена в прошлом относительно: {format_frontend_time(now)}")

        response = requests.post(url, json=payload, headers=self.headers, timeout=30)

        if response.status_code != 200:
            print(f"❌ Ошибка завершения рейса: {response.status_code}")
            print(f"Ответ: {response.text}")
            print(f"Запрос: {json.dumps(payload, indent=2, ensure_ascii=False)}")
            response.raise_for_status()

        result = response.json()
        print(f"✅ Рейс завершен: {result}")
        return result

    def complete_all_points_simple(self, truck_delivery_id: str) -> Dict[str, Any]:
        """Простой вариант завершения - с startedAt и completedAt"""
        url = f"{self.base_url}/truck-deliveries/{truck_delivery_id}/points/update/statuses"

        from datetime import datetime, timezone, timedelta

        # Время в прошлом (2 минуты назад)
        past_time = datetime.now(timezone.utc) - timedelta(minutes=2)

        def format_frontend_time(dt):
            return dt.replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%S") + "Z"

        time_str = format_frontend_time(past_time)
        time_str_started = format_frontend_time(past_time - timedelta(seconds=30))

        payload = {
            "points": [
                {
                    "position": 1,
                    "startedAt": time_str_started,
                    "completedAt": time_str
                },
                {
                    "position": 2,
                    "startedAt": time_str_started,
                    "completedAt": time_str
                },
                {
                    "position": 3,
                    "startedAt": time_str_started,
                    "completedAt": time_str
                }
            ]
        }

        print(f"🏁 [SimpleComplete] Завершение рейса {truck_delivery_id}")
        print(f"   startedAt: {time_str_started}, completedAt: {time_str}")

        response = requests.post(url, json=payload, headers=self.headers, timeout=30)

        if response.status_code != 200:
            print(f"⚠️ Ошибка простого завершения: {response.status_code}")
            print(f"Ответ: {response.text[:200]}")
            # Пробуем еще более простой вариант
            return self.complete_all_points_minimal(truck_delivery_id)

        result = response.json()
        print(f"✅ Рейс завершен простым способом: {result}")
        return result

    def complete_all_points_minimal(self, truck_delivery_id: str) -> Dict[str, Any]:
        """Минимальный вариант завершения - только completedAt"""
        url = f"{self.base_url}/truck-deliveries/{truck_delivery_id}/points/update/statuses"

        from datetime import datetime, timezone, timedelta

        # Время в далеком прошлом (вчера)
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)

        def format_frontend_time(dt):
            return dt.replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%S") + "Z"

        time_str = format_frontend_time(yesterday)

        payload = {
            "points": [
                {"position": 1, "completedAt": time_str},
                {"position": 2, "completedAt": time_str},
                {"position": 3, "completedAt": time_str}
            ]
        }

        print(f"🏁 [MinimalComplete] Завершение рейса {truck_delivery_id}")
        print(f"   completedAt (вчера): {time_str}")

        response = requests.post(url, json=payload, headers=self.headers, timeout=30)

        if response.status_code != 200:
            print(f"❌ Ошибка минимального завершения: {response.status_code}")
            print(f"Ответ: {response.text[:200]}")
            raise Exception(f"Не удалось завершить рейс никаким способом: {response.text}")

        result = response.json()
        print(f"✅ Рейс завершен минимальным способом: {result}")
        return result


    def update_points_statuses(self, truck_delivery_id: str, points_count: int = 3) -> Dict[str, Any]:
        """Старый метод для обратной совместимости"""
        print(f"⚠️  Используется устаревший метод update_points_statuses, используйте complete_all_points")
        return self.complete_all_points(truck_delivery_id)
