import allure
import pytest
import json

from pages.cargo_create_or_update_list_page import CargoPlaceCreateOrUpdateListClient
from config.settings import BASE_URL


VALID_EXTERNAL_IDS = [
    ("Izhevsk 76-276", "Izhevsk 36-950"),
    ("IZH - 50let 40", "IZH - deryabino 702"),
    ("IZH - promish 29", "Izhevsk - Telegina - 47"),
]


@allure.story("Smoke test")
@allure.feature("Грузоместа")
@allure.description("Создание или обновление списка из 3 грузомест через /create-or-update-list")
@pytest.mark.parametrize("role", ["lke"])
def test_create_or_update_cargo_places_list(role, get_auth_token):
    token = get_auth_token(role)["token"]
    client = CargoPlaceCreateOrUpdateListClient(BASE_URL, token)

    cargo_list = []
    for i, (dep_ext, del_ext) in enumerate(VALID_EXTERNAL_IDS):
        cargo = client.generate_cargo_place(
            departure_external_id=dep_ext,
            delivery_external_id=del_ext,
            external_id=f"EXT-GM-UPD-{role}-{i + 1:03d}",
            bar_code=f"BC-UPD-{role}-{i + 1:03d}",
            invoice_number=f"INV-UPD-{role}-{i + 1:03d}",
            is_planned=False
        )
        cargo_list.append(cargo)

    with allure.step("Отправка запроса на создание/обновление 3 грузомест"):
        response = client.create_or_update_cargo_places_list(cargo_list)

    with allure.step("Проверка структуры ответа"):
        assert response.get("status") == "ok", f"Ожидался 'ok', получен: {response.get('status')}"

        data = response.get("data", [])
        assert len(data) == 3, f"Ожидалось 3 ГМ, получено: {len(data)}"

        for item in data:
            assert "id" in item and isinstance(item["id"], int) and item["id"] > 0
            assert item.get("status") == "ok"
            assert "errors" in item and isinstance(item["errors"], list)

    with allure.step("Детали запроса и ответа"):
        allure.attach(
            json.dumps({"request": {"data": cargo_list}}, indent=2, ensure_ascii=False),
            name="Запрос (create-or-update-list)",
            attachment_type=allure.attachment_type.JSON
        )
        allure.attach(
            json.dumps(response, indent=2, ensure_ascii=False),
            name="Ответ API (create-or-update-list)",
            attachment_type=allure.attachment_type.JSON
        )

    print(f"\n✅ Успешно создано/обновлено 3 грузоместа для роли {role}")
