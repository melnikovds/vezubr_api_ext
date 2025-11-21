import requests
from config.settings import BASE_URL, TIMEOUT


def get_two_valid_addresses(headers: dict) -> tuple[dict, dict]:
    resp = requests.post(
        f"{BASE_URL}/contractor-point/list-info",
        headers=headers,
        json={"itemsPerPage": 200},
        timeout=TIMEOUT
    )
    resp.raise_for_status()
    points = resp.json().get("points", [])

    # Фильтруем: externalId должен быть непустой строкой И не "unknown"
    valid = [
        p for p in points
        if p.get("externalId")
           and isinstance(p["externalId"], str)
           and p["externalId"].strip().lower() != "unknown"
           and p.get("id")
    ]

    assert len(valid) >= 2, (
        f"Недостаточно валидных адресов (без 'unknown'): {len(valid)}\n"
        f"Доступные externalId: {[p.get('externalId') for p in points[:10]]}"
    )
    return valid[0], valid[1]