import streamlit as st
import pandas as pd
from modules.fraud import detect_statistical_outliers, find_duplicate_transactions, suspicious_round_values
from modules.auditoria import detectar_valores_invalidos


def analisar_contribuinte(df):

    st.subheader("🔍 Investigação de Contribuinte")

    if df is None:
        st.warning("Sem dados carregados")
        return

    # ==========================
    # CAMPOS DISPONÍVEIS
    # ==========================
    colunas = df.columns.tolist()

    campos_busca = [
        c for c in colunas
        if any(k in c for k in ["cliente", "fornecedor", "nif", "nome"])
    ]

    if not campos_busca:
        st.warning("Nenhum campo válido para pesquisa")
        return

    # ==========================
    # SELEÇÃO
    # ==========================
    col_busca = st.selectbox("Campo de pesquisa", campos_busca)

    valor = st.text_input("Pesquisar contribuinte")

    if not valor:
        return

    # ==========================
    # FILTRAR GLOBAL
    # ==========================
    df_filtrado = df[
        df[col_busca].astype(str).str.contains(valor, case=False, na=False)
    ]

    st.write("### 📊 Registos encontrados")
    st.dataframe(df_filtrado)

    if df_filtrado.empty:
        st.info("Sem resultados")
        return

    # ==========================
    # COMO CLIENTE
    # ==========================
    if "cliente" in df.columns:

        df_cliente = df[
            df["cliente"].astype(str).str.contains(valor, case=False, na=False)
        ]

        total_cliente = df_cliente["valor"].sum() if "valor" in df.columns else 0

        st.subheader("🟢 Como Cliente")
        st.metric("Total Compras", f"{total_cliente:,.0f}")
        st.dataframe(df_cliente)

    # ==========================
    # COMO FORNECEDOR
    # ==========================
    if "fornecedor" in df.columns:

        df_fornecedor = df[
            df["fornecedor"].astype(str).str.contains(valor, case=False, na=False)
        ]

        total_fornecedor = df_fornecedor["valor"].sum() if "valor" in df.columns else 0

        st.subheader("🔵 Como Fornecedor")
        st.metric("Total Vendas", f"{total_fornecedor:,.0f}")
        st.dataframe(df_fornecedor)

    # ==========================
    # RELAÇÕES
    # ==========================
    if {"cliente", "fornecedor"}.issubset(df.columns):

        df_rel = df[
            df["cliente"].astype(str).str.contains(valor, case=False, na=False) |
            df["fornecedor"].astype(str).str.contains(valor, case=False, na=False)
        ]

        st.subheader("🔗 Relações com outros contribuintes")
        st.dataframe(df_rel)

        # ==========================
        # TOP PARCEIROS
        # ==========================
        if "valor" in df.columns and not df_rel.empty:

            parceiros = (
                df_rel.groupby(["fornecedor", "cliente"])["valor"]
                .sum()
                .reset_index()
                .sort_values(by="valor", ascending=False)
            )

            st.subheader("🏆 Principais relações")
            st.dataframe(parceiros.head(10))

        # ==========================
        # SELECIONAR PARCEIRO
        # ==========================
        lista_parceiros = list(set(
            df_rel["cliente"].tolist() +
            df_rel["fornecedor"].tolist()
        ))

        parceiro = st.selectbox("Selecionar parceiro específico", lista_parceiros)

        df_pair = df[
            (
                df["cliente"].astype(str).str.contains(valor, case=False) &
                (df["fornecedor"] == parceiro)
            ) |
            (
                df["fornecedor"].astype(str).str.contains(valor, case=False) &
                (df["cliente"] == parceiro)
            )
        ]

        st.subheader(f"🔗 Relação detalhada com {parceiro}")
        st.dataframe(df_pair)

        # ==========================
        # KPIs
        # ==========================
        if "valor" in df.columns and not df_pair.empty:
            total = df_pair["valor"].sum()
            count = len(df_pair)

            col1, col2 = st.columns(2)
            col1.metric("💰 Volume relação", f"{total:,.0f}")
            col2.metric("📄 Nº transações", count)

    # ==========================
    # 🚨 ANOMALIAS E EVIDÊNCIAS (NOVO)
    # ==========================
    st.divider()
    st.subheader("🚨 Anomalias e Evidências")
    st.caption("Filtra irregularidades específicas deste contribuinte (outliers, duplicados, datas futuras ou valores redondos) para fundamentar a prova de fraude ou erro.")
    from modules.methodology import mostrar_metodologia
    mostrar_metodologia()
    
    with st.expander("🔍 Verificar Irregularidades Deste Contribuinte"):
        # Selecionar e ordenar colunas de evidência
        cols_evidencia = ['motivo_anomalia'] + [c for c in ['fatura', 'data', 'valor'] if c in df_filtrado.columns]
        
        # 1. Outliers
        if "valor" in df_filtrado.columns:
            outliers = detect_statistical_outliers(df_filtrado)
            if outliers is not None and not outliers.empty:
                st.warning(f"🚩 **Outliers Detectados**: Encontradas {len(outliers)} transações com valores estatisticamente anômalos.")
                st.dataframe(outliers[cols_evidencia] if all(c in outliers.columns for c in cols_evidencia) else outliers)
            
            # 2. Valores Redondos
            round_vals = suspicious_round_values(df_filtrado)
            if round_vals is not None and not round_vals.empty:
                st.warning(f"🚩 **Valores Redondos**: {len(round_vals)} transações com valores suspeitosamente redondos.")
                st.dataframe(round_vals[cols_evidencia] if all(c in round_vals.columns for c in cols_evidencia) else round_vals)
                
        # 3. Duplicados
        dupes = find_duplicate_transactions(df_filtrado)
        if dupes is not None and not dupes.empty:
            st.warning(f"🚩 **Transações Duplicadas**: {len(dupes)} registros idênticos que sugerem duplicidade indevida.")
            st.dataframe(dupes[['motivo_anomalia'] + [c for c in dupes.columns if c != 'motivo_anomalia']])
            
        # 4. Valores Inválidos
        invalidos = detectar_valores_invalidos(df_filtrado)
        if invalidos is not None and not invalidos.empty:
            st.error(f"🚩 **Valores Inválidos**: {len(invalidos)} transações com valores negativos ou zero.")
            st.dataframe(invalidos[['motivo_anomalia'] + [c for c in invalidos.columns if c != 'motivo_anomalia']])
            
        # 5. Datas Suspeitas
        for col in df_filtrado.columns:
            if "data" in col.lower():
                dates = pd.to_datetime(df_filtrado[col], errors='coerce')
                if dates.dt.tz is not None:
                    dates = dates.dt.tz_localize(None)
                future_dates = df_filtrado[dates > pd.Timestamp.now() + pd.Timedelta(days=1)]
                if not future_dates.empty:
                    st.error(f"🚩 **Datas Futuras**: {len(future_dates)} faturas com datas no futuro.")
                    st.dataframe(future_dates)

    # ==========================
    # ANÁLISE TEMPORAL DO CONTRIBUINTE
    # ==========================
    for col in df.columns:
        if "data" in col:

            df[col] = pd.to_datetime(df[col], errors="coerce")
            if df[col].dt.tz is not None:
                df[col] = df[col].dt.tz_localize(None)

            temp = df_filtrado.copy()
            temp[col] = pd.to_datetime(temp[col], errors="coerce")
            if temp[col].dt.tz is not None:
                temp[col] = temp[col].dt.tz_localize(None)
            temp = temp.dropna(subset=[col])
            
            if not temp.empty:
                temp["mes"] = temp[col].dt.to_period("M").astype(str)

            resumo = temp.groupby("mes")["valor"].sum().reset_index()

            st.subheader("📅 Evolução mensal")
            st.line_chart(resumo.set_index("mes"))
            break