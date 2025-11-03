import os
from pathlib import Path
import pytest
import requests
from dotenv import load_dotenv
from config.settings import BASE_URL, TIMEOUT

dotenv_path = Path(__file__).parent / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)

# === КЭШ ДЛЯ ТОКЕНОВ НА ВСЮ СЕССИЮ ===
_auth_cache = {}


@pytest.fixture(scope="session")
def get_auth_token():
    def _login(role: str):
        # Возвращаем из кэша, если уже авторизовывались под этой ролью
        if role in _auth_cache:
            return _auth_cache[role]

        email = os.getenv(f"{role.upper()}_EMAIL")
        password = os.getenv(f"{role.upper()}_PASSWORD")
        if not email or not password:
            raise ValueError(f"Данные для {role} не найдены в .env")

        print(f"\n[Auth] Запрос роли: {role}")
        print(f"[Auth] Получен email: {repr(email)}")
        print(f"[Auth] Получен пароль: {repr(password)}")

        payload = {"username": email, "password": password}
        response = requests.post(
            f"{BASE_URL}/user/login",
            json=payload,
            timeout=TIMEOUT
        )
        assert response.status_code == 200, f"Login failed: {response.text}"
        data = response.json()
        token_info = {
            "token": data["token"],
            "role": data["role"]
        }
        # Сохраняем в кэш
        _auth_cache[role] = token_info
        return token_info

    return _login



@pytest.fixture
def client_id():
    return int(os.getenv("CLIENT_ID", "1939"))


@pytest.fixture
def producer_id():
    return int(os.getenv("PRODUCER_ID", "1599"))


@pytest.fixture
def contract_id():
    return int(os.getenv("CONTRACT_ID", "17142"))