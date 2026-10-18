"""Temperaturas com validação do zero absoluto."""

from decimal import Decimal
from .validacao import validar

UNIDADES = ("c", "f", "k")
LIMITES = {"c": Decimal("-273.15"), "f": Decimal("-459.67"), "k": Decimal("0")}


def converter(valor: Decimal, origem: str, destino: str) -> Decimal:
    validar(valor, negativo=True)
    if origem not in UNIDADES or destino not in UNIDADES:
        raise ValueError("Use c, f ou k para temperatura.")
    if valor < LIMITES[origem]:
        raise ValueError("Temperatura abaixo do zero absoluto.")
    if origem == destino:
        return valor
    celsius = valor
    if origem == "f":
        celsius = (valor - 32) * 5 / 9
    elif origem == "k":
        celsius = valor - Decimal("273.15")
    if destino == "f":
        return celsius * 9 / 5 + 32
    if destino == "k":
        return celsius + Decimal("273.15")
    return celsius
