"""Interface de terminal; os cálculos ficam nos módulos de domínio."""

from datetime import datetime
from decimal import Decimal, DecimalException, ROUND_HALF_UP, localcontext
from pathlib import Path
from . import historico, moedas, temperaturas, unidades
from .validacao import numero

BASE = Path(__file__).resolve().parent.parent / "dados"
CATEGORIAS = {"1": "comprimento", "2": "massa", "3": "temperatura", "4": "tempo", "5": "moedas"}
MENU = """
CONVERTEPY
1. Comprimento
2. Massa
3. Temperatura
4. Tempo
5. Moedas
6. Histórico
7. Exportar histórico
8. Configurar e consultar taxas
0. Sair
"""


def formatar(valor: Decimal, dinheiro: bool = False) -> str:
    if dinheiro:
        valor = valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return format(valor, ".2f").replace(".", ",")
    texto = format(valor, "f")
    if "." in texto:
        texto = texto.rstrip("0").rstrip(".")
    return texto.replace(".", ",")


def converter(categoria: str) -> None:
    disponiveis = moedas.MOEDAS if categoria == "moedas" else (
        temperaturas.UNIDADES if categoria == "temperatura" else unidades.FATORES[categoria]
    )
    print("Unidades:", ", ".join(disponiveis))
    valor = numero(input("Valor: "))
    origem = input("Unidade de origem: ").strip()
    destino = input("Unidade de destino: ").strip()
    origem, destino = (origem.upper(), destino.upper()) if categoria == "moedas" else (origem.lower(), destino.lower())
    taxa, referencia = "", ""
    if categoria == "moedas":
        dados = moedas.carregar(BASE / "taxas.json")
        referencia = dados["data_referencia"]
        print(f"Taxas demonstrativas, cadastradas manualmente. Referência: {referencia}")
        resultado, taxa_aplicada = moedas.converter(valor, origem, destino, dados)
        taxa = str(taxa_aplicada)
    elif categoria == "temperatura":
        resultado = temperaturas.converter(valor, origem, destino)
    else:
        resultado = unidades.converter(valor, categoria, origem, destino)
    print(f"Resultado: {formatar(valor, categoria == 'moedas')} {origem} = {formatar(resultado, categoria == 'moedas')} {destino}")
    registro = dict(categoria=categoria, valor=str(valor), origem=origem, destino=destino,
                    resultado=str(resultado), data=datetime.now().astimezone().isoformat(),
                    taxa=taxa, data_referencia=referencia)
    historico.registrar(BASE / "historico.json", registro)
    print("Conversão salva no histórico.")


def configurar_taxas() -> None:
    caminho = BASE / "taxas.json"
    dados = moedas.carregar(caminho)
    print(f"Taxas demonstrativas em BRL por unidade. Referência: {dados['data_referencia']}")
    for moeda, taxa in dados["taxas"].items():
        print(f"1 {moeda} = {taxa} BRL")
    if input("Atualizar? (s/n): ").strip().lower() != "s":
        return
    referencia = input("Data de referência (AAAA-MM-DD): ").strip()
    taxas = {"BRL": "1"}
    for moeda in ("USD", "EUR"):
        taxas[moeda] = str(numero(input(f"1 {moeda} equivale a quantos BRL? ")))
    moedas.salvar(caminho, {"data_referencia": referencia, "taxas": taxas})
    print("Taxas atualizadas.")


def executar() -> None:
    while True:
        try:
            print(MENU)
            escolha = input("Escolha: ").strip()
            with localcontext() as contexto:
                contexto.prec = 28
                if escolha == "0":
                    print("Até logo!")
                    return
                if escolha in CATEGORIAS:
                    converter(CATEGORIAS[escolha])
                elif escolha == "6":
                    registros = historico.carregar(BASE / "historico.json")
                    print("Últimas 10 conversões:" if registros else "Histórico vazio.")
                    for item in registros[-10:]:
                        print(f"{item['data']} | {item['categoria']} | {item['valor']} {item['origem']} = {item['resultado']} {item['destino']}")
                        if item["taxa"]:
                            print(f"  Taxa: {item['taxa']} | Referência: {item['data_referencia']}")
                elif escolha == "7":
                    destino = BASE / "historico.csv"
                    total = historico.exportar(BASE / "historico.json", destino)
                    print(f"{total} registros exportados para {destino}")
                elif escolha == "8":
                    configurar_taxas()
                else:
                    print("Opção inválida. Escolha de 0 a 8.")
        except (ValueError, OSError, DecimalException) as erro:
            print(f"Não foi possível concluir a operação: {erro}")
        except (EOFError, KeyboardInterrupt):
            print("\nAté logo!")
            return
