import streamlit as st
import pandas as pd
import plotly.express as px

def multi_file_compare(dfs, file_names):
    """
    Componente interativo para cruzamento, comparação e filtragem multi-ficheiro (mais de 4 anexos).
    """
    st.markdown('<h2 class="main-header">⚖️ Cruzamento e Comparação Multi-Ficheiro</h2>', unsafe_allow_html=True)
    st.caption("Esta ferramenta permite analisar múltiplos períodos ou anexos carregados simultaneamente para identificar omissões, discrepâncias e tendências consolidadas.")

    if not dfs or len(dfs) < 2:
        st.warning("⚠️ Carregue pelo menos 2 ficheiros para habilitar a análise multi-ficheiro.")
        return

    # ==========================================
    # 1. MATRIZ COMPARATIVA DE RESUMO (KPIs)
    # ==========================================
    st.subheader("📊 Matriz de Resumo dos Anexos")
    st.caption("Visão geral comparativa das métricas-chave de cada arquivo carregado.")

    summary_data = []
    for idx, df_temp in enumerate(dfs):
        vol = df_temp['valor'].sum() if 'valor' in df_temp.columns else 0
        count = len(df_temp)
        ticket = vol / count if count > 0 else 0
        
        # Clientes e fornecedores
        num_clientes = df_temp['cliente'].nunique() if 'cliente' in df_temp.columns else 0
        num_fornecedores = df_temp['fornecedor'].nunique() if 'fornecedor' in df_temp.columns else 0
        
        # Período de datas
        data_inicio = "N/D"
        data_fim = "N/D"
        if 'data' in df_temp.columns:
            dates = pd.to_datetime(df_temp['data'], errors='coerce').dropna()
            if not dates.empty:
                data_inicio = dates.min().strftime('%d/%m/%Y')
                data_fim = dates.max().strftime('%d/%m/%Y')

        summary_data.append({
            "Ficheiro / Folha": file_names[idx],
            "Volume Financeiro (FCFA)": vol,
            "Nº Transações": count,
            "Ticket Médio (FCFA)": ticket,
            "Clientes Únicos": num_clientes,
            "Fornecedores Únicos": num_fornecedores,
            "Data Início": data_inicio,
            "Data Fim": data_fim
        })

    df_summary = pd.DataFrame(summary_data)
    st.dataframe(
        df_summary.style.format({
            "Volume Financeiro (FCFA)": "{:,.2f}",
            "Ticket Médio (FCFA)": "{:,.2f}",
            "Nº Transações": "{:,}",
            "Clientes Únicos": "{:,}",
            "Fornecedores Únicos": "{:,}"
        }), 
        width='stretch'
    )

    # Gráfico comparativo de volume
    fig_vol = px.bar(
        df_summary, 
        x="Ficheiro / Folha", 
        y="Volume Financeiro (FCFA)", 
        color="Ficheiro / Folha",
        title="Volume Financeiro Comparado entre Ficheiros",
        text_auto='.2s'
    )
    st.plotly_chart(fig_vol, width='stretch')

    st.divider()

    # ==========================================
    # 2. CRUZADOR DE TRANSAÇÕES (DIFF)
    # ==========================================
    st.subheader("🔍 Cruzador de Discrepâncias entre Ficheiros")
    st.caption("Compare e encontre diferenças diretas ou transações ausentes entre dois arquivos selecionados.")

    col1, col2 = st.columns(2)
    with col1:
        f1_idx = st.selectbox("Selecione o Ficheiro A (Referência)", range(len(dfs)), format_func=lambda idx: file_names[idx], key="diff_a")
    with col2:
        # Default para o segundo se houver
        f2_default = 1 if len(dfs) > 1 else 0
        f2_idx = st.selectbox("Selecione o Ficheiro B (Comparação)", range(len(dfs)), index=f2_default, format_func=lambda idx: file_names[idx], key="diff_b")

    if f1_idx == f2_idx:
        st.warning("⚠️ Selecione dois ficheiros diferentes para realizar o cruzamento.")
        return

    df_a = dfs[f1_idx].copy()
    df_b = dfs[f2_idx].copy()

    # Identificar colunas em comum
    common_cols = list(set(df_a.columns) & set(df_b.columns))
    # Excluir metadados e colunas internas do merge
    common_cols = [c for c in common_cols if c not in ['origem_ficheiro', 'tipo_declaracao', 'imposto_calculado']]

    st.write(f"🧬 **Campos de correspondência em comum:** `{', '.join(common_cols)}`")

    # Selecionar chaves para cruzamento
    key_options = [c for c in common_cols if c in ['cliente', 'fornecedor', 'fatura', 'data']]
    if not key_options:
        key_options = common_cols[:2] if len(common_cols) >= 2 else common_cols

    selected_keys = st.multiselect(
        "Chaves de Cruzamento (Campos para parear transações)",
        common_cols,
        default=key_options
    )

    if not selected_keys:
        st.error("❌ Por favor, selecione pelo menos uma chave de cruzamento.")
        return

    # Realizar merge externo para encontrar diferenças
    # Forçar chaves para string para correspondência perfeita
    df_a_comp = df_a.copy()
    df_b_comp = df_b.copy()
    for col in selected_keys:
        df_a_comp[col] = df_a_comp[col].astype(str).str.strip().str.lower()
        df_b_comp[col] = df_b_comp[col].astype(str).str.strip().str.lower()

    # Cruzamento
    merged = pd.merge(
        df_a_comp, 
        df_b_comp, 
        on=selected_keys, 
        how='outer', 
        suffixes=('_A', '_B')
    )

    # Transações que só existem no A
    only_in_a = merged[merged['valor_B'].isna() & merged['valor_A'].notna()]
    # Transações que só existem no B
    only_in_b = merged[merged['valor_A'].isna() & merged['valor_B'].notna()]
    # Transações em ambos mas com divergência de valor
    divergent_val = merged[merged['valor_A'].notna() & merged['valor_B'].notna() & (abs(merged['valor_A'] - merged['valor_B']) > 0.01)]

    # Tabs de cruzamento
    tab_diff1, tab_diff2, tab_diff3 = st.tabs([
        f"🔴 Apenas no Ficheiro A ({len(only_in_a)})",
        f"🔵 Apenas no Ficheiro B ({len(only_in_b)})",
        f"🟡 Divergências de Valores ({len(divergent_val)})"
    ])

    with tab_diff1:
        st.markdown(f"#### Transações que constam em **{file_names[f1_idx]}** mas faltam em **{file_names[f2_idx]}**")
        st.caption("Útil para identificar faturas que foram declaradas por um contribuinte mas omitidas pelo outro.")
        if not only_in_a.empty:
            cols_to_show = selected_keys + [c for c in only_in_a.columns if c.endswith('_A')]
            st.dataframe(only_in_a[cols_to_show], width='stretch')
        else:
            st.success("✅ Nenhuma transação exclusiva encontrada no Ficheiro A.")

    with tab_diff2:
        st.markdown(f"#### Transações que constam em **{file_names[f2_idx]}** mas faltam em **{file_names[f1_idx]}**")
        st.caption("Útil para cruzar as compras e vendas e detectar omissões de lançamento fiscal.")
        if not only_in_b.empty:
            cols_to_show = selected_keys + [c for c in only_in_b.columns if c.endswith('_B')]
            st.dataframe(only_in_b[cols_to_show], width='stretch')
        else:
            st.success("✅ Nenhuma transação exclusiva encontrada no Ficheiro B.")

    with tab_diff3:
        st.markdown("#### Transações com a mesma chave mas com valores divergentes")
        st.caption("Identifica faturas que foram registradas com valores discrepantes por ambas as partes (indício de erro ou fraude de inflação de custos).")
        if not divergent_val.empty:
            divergent_val['Diferença Absoluta'] = abs(divergent_val['valor_A'] - divergent_val['valor_B'])
            cols_to_show = selected_keys + ['valor_A', 'valor_B', 'Diferença Absoluta']
            st.dataframe(divergent_val[cols_to_show].sort_values(by='Diferença Absoluta', ascending=False), width='stretch')
        else:
            st.success("✅ Nenhuma divergência de valor detectada nas faturas pareadas.")

    st.divider()

    # ==========================================
    # 3. FILTRAGEM DINÂMICA CRUZADA
    # ==========================================
    st.subheader("⚙️ Filtro Cruzado e Tendência Consolidada")
    st.caption("Aplique um filtro dinâmico que atua sobre a consolidação de todos os arquivos carregados simultaneamente.")

    # Combinar tudo em um único dataframe
    all_df = pd.concat([df.assign(Ficheiro=file_names[i]) for i, df in enumerate(dfs)], ignore_index=True)

    # Filtros interativos
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        if 'cliente' in all_df.columns:
            clientes_disponiveis = ["Todos"] + sorted(all_df['cliente'].dropna().astype(str).unique().tolist())
            sel_cliente = st.selectbox("Filtrar por Cliente", clientes_disponiveis, key="multi_cli")
        else:
            sel_cliente = "Todos"
    with col_f2:
        if 'fornecedor' in all_df.columns:
            fornecedores_disponiveis = ["Todos"] + sorted(all_df['fornecedor'].dropna().astype(str).unique().tolist())
            sel_fornecedor = st.selectbox("Filtrar por Fornecedor", fornecedores_disponiveis, key="multi_forn")
        else:
            sel_fornecedor = "Todos"

    # Filtrar
    filtered_all = all_df.copy()
    if sel_cliente != "Todos":
        filtered_all = filtered_all[filtered_all['cliente'] == sel_cliente]
    if sel_fornecedor != "Todos":
        filtered_all = filtered_all[filtered_all['fornecedor'] == sel_fornecedor]

    st.write(f"📊 **Registos encontrados na consolidação:** `{len(filtered_all)}` de `{len(all_df)}` total.")
    st.dataframe(filtered_all, width='stretch')

    if not filtered_all.empty and 'valor' in filtered_all.columns:
        fig_trend = px.box(
            filtered_all, 
            x="Ficheiro", 
            y="valor", 
            color="Ficheiro",
            title="Distribuição de Valores de Faturamento por Arquivo (Filtro Ativo)"
        )
        st.plotly_chart(fig_trend, width='stretch')
