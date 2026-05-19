import streamlit as st
import pandas as pd


def analise_temporal(df):

    st.subheader("📅 Análise Temporal de Faturação")

    if df is None:
        st.warning("Sem dados disponíveis")
        return

    # ==========================
    # DETECTAR COLUNA DE DATA
    # ==========================
    col_data = None

    for col in df.columns:
        if "data" in col:
            col_data = col
            break

    if col_data is None:
        st.warning("⚠️ Nenhuma coluna de data encontrada")
        return

    # converter para datetime
    df[col_data] = pd.to_datetime(df[col_data], errors="coerce")
    if df[col_data].dt.tz is not None:
        df[col_data] = df[col_data].dt.tz_localize(None)

    # verificar coluna valor
    if "valor" not in df.columns:
        st.warning("⚠️ Sem coluna 'valor'")
        return

    # ==========================
    # SELECIONAR PERÍODO
    # ==========================
    periodo = st.selectbox(
        "Seleciona período",
        ["Mensal", "Trimestral", "Semestral", "Anual"]
    )

    if periodo == "Mensal":
        df["periodo"] = df[col_data].dt.to_period("M")
    elif periodo == "Trimestral":
        df["periodo"] = df[col_data].dt.to_period("Q")
    elif periodo == "Semestral":
        df["periodo"] = df[col_data].dt.to_period("2Q")
    else:
        df["periodo"] = df[col_data].dt.to_period("Y")

    # ==========================
    # AGRUPAMENTO
    # ==========================
    resumo = (
        df.groupby("periodo")["valor"]
        .sum()
        .reset_index()
    )

    st.write("### 📊 Faturação por período")
    st.dataframe(resumo)

    # ==========================
    # GRÁFICO
    # ==========================
    st.line_chart(resumo.set_index("periodo"))

    # ==========================
    # ANÁLISE DE ANOMALIAS
    # ==========================
    media = resumo["valor"].mean()

    picos = resumo[resumo["valor"] > media * 2]
    quedas = resumo[resumo["valor"] < media * 0.3]

    st.write("### ⚠️ Picos de faturação")
    st.dataframe(picos)

    st.write("### ⚠️ Quedas suspeitas")
    st.dataframe(quedas)