import re
import sys
from pathlib import Path

import pandas as pd


def normalizar_nome(nome: str) -> str:
    if not isinstance(nome, str):
        return ""
    return re.sub(r"\s+", " ", nome.strip()).lower()


def normalizar_empresa(empresa: str) -> str:
    """Normaliza o nome da empresa para comparação (case-insensitive, sem espaços extras)."""
    if not isinstance(empresa, str):
        return ""
    return re.sub(r"\s+", " ", empresa.strip()).lower()


def parsear_grupos(valor: str) -> tuple[str, str]:
    """Extrai estado e empresa do campo Grupos.

    Formato esperado: 'Pernambuco: Aponti PE - 00.501.070/0001-23'
    Retorna: (estado, empresa)
    """
    if not isinstance(valor, str):
        return ("", "")
    partes = valor.split(":", 1)
    if len(partes) < 2:
        return (valor.strip(), "")
    estado = partes[0].strip()
    resto = partes[1].strip()
    empresa = resto.split(" - ")[0].strip()
    return (estado, empresa)


def listar_csvs(diretorio: Path) -> list[Path]:
    csvs = sorted(diretorio.glob("*.csv"))
    if not csvs:
        print("Nenhum arquivo .csv encontrado no diretório atual.")
        sys.exit(1)
    print("\nArquivos CSV encontrados:")
    for i, f in enumerate(csvs, 1):
        print(f"  [{i}] {f.name}")
    return csvs


def selecionar_planilha_geral(csvs: list[Path]) -> Path:
    while True:
        try:
            escolha = int(input("\nDigite o número da planilha GERAL de alunos: "))
            if 1 <= escolha <= len(csvs):
                return csvs[escolha - 1]
            print(f"  Digite um número entre 1 e {len(csvs)}.")
        except ValueError:
            print("  Entrada inválida. Digite apenas o número.")


def carregar_alunos(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str).fillna("")

    colunas_necessarias = {"Nome", "Sobrenome"}
    faltando = colunas_necessarias - set(df.columns)
    if faltando:
        print(f"ERRO: A planilha geral não tem as colunas: {faltando}")
        sys.exit(1)

    df["nome_completo"] = (df["Nome"] + " " + df["Sobrenome"]).str.strip()
    df["_nome_norm"] = df["nome_completo"].apply(normalizar_nome)

    if "Grupos" in df.columns:
        grupos_parsed = df["Grupos"].apply(parsear_grupos)
        df["estado"] = grupos_parsed.apply(lambda x: x[0])
        df["empresa"] = grupos_parsed.apply(lambda x: x[1])
    else:
        df["estado"] = ""
        df["empresa"] = ""

    return df[["nome_completo", "_nome_norm", "estado", "empresa"]].drop_duplicates(
        subset=["_nome_norm"]
    )


def selecionar_filtro_empresa(df_alunos: pd.DataFrame) -> str | None:
    """Pergunta ao usuário se deseja filtrar por empresa e retorna o filtro escolhido."""
    empresas_unicas = sorted(df_alunos["empresa"].unique().tolist())
    empresas_unicas = [e for e in empresas_unicas if e]  # remove vazios

    if not empresas_unicas:
        print("\nNenhuma empresa encontrada na planilha. Auditando todos.")
        return None

    print("\nEmpresas encontradas:")
    print("  [0] Todas as empresas (sem filtro)")
    for i, emp in enumerate(empresas_unicas, 1):
        print(f"  [{i}] {emp}")

    while True:
        try:
            escolha = int(input("\nFiltrar por empresa? Digite o número (0 para todas): "))
            if escolha == 0:
                return None
            if 1 <= escolha <= len(empresas_unicas):
                empresa_selecionada = empresas_unicas[escolha - 1]
                print(f"\nFiltro aplicado: apenas residentes de '{empresa_selecionada}'")
                return empresa_selecionada
            print(f"  Digite um número entre 0 e {len(empresas_unicas)}.")
        except ValueError:
            print("  Entrada inválida. Digite apenas o número.")


def filtrar_por_empresa(df_alunos: pd.DataFrame, empresa: str | None) -> pd.DataFrame:
    """Filtra o DataFrame de alunos pela empresa (parcial, case-insensitive)."""
    if not empresa:
        return df_alunos

    filtro = normalizar_empresa(empresa)
    mask = df_alunos["empresa"].apply(normalizar_empresa).str.contains(filtro, regex=False)
    df_filtrado = df_alunos[mask].copy()

    if df_filtrado.empty:
        print(f"\nAVISO: Nenhum aluno encontrado para a empresa '{empresa}'.")

    return df_filtrado


