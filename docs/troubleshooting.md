# Troubleshooting (WSL2 + Docker)

## Containers não acessam APIs que exigem VPN
O Docker Desktop/Engine no WSL2 não herda automaticamente a VPN do Windows.

Opções:
1. Habilitar rede espelhada no `%UserProfile%\.wslconfig` e reiniciar o WSL (`wsl --shutdown`):
   ```ini
   [wsl2]
   networkingMode=mirrored
   dnsTunneling=true
   ```
2. Executar a extração num host com acesso à VPN e entregar o arquivo ao pipeline.
3. Usar um proxy HTTP no host e configurar `HTTPS_PROXY` nos containers.

## Instabilidade de DNS
Sintoma: `NameResolutionError` intermitente. `dnsTunneling=true` (acima) costuma resolver.

## DAG não aparece na UI
- Verifique quebras de linha: `file dags/*.py` deve mostrar `ASCII text`, não `CRLF`.
- `docker compose exec airflow-scheduler airflow dags list-import-errors`.

## `pd.read_sql` falhando após upgrade
Use `PostgresHook.get_pandas_df()` ou `hook.get_sqlalchemy_engine()` — evita incompatibilidades entre pandas e SQLAlchemy 2.x.
