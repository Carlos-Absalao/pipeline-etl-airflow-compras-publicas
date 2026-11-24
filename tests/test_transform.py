import sys
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "dags"))

from etl_lib.extract import SAMPLE  # noqa: E402
from etl_lib.transform import ErroQualidade, para_processed, para_trusted, status_vigencia  # noqa: E402


@pytest.fixture
def bruto():
    return pd.read_csv(SAMPLE, dtype=str)


def test_processed_tipa_valores_brasileiros(bruto):
    df = para_processed(bruto)
    assert df["valor_unitario"].dtype.kind == "f"
    assert df.loc[df["numero_ata"] == "ARP-2026-0001", "valor_unitario"].iloc[0] == 1234.56


def test_trusted_remove_duplicatas_e_invalidos(bruto):
    df = para_trusted(para_processed(bruto), hoje=date(2026, 6, 1))
    assert df["numero_ata"].is_unique
    assert (df["valor_unitario"] >= 0).all()
    assert "ARP-2026-0009" not in set(df["numero_ata"])  # valor negativo


def test_coluna_faltando_falha_alto(bruto):
    with pytest.raises(ErroQualidade):
        para_processed(bruto.drop(columns=["TerminoVigencia"]))


@pytest.mark.parametrize(
    "hoje,esperado",
    [(date(2025, 12, 31), "A_INICIAR"), (date(2026, 6, 1), "VIGENTE"), (date(2027, 1, 2), "VENCIDA")],
)
def test_status_vigencia(hoje, esperado):
    assert status_vigencia(date(2026, 1, 1), date(2027, 1, 1), hoje) == esperado
