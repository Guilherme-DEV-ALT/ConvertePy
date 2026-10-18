"""Persistência JSON e exportação CSV. Arquivos inválidos são preservados."""

import csv
import json
from pathlib import Path

CAMPOS = ("categoria", "valor", "origem", "destino", "resultado", "data", "taxa", "data_referencia")


def ler_json(caminho: Path):
    try:
        return json.loads(caminho.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeError) as erro:
        raise ValueError(f"Arquivo inválido preservado: {caminho}") from erro


def gravar_json(caminho: Path, conteudo) -> None:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temporario = caminho.with_suffix(caminho.suffix + ".tmp")
    temporario.write_text(json.dumps(conteudo, ensure_ascii=False, indent=2), encoding="utf-8")
    temporario.replace(caminho)


def carregar(caminho: Path) -> list:
    if not caminho.exists():
        return []
    registros = ler_json(caminho)
    if not isinstance(registros, list) or any(
        not isinstance(item, dict) or not set(CAMPOS).issubset(item)
        or any(not isinstance(item[campo], str) for campo in CAMPOS)
        for item in registros
    ):
        raise ValueError(f"Histórico inválido preservado: {caminho}")
    return registros


def registrar(caminho: Path, registro: dict) -> None:
    registros = carregar(caminho)
    registros.append(registro)
    gravar_json(caminho, registros)


def exportar(caminho: Path, destino: Path) -> int:
    registros = carregar(caminho)
    with destino.open("w", newline="", encoding="utf-8-sig") as arquivo:
        writer = csv.DictWriter(arquivo, fieldnames=CAMPOS, delimiter=";")
        writer.writeheader()
        writer.writerows({campo: item[campo] for campo in CAMPOS} for item in registros)
    return len(registros)
