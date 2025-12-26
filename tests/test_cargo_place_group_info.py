import json
import os
import allure
import pytest
import requests

from pages.cargo_create_list_page import CargoPlaceListClient
from config.settings import BASE_URL
from utils.api_helpers import get_two_valid_addresses


@allure.story("API test")
@allure.feature("Грузоместа")
@allure.description("Получение информации о созданных грузоместах через /group-info")
@pytest.mark.parametrize("role", ["lkz"])
def test_get_cargo_place_group_info(
        role,
        get_auth_token,
        client_id,
        producer_id,
        contract_id,
):
    # 1. Авторизация
    token_info = get_auth_token(role)
    token = token_info["token"]
    headers = {"Authorization": token}
    allure.attach(
        f"Роль: {role}\nEmail: {os.getenv(f'{role.upper()}_EMAIL', 'N/A')}",
        name="Авторизация",
        attachment_type=allure.attachment_type.TEXT,
    )

    # 2. Получаем два валидных адреса текущей роли
    with allure.step("Получение 2 валидных адресов"):
        dep_addr, del_addr = get_two_valid_addresses(headers)
        allure.attach(
            json.dumps([dep_addr, del_addr], indent=2, ensure_ascii=False),
            name="Выбранные адреса",
            attachment_type=allure.attachment_type.JSON,
        )

    # 3. Инициализация клиента
    client = CargoPlaceListClient(BASE_URL, token)

    # 4. Генерация 2 грузомест с этими externalId
    cargo_list = []
    for i in range(2):
        cargo = client.generate_cargo_place(
            departure_external_id=dep_addr["externalId"],
            delivery_external_id=del_addr["externalId"],
            external_id=f"EXT-GM-{role}-{i + 1:03d}",
            bar_code=f"BC-{role}-{i + 1:03d}",
            invoice_number=f"INV-{role}-{i + 1:03d}",
            is_planned=False,
            producer_id=producer_id,
            contract_id=contract_id,
            client_id=client_id,
        )
        cargo_list.append(cargo)

    # 5. Создание
    with allure.step("Создание 2 грузомест через /create-list"):
        create_resp = client.create_cargo_places_list(cargo_list)

        allure.attach(
            json.dumps(create_resp, indent=2, ensure_ascii=False),
            name="Ответ /create-list",
            attachment_type=allure.attachment_type.JSON,
        )

        assert create_resp.get("status") == "ok", f"❌ create-list failed: {create_resp}"
        created_data = create_resp.get("data", [])
        assert len(created_data) == 2

        created_ids = []
        for item in created_data:
            gm_id = item.get("id")
            if item.get("status") == "ok" and gm_id:
                created_ids.append(gm_id)
            else:
                pytest.fail(f"❌ ГМ не создан: {item}")

        assert len(created_ids) == 2

    # 6. Запрос group-info
    with allure.step("Запрос через /group-info"):
        payload = {"ids": created_ids}
        response = requests.post(
            f"{BASE_URL}/cargo-place/group-info",
            headers=headers,
            json=payload,
            timeout=10,
        )

        allure.attach(
            json.dumps(payload, indent=2, ensure_ascii=False),
            name="Запрос /group-info",
            attachment_type=allure.attachment_type.JSON,
        )
        allure.attach(
            response.text,
            name=f"Ответ (HTTP {response.status_code})",
            attachment_type=allure.attachment_type.JSON
            if "application/json" in response.headers.get("content-type", "")
            else allure.attachment_type.TEXT,
        )

        assert response.status_code == 200

        # Парсинг: поддерживаем {"cargoPlaces": [...]} или [...]
        try:
            resp_json = response.json()
        except json.JSONDecodeError:
            pytest.fail(f"Некорректный JSON: {response.text}")

        if isinstance(resp_json, dict):
            data = resp_json.get("cargoPlaces") or resp_json.get("data", [])
        elif isinstance(resp_json, list):
            data = resp_json
        else:
            pytest.fail(f"Неподдерживаемый ответ: {type(resp_json)}")

        assert isinstance(data, list)
        assert len(data) == 2

    # 7. Проверка — только обязательные поля + адреса
    with allure.step("Проверка структуры ГМ"):
        for idx, gm in enumerate(data):
            gm_id = gm.get("id")
            allure.attach(
                json.dumps(gm, indent=2, ensure_ascii=False),
                name=f"ГМ #{idx + 1} (ID={gm_id})",
                attachment_type=allure.attachment_type.JSON,
            )

            # Обязательные поля (гарантированно не null)
            for field in ["id", "externalId", "status", "type", "barCode", "isDeleted"]:
                assert field in gm, f"❌ Отсутствует '{field}' в ГМ ID={gm_id}"
                assert gm[field] is not None, f"❌ '{field}' = null в ГМ ID={gm_id}"

            # Адреса — должны быть объектами с id и externalId
            for addr_name in ["departurePoint", "deliveryPoint"]:
                addr = gm.get(addr_name)
                assert addr is not None, f"❌ {addr_name} = null"
                assert isinstance(addr, dict), f"❌ {addr_name} не объект"
                assert "id" in addr, f"❌ {addr_name}.id отсутствует"
                assert "externalId" in addr, f"❌ {addr_name}.externalId отсутствует"
                assert addr["externalId"], f"❌ {addr_name}.externalId пустой"

            assert gm_id in created_ids

    print(f"\n✅ Проверено 2 ГМ с адресами для роли '{role}'")
