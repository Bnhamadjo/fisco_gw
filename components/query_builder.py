import streamlit as st
import pandas as pd

def query_builder(df):
    st.markdown('<h2 class="main-header">🧪 Motor de Consulta Criteriosa</h2>', unsafe_allow_html=True)

    if df is None:
        st.warning("⚠️ Carregue dados para iniciar a consulta avançada.")
        return df

    df_result = df.copy()
    cols = df.columns.tolist()

    # Layout de 2 colunas para Configurações de Filtro
    with st.expander("🛠️ Configurar Filtros e Critérios", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 🔍 Filtros de Texto e Categoria")
            # Multiselect de Colunas para Exibição
            selected_cols = st.multiselect(
                "Colunas para Visualizar",
                cols,
                default=[c for c in cols if c in ['data', 'fatura', 'cliente', 'fornecedor', 'valor', 'iva_liquidado', 'iva_suportado']]
            )
            
            # Filtro Global
            search = st.text_input("🔍 Pesquisa Global (Contém...)", placeholder="Ex: Petromar, Fatura 123...")

        with col2:
            st.markdown("##### 📉 Filtros Numéricos e Datas")
            # Filtro de Intervalo de Valor
            if "valor" in df.columns:
                # Garantir que é numérico
                df_result["valor"] = pd.to_numeric(df_result["valor"], errors='coerce').fillna(0)
                min_val = float(df_result["valor"].min())
                max_val = float(df_result["valor"].max())
                if min_val < max_val:
                    val_range = st.slider("Faixa de Valor (FCFA)", min_val, max_val, (min_val, max_val))
                    df_result = df_result[(df_result["valor"] >= val_range[0]) & (df_result["valor"] <= val_range[1])]

            # Filtro de Datas
            date_cols = [c for c in cols if "data" in c.lower()]
            if date_cols:
                date_col = st.selectbox("Filtrar por Data", ["Nenhum"] + date_cols)
                if date_col != "Nenhum":
                    df_result[date_col] = pd.to_datetime(df_result[date_col], errors='coerce')
                    df_result = df_result.dropna(subset=[date_col])
                    if not df_result.empty:
                        min_date = df_result[date_col].min().date()
                        max_date = df_result[date_col].max().date()
                        date_range = st.date_input("Intervalo de Datas", [min_date, max_date])
                        if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
                            df_result = df_result[(df_result[date_col].dt.date >= date_range[0]) & (df_result[date_col].dt.date <= date_range[1])]

    # Pesquisa Global Logic
    if search:
        df_result = df_result[
            df_result.astype(str).apply(
                lambda row: row.str.contains(search, case=False).any(),
                axis=1
            )
        ]

    # FILTRO AVANÇADO (Lógica AND)
    with st.expander("⚙️ Filtros por Coluna Específica"):
        col_to_filter = st.selectbox("Escolha a Coluna", ["Nenhuma"] + cols)
        if col_to_filter != "Nenhuma":
            if df[col_to_filter].dtype == 'object' or df[col_to_filter].dtype == 'string':
                unique_vals = sorted(df[col_to_filter].dropna().unique().tolist())
                selected_vals = st.multiselect(f"Valores em {col_to_filter}", unique_vals)
                if selected_vals:
                    df_result = df_result[df_result[col_to_filter].isin(selected_vals)]
            else:
                st.info(f"A coluna {col_to_filter} é numérica. Use os sliders acima ou o seletor de range.")

    # ORDENAÇÃO
    with st.sidebar:
        st.divider()
        st.subheader("🔃 Ordenação")
        order_col = st.selectbox("Ordenar por", ["Padrão"] + list(df_result.columns))
        if order_col != "Padrão":
            asc = st.radio("Sentido", ["Descendente", "Ascendente"]) == "Ascendente"
            df_result = df_result.sort_values(by=order_col, ascending=asc)

    # RESULTADO E KPIs
    st.divider()
    
    # KPIs Dinâmicos
    k1, k2, k3 = st.columns(3)
    k1.metric("📑 Registros Filtrados", len(df_result))
    if "valor" in df_result.columns:
        total_v = df_result['valor'].sum()
        k2.metric("💰 Volume Filtrado", f"{total_v:,.2f} FCFA")
        if len(df_result) > 0:
            k3.metric("🎫 Ticket Médio", f"{(total_v/len(df_result)):,.2f} FCFA")

    # Exibição Final
    if selected_cols:
        # Garantir que as colunas selecionadas existem no df filtrado (especialmente após transformações)
        cols_to_show = [c for c in selected_cols if c in df_result.columns]
        st.dataframe(df_result[cols_to_show], use_container_width=True)
    else:
        st.dataframe(df_result, use_container_width=True)

    # Exportação
    if not df_result.empty:
        from modules.exporter import download_buttons
        download_buttons(df_result, filename="consulta_customizada", key_prefix="query_explorer")

    return df_result