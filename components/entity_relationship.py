import streamlit as st


def analisar_relacao(df):

    st.subheader("🔗 Relação entre Contribuintes")

    if df is None:
        st.warning("Sem dados carregados")
        return

    if "cliente" not in df.columns or "fornecedor" not in df.columns:
        st.warning("Dados insuficientes (cliente/fornecedor)")
        return

    # ==========================
    # LISTA DE ENTIDADES
    # ==========================
    entidades = list(set(
        df["cliente"].dropna().astype(str).tolist() +
        df["fornecedor"].dropna().astype(str).tolist()
    ))

    if not entidades:
        st.warning("Sem entidades disponíveis")
        return

    # ==========================
    # SELEÇÃO
    # ==========================
    contribuinte1 = st.selectbox("Contribuinte principal", entidades)

    df_rel_geral = df[
        (df["cliente"] == contribuinte1) |
        (df["fornecedor"] == contribuinte1)
    ]

    st.subheader("📄 Transações do contribuinte")
    st.dataframe(df_rel_geral)

    # ==========================
    # PARCEIROS
    # ==========================
    parceiros = list(set(
        df_rel_geral["cliente"].tolist() +
        df_rel_geral["fornecedor"].tolist()
    ))

    parceiros = [p for p in parceiros if p != contribuinte1]

    if not parceiros:
        st.info("Sem parceiros")
        return

    contribuinte2 = st.selectbox("Seleciona parceiro", parceiros)

    # ==========================
    # RELAÇÃO ENTRE DOIS
    # ==========================
    df_pair = df[
        ((df["cliente"] == contribuinte1) & (df["fornecedor"] == contribuinte2)) |
        ((df["cliente"] == contribuinte2) & (df["fornecedor"] == contribuinte1))
    ]

    st.subheader(f"🔗 Relação: {contribuinte1} ↔ {contribuinte2}")
    st.dataframe(df_pair)

    # ==========================
    # KPIs + ALERTAS
