"""Carga por camada. Sempre com schema explícito."""
import json
import logging

import pandas as pd
from airflow.providers.postgres.hooks.postgres import PostgresHook

from etl_lib.utils import CONN_ID

log = logging.getLogger(__name__)


def _hook() -> PostgresHook:
    return PostgresHook(postgres_conn_id=CONN_ID)


def carregar_raw(df: pd.DataFrame) -> None:
    linhas = [(json.dumps(r, ensure_ascii=False, default=str),) for r in df.to_dict("records")]
    _hook().insert_rows(table="raw.atas", rows=linhas, target_fields=["payload"])
    log.info("raw.atas: +%s linhas", len(linhas))


def carregar_trusted(df: pd.DataFrame) -> None:
    """Substitui o snapshot da camada trusted numa transação."""
    hook = _hook()
    engine = hook.get_sqlalchemy_engine()  # compatível com SQLAlchemy 2.x
    with engine.begin() as conn:
        conn.exec_driver_sql("TRUNCATE trusted.atas")
        df.to_sql("atas", conn, schema="trusted", if_exists="append", index=False)
    log.info("trusted.atas: %s linhas", len(df))


def ler(sql: str) -> pd.DataFrame:
    return _hook().get_pandas_df(sql)
