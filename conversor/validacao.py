"""Validação compartilhada, sem leitura pelo teclado."""

import re
from decimal import Decimal


def numero(texto: str) -> Decimal:
    """Aceita um separador decimal, sem agrupamento de milhares."""
    texto = texto.strip()
    if not re.fullmatch(r"[+-]?(?:[0-9]+(?:[.,][0-9]+)?|[.,][0-9]+)", texto):
        raise ValueError("Informe um número com vírgula ou ponto, sem milhares.")
    return Decimal(texto.replace(",", "."))


def validar(valor: Decimal, negativo: bool = False) -> None:
    if not valor.is_finite():
        raise ValueError("O valor precisa ser finito.")
    if not negativo and valor < 0:
        raise ValueError("O valor não pode ser negativo.")
