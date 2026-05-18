import streamlit as st
import pandas as pd

def aplicar_filtros(df):
    st.sidebar.title("🔎 Filtros")

    # ==========================
    # 👤 FILTRO CLIENTE
    # ==========================
    if "cliente" in df.columns:
        clientes = st.sidebar.multiselect(
            "Cliente",
            sorted(df["cliente"].dropna().unique())
        )
        if clientes:
            df = df[df["cliente"].isin(clientes)]

    # ==========================
    # 🏢 FILTRO FORNECEDOR
    # ==========================
    if "fornecedor" in df.columns:
        forn = st.sidebar.multiselect(
            "Fornecedor",
            sorted(df["fornecedor"].dropna().unique())
        )
        if forn:
            df = df[df["fornecedor"].isin(forn)]

    # ==========================
    # 📑 FILTRO FATURA
    # ==========================
    if "fatura" in df.columns:
        faturas = st.sidebar.multiselect(
            "Número de Fatura",
            sorted(df["fatura"].dropna().unique())
        )
        if faturas:
            df = df[df["fatura"].isin(faturas)]

    # ==========================
    # 🔍 BUSCA GLOBAL
    # ==========================
    search = st.sidebar.text_input("🔍 Busca Global (Qualquer campo)")
    if search:
        df = df[df.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)]

    # ==========================
    # 💰 FILTRO VALOR (CORRIGIDO)
    # ==========================
    if "valor" in df.columns:
        # garantir que não há valores nulos
        df["valor"] = pd.to_numeric(df["valor"], errors='coerce').fillna(0)

        min_val = float(df["valor"].min())
        max_val = float(df["valor"].max())

        # ✅ CASO NORMAL (intervalo válido)
        if min_val < max_val:
            selected_range = st.sidebar.slider(
                "Intervalo de Valor",
                min_val,
                max_val,
                (min_val, max_val)
            )

            df = df[
                (df["valor"] >= selected_range[0]) &
                (df["valor"] <= selected_range[1])
            ]
        else:
            st.sidebar.info(
                f"⚠️ Todos os valores são iguais ({min_val:,.0f}). Filtro desativado."
            )

    return df