def carregar_relatorio(path: Path) -> set[str]:
    df = pd.read_csv(path, dtype=str).fillna("")

    if "Nome completo" not in df.columns:
        print(f"  AVISO: '{path.name}' não tem coluna 'Nome completo'. Pulando.")
        return set()

    return {normalizar_nome(n) for n in df["Nome completo"] if n.strip()}


def calcular_ausencias(
    df_alunos: pd.DataFrame, relatorios: dict[str, set[str]]
) -> pd.DataFrame:
    linhas = []
    for _, aluno in df_alunos.iterrows():
        ausentes = [
            nome_rel
            for nome_rel, respondentes in relatorios.items()
            if aluno["_nome_norm"] not in respondentes
        ]
        if ausentes:
            linhas.append(
                {
                    "nome_completo": aluno["nome_completo"],
                    "estado": aluno["estado"],
                    "empresa": aluno["empresa"],
                    "relatorios_ausentes": ", ".join(sorted(ausentes)),
                    "total_ausencias": len(ausentes),
                }
            )
    return pd.DataFrame(linhas)


def exibir_resultado(df: pd.DataFrame, nomes_relatorios: list[str], empresa_filtro: str | None) -> None:
    print(f"\nRelatórios processados: {', '.join(sorted(nomes_relatorios))}")
    if empresa_filtro:
        print(f"Filtro de empresa aplicado: {empresa_filtro}")
    print("-" * 80)

    if df.empty:
        print("\nTodos os alunos responderam todos os relatórios.")
        return

    col_nome = max(df["nome_completo"].str.len().max(), len("Nome Completo"))
    col_estado = max(df["estado"].str.len().max(), len("Estado"))
    col_empresa = max(df["empresa"].str.len().max(), len("Empresa"))

    header = (
        f"{'Nome Completo':<{col_nome}}  "
        f"{'Estado':<{col_estado}}  "
        f"{'Empresa':<{col_empresa}}  "
        f"Relatórios Ausentes"
    )
    print(f"\nAlunos com ausências:\n{header}")
    print("-" * len(header))

    for _, row in df.iterrows():
        print(
            f"{row['nome_completo']:<{col_nome}}  "
            f"{row['estado']:<{col_estado}}  "
            f"{row['empresa']:<{col_empresa}}  "
            f"{row['relatorios_ausentes']}"
        )

    print(f"\nTotal: {len(df)} aluno(s) com pelo menos 1 ausência.")


def salvar_resultado(df: pd.DataFrame, destino: Path, empresa_filtro: str | None) -> None:
    if df.empty:
        print("Nenhuma ausência encontrada. Arquivo de resultado não gerado.")
        return

    # Se houver filtro, inclui o nome da empresa no arquivo de saída
    if empresa_filtro:
        sufixo = re.sub(r"[^\w]", "_", empresa_filtro.strip().lower())
        destino = destino.parent / f"resultado_auditoria_{sufixo}.csv"

    df.to_csv(destino, index=False, encoding="utf-8-sig")
    print(f"Resultado salvo em: {destino}")


def main() -> None:
    diretorio = Path(".")
    csvs = listar_csvs(diretorio)
    planilha_geral = selecionar_planilha_geral(csvs)

    print(f"\nCarregando planilha geral: {planilha_geral.name}")
    df_alunos = carregar_alunos(planilha_geral)
    print(f"  {len(df_alunos)} aluno(s) encontrado(s).")

    # --- Filtro por empresa ---
    empresa_filtro = selecionar_filtro_empresa(df_alunos)
    df_alunos = filtrar_por_empresa(df_alunos, empresa_filtro)
    print(f"  {len(df_alunos)} aluno(s) após filtro.")

    if df_alunos.empty:
        print("Nenhum aluno para auditar. Encerrando.")
        sys.exit(0)

    relatorios_paths = [p for p in csvs if p != planilha_geral]
    if not relatorios_paths:
        print("Nenhum relatório encontrado além da planilha geral. Encerrando.")
        sys.exit(0)

    relatorios: dict[str, set[str]] = {}
    for path in relatorios_paths:
        respondentes = carregar_relatorio(path)
        if respondentes or "Nome completo" in pd.read_csv(path, nrows=0).columns:
            relatorios[path.stem] = respondentes

    if not relatorios:
        print("Nenhum relatório válido encontrado. Encerrando.")
        sys.exit(0)

    df_resultado = calcular_ausencias(df_alunos, relatorios)
    exibir_resultado(df_resultado, list(relatorios.keys()), empresa_filtro)
    salvar_resultado(df_resultado, diretorio / "resultado_auditoria.csv", empresa_filtro)


if __name__ == "__main__":
    main()