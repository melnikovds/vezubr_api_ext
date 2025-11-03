import allure
import pytest
import requests
from config.settings import BASE_URL

@allure.story("Smoke test")
@allure.feature("Задание")
@allure.description("удаление Задания с рандомизированными данными")
@pytest.mark.parametrize("role", ["lkz"])
def test_delete_task(role, get_auth_token):
    # Авторизация
    token = get_auth_token(role)["token"]
    headers = {"Authorization": token}



