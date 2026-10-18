"""Conversões por fatores relativos a uma unidade base."""

from decimal import Decimal
from .validacao import validar

FATORES = {
    "comprimento": {"mm": "0.001", "cm": "0.01", "m": "1", "km": "1000"},
    "massa": {"g": "0.001", "kg": "1", "t": "1000"},
    "tempo": {"s": "1", "min": "60", "h": "3600", "dia": "86400"},
}


def converter(valor: Decimal, categoria: str, origem: str, destino: str) -> Decimal:
    validar(valor)
    fatores = FATORES.get(categoria, {})
    if origem not in fatores or destino not in fatores:
        raise ValueError("Escolha unidades da categoria selecionada.")
    if origem == destino:
        return valor
    return valor * Decimal(fatores[origem]) / Decimal(fatores[destino])


def converter_comprimento(valor: Decimal, origem: str, destino: str) -> Decimal:
    return converter(valor, "comprimento", origem, destino)
