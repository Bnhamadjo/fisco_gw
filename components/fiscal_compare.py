import streamlit as st


def cruzamento_fiscal(df):

    st.subheader("⚖️ Cruzamento Fiscal Avançado")

    if "valor" not in df.columns:
        st.warning("Sem dados financeiros")
        return

    total = df["valor"].sum()

    # ==========================
    # SEPARAÇÃO CRÍTICA ✅
    # ==========================
    compras = 0
    vendas = 0

    if "cliente" in df.columns:
        compras = df[df["cliente"].notna()]["valor"].sum()

    if "fornecedor" in df.columns:
        vendas = df[df["fornecedor"].notna()]["valor"].sum()

    margem = vendas - compras

    # ==========================
    # IMPOSTO
    # ==========================
    imposto_estimado = margem * 0.25 if margem > 0 else 0
    minimo = total * 0.01

    imposto_final = max(imposto_estimado, minimo)

    # ==========================
    # KPIs
    # ==========================
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("💰 Volume total", f"{total:,.0f}")
    col2.metric("🛒 Compras", f"{compras:,.0f}")
    col3.metric("🏪 Vendas", f"{vendas:,.0f}")
    col4.metric("📊 Margem", f"{margem:,.0f}")

    st.metric("⚖️ Imposto estimado", f"{imposto_final:,.0f}")

    # ==========================
    # ALERTAS INTELIGENTES 🔥
    # ==========================
    st.subheader("🚨 Análise de Consistência")

    if total < 100000:
        st.warning("⚠️ Faturação muito baixa")

    if total > 10_000_000:
        st.warning("⚠️ Volume elevado — verificar consistência")

    if margem < 0:
        st.error("❌ Margem negativa → possível evasão ou inconsistência")

    if vendas > 0 and compras > vendas * 2:
        st.warning("⚠️ Compras muito superiores às vendas")

    if vendas > compras * 5:
        st.warning("⚠️ Vendas muito acima do padrão")

    # ==========================
    # ANÁLISE DE RISCO
    # ==========================
    ratio = vendas / compras if compras > 0 else 0

    if 0 < ratio < 0.5:
        st.warning("⚠️ Baixa conversão — vendas muito baixas")

    if ratio > 5:
        st.warning("⚠️ Relação compras/vendas anormal")

    # ==========================
    # INTERPRETAÇÃO
    # ==========================
    st.subheader("🧠 Interpretação")

    st.write(f"""
    - Volume Total: {total:,.0f}
    - Compras: {compras:,.0f}
    - Vendas: {vendas:,.0f}
    - Margem estimada: {margem:,.0f}
    - Imposto calculado: {imposto_final:,.0f}
    """)