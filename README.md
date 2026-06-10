# Auditoria de Relatórios — Residentes Aponti

## Autores

- Leandro Carvalho [Linkedin](https://www.linkedin.com/in/leandro-c-s/)
- Caio Tenório [Linkedin](https://www.linkedin.com/in/caiomatenorio/)

Script para auditar quais residentes/alunos responderam (ou não) seus relatórios semanais.

## Requisitos

- Python 3.10+
- pandas

```bash
pip install pandas
```

## Como usar

### Modo interativo (sem argumentos)

Execute o script sem argumentos:

```bash
python pente_fino.py
```

O script fará 4 perguntas em sequência:

1. **Pasta de input** (onde estão os CSVs)
   - Deixe em branco ou pressione Enter para usar a pasta atual

2. **Planilha principal**
   - Escolha o número da planilha geral de alunos (será listada os CSVs encontrados)

3. **Modo de visualização**
   - Escolha: `1` para "Não feitos" ou `2` para "Feitos"

4. **Caminho de saída**
   - Deixe em branco para salvar em `./resultado.csv`
   - Ou informe um caminho completo

### Modo CLI (com argumentos)

Você pode passar alguns ou todos os argumentos na linha de comando, pulando as perguntas interativas:

```bash
python pente_fino.py --pasta-origem ./relatorios -p residentes.csv -m nao_feitos -o resultado_custom.csv
```

**Importante:** Quando você passa `--planilha` via CLI, o script ignora a pasta de input e busca o arquivo no caminho descrito (absoluto ou relativo à pasta atual onde você rodar o comando).

### Exemplos

```bash
# Modo interativo completo
python pente_fino.py

# Modo interativo com pasta de input já definida
python pente_fino.py --pasta-origem ./relatorios

# Modo semi-automático: abre a pasta, pergunta o resto
python pente_fino.py -d ./relatorios

# Modo CLI completo: nenhuma pergunta
python pente_fino.py -d ./relatorios -p residentes.csv -m nao_feitos -o saida.csv

# Planilha em outro local: busca o arquivo sem considerar pasta de input
python pente_fino.py -p /home/user/dados/residentes.csv -m feitos
```

### Argumentos de CLI

- `--pasta-origem` ou `-d`: Define a pasta onde estão os CSVs (padrão interativo: pasta atual)
- `--planilha` ou `-p`: Define a planilha geral (em modo CLI, ignora a pasta de input e usa o caminho descrito)
- `--modo` ou `-m`: Escolhe o modo: `feitos` ou `nao_feitos`
- `--output` ou `-o`: Define o arquivo de saída (padrão: `./resultado.csv`)

## Formato esperado das planilhas

### Planilha geral de alunos

| Nome   | Sobrenome       | Endereço de e-mail | Grupos                                     |
| ------ | --------------- | ------------------ | ------------------------------------------ |
| ADRIEL | FULANO DA SILVA | fulano@email.com   | Pernambuco: Aponti PE - 00.501.070/0001-23 |

O campo **Grupos** deve seguir o formato `Estado: Empresa - CNPJ`. Estado e empresa são extraídos automaticamente.

### Planilhas de relatório

Devem conter uma coluna chamada **`Nome completo`** com o nome de quem respondeu.

| Nome completo          | Grupos | Endereço de e-mail | Data | ... |
| ---------------------- | ------ | ------------------ | ---- | --- |
| ADRIEL FULANO DA SILVA | ...    | ...                | ...  | ... |

## Resultado

### Modo 1: Não feitos

Mostra alunos que **não responderam** relatórios.

#### Terminal

```
Relatórios processados: relatorio_semana_01, relatorio_semana_02

Nome Completo              Estado       Empresa      Relatórios Ausentes    Total
-------------------------- ------------ ------------ ---------------------- -----
ADRIEL FULANO DA SILVA     Pernambuco   Aponti PE    relatorio_semana_02    1
MARIA FULANA               São Paulo    Aponti SP    relatorio_semana_01    1

Total: 2 aluno(s) | 2 aluno(s) com pelo menos 1 ausência.
Resultado salvo em: resultado_auditoria.csv
```

#### Arquivo `resultado_auditoria.csv`

| nome_completo | estado | empresa | relatorios_ausentes | total_ausencias |
|---|---|---|---|---|
| ADRIEL FULANO DA SILVA | Pernambuco | Aponti PE | relatorio_semana_02 | 1 |
| MARIA FULANA | São Paulo | Aponti SP | relatorio_semana_01 | 1 |

### Modo 2: Feitos

Mostra alunos que **responderam** relatórios. Exibe todos os alunos, indicando quais relatórios cada um completou.

#### Terminal

```
Relatórios processados: relatorio_semana_01, relatorio_semana_02

Nome Completo              Estado       Empresa      Relatórios Feitos                           Total
-------------------------- ------------ ------------ ------------------------------------------- -----
ADRIEL FULANO DA SILVA     Pernambuco   Aponti PE    relatorio_semana_01                        1
MARIA FULANA               São Paulo    Aponti SP    relatorio_semana_01, relatorio_semana_02   2
JOÃO SILVA                 Pernambuco   Aponti PE    Nenhum                                      0

Total: 3 aluno(s) | 2 aluno(s) com pelo menos 1 relatório feito.
Resultado salvo em: resultado_relatorios_feitos.csv
```

#### Arquivo `resultado_relatorios_feitos.csv`

| nome_completo | estado | empresa | relatorios_feitos | total_feitos |
|---|---|---|---|---|
| ADRIEL FULANO DA SILVA | Pernambuco | Aponti PE | relatorio_semana_01 | 1 |
| MARIA FULANA | São Paulo | Aponti SP | relatorio_semana_01, relatorio_semana_02 | 2 |
| JOÃO SILVA | Pernambuco | Aponti PE | | 0 |

## Arquivos de saída

Os CSVs são salvos com encoding `UTF-8 BOM` para abrir corretamente no Excel:
- **`resultado_auditoria.csv`**: gerado no modo "Não feitos"
- **`resultado_relatorios_feitos.csv`**: gerado no modo "Feitos"

## Observações

- A comparação de nomes é **case-insensitive** e ignora espaços extras — variações de digitação não geram falsos negativos.
- Se um relatório não tiver a coluna `Nome completo`, um aviso é exibido e o arquivo é pulado.
- Alunos presentes em todos os relatórios não aparecem no resultado.
