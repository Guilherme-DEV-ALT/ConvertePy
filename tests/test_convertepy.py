import csv
import json
import tempfile
import unittest
from datetime import datetime
from decimal import Decimal as D
from pathlib import Path
from unittest.mock import patch
from contextlib import redirect_stdout
from io import StringIO

from conversor import historico, interface, moedas, temperaturas, unidades
from conversor.validacao import numero


class ConversoesTest(unittest.TestCase):
    def test_unidades_e_inversas(self):
        for categoria, origem, destino, esperado in (
            ("comprimento", "km", "m", "2500"),
            ("massa", "t", "g", "2500000"),
            ("tempo", "dia", "h", "60"),
        ):
            with self.subTest(categoria=categoria):
                resultado = unidades.converter(D("2.5"), categoria, origem, destino)
                self.assertEqual(resultado, D(esperado))
                self.assertEqual(unidades.converter(resultado, categoria, destino, origem), D("2.5"))

    def test_mesma_unidade(self):
        self.assertEqual(unidades.converter(D("3"), "massa", "kg", "kg"), D("3"))
        self.assertEqual(temperaturas.converter(D("-12"), "c", "c"), D("-12"))

    def test_temperaturas(self):
        for valor, origem, destino, esperado in (
            ("0", "c", "f", "32"), ("32", "f", "c", "0"),
            ("0", "k", "c", "-273.15"), ("-459.67", "f", "k", "0"),
            ("100", "c", "k", "373.15"),
        ):
            self.assertEqual(temperaturas.converter(D(valor), origem, destino), D(esperado))
        for origem, valor in (("c", "-273.16"), ("f", "-459.68"), ("k", "-0.01")):
            with self.assertRaises(ValueError):
                temperaturas.converter(D(valor), origem, "c")

    def test_validacao(self):
        self.assertEqual(numero(" 2,5 "), D("2.5"))
        self.assertEqual(numero("2.5"), D("2.5"))
        for texto in ("abc", "NaN", "Infinity", "1.000,00", "1,000.00", "", "1 000"):
            with self.subTest(texto=texto), self.assertRaises(ValueError):
                numero(texto)
        for valor in ("-1", "NaN", "Infinity"):
            with self.assertRaises(ValueError):
                unidades.converter(D(valor), "massa", "kg", "g")
        with self.assertRaises(ValueError):
            unidades.converter(D("1"), "massa", "kg", "m")

    def test_moedas_e_arredondamento(self):
        dados = {"data_referencia": "2026-10-18", "taxas": {"BRL": "1", "USD": "5", "EUR": "6"}}
        self.assertEqual(moedas.converter(D("10"), "USD", "BRL", dados), (D("50"), D("5")))
        self.assertEqual(moedas.converter(D("10"), "EUR", "USD", dados)[0], D("12"))
        self.assertEqual(interface.formatar(D("1.005"), True), "1,01")
        # A taxa 5/6 é periódica, mas 3 USD equivalem exatamente a 2,5 EUR.
        self.assertEqual(moedas.converter(D("3"), "USD", "EUR", dados)[0], D("2.5"))
        for taxa in ("0", "-1", "NaN", "Infinity"):
            dados["taxas"]["USD"] = taxa
            with self.assertRaises(ValueError):
                moedas.validar_taxas(dados)

    def test_moedas_rejeitam_valores_e_cadastros_invalidos(self):
        dados = {"data_referencia": "2026-10-18", "taxas": {"BRL": "1", "USD": "5", "EUR": "6"}}
        for valor in ("-1", "NaN", "Infinity"):
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                moedas.converter(D(valor), "USD", "BRL", dados)
        with self.assertRaises(ValueError):
            moedas.converter(D("1"), "GBP", "BRL", dados)
        for cadastro in ({}, [], {**dados, "data_referencia": "2026-02-30"},
                         {**dados, "taxas": {"BRL": "2", "USD": "5", "EUR": "6"}}):
            with self.subTest(cadastro=cadastro), self.assertRaises(ValueError):
                moedas.validar_taxas(cadastro)


