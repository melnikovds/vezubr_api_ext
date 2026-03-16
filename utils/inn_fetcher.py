import requests
import random
import re
import time
from typing import List, Optional
from bs4 import BeautifulSoup


class INNFetcher:
    """Класс для получения ИНН с различных источников"""

    @staticmethod
    def fetch_inns_from_radar4site(count: int = 10) -> List[str]:
        """
        Получение сгенерированных ИНН с radar4site.ru

        Параметры:
        ----------
        count : int
            Сколько ИНН получить

        Возвращает:
        -----------
        List[str]
            Список ИНН
        """
        inns = []

        try:
            # URL для генерации ИНН
            url = "https://radar4site.ru/pages/innkpp.html"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            print(f"🔍 Загрузка страницы генератора ИНН...")
            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Ищем скрипты с генерацией ИНН
                scripts = soup.find_all('script')
                for script in scripts:
                    if script.string and 'ИНН' in script.string:
                        # Ищем ИНН в скрипте (10 цифр)
                        found_inns = re.findall(r'\b\d{10}\b', script.string)
                        inns.extend(found_inns)

                print(f"Найдено {len(inns)} ИНН на странице")

            else:
                print(f"❌ Ошибка загрузки: {response.status_code}")

        except Exception as e:
            print(f"❌ Ошибка при получении ИНН с radar4site: {e}")

        return inns[:count]

    @staticmethod
    def fetch_inns_from_star_pro(count: int = 10) -> List[str]:
        """
        Получение реальных ИНН с star-pro.ru

        ВНИМАНИЕ: Это реальные ИНН компаний!
        """
        inns = []

        try:
            url = "https://star-pro.ru/proverka-kontragenta/organization"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
            }

            print(f"🔍 Загрузка списка организаций...")
            response = requests.get(url, headers=headers, timeout=15)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')

                # Ищем ИНН на странице (формат: ИНН: 1234567890)
                text = soup.get_text()

                # Паттерны для поиска ИНН
                patterns = [
                    r'ИНН:\s*(\d{10})',  # ИНН: 1234567890
                    r'ИНН\s*(\d{10})',  # ИНН 1234567890
                    r'\b\d{10}\b'  # Просто 10 цифр
                ]

                for pattern in patterns:
                    found = re.findall(pattern, text)
                    inns.extend(found)

                # Убираем дубликаты
                inns = list(set(inns))
                print(f"Найдено {len(inns)} уникальных ИНН на star-pro.ru")

            else:
                print(f"❌ Ошибка загрузки star-pro: {response.status_code}")

        except Exception as e:
            print(f"❌ Ошибка при получении ИНН с star-pro: {e}")

        return inns[:count]

    @staticmethod
    def generate_random_valid_inn() -> str:
        """
        Генерация валидного ИНН с правильной контрольной суммой
        """

        def calculate_control_sum(numbers: list[int], coeffs: list[int]) -> int:
            return sum(a * b for a, b in zip(numbers, coeffs)) % 11 % 10

        # Генерация первых 9 цифр
        base = [random.randint(0, 9) for _ in range(9)]

        # Коэффициенты для ИНН юрлица
        coeffs = [2, 4, 10, 3, 5, 9, 4, 6, 8]

        # Расчет контрольной суммы
        control_sum = calculate_control_sum(base, coeffs)

        inn = ''.join(map(str, base)) + str(control_sum)
        return inn

    @staticmethod
    def get_fresh_inns(count: int = 5, source: str = "mixed") -> List[str]:
        """
        Получение свежих ИНН из различных источников

        Параметры:
        ----------
        count : int
            Сколько ИНН получить
        source : str
            Источник: "radar", "star", "generated", "mixed"

        Возвращает:
        -----------
        List[str]
            Список ИНН
        """
        inns = []

        if source in ["radar", "mixed"]:
            radar_inns = INNFetcher.fetch_inns_from_radar4site(count)
            inns.extend(radar_inns)
            print(f"📊 С radar4site: {len(radar_inns)} ИНН")

        if source in ["star", "mixed"]:
            star_inns = INNFetcher.fetch_inns_from_star_pro(count)
            inns.extend(star_inns)
            print(f"📊 Со star-pro: {len(star_inns)} ИНН")

        # Если не хватило, догенерируем
        if len(inns) < count and source in ["generated", "mixed"]:
            needed = count - len(inns)
            for _ in range(needed):
                inns.append(INNFetcher.generate_random_valid_inn())
            print(f"📊 Сгенерировано: {needed} ИНН")

        # Убираем дубликаты и обрезаем до нужного количества
        inns = list(set(inns))[:count]

        print(f"📦 Итоговый набор ИНН ({len(inns)} шт): {inns}")
        return inns


# ============================================================
# Тестирование INNFetcher
# ============================================================
if __name__ == "__main__":
    print("🔍 Тестирование получения ИНН...")

    # Тест 1: С radar4site
    print("\n1. Получение ИНН с radar4site:")
    radar_inns = INNFetcher.fetch_inns_from_radar4site(3)
    print(f"   Результат: {radar_inns}")

    # Тест 2: С star-pro
    print("\n2. Получение ИНН с star-pro:")
    star_inns = INNFetcher.fetch_inns_from_star_pro(3)
    print(f"   Результат: {star_inns}")

    # Тест 3: Генерация
    print("\n3. Генерация ИНН:")
    for _ in range(3):
        inn = INNFetcher.generate_random_valid_inn()
        print(f"   Сгенерирован: {inn}")

    # Тест 4: Смешанный источник
    print("\n4. Смешанный источник (5 ИНН):")
    mixed_inns = INNFetcher.get_fresh_inns(5, "mixed")
    print(f"   Результат: {mixed_inns}")