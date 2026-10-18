"""Câmbio manual: cada taxa representa BRL por unidade da moeda."""

from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from .historico import ler_json, gravar_json
from .validacao import validar

MOEDAS = ("BRL", "USD", "EUR")


def validar_taxas(dados: dict) -> dict:
    try:
        date.fromisoformat(dados["data_referencia"])
        taxas = {moeda: Decimal(dados["taxas"][moeda]) for moeda in MOEDAS}
        for taxa in taxas.values():
            validar(taxa)
            if taxa <= 0:
                raise ValueError("As taxas precisam ser maiores que zero.")
        if taxas["BRL"] != 1:
            raise ValueError("A taxa base BRL precisa ser 1.")
    except (KeyError, TypeError, InvalidOperation) as erro:
        raise ValueError("Estrutura de taxas inválida.") from erro
    return taxas


def carregar(caminho: Path) -> dict:
    dados = ler_json(caminho)
    validar_taxas(dados)
    return dados


def salvar(caminho: Path, dados: dict) -> None:
    validar_taxas(dados)
    # Não sobrescreve silenciosamente um cadastro corrompido.
    if caminho.exists():
        carregar(caminho)
    gravar_json(caminho, dados)


def converter(valor: Decimal, origem: str, destino: str, dados: dict) -> tuple:
    validar(valor)
    taxas = validar_taxas(dados)
    if origem not in taxas or destino not in taxas:
        raise ValueError("Use BRL, USD ou EUR.")
    taxa = taxas[origem] / taxas[destino]
    # Divide por último para evitar arredondar a taxa antes do cálculo.
    resultado = valor if origem == destino else valor * taxas[origem] / taxas[destino]
    return resultado, taxa
