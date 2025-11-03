
def expected_tariff_params(actual_params: dict):
    """
    Проверяет, что поля в serviceCosts и baseWorkCosts соответствуют ожидаемым значениям.
    """
    # Ожидаемые данные (эталон) — можно вынести в фикстуру или конфиг, если нужно использовать в нескольких тестах
    expected = {
        "serviceCosts": [
            {
                "article": 1405,
                "vehicleTypeId": 1,
                "costPerService": 70000
            },
            {
                "article": 1405,
                "vehicleTypeId": 2,
                "costPerService": 100000
            }
        ],
        "baseWorkCosts": [
            {
                "vehicleTypeId": 1,
                "cost": 50000,
                "hoursWork": 7,
                "hoursInnings": 1
            },
            {
                "vehicleTypeId": 2,
                "cost": 80000,
                "hoursWork": 7,
                "hoursInnings": 1
            }
        ]
    }

    # Проверяем наличие ключей
    assert "serviceCosts" in actual_params, "Поле serviceCosts отсутствует"
    assert "baseWorkCosts" in actual_params, "Поле baseWorkCosts отсутствует"

    actual_service_costs = actual_params["serviceCosts"]
    actual_base_work_costs = actual_params["baseWorkCosts"]

    assert len(actual_service_costs) == len(expected["serviceCosts"]), \
        f"Ожидалось {len(expected['serviceCosts'])} элементов в serviceCosts, получено: {len(actual_service_costs)}"
    assert len(actual_base_work_costs) == len(expected["baseWorkCosts"]), \
        f"Ожидалось {len(expected['baseWorkCosts'])} элементов в baseWorkCosts, получено: {len(actual_base_work_costs)}"

    # Проверяем каждый элемент
    for i, expected_item in enumerate(expected["serviceCosts"]):
        actual_item = actual_service_costs[i]
        assert actual_item["article"] == expected_item["article"], \
            f"serviceCosts[{i}].article: ожидалось {expected_item['article']}, получено {actual_item['article']}"
        assert actual_item["vehicleTypeId"] == expected_item["vehicleTypeId"], \
            f"serviceCosts[{i}].vehicleTypeId: ожидалось {expected_item['vehicleTypeId']}, получено {actual_item['vehicleTypeId']}"
        assert actual_item["costPerService"] == expected_item["costPerService"], \
            f"serviceCosts[{i}].costPerService: ожидалось {expected_item['costPerService']}, получено {actual_item['costPerService']}"

    for i, expected_item in enumerate(expected["baseWorkCosts"]):
        actual_item = actual_base_work_costs[i]
        assert actual_item["vehicleTypeId"] == expected_item["vehicleTypeId"], \
            f"baseWorkCosts[{i}].vehicleTypeId: ожидалось {expected_item['vehicleTypeId']}, получено {actual_item['vehicleTypeId']}"
        assert actual_item["cost"] == expected_item["cost"], \
            f"baseWorkCosts[{i}].cost: ожидалось {expected_item['cost']}, получено {actual_item['cost']}"
        assert actual_item["hoursWork"] == expected_item["hoursWork"], \
            f"baseWorkCosts[{i}].hoursWork: ожидалось {expected_item['hoursWork']}, получено {actual_item['hoursWork']}"
        assert actual_item["hoursInnings"] == expected_item["hoursInnings"], \
            f"baseWorkCosts[{i}].hoursInnings: ожидалось {expected_item['hoursInnings']}, получено {actual_item['hoursInnings']}"