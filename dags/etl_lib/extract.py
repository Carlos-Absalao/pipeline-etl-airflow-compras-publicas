"""Extração: API REST paginada ou CSV local (modo offline)."""
import logging
import os
from pathlib import Path

import pandas as pd
import requests

log = logging.getLogger(__name__)

SAMPLE = Path(__file__).resolve().parents[2] / "data" / "sample" / "atas_exemplo.csv"


def extrair_api(url: str, page_size: int = 500, timeout: int = 60) -> pd.DataFrame:
    """Percorre todas as páginas da API e devolve um DataFrame."""
    registros, pagina = [], 1
    with requests.Session() as s:
        while True:
            resp = s.get(url, params={"pagina": pagina, "tamanho": page_size}, timeout=timeout)
            resp.raise_for_status()
            dados = resp.json().get("dados", [])
            if not dados:
                break
            registros.extend(dados)
            pagina += 1
    log.info("API: %s registros em %s páginas", len(registros), pagina - 1)
    return pd.DataFrame(registros)


def extrair() -> pd.DataFrame:
    url = os.getenv("ATAS_API_URL")
    if url:
        return extrair_api(url)
    log.info("ATAS_API_URL não definida — usando CSV de exemplo")
    return pd.read_csv(SAMPLE, dtype=str)
