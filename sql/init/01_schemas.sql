-- Base analítica separada do metadata do Airflow
CREATE DATABASE dw;
\connect dw

CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS processed;
CREATE SCHEMA IF NOT EXISTS trusted;
CREATE SCHEMA IF NOT EXISTS gold;

CREATE TABLE IF NOT EXISTS raw.atas (
    payload      JSONB       NOT NULL,
    dt_carga     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS trusted.atas (
    numero_ata        TEXT PRIMARY KEY,
    orgao             TEXT NOT NULL,
    fornecedor        TEXT NOT NULL,
    item              TEXT NOT NULL,
    valor_unitario    NUMERIC(14,2) NOT NULL CHECK (valor_unitario >= 0),
    quantidade        INTEGER NOT NULL CHECK (quantidade >= 0),
    valor_total       NUMERIC(16,2) NOT NULL,
    inicio_vigencia   DATE NOT NULL,
    termino_vigencia  DATE NOT NULL,
    status_vigencia   TEXT NOT NULL,
    dt_carga          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE OR REPLACE VIEW gold.valor_por_fornecedor AS
SELECT fornecedor,
       count(*)              AS qtd_atas,
       sum(valor_total)      AS valor_total,
       sum(valor_total) FILTER (WHERE status_vigencia = 'VIGENTE') AS valor_vigente
FROM trusted.atas
GROUP BY fornecedor;

CREATE OR REPLACE VIEW gold.atas_por_status AS
SELECT status_vigencia, count(*) AS qtd_atas, sum(valor_total) AS valor_total
FROM trusted.atas
GROUP BY status_vigencia;
