def extrair_entidades(df):

    entidades = {}

    # ==========================
    # 👤 CONTRIBUINTES (clientes)
    # ==========================
    if "cliente" in df.columns:
        entidades["contribuintes"] = list(
            df["cliente"].dropna().astype(str).unique()
        )
    else:
        entidades["contribuintes"] = []

    # ==========================
    # 🏢 FORNECEDORES
    # ==========================
    if "fornecedor" in df.columns:
        entidades["fornecedores"] = list(
            df["fornecedor"].dropna().astype(str).unique()
        )
    else:
        entidades["fornecedores"] = []

    # ==========================
    # 🔗 RELAÇÕES
    # ==========================
    if "fornecedor" in df.columns and "cliente" in df.columns:
        entidades["relacoes"] = df[
            ["fornecedor", "cliente"]
        ].dropna()
    else:
        entidades["relacoes"] = None

    return entidades