import os
from typing import Literal, cast

_RAW_DOMAIN = os.getenv("DOMAIN", "com")

if _RAW_DOMAIN not in {"dev", "com", "ru"}:
    raise ValueError(f"Недопустимое значение DOMAIN: '{_RAW_DOMAIN}'. Допустимые: dev, com, ru")

DOMAIN: Literal['dev', 'com', 'ru'] = cast(Literal['dev', 'com', 'ru'], _RAW_DOMAIN)

BASE_URL = f"https://api.vezubr.{DOMAIN}/v1/api-ext"

TIMEOUT = 10
