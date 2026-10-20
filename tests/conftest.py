"""Configuração comum dos testes: deixa os módulos do projeto importáveis e carrega os dados reais."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from nucleo import data_loader  # noqa: E402


@pytest.fixture(scope="session")
def dados():
    return data_loader.carregar_genero("faroeste")
