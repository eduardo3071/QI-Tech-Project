"""Testes de caixa-preta: falam com a API so por HTTP, como qualquer cliente.

Nenhum arquivo daqui importa codigo de src/. A API alvo vem de API_URL
(padrao http://localhost:8000). Cada teste cria os proprios dados com
CNPJ e chaves aleatorios, entao a suite roda contra um banco limpo ou ja usado.
"""
import os
import time

import httpx
import pytest

API_URL = os.environ.get("API_URL", "http://localhost:8000")
INTERNAL_TOKEN = os.environ.get("INTERNAL_TOKEN", "dev-internal-token")
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "dev-admin-token")
INTERNAL_HEADERS = {"INTERNAL-TOKEN": INTERNAL_TOKEN}


@pytest.fixture(scope="session", autouse=True)
def wait_for_api():
    deadline = time.time() + 60
    last_error = None
    while time.time() < deadline:
        try:
            if httpx.get(f"{API_URL}/health", timeout=2).status_code == 200:
                return
        except httpx.HTTPError as error:
            last_error = error
        time.sleep(1)
    pytest.exit(f"API nao respondeu em {API_URL}/health: {last_error}", returncode=1)


@pytest.fixture
def anonymous():
    """Cliente sem INTERNAL-TOKEN, para provar que a API recusa quem vem de fora."""
    with httpx.Client(base_url=API_URL, timeout=30) as client:
        yield client


@pytest.fixture
def api():
    with httpx.Client(base_url=API_URL, timeout=30, headers=INTERNAL_HEADERS) as client:
        yield client
