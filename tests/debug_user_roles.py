# tests/debug_request_structure.py
import os
import requests
import json
import uuid
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Загружаем .env
dotenv_path = Path(__file__).parent / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)

# Базовый URL из вашего settings.py
DOMAIN = os.getenv("DOMAIN", "com")
BASE_URL = f"https://api.vezubr.{DOMAIN}/v1/api-ext"

# Импортируем CargoDeliveryClient
import sys

sys.path.append(str(Path(__file__).parent.parent))
from pages.cargo_delivery_page import CargoDeliveryClient


def debug_request_structure():
    """Смотрим полную структуру созданной заявки"""

    # Логинимся как LKZ
    lkz_login = requests.post(
        f"{BASE_URL}/user/login",
        json={"username": os.getenv("LKZ_EMAIL"), "password": os.getenv("LKZ_PASSWORD")}
    )
    lkz_token = lkz_login.json()["token"]

    print("🔍 Анализ структуры заявки...")

    lkz_client = CargoDeliveryClient(BASE_URL, lkz_token)

    test_addresses = [27648, 27649, 27650]
    departure_id, delivery_id = test_addresses[0], test_addresses[1]

    route = [
        lkz_client.create_route_point(
            point_id=departure_id,
            position=1,
            is_loading_work=True,
            is_unloading_work=False,
            required_arrive_at=(datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y %H:%M")
        ),
        lkz_client.create_route_point(
            point_id=delivery_id,
            position=2,
            is_loading_work=False,
            is_unloading_work=True
        )
    ]

    # Пробуем разные producer_id
    test_producers = [1939, 1599, None]  # LKE, LKP, и без назначения

    for producer_id in test_producers:
        print(f"\n{'=' * 60}")
        print(f"🔍 Тестируем producer_id: {producer_id}")

        client_identifier = f"DEBUG-{uuid.uuid4().hex[:8].upper()}"

        # Подготовка payload
        payload = {
            "deliveryType": "auto",
            "deliverySubType": "ftl",
            "parametersDetails": {
                "requiredBodyTypes": [3, 4, 7, 8],
                "requiredVehicleTypeId": 1,
                "orderType": 1,
                "pointChangeType": 2,
                "points": route
            },
            "comment": f"Тест назначения на {producer_id}",
            "clientIdentifier": client_identifier,
            "rate": 140000
        }

        # Добавляем producer_id только если он указан
        if producer_id is not None:
            payload["producerId"] = producer_id

        print(f"📦 Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")

        # Создаем заявку
        headers = {"Authorization": lkz_token, "Content-Type": "application/json"}
        response = requests.post(
            f"{BASE_URL}/cargo-delivery-requests/create-and-publish",
            headers=headers,
            json=payload
        )

        if response.status_code != 200:
            print(f"❌ Ошибка создания: {response.status_code} - {response.text}")
            continue

        response_data = response.json()
        request_id = response_data["id"]
        request_nr = response_data["requestNr"]

        print(f"✅ Заявка создана: {request_nr}")
        print(f"   Ответ создания:")
        print(f"   - ID: {response_data.get('id')}")
        print(f"   - Номер: {response_data.get('requestNr')}")
        print(f"   - Статус: {response_data.get('status')}")
        print(f"   - Producer в ответе: {response_data.get('producer')}")
        print(f"   - Все ключи в ответе: {list(response_data.keys())}")

        # Смотрим детали
        print(f"\n   📋 Детали заявки:")
        details_response = requests.get(
            f"{BASE_URL}/cargo-delivery-requests/{request_id}/details",
            headers=headers
        )

        if details_response.status_code == 200:
            details = details_response.json()
            print(f"   - Статус: {details.get('status')}")
            print(f"   - Producer: {details.get('producer')}")
            print(f"   - Клиент: {details.get('client', {}).get('title')}")
            print(f"   - SelectingStrategy: {details.get('selectingStrategy')}")
            print(f"   - Все ключи в деталях: {list(details.keys())}")

            # Если есть producer, покажем его структуру
            producer = details.get('producer')
            if producer:
                print(f"   🏢 Структура producer:")
                print(f"      - ID: {producer.get('id')}")
                print(f"      - Название: {producer.get('title')}")
                print(f"      - ИНН: {producer.get('inn')}")
                print(f"      - Все ключи producer: {list(producer.keys())}")
        else:
            print(f"   ❌ Ошибка получения деталей: {details_response.status_code}")


if __name__ == "__main__":
    debug_request_structure()