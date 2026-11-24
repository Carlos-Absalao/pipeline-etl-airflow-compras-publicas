"""DAG diária: atas de registro de preço → camadas raw / trusted / gold."""
from datetime import datetime, timedelta

from airflow.decorators import dag, task

default_args = {"retries": 2, "retry_delay": timedelta(minutes=5)}


@dag(
    dag_id="etl_atas_registro_preco",
    schedule="0 6 * * *",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    default_args=default_args,
    tags=["compras-publicas", "etl"],
    doc_md=__doc__,
)
def etl_atas():
    @task
    def extract() -> list[dict]:
        from etl_lib.extract import extrair

        return extrair().to_dict("records")

    @task
    def load_raw(registros: list[dict]) -> list[dict]:
        import pandas as pd
        from etl_lib.load import carregar_raw

        carregar_raw(pd.DataFrame(registros))
        return registros

    @task
    def transform_and_load_trusted(registros: list[dict]) -> int:
        import pandas as pd
        from etl_lib.load import carregar_trusted
        from etl_lib.transform import para_processed, para_trusted

        trusted = para_trusted(para_processed(pd.DataFrame(registros)))
        carregar_trusted(trusted)
        return len(trusted)

    @task
    def check_gold(qtd: int) -> None:
        from etl_lib.load import ler

        df = ler("SELECT * FROM gold.atas_por_status")
        assert df["qtd_atas"].sum() == qtd, "gold divergente da trusted"

    check_gold(transform_and_load_trusted(load_raw(extract())))


etl_atas()
