"""Mapeamentos e helpers compartilhados pelas etapas do pipeline."""

# Nome na origem -> nome padronizado no destino.
# Um erro de digitação aqui gera coluna nula silenciosamente,
# por isso transform.validar_colunas() falha se algo faltar.
COLUNAS = {
    "NumeroAta": "numero_ata",
    "Orgao": "orgao",
    "Fornecedor": "fornecedor",
    "Item": "item",
    "ValorUnitario": "valor_unitario",
    "Quantidade": "quantidade",
    "InicioVigencia": "inicio_vigencia",
    "TerminoVigencia": "termino_vigencia",
}

CONN_ID = "dw_postgres"


def normalizar_texto(valor: str) -> str:
    """Remove espaços extras e padroniza em maiúsculas."""
    if valor is None:
        return ""
    return " ".join(str(valor).split()).upper()
