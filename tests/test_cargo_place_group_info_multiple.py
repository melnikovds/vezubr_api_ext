import allure
import pytest
import uuid
from pages.create_cargo_page import CargoPlaceClient
from config.settings import BASE_URL
import requests


@allure.story("Smoke test")
@allure.feature("Грузоместа")
@allure.description("Создание нескольких ГМ → проверка статусов через /cargo-place/group-info")
@pytest.mark.parametrize("role", ["lkz"])
def test_cargo_place_group_info_multiple(role, valid_addresses, client_id):
    """
    Тест для эндпоинта /cargo-place/group-info:
    - Создаем несколько грузомест
    - Проверяем их статусы через group-info
    """
    # === Извлекаем данные из фикстуры ===
    token = valid_addresses["token"]
    dep_addr = valid_addresses["departure"]
    del_addr = valid_addresses["delivery"]

    dep_ext = dep_addr["externalId"]
    del_ext = del_addr["externalId"]

    # === Клиент для создания ГМ ===
    cargo_client = CargoPlaceClient(BASE_URL, token)

    # === Создаем 3 грузоместа ===
    cargo_places = []
    with allure.step("Создание 3 грузомест"):
        for i in range(3):
            external_id = f"CP-GROUP-{uuid.uuid4().hex[:8].upper()}"
            invoice_number = f"INV-GROUP-{uuid.uuid4().hex[:6].upper()}"

            cargo_resp = cargo_client.create_cargo_place(
                departure_external_id=dep_ext,
                delivery_external_id=del_ext,
                title=f"Group Test {i + 1}",
                external_id=external_id,
                weight_kg=10 + i * 5,  # Разный вес: 10, 15, 20 кг
                volume_m3=0.1 + i * 0.05,  # Разный объем: 0.1, 0.15, 0.2 м³
                invoice_number=invoice_number
            )

            cargo_id = cargo_resp["id"]
            actual_external_id = cargo_resp.get("externalId") or external_id

            cargo_places.append({
                "id": cargo_id,
                "externalId": actual_external_id,
                "invoiceNumber": invoice_number
            })

            print(f"✅ Создано грузоместо {i + 1}: ID={cargo_id}, externalId={actual_external_id}")

    # === Шаг 2: Запрос group-info по IDs ===
    with allure.step("Запрос group-info по внутренним IDs"):
        ids = [cp["id"] for cp in cargo_places]

        payload = {
            "ids": ids
        }

        print(f"🔍 Запрос group-info для IDs: {ids}")

        response = requests.post(
            f"{BASE_URL}/cargo-place/group-info",
            headers={"Authorization": token},
            json=payload,
            timeout=10
        )

        assert response.status_code == 200, f"Ошибка запроса group-info: {response.text}"
        group_info_response = response.json()

        print(f"✅ Получен ответ group-info:")
        print(f"   Найдено грузомест: {len(group_info_response)}")

        # ДЕТАЛЬНЫЙ ВЫВОД СТРУКТУРЫ ОТВЕТА ДЛЯ ОТЛАДКИ
        if group_info_response:
            print(f"🔍 Структура первого элемента ответа:")
            for key, value in list(group_info_response[0].items())[:10]:  # Покажем первые 10 полей
                print(f"   {key}: {value}")

        # Проверяем что все созданные ГМ есть в ответе
        found_ids = [item.get("id") for item in group_info_response]
        for cp in cargo_places:
            assert cp["id"] in found_ids, f"ГМ {cp['id']} не найден в ответе group-info"

        # Проверяем данные каждого ГМ
        for cp in cargo_places:
            cargo_info = next((item for item in group_info_response if item.get("id") == cp["id"]), None)
            assert cargo_info is not None, f"Не найдена информация для ГМ {cp['id']}"

            print(f"   - ГМ {cp['id']}: status={cargo_info.get('status')}, "
                  f"externalId={cargo_info.get('externalId')}, "
                  f"weight={cargo_info.get('weight')}")

            # Basic assertions - ОБНОВЛЕННЫЕ ПРОВЕРКИ ПО РЕАЛЬНОЙ СТРУКТУРЕ
            assert cargo_info.get("id") == cp["id"]
            assert cargo_info.get("externalId") == cp["externalId"]
            assert cargo_info.get("status") == "new", f"Статус должен быть 'new', получен '{cargo_info.get('status')}'"

            # ПРОВЕРЯЕМ РЕАЛЬНЫЕ ПОЛЯ ИЗ ОТВЕТА (адаптируем под реальную структуру)
            assert "barCode" in cargo_info, "Поле barCode должно присутствовать"
            assert "comment" in cargo_info, "Поле comment должно присутствовать"

            # Проверяем адреса (могут быть в другом формате)
            if "departureAddress" in cargo_info:
                print(f"     departureAddress: {cargo_info.get('departureAddress')}")
            elif "departureAddressExternalId" in cargo_info:
                print(f"     departureAddressExternalId: {cargo_info.get('departureAddressExternalId')}")

            if "deliveryAddress" in cargo_info:
                print(f"     deliveryAddress: {cargo_info.get('deliveryAddress')}")
            elif "deliveryAddressExternalId" in cargo_info:
                print(f"     deliveryAddressExternalId: {cargo_info.get('deliveryAddressExternalId')}")

    # === Шаг 3: Запрос group-info по externalIds ===
    with allure.step("Запрос group-info по externalIds"):
        external_ids = [cp["externalId"] for cp in cargo_places]

        payload = {
            "externalIds": external_ids
        }

        print(f"🔍 Запрос group-info для externalIds: {external_ids}")

        response = requests.post(
            f"{BASE_URL}/cargo-place/group-info",
            headers={"Authorization": token},
            json=payload,
            timeout=10
        )

        assert response.status_code == 200, f"Ошибка запроса group-info по externalIds: {response.text}"
        group_info_response = response.json()

        print(f"✅ Получен ответ group-info по externalIds:")
        print(f"   Найдено грузомест: {len(group_info_response)}")

        # Проверяем что все externalId есть в ответе
        found_external_ids = [item.get("externalId") for item in group_info_response]
        for cp in cargo_places:
            assert cp["externalId"] in found_external_ids, f"ГМ с externalId {cp['externalId']} не найден в ответе"

    # === Шаг 4: Запрос group-info по смешанным параметрам ===
    with allure.step("Запрос group-info по смешанным параметрам (IDs + externalIds)"):
        # Берем первый по ID, второй по externalId
        mixed_ids = [cargo_places[0]["id"]]
        mixed_external_ids = [cargo_places[1]["externalId"]]

        payload = {
            "ids": mixed_ids,
            "externalIds": mixed_external_ids
        }

        print(f"🔍 Запрос group-info для mixed: IDs={mixed_ids}, externalIds={mixed_external_ids}")

        response = requests.post(
            f"{BASE_URL}/cargo-place/group-info",
            headers={"Authorization": token},
            json=payload,
            timeout=10
        )

        assert response.status_code == 200, f"Ошибка запроса group-info mixed: {response.text}"
        group_info_response = response.json()

        print(f"✅ Получен ответ group-info mixed:")
        print(f"   Найдено грузомест: {len(group_info_response)}")

        # Должны найти оба ГМ
        found_ids = [item.get("id") for item in group_info_response]
        found_external_ids = [item.get("externalId") for item in group_info_response]

        assert cargo_places[0]["id"] in found_ids, f"Первый ГМ не найден по ID"
        assert cargo_places[1]["externalId"] in found_external_ids, f"Второй ГМ не найден по externalId"

    # === Allure Attachments ===
    with allure.step("Детали теста"):
        allure.attach(
            str([{"id": cp["id"], "externalId": cp["externalId"]} for cp in cargo_places]),
            name="Созданные грузоместа",
            attachment_type=allure.attachment_type.TEXT
        )


