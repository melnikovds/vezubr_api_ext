import allure
import pytest
import requests
import json

from config.settings import BASE_URL

# Список ID рейсов для проверки (можно расширить)
ORDER_IDS = [40179, 40178]


@allure.story("Smoke test")
@allure.feature("Транспортные заявки")
@allure.description("Получение деталей существующей транспортной заявки")
@pytest.mark.parametrize("order_id", ORDER_IDS)
def test_get_order_details(order_id, get_auth_token):
    # 1. Авторизация (используем роль lke, как в предыдущих тестах)
    token = get_auth_token("lke")["token"]
    headers = {"Authorization": token}

    # 2. Запрос деталей рейса
    with allure.step(f"Получение деталей рейса с ID={order_id}"):
        response = requests.get(
            f"{BASE_URL}/order/{order_id}/details",
            headers=headers
        )
        assert response.status_code == 200, f"Ошибка получения деталей: {response.text}"

    # 3. Проверка структуры ответа
    order_data = response.json()
    with allure.step("Проверка структуры ответа"):
        assert isinstance(order_data, dict), "Ответ должен быть объектом"

        # Обязательные поля на верхнем уровне
        required_fields = {"id", "orderIdentifier", "state", "transportOrder"}
        missing = required_fields - order_data.keys()
        assert not missing, f"В ответе отсутствуют поля: {missing}"

        # Проверка ID
        assert order_data["id"] == order_id, f"ID в ответе ({order_data['id']}) не совпадает с запрошенным ({order_id})"

        # Проверка точек маршрута (аналог 'addresses')
        transport_order = order_data["transportOrder"]
        assert isinstance(transport_order, dict), "Поле 'transportOrder' должно быть объектом"

        points = transport_order.get("points")
        assert isinstance(points, list), "Поле 'transportOrder.points' должно быть списком"
        assert len(points) >= 2, f"Ожидалось минимум 2 точки маршрута, получено: {len(points)}"

        # Проверка первой точки
        first_point = points[0]
        assert "addressString" in first_point, "В точке маршрута должно быть поле 'addressString'"
        assert "externalId" in first_point, "В точке маршрута должно быть поле 'externalId'"

    # 4. Вывод информации
    identifier = order_data.get("orderIdentifier", "—")
    print(f"\n✅ Получены детали рейса ID={order_id}, orderIdentifier={identifier}")

    with allure.step(f"✅ Детали рейса ID={order_id} получены"):
        allure.attach(
            json.dumps(order_data, ensure_ascii=False, indent=2),
            name="Ответ API",
            attachment_type=allure.attachment_type.JSON
        )