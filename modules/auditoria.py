# ✅ DETECTAR VALORES INVALIDOS
def detectar_valores_invalidos(df):
    if "valor" not in df.columns:
        return None
    invalidos = df[df["valor"] <= 0].copy()
    invalidos['motivo_anomalia'] = invalidos['valor'].apply(lambda x: "Valor Negativo" if x < 0 else "Valor Zero")
    return invalidos


# ✅ CLIENTES SEM NOME (opcional)
def clientes_sem_nome(df):
    if "cliente" not in df.columns:
        return None
    invalidos = df[df["cliente"].isna()].copy()
    invalidos['motivo_anomalia'] = "Contribuinte sem Nome/Identificação"
    return invalidos


# ✅ TOP SUSPEITOS
def top_suspeitos(df):
    if "valor" not in df.columns:
        return None
    top = df.sort_values(by="valor", ascending=False).head(10).copy()
    top['motivo_anomalia'] = "Top 10 Valores Mais Altos do Ficheiro"
    return top


# ✅ DETECTAR ANOMALIAS
def detectar_anomalias(df):
    if "valor" not in df.columns:
        return None

    media = df["valor"].mean()
    anomalias = df[df["valor"] > media * 5].copy()
    anomalias['motivo_anomalia'] = anomalias['valor'].apply(lambda x: f"Valor 5x superior à média do ficheiro (Média: {media:,.2f})")
    return anomalias


# ✅ CRUZAMENTO
def cruzar_dados(df):
    if "fornecedor" not in df.columns or "cliente" not in df.columns or "valor" not in df.columns:
        return None, None

    cruzado = df.groupby(["fornecedor", "cliente"])["valor"].sum().reset_index()
    problemas = cruzado[cruzado["valor"] == 0]

    return cruzado, problemas


# ✅ ALERTAS
def gerar_alertas(df):
    alertas = []

    if "valor" in df.columns:
        if df["valor"].max() > 10_000_000:
            alertas.append("⚠️ Valores muito altos detectados")

        if df["valor"].min() <= 0:
            alertas.append("⚠️ Existem valores inválidos")

    if "cliente" in df.columns and df["cliente"].isna().sum() > 0:
        alertas.append("⚠️ Existem clientes sem identificação")

    return alertas