class PersistenciaTest(unittest.TestCase):
    def setUp(self):
        self.temporario = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporario.cleanup)
        self.base = Path(self.temporario.name)

    def test_historico_e_csv(self):
        caminho = self.base / "historico.json"
        registro = dict(categoria="massa", valor="1", origem="kg", destino="g",
                        resultado="1000", data="2026-10-18T10:00:00-03:00", taxa="", data_referencia="")
        historico.registrar(caminho, registro)
        self.assertEqual(historico.carregar(caminho), [registro])
        destino = self.base / "historico.csv"
        self.assertEqual(historico.exportar(caminho, destino), 1)
        with destino.open(encoding="utf-8-sig", newline="") as arquivo:
            self.assertEqual(list(csv.DictReader(arquivo, delimiter=";")), [registro])

    def test_arquivo_invalido_preservado(self):
        caminho = self.base / "historico.json"
        for conteudo in ("{ quebrado", '{}', '[{}]'):
            caminho.write_text(conteudo, encoding="utf-8")
            with self.assertRaises(ValueError):
                historico.registrar(caminho, {})
            self.assertEqual(caminho.read_text(encoding="utf-8"), conteudo)

    def test_taxas_persistidas(self):
        caminho = self.base / "taxas.json"
        dados = {"data_referencia": "2026-10-18", "taxas": {"BRL": "1", "USD": "5", "EUR": "6"}}
        moedas.salvar(caminho, dados)
        self.assertEqual(moedas.carregar(caminho), dados)

    def test_taxas_corrompidas_preservadas(self):
        caminho = self.base / "taxas.json"
        original = '{"taxas": "inválidas"}'
        caminho.write_text(original, encoding="utf-8")
        dados = {"data_referencia": "2026-10-18", "taxas": {"BRL": "1", "USD": "5", "EUR": "6"}}
        with self.assertRaises(ValueError):
            moedas.salvar(caminho, dados)
        self.assertEqual(caminho.read_text(encoding="utf-8"), original)

    def test_menu_todas_categorias_e_atualizacao_taxas(self):
        dados = {"data_referencia": "2026-10-18", "taxas": {"BRL": "1", "USD": "5", "EUR": "6"}}
        (self.base / "taxas.json").write_text(json.dumps(dados), encoding="utf-8")
        entradas = ["2", "2", "kg", "g", "3", "0", "c", "f", "4", "1", "dia", "h",
                    "8", "s", "2026-10-18", "5,5", "6,5", "5", "2", "usd", "brl", "0"]
        with patch.object(interface, "BASE", self.base), patch("builtins.input", side_effect=entradas), redirect_stdout(StringIO()):
            interface.executar()
        registros = historico.carregar(self.base / "historico.json")
        self.assertEqual([D(item["resultado"]) for item in registros], [D("2000"), D("32"), D("24"), D("11")])
        self.assertTrue(all(datetime.fromisoformat(item["data"]).utcoffset() is not None
                            for item in registros))
        self.assertEqual(moedas.carregar(self.base / "taxas.json")["taxas"]["USD"], "5.5")

    def test_menu_recupera_erro_e_registra_apenas_sucesso(self):
        entradas = ["9", "1", "abc", "1", "2,5", "km", "m", "5", "10", "usd", "brl", "6", "7", "0"]
        saida = StringIO()
        (self.base / "taxas.json").write_text(json.dumps({
            "data_referencia": "2026-10-18", "taxas": {"BRL": "1", "USD": "5", "EUR": "6"}
        }), encoding="utf-8")
        with patch.object(interface, "BASE", self.base), patch("builtins.input", side_effect=entradas), redirect_stdout(saida):
            interface.executar()
        registros = historico.carregar(self.base / "historico.json")
        self.assertEqual(len(registros), 2)
        self.assertEqual(D(registros[0]["resultado"]), D("2500"))
        self.assertEqual(registros[1]["taxa"], "5")
        self.assertIn("Opção inválida", saida.getvalue())
        self.assertIn("Até logo!", saida.getvalue())
        self.assertTrue((self.base / "historico.csv").exists())


if __name__ == "__main__":
    unittest.main()
