import os
from pathlib import Path
import pytest
import requests
from dotenv import load_dotenv
from config.settings import BASE_URL, TIMEOUT
from pages.create_contractor_page import CreateContractorPage

dotenv_path = Path(__file__).parent / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)

# === КЭШ ДЛЯ ТОКЕНОВ ===
_auth_cache = {}


# === ROLE-RELATED FIXTURES ===
@pytest.fixture(params=["lkp"])
def role(request):
    """
    Фикстура для указания роли пользователя.
    По умолчанию используем LKP (подрядчик), так как он нужен для большинства тестов.
    """
    return request.param


@pytest.fixture(scope="session")
def get_auth_token():
    def _login(role: str):
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
        token_info = {"token": data["token"], "role": data["role"]}
        _auth_cache[role] = token_info
        return token_info

    return _login


# === ROLE-AWARE CONFIGURATION ===
_ROLE_MAP = {
    "lke": {"client_id": 1939, "producer_id": 1599, "contract_id": 17142},
    "lkz": {"client_id": 1598, "producer_id": 1939, "contract_id": 21017},
    "lkp": {"client_id": 1937, "producer_id": 3478, "contract_id": 26134},
}


def _get_role_from_request(request):
    # 1. Если тест параметризован по "role"
    if "role" in request.fixturenames:
        try:
            return request.getfixturevalue("role")
        except:
            pass
    # 2. Если параметризация через valid_addresses[indirect=True]
    if hasattr(request, "param") and isinstance(request.param, str):
        return request.param
    # 3. Fallback - возвращаем 'lkp' как наиболее частый случай
    return "lkp"


# === ROLE-AWARE FIXTURES (ТОЛЬКО ОНИ!) ===
@pytest.fixture
def client_id(request):
    role = _get_role_from_request(request)
    res = _ROLE_MAP[role]["client_id"]
    print(f"\n🔧 client_id: роль={role!r}, возвращаем {res}")
    return res


@pytest.fixture
def producer_id(request):
    role = _get_role_from_request(request)
    return _ROLE_MAP[role]["producer_id"]


@pytest.fixture
def contract_id(request):
    role = _get_role_from_request(request)
    return _ROLE_MAP[role]["contract_id"]


# === VALID_ADDRESSES (работает с role и indirect) ===
@pytest.fixture(scope="function")
def valid_addresses(get_auth_token, role):
    token = get_auth_token(role)["token"]
    headers = {"Authorization": token}

    resp = requests.post(
        f"{BASE_URL}/contractor-point/list-info",
        headers=headers,
        json={"itemsPerPage": 200},
        timeout=TIMEOUT
    )
    resp.raise_for_status()
    points = resp.json().get("points", [])

    valid = [
        p for p in points
        if p.get("externalId")
           and p.get("id")
           and p["externalId"] != "unknown"
           and isinstance(p["externalId"], str)
           and p["externalId"].strip()
    ]
    assert len(valid) >= 2, f"Для роли {role} найдено <2 валидных адресов"

    return {
        "role": role,
        "token": token,
        "departure": valid[0],
        "delivery": valid[1]
    }


@pytest.fixture
def lke_token(get_auth_token):
    """Токен пользователя LKE (исполнитель)"""
    token_info = get_auth_token("lke")
    return token_info["token"]


@pytest.fixture
def lkz_token(get_auth_token):
    """Токен пользователя LKZ (заказчик)"""
    token_info = get_auth_token("lkz")
    return token_info["token"]


@pytest.fixture
def lkp_token(get_auth_token):
    """Токен пользователя LKP (подрядчик)"""
    token_info = get_auth_token("lkp")
    return token_info["token"]


@pytest.fixture
def create_contractor_page():


    def _create_page(base_url: str, token: str):
        return CreateContractorPage(base_url, token)

    return _create_page


@pytest.fixture
def contractor_page_lke(lke_token):

    from config.settings import BASE_URL
    return CreateContractorPage(BASE_URL, lke_token)


@pytest.fixture
def contractor_page_lkz(lkz_token):

    from config.settings import BASE_URL
    return CreateContractorPage(BASE_URL, lkz_token)


@pytest.fixture
def contractor_page_lkp(lkp_token):
    """Фикстура для Page Object контрагента с токеном LKP"""
    from config.settings import BASE_URL
    return CreateContractorPage(BASE_URL, lkp_token)
