import os
from pathlib import Path
import pytest
import requests
from dotenv import load_dotenv
from config.settings import BASE_URL, TIMEOUT

dotenv_path = Path(__file__).parent / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)


@pytest.fixture
def get_auth_token():
    def _login(role: str):
        email = os.getenv(f"{role.upper()}_EMAIL")
        password = os.getenv(f"{role.upper()}_PASSWORD")
        if not email or not password:
            raise ValueError(f"Данные для {role} не найдены в .env")

        # отладочный вывод в консоль
        print(f"\n Запрос роли: {role}")
        print(f" Получен email: {repr(email)}")
        print(f" Получен пароль: {repr(password)}")

        payload = {"username": email, "password": password}
        response = requests.post(
            f"{BASE_URL}/user/login",
            json=payload,
            timeout=TIMEOUT
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        return {
            "token": data["token"],
            "role": data["role"]
        }

    return _login
