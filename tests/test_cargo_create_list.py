import allure
import pytest
import json

from pages.cargo_create_list_page import CargoPlaceListClient
from config.settings import BASE_URL

# Внешние ID и внутренние ID адресов — подставьте реальные значения из вашей системы
VALID_EXTERNAL_IDS = [
    ("Izhevsk 76-276", "Izhevsk 36-950"),
    ("IZH - 50let 40", "IZH - deryabino 702"),
    ("IZH - promish 29", "Izhevsk - Telegina - 47"),
]


@allure.story("Smoke test")
@allure.feature("Грузоместа")
@allure.description("Создание списка из 3 грузомест через /create-list")
@pytest.mark.parametrize("role", ["lke"])
def test_create_cargo_places_list(role, get_auth_token):
    # 1. Авторизация
    token = get_auth_token(role)["token"]

    # 2. Инициализация клиента
    client = CargoPlaceListClient(BASE_URL, token)

    # 3. Генерация 3 грузомест
    cargo_list = []
    for i, (dep_ext, del_ext) in enumerate(VALID_EXTERNAL_IDS):
        cargo = client.generate_cargo_place(
            departure_external_id=dep_ext,
            delivery_external_id=del_ext,
            external_id=f"EXT-GM-{role}-{i + 1:03d}",
            bar_code=f"BC-{role}-{i + 1:03d}",
            invoice_number=f"INV-{role}-{i + 1:03d}",
            is_planned=False
        )
        cargo_list.append(cargo)

    # 4. Отправка запроса
    with allure.step("Отправка запроса на создание 3 грузомест"):
        response = client.create_cargo_places_list(cargo_list)

    # 5. Проверка ответа
    with allure.step("Проверка структуры ответа"):
        assert response.get("status") == "ok", f"Ожидался статус 'ok', получен: {response.get('status')}"

        data = response.get("data", [])
        assert len(data) == 3, f"Ожидалось 3 грузоместа, получено: {len(data)}"

        for item in data:
            assert "id" in item and isinstance(item["id"], int) and item["id"] > 0
            assert item.get("status") == "ok"
            assert "errors" in item and isinstance(item["errors"], list)

    # 6. Прикрепление в Allure
    with allure.step("Детали запроса и ответа"):
        allure.attach(
            json.dumps({"request": {"data": cargo_list}}, indent=2, ensure_ascii=False),
            name="Запрос (create-list)",
            attachment_type=allure.attachment_type.JSON
        )
        allure.attach(
            json.dumps(response, indent=2, ensure_ascii=False),
            name="Ответ API (create-list)",
            attachment_type=allure.attachment_type.JSON
        )

    print(f"\n✅ Успешно создано 3 грузоместа для роли {role}")