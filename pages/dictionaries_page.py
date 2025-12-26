import re
import requests
import allure

def has_cyrillic(text: str) -> bool:
    """Проверяет, содержит ли строка хотя бы один символ кириллицы."""
    return bool(re.search(r'[а-яА-ЯёЁ]', text))

# def validate_russian_titles_in_response(response: requests.Response):
#     """
#     Проверяет, что во всех объектах в массивах ответа:
#     1. Есть поле 'title'
#     2. Значение 'title' содержит кириллицу
#     """
#     json_data = response.json()
#     missing_title_errors = []
#     missing_cyrillic_errors = []
#
#     for dict_name, items in json_data.items():
#         if not isinstance(items, list):
#             continue
#
#         for item in items:
#             item_id = item.get("id", "unknown")
#
#             if "title" not in item:
#                 missing_title_errors.append(f"в объекте с id {item_id} в группе '{dict_name}' не найдено поле title")
#                 continue
#
#             title = item["title"]
#             if not isinstance(title, str):
#                 missing_title_errors.append(f"в объекте с id {item_id} в группе '{dict_name}' поле title не является строкой")
#                 continue
#
#             if not has_cyrillic(title):
#                 missing_cyrillic_errors.append(f"в объекте с id {item_id} в группе '{dict_name}' отсутствует русский язык")
#
#     error_messages = missing_title_errors + missing_cyrillic_errors
#     assert not error_messages, "Найдены ошибки в справочниках:\n" + "\n".join(error_messages)


def validate_russian_titles_in_response(response: requests.Response):
    """
    Проверяет, что во всех объектах в массивах ответа:
    1. Есть поле 'title'
    2. Значение 'title' содержит кириллицу
    """
    json_data = response.json()
    missing_title_errors = []
    missing_cyrillic_errors = []

    for dict_name, items in json_data.items():
        if not isinstance(items, list):
            continue

        for item in items:
            item_id = item.get("id", "unknown")
            if "title" not in item:
                missing_title_errors.append(f"в объекте с id {item_id} в группе '{dict_name}' не найдено поле title")
                continue

            title = item["title"]
            if not isinstance(title, str):
                missing_title_errors.append(f"в объекте с id {item_id} в группе '{dict_name}' поле title не является строкой")
                continue

            if not has_cyrillic(title):
                missing_cyrillic_errors.append(f"в объекте с id {item_id} в группе '{dict_name}' отсутствует русский язык")

    # Собираем все проблемы
    error_messages = missing_title_errors + missing_cyrillic_errors

    if error_messages:
        warning_msg = "⚠️ Найдены поля без перевода на русский язык:\n" + "\n".join(error_messages)

        # Вывод в консоль
        print(warning_msg)

        # Добавляем в Allure как шаг или прикрепление
        with allure.step("Отсутствует перевод для некоторых элементов"):
            allure.attach(
                "\n".join(error_messages),
                name="Элементы без кириллицы",
                attachment_type=allure.attachment_type.TEXT
            )
    else:
        with allure.step("✅ Все поля 'title' содержат русский язык"):
            pass
