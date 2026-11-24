"""Transformação: processed (tipagem) e trusted (regras de qualidade)."""
from datetime import date

import pandas as pd

from etl_lib.utils import COLUNAS, normalizar_texto


class ErroQualidade(Exception):
    """Falha de contrato de dados — interrompe a DAG."""


def validar_colunas(df: pd.DataFrame) -> None:
    faltando = set(COLUNAS) - set(df.columns)
    if faltando:
        raise ErroQualidade(f"Colunas ausentes na origem: {sorted(faltando)}")


def para_processed(df: pd.DataFrame) -> pd.DataFrame:
    validar_colunas(df)
    out = df[list(COLUNAS)].rename(columns=COLUNAS).copy()

    for col in ("orgao", "fornecedor", "item"):
        out[col] = out[col].map(normalizar_texto)
    out["numero_ata"] = out["numero_ata"].astype(str).str.strip()

    # Valores no padrão brasileiro: "1.234,56"
    out["valor_unitario"] = pd.to_numeric(
        out["valor_unitario"].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False),
        errors="coerce",
    )
    out["quantidade"] = pd.to_numeric(out["quantidade"], errors="coerce").astype("Int64")
    for col in ("inicio_vigencia", "termino_vigencia"):
        out[col] = pd.to_datetime(out[col], dayfirst=True, errors="coerce").dt.date
    return out


def status_vigencia(inicio: date, termino: date, hoje: date) -> str:
    if hoje < inicio:
        return "A_INICIAR"
    if hoje > termino:
        return "VENCIDA"
    return "VIGENTE"


def para_trusted(df: pd.DataFrame, hoje: date | None = None) -> pd.DataFrame:
    hoje = hoje or date.today()
    out = df.dropna(subset=["numero_ata", "valor_unitario", "quantidade", "inicio_vigencia", "termino_vigencia"])
    out = out[(out["valor_unitario"] >= 0) & (out["quantidade"] >= 0)]
    out = out[out["termino_vigencia"] >= out["inicio_vigencia"]]
    out = out.drop_duplicates(subset="numero_ata", keep="last").copy()

    out["valor_total"] = (out["valor_unitario"] * out["quantidade"].astype(float)).round(2)
    out["status_vigencia"] = [
        status_vigencia(i, t, hoje) for i, t in zip(out["inicio_vigencia"], out["termino_vigencia"])
    ]
    return out.reset_index(drop=True)
