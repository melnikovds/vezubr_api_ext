import allure
import pytest
import requests
from config.settings import BASE_URL

# Ваши целевые externalId
EXTERNAL_IDS = ["Izhevsk 81-870", "Izhevsk 71-130", "Izhevsk 64-649"]


@allure.story("Smoke test")
@allure.feature("Адресные точки")
@allure.description("Получение списка адресных точек и проверка наличия заданных externalId")
@pytest.mark.parametrize("role", ["lke"])
def test_get_address_list(role, get_auth_token):
    # 1. Авторизация
    token = get_auth_token(role)["token"]
    headers = {"Authorization": token}

    # 2. Запрос списка адресов
    with allure.step(f"Получение списка адресных точек для роли '{role}'"):
        payload = {"itemsPerPage": 100}
        response = requests.post(
            f"{BASE_URL}/contractor-point/list-info",
            headers=headers,
            json=payload,
        )
        assert response.status_code == 200, f"Ошибка получения списка: {response.text}"

    # 3. Извлечение и проверка структуры
    data = response.json()
    with allure.step("Проверка структуры ответа"):
        assert isinstance(data, dict), "Ответ должен быть JSON-объектом"
        assert "points" in data, "В ответе должно быть поле 'points'"
        points = data["points"]
        assert isinstance(points, list), "Поле 'points' должно быть списком"

        # Проверка структуры первой точки (если есть)
        if points:
            first = points[0]
            # Поля могут быть null, но должны присутствовать
            expected_fields = {"id", "externalId", "addressString", "cityName", "status", "title"}
            missing = expected_fields - set(first.keys())
            assert not missing, f"В точке отсутствуют поля: {missing}"

    # 4. Поиск нужных externalId
    found = []
    for point in points:
        ext_id = point.get("externalId")
        if ext_id in EXTERNAL_IDS:
            found.append(point)

    # 5. Проверка, что все externalId найдены
    found_ids = {p["externalId"] for p in found}
    missing_ids = set(EXTERNAL_IDS) - found_ids

    with allure.step("Проверка наличия всех ожидаемых externalId"):
        assert not missing_ids, f"Не найдены externalId: {missing_ids}"

    # 6. Логирование
    print(f"\n✅ Найдено {len(found)} из {len(EXTERNAL_IDS)} ожидаемых адресов для роли {role}")
    for p in found:
        print(f"  - externalId: {p['externalId']}, title: {p.get('title') or '—'}, address: {p['addressString']}")

    with allure.step(f"✅ Найдено адресов: {len(found)}"):
        pass
