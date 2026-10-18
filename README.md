# ConvertePy

Conversor de valores pelo terminal, desenvolvido em Python puro para um Desafio de Projeto da DIO. Demonstra funções, validação, persistência e testes sem dependências externas.

## Executar

Requer Python 3.10 ou superior. Abra o terminal na pasta deste repositório e execute:

```powershell
python main.py
```

Nenhuma instalação de pacote é necessária. Se você estiver na pasta local `DIO`, entre primeiro em `Project` com `cd Project`.

## Funcionalidades

| Categoria | Unidades |
| --- | --- |
| Comprimento | mm, cm, m, km |
| Massa | g, kg, t |
| Temperatura | c, f, k |
| Tempo | s, min, h, dia |
| Moedas | BRL, USD, EUR |

O menu permite repetir operações, consultar as últimas dez conversões, exportar o histórico e consultar ou atualizar taxas de câmbio.

Exemplo de sessão:

```text
Escolha: 1
Unidades: mm, cm, m, km
Valor: 2,5
Unidade de origem: km
Unidade de destino: m
Resultado: 2,5 km = 2500 m
Conversão salva no histórico.
```

## Regras

- Use ponto ou vírgula como separador decimal, sem separadores de milhar. `1.234` significa um inteiro e 234 milésimos.
- Comprimento, massa, tempo e dinheiro devem ser não negativos e finitos.
- Temperaturas negativas são aceitas até o zero absoluto: -273,15 °C, -459,67 °F ou 0 K.
- Unidades de categorias diferentes são rejeitadas. Converter para a mesma unidade preserva o valor.
- Valores monetários são apresentados com duas casas decimais e arredondamento `ROUND_HALF_UP`. O histórico guarda o resultado anterior ao arredondamento de apresentação.
- Os cálculos usam `Decimal` com precisão de 28 algarismos significativos; divisões periódicas têm precisão limitada.

## Câmbio manual e demonstrativo

As taxas iniciais são exemplos, **não cotações de mercado**: 1 USD = 5 BRL e 1 EUR = 6 BRL, com referência em 2026-10-18. Não há consultas à internet.

Cada taxa representa quantos reais equivalem a uma unidade da moeda. BRL é a base fixa de valor 1. No menu 8, informe taxas positivas e a data no formato `AAAA-MM-DD`. A conversão usa `valor × taxa_origem / taxa_destino`.

## Dados e recuperação de erros

Os arquivos ficam em `dados/`, independentemente da pasta em que o comando foi iniciado:

- `taxas.json`: taxas e data de referência, incluídas no projeto.
- `historico.json`: criado após a primeira conversão salva.
- `historico.csv`: exportado pelo menu 7, em UTF-8 com BOM e delimitador `;`.

Cada registro contém categoria, valor, unidades, resultado e data com fuso horário local. Conversões monetárias incluem a taxa aplicada e sua referência. Entradas inválidas não geram registros.

Arquivos JSON inválidos são informados e preservados. A gravação ocorre por arquivo temporário seguido de substituição. Se houver corrupção, feche o programa, faça uma cópia do arquivo e corrija seu conteúdo ou renomeie-o para reiniciar o histórico. Para taxas, restaure o exemplo do repositório. Se a gravação falhar, o resultado pode ter sido exibido, mas não haverá confirmação de salvamento.

## Testes

Na pasta `Project`:

```powershell
python -m unittest discover -s tests -v
```

Os testes verificam resultados conhecidos, conversões inversas, zero absoluto, entradas inválidas, câmbio fixo, arredondamento, persistência, CSV, preservação de arquivos inválidos e recuperação do menu. Usam pastas temporárias para preservar seus dados.

A revisão de entrega executou 12 testes com sucesso, incluindo todas as categorias pelo menu, atualização de taxas e datas com fuso horário. O cálculo monetário multiplica o valor pela taxa de origem antes de dividir pela taxa de destino para evitar arredondamento intermediário desnecessário.

## Organização e decisões

`main.py` inicia `conversor/interface.py`. Os módulos `unidades.py`, `temperaturas.py` e `moedas.py` recebem valores e retornam resultados sem ler o teclado. `validacao.py` valida entradas e `historico.py` concentra JSON e CSV.

1. **Decimal:** evita a representação binária de valores monetários e permite escolher explicitamente o arredondamento.
2. **Interface separada:** permite testar regras sem navegar pelo menu e facilita uma futura interface diferente.
3. **Resultados verificáveis:** exemplos conhecidos e arquivos temporários permitem conferir cálculos e persistência de forma repetível.

## Limitações e portfólio

Não há interface gráfica, usuários, banco de dados ou atualização automática de câmbio. A aplicação foi projetada para uma única execução por vez; não há coordenação entre processos que gravem os mesmos arquivos.

Para apresentar na DIO, publique o projeto em um repositório seu, inclua uma captura ou gravação de uma sessão e entregue o link com uma descrição do que implementou. Explique as três decisões acima com suas próprias palavras.

Para o laboratório **Contribuindo em um Projeto Open Source no GitHub**, a entrega é o Profile README no diretório `community` do fork [Guilherme-DEV-ALT/dio-lab-open-source](https://github.com/Guilherme-DEV-ALT/dio-lab-open-source), acompanhado de um pull request para o repositório da DIO. O código do ConvertePy é um projeto de portfólio e deve ser publicado separadamente; ele não faz parte do PR desse laboratório.