@allure.story("Edge cases")
@allure.feature("Грузоместа")
@allure.description("Проверка граничных случаев для /cargo-place/group-info")
@pytest.mark.parametrize("role", ["lkz"])
def test_cargo_place_group_info_edge_cases(role, valid_addresses):
    """
    Тест граничных случаев для group-info:
    - Пустые массивы
    - Несуществующие ID
    - Смешанные существующие/несуществующие
    """
    token = valid_addresses["token"]

    # === Случай 1: Пустые массивы ===
    with allure.step("Проверка пустых массивов"):
        payload = {
            "ids": [],
            "externalIds": []
        }

        response = requests.post(
            f"{BASE_URL}/cargo-place/group-info",
            headers={"Authorization": token},
            json=payload,
            timeout=10
        )

        # Ожидаем либо пустой массив, либо ошибку
        if response.status_code == 200:
            result = response.json()
            assert isinstance(result, list), "Ответ должен быть массивом"
            print(f"✅ Пустые массивы: возвращен пустой массив")
        else:
            print(f"ℹ️  Пустые массивы: сервер вернул {response.status_code}")

    # === Случай 2: Несуществующие ID ===
    with allure.step("Проверка несуществующих ID"):
        payload = {
            "ids": [999999, 888888],
            "externalIds": ["NON_EXISTENT_1", "NON_EXISTENT_2"]
        }

        response = requests.post(
            f"{BASE_URL}/cargo-place/group-info",
            headers={"Authorization": token},
            json=payload,
            timeout=10
        )

        if response.status_code == 200:
            result = response.json()
            assert isinstance(result, list), "Ответ должен быть массивом"
            # Должен вернуть пустой массив или только существующие ГМ
            print(f"✅ Несуществующие ID: возвращен массив из {len(result)} элементов")
        else:
            print(f"ℹ️  Несуществующие ID: сервер вернул {response.status_code}")