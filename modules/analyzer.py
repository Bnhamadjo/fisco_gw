def calcular_volume_negocio(df):
    if "valor" not in df.columns:
        return 0
    return df["valor"].sum()

def resumo_clientes(df):
    if "cliente" not in df.columns or "valor" not in df.columns:
        return None
    return df.groupby("cliente")["valor"].sum().reset_index()

def resumo_fornecedores(df):
    if "fornecedor" not in df.columns or "valor" not in df.columns:
        return None
    return df.groupby("fornecedor")["valor"].sum().reset_index()

def encontrar_coluna_valor(df):
    for col in df.columns:
        if "valor" in col or "total" in col or "montante" in col:
            return col
    return None