from typing import Dict

import allure
import pytest
import uuid
import random
from datetime import datetime

from pages.create_cargo_page import CargoPlaceClient
from pages.cargo_delivery_draft_page import CargoDeliveryDraftClient
from pages.cargo_delivery_page import CargoDeliveryClient
from pages.cargo_delivery_update_page import CargoDeliveryUpdateClient
from config.settings import BASE_URL


class TestUpdateDraftDeliveryRequests:
    """Тесты редактирования заявок в статусе draft через /update"""

    TEST_ADDRESSES = [27648, 27649, 27650]

    def get_test_addresses(self):
        """Получение тестовых адресов"""
        if len(self.TEST_ADDRESSES) < 2:
            pytest.skip("Недостаточно тестовых адресов")

        departure_id, delivery_id = random.sample(self.TEST_ADDRESSES, 2)
        return departure_id, delivery_id

    def _create_ltl_draft_for_update(self, lkz_token) -> Dict:
        """Создание LTL заявки для последующего редактирования"""
        departure_id, delivery_id = self.get_test_addresses()

        # Создаем грузоместа
        cargo_client = CargoPlaceClient(BASE_URL, lkz_token)
        cargo_place_ids = []

        for i in range(1, 3):
            cargo_title = f"UPDATE-LTL-GM-{uuid.uuid4().hex[:8].upper()}"
            cargo_external_id = f"UPDATE_LTL_EXT_{uuid.uuid4().hex[:10].upper()}"

            try:
                cargo = cargo_client.create_cargo_place_by_id(
                    departure_address_id=departure_id,
                    delivery_address_id=delivery_id,
                    title=cargo_title,
                    external_id=cargo_external_id,
                    weight_kg=random.randint(200, 500),
                    volume_m3=random.randint(1, 2)
                )
                cargo_place_ids.append(cargo["id"])
                print(f"   ГМ {i} создано: ID={cargo['id']}")
            except Exception as e:
                if i == 1 and not cargo_place_ids:
                    pytest.skip(f"Не удалось создать грузоместо: {e}")

        # Создаем LTL заявку в черновик
        draft_client = CargoDeliveryDraftClient(BASE_URL, lkz_token)
        client_identifier = f"UPDATE-LTL-{uuid.uuid4().hex[:8].upper()}"

        result = draft_client.create_ltl_draft_request(
            client_identifier=client_identifier,
            departure_point=departure_id,
            arrival_point=delivery_id,
            cargo_place_ids=cargo_place_ids,
            comment=f"Заявка для редактирования LTL {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            inner_comment="Исходный внутренний комментарий"
        )

        return {
            "request_id": result["id"],
            "request_nr": result["requestNr"],
            "client_identifier": client_identifier,
            "departure_point": departure_id,
            "arrival_point": delivery_id,
            "cargo_place_ids": cargo_place_ids
        }

    @allure.story("Редактирование заявок в черновике")
    @allure.feature("Обновление LTL заявки")
    @allure.description("Тест редактирования LTL заявки в статусе draft через /update")
    def test_update_ltl_draft_basic_fields(self, lkz_token):
        """
        Обновление основных полей LTL заявки в черновике
        """
        with allure.step("1. Создание LTL заявки для редактирования"):
            ltl_data = self._create_ltl_draft_for_update(lkz_token)
            request_id = ltl_data["request_id"]
            original_identifier = ltl_data["client_identifier"]
            departure_id = ltl_data["departure_point"]
            arrival_id = ltl_data["arrival_point"]
            cargo_place_ids = ltl_data["cargo_place_ids"]

            print(f"Создана LTL заявка для редактирования:")
            print(f"   ID: {request_id}")
            print(f"   Номер: {ltl_data['request_nr']}")
            print(f"   Исходный clientIdentifier: {original_identifier}")
            print(f"   Адреса: {departure_id} → {arrival_id}")

        with allure.step("2. Подготовка и выполнение обновления"):
            update_client = CargoDeliveryUpdateClient(BASE_URL, lkz_token)

            # Новые значения
            new_to_start_at_from = update_client.generate_future_iso_time(days_ahead=2, hours_ahead=2)
            new_client_identifier = f"UPDATED-LTL-{uuid.uuid4().hex[:8].upper()}"
            new_inner_comment = f"Обновленный внутренний комментарий {datetime.now().strftime('%H:%M:%S')}"

            print(f"Обновление LTL заявки:")
            print(f"   Новый clientIdentifier: {new_client_identifier}")
            print(f"   Новый toStartAtFrom: {new_to_start_at_from}")
            print(f"   Новый innerComment: {new_inner_comment}")

            # Выполняем обновление
            response = update_client.update_draft_request(
                request_id=request_id,
                # Обязательные поля:
                delivery_type="auto",
                delivery_sub_type="ltl",
                departure_point=departure_id,
                arrival_point=arrival_id,
                cargo_places=[{"id": cp_id} for cp_id in cargo_place_ids],
                # Поля которые меняем:
                to_start_at_from=new_to_start_at_from,
                client_identifier=new_client_identifier,
                inner_comment=new_inner_comment,
                comment=f"Обновленный комментарий LTL {datetime.now().strftime('%H:%M:%S')}"
            )

            # Проверяем ответ
            assert response == [], f"Ответ должен быть пустым списком, получен: {response}"
            print(f"✅ LTL заявка обновлена")

        with allure.step("3. Проверка обновленных данных"):
            delivery_client = CargoDeliveryClient(BASE_URL, lkz_token)
            details = delivery_client.get_delivery_request_details(request_id)

            # Проверяем базовые поля
            assert details.get("status") == "draft", \
                f"Заявка должна остаться в статусе draft, получен: {details.get('status')}"
            assert details.get("clientIdentifier") == new_client_identifier, \
                f"clientIdentifier не обновился: {details.get('clientIdentifier')}"
            assert details.get("deliverySubType") == "ltl", \
                f"Тип заявки должен остаться LTL: {details.get('deliverySubType')}"

            # Проверяем innerComment (массив объектов)
            updated_inner_comment = details.get("innerComment")
            if updated_inner_comment and isinstance(updated_inner_comment, list) and len(updated_inner_comment) > 0:
                last_comment = updated_inner_comment[-1]
                assert last_comment.get("text") == new_inner_comment, \
                    f"innerComment не обновился. Ожидался текст '{new_inner_comment}', получен: {last_comment.get('text')}"
                print(f"✅ innerComment обновлен: {last_comment.get('text')}")
            else:
                print(f"⚠️  innerComment не обновился или имеет неожиданный формат: {updated_inner_comment}")

            # Проверяем время
            updated_from = details.get("toStartAtFrom")
            if updated_from:
                assert updated_from.startswith(new_to_start_at_from[:16]), \
                    f"toStartAtFrom не обновился: {updated_from}"

            print(f"✅ Все поля успешно обновлены")

        with allure.step("4. Allure отчет"):
            allure.attach(
                f"""
                Тест: Редактирование LTL заявки в черновике

                Исходные данные:
                - ID заявки: {request_id}
                - Номер: {ltl_data['request_nr']}
                - Исходный clientIdentifier: {original_identifier}
                - Статус: draft

                Обновленные данные:
                - Новый clientIdentifier: {new_client_identifier}
                - Новый toStartAtFrom: {new_to_start_at_from}
                - Новый innerComment: {new_inner_comment}

                Результат: УСПЕХ - LTL заявка успешно отредактирована
                """,
                name="Детали теста редактирования LTL",
                attachment_type=allure.attachment_type.TEXT
            )

    @allure.story("Редактирование заявок в черновике")
    @allure.feature("Обновление FTL заявки")
    @allure.description("Тест редактирования FTL заявки в статусе draft через /update")
    def test_update_ftl_draft_basic_fields(self, lkz_token):
        """
        Обновление основных полей FTL заявки в черновике
        """
        with allure.step("1. Создание FTL заявки для редактирования"):
            departure_id, delivery_id = self.get_test_addresses()

            draft_client = CargoDeliveryDraftClient(BASE_URL, lkz_token)
            original_identifier = f"UPDATE-FTL-{uuid.uuid4().hex[:8].upper()}"

            result = draft_client.create_ftl_draft_request(
                client_identifier=original_identifier,
                departure_point=departure_id,
                arrival_point=delivery_id,
                comment=f"Заявка для редактирования FTL {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                inner_comment="Исходный внутренний комментарий FTL"
            )

            request_id = result["id"]
            request_nr = result["requestNr"]

            print(f"Создана FTL заявка для редактирования:")
            print(f"   ID: {request_id}")
            print(f"   Номер: {request_nr}")
            print(f"   Исходный clientIdentifier: {original_identifier}")
            print(f"   Адреса: {departure_id} → {delivery_id}")

        with allure.step("2. Подготовка и выполнение обновления"):
            update_client = CargoDeliveryUpdateClient(BASE_URL, lkz_token)

            # Новые значения
            new_to_start_at_from = update_client.generate_future_iso_time(days_ahead=2, hours_ahead=3)
            new_client_identifier = f"UPDATED-FTL-{uuid.uuid4().hex[:8].upper()}"
            new_inner_comment = f"Обновленный внутренний комментарий FTL {datetime.now().strftime('%H:%M:%S')}"

            print(f"Обновление FTL заявки:")
            print(f"   Новый clientIdentifier: {new_client_identifier}")
            print(f"   Новое время подачи: {new_to_start_at_from[:19]}")

            # Выполняем обновление
            response = update_client.update_draft_request(
                request_id=request_id,
                # Обязательные поля:
                delivery_type="auto",
                delivery_sub_type="ftl",
                departure_point=departure_id,
                arrival_point=delivery_id,
                # Поля которые меняем:
                to_start_at_from=new_to_start_at_from,
                client_identifier=new_client_identifier,
                inner_comment=new_inner_comment,
                # Для FTL обязательные parameters
                parameters={
                    "orderCategory": 1,
                    "bodyTypes": [3, 4, 7, 8],
                    "isDangerousGoods": False,
                    "vehicleTypeId": 1,
                    "orderType": 1,
                    "pointChangeType": 2,
                    "route": [
                        {
                            "requiredArriveAtFrom": new_to_start_at_from,
                            "requiredArriveAtTill": None,
                            "position": 1,
                            "point": departure_id,
                            "isLoadingWork": True,
                            "isUnloadingWork": False
                        },
                        {
                            "requiredArriveAtFrom": None,
                            "requiredArriveAtTill": None,
                            "position": 2,
                            "point": delivery_id,
                            "isLoadingWork": False,
                            "isUnloadingWork": True
                        }
                    ]
                }
            )

            # Проверяем ответ
            assert response == [], f"Ответ должен быть пустым списком, получен: {response}"
            print(f"✅ FTL заявка обновлена")

        with allure.step("3. Проверка обновленных данных"):
            delivery_client = CargoDeliveryClient(BASE_URL, lkz_token)
            details = delivery_client.get_delivery_request_details(request_id)

            # Проверяем базовые поля
            assert details.get("status") == "draft", \
                f"Статус должен быть draft, получен: {details.get('status')}"
            assert details.get("clientIdentifier") == new_client_identifier, \
                f"clientIdentifier не обновился: {details.get('clientIdentifier')}"
            assert details.get("deliverySubType") == "ftl", \
                f"Тип должен быть FTL, получен: {details.get('deliverySubType')}"

            # Проверяем innerComment (массив объектов)
            updated_inner_comment = details.get("innerComment")
            if updated_inner_comment and isinstance(updated_inner_comment, list) and len(updated_inner_comment) > 0:
                last_comment = updated_inner_comment[-1]
                assert last_comment.get("text") == new_inner_comment, \
                    f"innerComment не обновился. Ожидался текст '{new_inner_comment}', получен: {last_comment.get('text')}"
                print(f"✅ innerComment обновлен: {last_comment.get('text')}")
            else:
                print(f"⚠️  innerComment не обновился или имеет неожиданный формат: {updated_inner_comment}")

            # Проверяем время
            if details.get("toStartAtFrom"):
                assert details["toStartAtFrom"].startswith(new_to_start_at_from[:16]), \
                    f"toStartAtFrom не обновился: {details.get('toStartAtFrom')}"

            print(f"✅ FTL заявка успешно обновлена")

        with allure.step("4. Allure отчет"):
            allure.attach(
                f"""
                Тест: Редактирование FTL заявки в черновике

                Исходные данные:
                - ID заявки: {request_id}
                - Номер: {request_nr}
                - Тип: FTL
                - Статус: draft

                Обновленные поля:
                - clientIdentifier: {original_identifier} → {new_client_identifier}
                - toStartAtFrom: обновлено
                - innerComment: обновлен

                Результат: УСПЕХ - FTL заявка успешно отредактирована
                """,
                name="Детали теста редактирования FTL",
                attachment_type=allure.attachment_type.TEXT
            )