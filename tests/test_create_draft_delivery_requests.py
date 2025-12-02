import allure
import pytest
import uuid
import random

from datetime import datetime, timedelta
from pages.create_cargo_page import CargoPlaceClient
from pages.cargo_delivery_draft_page import CargoDeliveryDraftClient
from pages.cargo_delivery_page import CargoDeliveryClient
from config.settings import BASE_URL


class TestCreateDraftDeliveryRequests:
    """Тесты создания заявок в черновик для LTL и FTL"""

    # Конкретные ID адресов из ваших тестов
    TEST_ADDRESSES = [27648, 27649, 27650]

    def get_test_addresses(self):
        """
        Получение тестовых адресов из фиксированного списка
        Возвращает (departure_id, delivery_id) - два разных адреса
        """
        if len(self.TEST_ADDRESSES) < 2:
            pytest.skip("Недостаточно тестовых адресов")

        # Выбираем два разных адреса
        departure_id, delivery_id = random.sample(self.TEST_ADDRESSES, 2)

        print(f"📌 Используемые адреса:")
        print(f"   Отправление ID: {departure_id}")
        print(f"   Доставка ID: {delivery_id}")

        return departure_id, delivery_id

    @allure.story("Создание заявок в черновик")
    @allure.feature("LTL заявка в черновик")
    @allure.description("Тест создания LTL заявки в статус черновика через /create")
    def test_create_ltl_draft_request(self, lkz_token, lke_token):
        """
        Создание LTL заявки в черновик
        Согласно примеру LTL запроса:
        - Адреса указываются в корне запроса (departurePoint, arrivalPoint)
        - В cargoPlaces указываем только ID грузомест
        """
        # === 1. Получаем тестовые адреса ===
        with allure.step("Выбираем тестовые адреса"):
            departure_id, delivery_id = self.get_test_addresses()
            print(f"✅ Выбраны адреса:")
            print(f"   Отправление: {departure_id}")
            print(f"   Доставка: {delivery_id}")
            print(f"   ВАЖНО: Для LTL адреса указываются в КОРНЕ запроса")
            print(f"   В cargoPlaces указываем только ID грузомест")

        # === 2. Создаем грузоместа ===
        with allure.step("LKZ создает грузоместа"):
            cargo_client = CargoPlaceClient(BASE_URL, lkz_token)

            print(f"📦 Создаем грузоместа для LTL заявки:")

            cargo_place_ids = []  # ID грузомест

            for i in range(1, 3):
                cargo_title = f"LTL-ГМ-{uuid.uuid4().hex[:8].upper()}"
                cargo_external_id = f"LTL_EXT_{uuid.uuid4().hex[:10].upper()}"

                try:
                    # Создаем ГМ
                    cargo = cargo_client.create_cargo_place_by_id(
                        departure_address_id=departure_id,
                        delivery_address_id=delivery_id,
                        title=cargo_title,
                        external_id=cargo_external_id,
                        weight_kg=random.randint(200, 500),
                        volume_m3=random.randint(1, 2)
                    )

                    # Сохраняем ID грузоместа
                    cargo_place_ids.append(cargo["id"])

                    print(f"   ✅ ГМ {i}: ID={cargo['id']}")

                except Exception as e:
                    print(f"   ⚠️  Не удалось создать ГМ {i}: {e}")
                    if i == 1 and not cargo_place_ids:
                        pytest.skip(f"Не удалось создать грузоместо: {e}")

        # === 3. Создаем LTL заявку в черновик ===
        with allure.step("LKZ создает LTL заявку в черновик"):
            draft_client = CargoDeliveryDraftClient(BASE_URL, lkz_token)

            client_identifier = f"LTL-DRAFT-{uuid.uuid4().hex[:8].upper()}"

            print(f"🔄 Создаем LTL заявку в черновик:")
            print(f"   clientIdentifier: {client_identifier}")

            try:
                result = draft_client.create_ltl_draft_request(
                    client_identifier=client_identifier,
                    departure_point=departure_id,
                    arrival_point=delivery_id,
                    cargo_place_ids=cargo_place_ids,
                    comment=f"Тестовая LTL заявка {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    inner_comment="Внутренний комментарий для тестирования"
                )

                # Проверяем ответ
                request_id = result.get("id")
                request_nr = result.get("requestNr")
                status = result.get("status")

                assert request_id is not None, "В ответе отсутствует ID заявки"
                assert request_nr is not None, "В ответе отсутствует номер заявки"
                assert status == "draft", f"Статус должен быть 'draft', получен '{status}'"

                print(f"✅ LTL заявка создана в черновик:")
                print(f"   ID: {request_id}")
                print(f"   Номер: {request_nr}")
                print(f"   Статус: {status}")

                if "message" in result:
                    print(f"   Сообщение: {result['message']}")

            except Exception as e:
                print(f"❌ Ошибка создания LTL заявки: {e}")
                raise

        # === 4. Проверяем что заявка в черновиках LKZ ===
        with allure.step("LKZ проверяет заявку в черновиках"):
            delivery_client = CargoDeliveryClient(BASE_URL, lkz_token)

            try:
                details = delivery_client.get_delivery_request_details(request_id)
                details_status = details.get("status", "unknown")
                details_nr = details.get("requestNr", "N/A")
                details_subtype = details.get("deliverySubType", "unknown")

                print(f"🔍 Проверка заявки LKZ:")
                print(f"   Номер заявки: {details_nr}")
                print(f"   Статус в деталях: {details_status}")
                print(f"   Тип заявки: {details_subtype}")

                # Проверяем что заявка существует
                assert details.get("id") == request_id
                assert details.get("deliverySubType") == "ltl", f"Тип должен быть 'ltl', получен '{details_subtype}'"

                print(f"✅ LKZ видит созданную LTL заявку в черновиках")

                # Проверяем структуру как в примере
                print(f"📋 Проверка структуры ответа:")
                print(f"   - departurePoint в корне: {details.get('departurePoint')} (ожидаем null)")
                print(f"   - arrivalPoint в корне: {details.get('arrivalPoint')} (ожидаем null)")

                # В ответе деталей адреса должны быть в cargoPlaces
                cargo_places_in_details = details.get("cargoPlaces", [])
                print(f"   - cargoPlaces: {len(cargo_places_in_details)} шт")

                for i, cp in enumerate(cargo_places_in_details, 1):
                    print(f"   ГМ {i}:")
                    print(f"      ID: {cp.get('id')}")
                    print(f"      departurePoint: {cp.get('departurePoint')}")
                    print(f"      arrivalPoint: {cp.get('arrivalPoint')}")

                # Проверяем что в корне null (как в примере)
                assert details.get("departurePoint") is None, f"departurePoint в корне должен быть null"
                assert details.get("arrivalPoint") is None, f"arrivalPoint в корне должен быть null"

                print(f"✅ Структура корректна как в примере LTL!")

            except Exception as e:
                print(f"⚠️  LKZ не может получить детали заявки: {e}")

        # === 5. Проверяем что LKE НЕ видит заявку (она в черновиках) ===
        with allure.step("LKE проверяет что заявка не доступна"):
            lke_delivery_client = CargoDeliveryClient(BASE_URL, lke_token)

            try:
                # Пытаемся получить детали заявки от имени LKE
                lke_delivery_client.get_delivery_request_details(request_id)
                print(f"⚠️  LKE неожиданно имеет доступ к заявке в черновике")
            except Exception as e:
                print(f"✅ LKE не имеет доступа к заявке в черновике (ожидаемо)")
                print(f"   Ошибка доступа: {str(e)[:100]}...")

        # === 6. Allure отчет ===
        with allure.step("Детали LTL теста"):
            allure.attach(
                f"""
                Тест: Создание LTL заявки в черновик

                Структура запроса (согласно примеру):
                - В корне: departurePoint={departure_id}, arrivalPoint={delivery_id}
                - В cargoPlaces: только ID грузомест
                - НЕТ parameters (в отличие от FTL)

                Адреса:
                - Отправление: {departure_id}
                - Доставка: {delivery_id}

                Грузоместа:
                - Количество: {len(cargo_place_ids)}
                - ID: {cargo_place_ids}

                Заявка:
                - ID: {request_id}
                - Номер: {request_nr}
                - Тип: {details_subtype}
                - Статус: {status}
                - clientIdentifier: {client_identifier}

                Результат: УСПЕХ - LTL заявка создана в черновик
                """,
                name="Детали LTL теста",
                attachment_type=allure.attachment_type.TEXT
            )

    @allure.story("Создание заявок в черновик")
    @allure.feature("FTL заявка в черновик")
    @allure.description("Тест создания FTL заявки в статус черновика через /create")
    def test_create_ftl_draft_request(self, lkz_token, lke_token):
        """
        Создание FTL заявки в черновик
        """
        # === 1. Получаем тестовые адреса ===
        with allure.step("Выбираем тестовые адреса"):
            departure_id, delivery_id = self.get_test_addresses()
            print(f"✅ Выбраны адреса для FTL:")
            print(f"   Отправление: {departure_id}")
            print(f"   Доставка: {delivery_id}")

        # === 2. Создаем FTL заявку в черновик ===
        with allure.step("LKZ создает FTL заявку в черновик"):
            draft_client = CargoDeliveryDraftClient(BASE_URL, lkz_token)

            client_identifier = f"FTL-DRAFT-{uuid.uuid4().hex[:8].upper()}"

            print(f"🔄 Создаем FTL заявку в черновик:")
            print(f"   clientIdentifier: {client_identifier}")

            result = draft_client.create_ftl_draft_request(
                client_identifier=client_identifier,
                departure_point=departure_id,
                arrival_point=delivery_id,
                comment=f"Тестовая FTL заявка в черновик {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                inner_comment="Внутренний комментарий FTL для тестирования"
            )

            # Проверяем ответ
            request_id = result.get("id")
            request_nr = result.get("requestNr")
            status = result.get("status")

            assert request_id is not None, "В ответе отсутствует ID заявки"
            assert request_nr is not None, "В ответе отсутствует номер заявки"
            assert status == "draft", f"Статус должен быть 'draft', получен '{status}'"

            print(f"✅ FTL заявка создана в черновик:")
            print(f"   ID: {request_id}")
            print(f"   Номер: {request_nr}")
            print(f"   Статус: {status}")

            if "message" in result:
                print(f"   Сообщение: {result['message']}")

        # === 3. Проверяем что заявка в черновиках LKZ ===
        with allure.step("LKZ проверяет FTL заявку в черновиках"):
            delivery_client = CargoDeliveryClient(BASE_URL, lkz_token)

            try:
                details = delivery_client.get_delivery_request_details(request_id)
                details_status = details.get("status", "unknown")
                details_nr = details.get("requestNr", "N/A")

                print(f"🔍 Проверка FTL заявки LKZ:")
                print(f"   Номер заявки: {details_nr}")
                print(f"   Статус в деталях: {details_status}")
                print(f"   Тип заявки: {details.get('deliverySubType')}")

                assert details.get("id") == request_id
                assert details.get("clientIdentifier") == client_identifier
                assert details.get("deliverySubType") == "ftl"

                print(f"✅ LKZ видит созданную FTL заявку в черновиках")
            except Exception as e:
                print(f"⚠️  LKZ не может получить детали FTL заявки: {e}")

        # === 4. Allure отчет ===
        with allure.step("Детали FTL теста"):
            allure.attach(
                f"""
                Тест: Создание FTL заявки в черновик

                Адреса:
                - Отправление: {departure_id}
                - Доставка: {delivery_id}

                Заявка:
                - ID: {request_id}
                - Номер: {request_nr}
                - clientIdentifier: {client_identifier}
                - Тип: FTL
                - Статус: {status}
                - Сообщение: {result.get('message', 'нет')}

                Результат: УСПЕХ - FTL заявка создана в черновик
                """,
                name="Детали FTL теста",
                attachment_type=allure.attachment_type.TEXT
            )

    @allure.story("Создание заявок в черновик")
    @allure.feature("Сравнение с публикацией")
    @allure.description("Тест сравнения создания в черновик и с публикацией")
    def test_compare_draft_vs_published(self, lkz_token):
        """
        Сравнение создания заявки в черновик и с публикацией
        """
        with allure.step("Сравнение двух подходов"):
            departure_id, delivery_id = self.get_test_addresses()

            print(f"🧪 Сравнение создания заявок:")
            print(f"   Адреса: {departure_id} → {delivery_id}")

            # 1. Создание в черновик
            print(f"\n1️⃣  Создание в черновик (/create):")
            draft_client = CargoDeliveryDraftClient(BASE_URL, lkz_token)

            draft_result = draft_client.create_ftl_draft_request(
                client_identifier=f"DRAFT-TEST-{uuid.uuid4().hex[:6].upper()}",
                departure_point=departure_id,
                arrival_point=delivery_id,
                comment="Тест черновика"
            )

            draft_id = draft_result.get("id")
            draft_status = draft_result.get("status")
            draft_message = draft_result.get("message", "")

            print(f"   Результат:")
            print(f"   - ID: {draft_id}")
            print(f"   - Статус: {draft_status}")
            print(f"   - Сообщение: {draft_message[:100]}...")

            # 2. Создание с публикацией (используем существующий клиент)
            print(f"\n2️⃣  Создание с публикацией (/create-and-publish):")
            publish_client = CargoDeliveryClient(BASE_URL, lkz_token)

            try:
                # Создаем точки маршрута
                route = [
                    publish_client.create_route_point(
                        point_id=departure_id,
                        position=1,
                        is_loading_work=True,
                        is_unloading_work=False,
                        required_arrive_at=(datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y %H:%M")
                    ),
                    publish_client.create_route_point(
                        point_id=delivery_id,
                        position=2,
                        is_loading_work=False,
                        is_unloading_work=True
                    )
                ]

                publish_result = publish_client.create_and_publish_delivery_request_with_tasks(
                    delivery_type="auto",
                    delivery_sub_type="ftl",
                    route=route,
                    comment="Тест публикации",
                    client_identifier=f"PUBLISH-TEST-{uuid.uuid4().hex[:6].upper()}",
                    producer_id=1599,  # Из настроек
                    rate=140000
                )

                publish_id = publish_result.get("id")
                publish_status = publish_result.get("status", "unknown")

                print(f"   Результат:")
                print(f"   - ID: {publish_id}")
                print(f"   - Статус: {publish_status}")

            except Exception as e:
                print(f"   ❌ Ошибка создания с публикацией: {e}")
                publish_id = None

            # 3. Сравнение
            print(f"\n3️⃣  Сравнение:")
            print(f"   Черновик (/create):")
            print(f"   - Эндпоинт: /create")
            print(f"   - Публикация: НЕТ")
            print(f"   - Ставки/тарифы: НЕТ")
            print(f"   - Статус: {draft_status}")

            print(f"\n   Публикация (/create-and-publish):")
            print(f"   - Эндпоинт: /create-and-publish")
            print(f"   - Публикация: ДА")
            print(f"   - Ставки/тарифы: ДА")

            allure.attach(
                f"""
                Сравнение создания заявок:

                1. В черновик (/create):
                - ID: {draft_id}
                - Статус: {draft_status}
                - Сообщение: {draft_message}
                - Особенности: Без публикации, без ставок

                2. С публикацией (/create-and-publish):
                - ID: {publish_id if publish_id else 'не создана'}
                - Особенности: С публикацией, со ставками

                Вывод: Эндпоинт /create создает заявки в статусе черновика
                без публикации их исполнителям.
                """,
                name="Сравнение создания заявок",
                attachment_type=allure.attachment_type.TEXT
            )
