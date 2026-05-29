# Auditoria de Relatórios — Residentes Aponti

## Autores

- Leandro Carvalho [Linkedin](https://www.linkedin.com/in/leandro-c-s/)
- Caio Tenório [Linkedin](https://www.linkedin.com/in/caiomatenorio/)

Script para identificar quais residentes/alunos não responderam seus relatórios semanais.

## Requisitos

- Python 3.10+
- pandas

```bash
pip install pandas
```

## Como usar

1. Coloque todos os arquivos `.csv` no mesmo diretório:
   - A **planilha geral** de alunos
   - As **planilhas de relatório** (uma por relatório)

2. Execute o script na pasta onde estão os arquivos:

```bash
python pente_fino.py
```

3. O script lista os CSVs encontrados e pergunta qual é a planilha geral:

```
Arquivos CSV encontrados:
  [1] alunos.csv
  [2] relatorio_semana_01.csv
  [3] relatorio_semana_02.csv

Digite o número da planilha GERAL de alunos: 1
```

4. Em seguida, o script exibe as empresas encontradas e pergunta se deseja filtrar:

```
Empresas encontradas:
  [0] Todas as empresas (sem filtro)
  [1] Aponti PE
  [2] Aponti SP
  [3] Aponti RN

  Dica: para várias empresas, separe os números com espaço (ex: 1 3)

Filtrar por empresa? Digite o(s) número(s) (0 para todas): 1
```

- Digite **0** para auditar todos os residentes sem distinção de empresa.
- Digite **um número** para filtrar por uma empresa específica.
- Digite **vários números separados por espaço** para filtrar por múltiplas empresas ao mesmo tempo (ex: `1 3` seleciona Aponti PE + Aponti RN).

5. O resultado é exibido no terminal e salvo em arquivo `.csv`.

## Formato esperado das planilhas

### Planilha geral de alunos

| Nome   | Sobrenome       | Endereço de e-mail | Grupos                                     |
|--------|-----------------|--------------------|--------------------------------------------|
| ADRIEL | FULANO DA SILVA | fulano@email.com   | Pernambuco: Aponti PE - 00.501.070/0001-23 |

O campo **Grupos** deve seguir o formato `Estado: Empresa - CNPJ`. Estado e empresa são extraídos automaticamente.

### Planilhas de relatório

Devem conter uma coluna chamada **`Nome completo`** com o nome de quem respondeu.

| Nome completo          | Grupos | Endereço de e-mail | Data | ... |
|------------------------|--------|--------------------|------|-----|
| ADRIEL FULANO DA SILVA | ...    | ...                | ...  | ... |

## Resultado

### Terminal

```
Relatórios processados: relatorio_semana_01, relatorio_semana_02
Filtro de empresa aplicado: Aponti PE
--------------------------------------------------------------------------------

Alunos com ausências:
Nome Completo           Estado      Empresa    Relatórios Ausentes
----------------------- ----------- ---------- -------------------
ADRIEL FULANO DA SILVA  Pernambuco  Aponti PE  relatorio_semana_02

Total: 1 aluno(s) com pelo menos 1 ausência.
Resultado salvo em: resultado_auditoria_aponti_pe.csv
```

### Arquivo de saída `.csv`

| nome_completo          | estado     | empresa   | relatorios_ausentes   | total_ausencias |
|------------------------|------------|-----------|-----------------------|-----------------|
| ADRIEL FULANO DA SILVA | Pernambuco | Aponti PE | relatorio_semana_02   | 1               |

O CSV é salvo com encoding `UTF-8 BOM` para abrir corretamente no Excel.

**Nome do arquivo de saída:**
- Sem filtro: `resultado_auditoria.csv`
- Com filtro de uma empresa: `resultado_auditoria_aponti_pe.csv`
- Com filtro de múltiplas empresas: `resultado_auditoria_aponti_pe_aponti_rn.csv`

## Observações

- A comparação de nomes é **case-insensitive** e ignora espaços extras — variações de digitação não geram falsos negativos.
- Se um relatório não tiver a coluna `Nome completo`, um aviso é exibido e o arquivo é pulado.
- Alunos presentes em todos os relatórios não aparecem no resultado.
- O filtro de empresa também é **case-insensitive**.
