# ==================== CONFIGURAÇÃO INICIAL (OBRIGATÓRIA) ====================
import streamlit as st

# ==================== IMPORTS ====================
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from typing import Optional, Tuple, List, Dict
import warnings
import numpy as np
warnings.filterwarnings('ignore')

# ==================== CSS PERSONALIZADO ====================
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white !important;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        transition: transform 0.3s;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .risk-high {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 0.75rem;
        border-radius: 8px;
        font-weight: bold;
        animation: pulse 1.5s infinite;
    }
    .risk-medium {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        color: #333;
        padding: 0.75rem;
        border-radius: 8px;
        font-weight: bold;
    }
    .risk-low {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        color: #333;
        padding: 0.75rem;
        border-radius: 8px;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.8; }
        100% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# ==================== FUNÇÕES DE UTILIDADE ====================
@st.cache_data(ttl=3600, show_spinner=False)
def cache_dataframe(df: pd.DataFrame, operation: str) -> pd.DataFrame:
    """Cache operations for better performance"""
    return df.copy()

def limpar_dados_entidade(df: pd.DataFrame, coluna: str) -> pd.Series:
    """Limpa e padroniza dados de entidades"""
    if coluna not in df.columns:
        return pd.Series(dtype=str)
    
    # Remove nulos, converte para string, remove espaços extras
    return df[coluna].dropna().astype(str).str.strip()

def obter_lista_entidades(df: pd.DataFrame) -> List[str]:
    """Obtém lista única de todas as entidades (clientes e fornecedores)"""
    entidades = set()
    
    if 'cliente' in df.columns:
        clientes = limpar_dados_entidade(df, 'cliente')
        entidades.update(clientes)
    
    if 'fornecedor' in df.columns:
        fornecedores = limpar_dados_entidade(df, 'fornecedor')
        entidades.update(fornecedores)
    
    # Remove entradas vazias ou inválidas
    entidades_validas = {e for e in entidades if e and e not in ['nan', 'None', '']}
    
    return sorted(list(entidades_validas))

@st.cache_data(ttl=300, show_spinner=False)
def detectar_anomalias_avancado(df: pd.DataFrame, coluna_valor: str = 'valor') -> pd.DataFrame:
    """Advanced anomaly detection with multiple statistical methods"""
    if coluna_valor not in df.columns or df.empty:
        return pd.DataFrame()
    
    # Limpar dados para análise numérica
    df_clean = df.dropna(subset=[coluna_valor])
    if df_clean.empty:
        return pd.DataFrame()
    
    df_anomalias = df_clean.copy()
    
    # Converter valores para numérico
    df_anomalias[coluna_valor] = pd.to_numeric(df_anomalias[coluna_valor], errors='coerce')
    df_anomalias = df_anomalias.dropna(subset=[coluna_valor])
    
    if df_anomalias.empty:
        return pd.DataFrame()
    
    # Método 1: Z-score (3 sigma rule)
    media = df_anomalias[coluna_valor].mean()
    desvio = df_anomalias[coluna_valor].std()
    
    if desvio > 0:
        df_anomalias['z_score'] = (df_anomalias[coluna_valor] - media) / desvio
        df_anomalias['anomalia_zscore'] = abs(df_anomalias['z_score']) > 3
    else:
        df_anomalias['z_score'] = 0
        df_anomalias['anomalia_zscore'] = False
    
    # Método 2: IQR (Interquartile Range)
    Q1 = df_anomalias[coluna_valor].quantile(0.25)
    Q3 = df_anomalias[coluna_valor].quantile(0.75)
    IQR = Q3 - Q1
    
    if IQR > 0:
        limite_inferior_iqr = Q1 - 1.5 * IQR
        limite_superior_iqr = Q3 + 1.5 * IQR
        df_anomalias['anomalia_iqr'] = (df_anomalias[coluna_valor] < limite_inferior_iqr) | (df_anomalias[coluna_valor] > limite_superior_iqr)
    else:
        df_anomalias['anomalia_iqr'] = False
    
    # Classificação final
    df_anomalias['e_anomalia'] = df_anomalias['anomalia_zscore'] | df_anomalias['anomalia_iqr']
    df_anomalias['nivel_risco'] = df_anomalias['z_score'].apply(
        lambda x: 'Alto' if abs(x) > 3 else ('Médio' if abs(x) > 2 else 'Baixo')
    )
    
    return df_anomalias[df_anomalias['e_anomalia']].copy()

def calcular_resumo_entidade(df: pd.DataFrame, entidade: str) -> Dict:
    """Calculate comprehensive summary for an entity"""
    entidade_str = str(entidade).strip()
    
    resumo = {
        'entidade': entidade_str,
        'total_vendas': 0,
        'total_compras': 0,
        'num_transacoes_vendas': 0,
        'num_transacoes_compras': 0,
        'parceiros_unicos_vendas': 0,
        'parceiros_unicos_compras': 0,
    }
    
    if 'fornecedor' in df.columns and 'valor' in df.columns:
        vendas_mask = df['fornecedor'].astype(str).str.strip() == entidade_str
        resumo['total_vendas'] = df.loc[vendas_mask, 'valor'].sum()
        resumo['num_transacoes_vendas'] = vendas_mask.sum()
        
        if 'cliente' in df.columns:
            resumo['parceiros_unicos_vendas'] = df.loc[vendas_mask, 'cliente'].nunique()
    
    if 'cliente' in df.columns and 'valor' in df.columns:
        compras_mask = df['cliente'].astype(str).str.strip() == entidade_str
        resumo['total_compras'] = df.loc[compras_mask, 'valor'].sum()
        resumo['num_transacoes_compras'] = compras_mask.sum()
        
        if 'fornecedor' in df.columns:
            resumo['parceiros_unicos_compras'] = df.loc[compras_mask, 'fornecedor'].nunique()
    
    resumo['saldo_liquido'] = resumo['total_vendas'] - resumo['total_compras']
    return resumo

# ==================== FUNÇÃO PRINCIPAL ====================
def investigador_inteligente(df: pd.DataFrame):
    """Main investigation function with enhanced features"""
    
    st.markdown('<div class="main-header"><h1>🔎 Investigador Fiscal Inteligente</h1><p>Sistema Avançado de Auditoria e Detecção de Riscos</p></div>', 
                unsafe_allow_html=True)
    
    from modules.methodology import mostrar_metodologia
    mostrar_metodologia()
    
    # Validação de dados
    if df is None or df.empty:
        st.warning("⚠️ Nenhum dado carregado. Por favor, carregue um arquivo para iniciar a investigação.")
        return
    
    # Limpeza inicial dos dados
    # Converter colunas de texto para string e tratar nulos
    for col in ['cliente', 'fornecedor']:
        if col in df.columns:
            df[col] = df[col].fillna('').astype(str).str.strip()
            df.loc[df[col] == '', col] = 'Não Identificado'
    
    # Converter valor para numérico
    if 'valor' in df.columns:
        df['valor'] = pd.to_numeric(df['valor'], errors='coerce').fillna(0)
    
    # Verificar colunas essenciais
    colunas_essenciais = ['cliente', 'fornecedor', 'valor']
    colunas_faltando = [col for col in colunas_essenciais if col not in df.columns]
    
    if colunas_faltando:
        st.error(f"❌ Colunas obrigatórias não encontradas: {', '.join(colunas_faltando)}")
        st.info("📋 O arquivo deve conter as colunas: cliente, fornecedor, valor (e opcionalmente: fatura, data, iva_liquidado, etc.)")
        return
    
    # Sidebar com controles
    with st.sidebar:
        st.header("🎛️ Painel de Controle")
        
        # Informações do dataset
        st.markdown("### 📊 Dataset")
        st.metric("Total Transações", f"{len(df):,}")
        
        valor_total = df['valor'].sum() if 'valor' in df.columns else 0
        st.metric("Valor Total", f"{valor_total:,.0f} FCFA")
        
        # Número de entidades únicas
        entidades_unicas = obter_lista_entidades(df)
        st.metric("Entidades Únicas", f"{len(entidades_unicas):,}")
        
        st.divider()
        
        # Filtros
        st.markdown("### 🔍 Filtros")
        
        # Filtro por valor
        if 'valor' in df.columns:
            valor_min = st.number_input("Valor Mínimo (FCFA)", min_value=0, value=0, step=1000)
            valor_max = st.number_input("Valor Máximo (FCFA)", min_value=0, 
                                       value=int(df['valor'].max()), step=10000)
        else:
            valor_min, valor_max = 0, 0
        
        # Filtro por data (se existir)
        if 'data' in df.columns:
            df['data'] = pd.to_datetime(df['data'], errors='coerce')
            if not df['data'].isna().all():
                min_date = df['data'].min().date()
                max_date = df['data'].max().date()
                date_range = st.date_input("Período", value=[min_date, max_date],
                                          min_value=min_date, max_value=max_date)
                if len(date_range) == 2:
                    df = df[(df['data'].dt.date >= date_range[0]) & 
                           (df['data'].dt.date <= date_range[1])]
        
        # Aplicar filtros
        df_filtrado = df.copy()
        if 'valor' in df.columns:
            df_filtrado = df_filtrado[(df_filtrado['valor'] >= valor_min) & (df_filtrado['valor'] <= valor_max)]
        
        st.divider()
        
        # Botões de ação
        if st.button("🔄 Resetar Filtros", width='stretch'):
            st.rerun()
    
    # Métricas rápidas
    st.subheader("📈 Dashboard Rápido")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("💰 Volume Total", f"{df_filtrado['valor'].sum():,.0f} FCFA")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("📊 Ticket Médio", f"{df_filtrado['valor'].mean():,.0f} FCFA")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("🔄 Transações", f"{len(df_filtrado):,}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        anomalias = detectar_anomalias_avancado(df_filtrado)
        nivel_risco = "🔴 Alto" if len(anomalias) > len(df_filtrado) * 0.1 else ("🟡 Médio" if len(anomalias) > 0 else "🟢 Baixo")
        st.metric("🚨 Nível de Risco", nivel_risco, delta=f"{len(anomalias)} anomalias")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tabs principais
    tab_iso, tab_col, tab_cross, tab_bilateral, tab_anomalias, tab_tendencia, tab_ml = st.tabs([
        "🎯 Visão por Entidade",
        "📊 Análise de Fluxos", 
        "⚖️ Cruzamento Fiscal",
        "🤝 Auditoria Bilateral",
        "🚨 Detecção de Anomalias",
        "📈 Tendências",
        "🧠 IA Preditiva"
    ])
    
    # Preparar listas de entidades (VERSÃO CORRIGIDA)
    all_entities = obter_lista_entidades(df_filtrado)
    
    # Se não houver entidades, mostrar aviso
    if not all_entities:
        st.warning("⚠️ Nenhuma entidade válida encontrada nos dados.")
        return
    
    # TAB 1: VISÃO POR ENTIDADE
    with tab_iso:
        st.subheader("🔍 Análise Detalhada por Entidade")
        
        entidade = st.selectbox("Selecione uma entidade", all_entities, key="iso_ent")
        
        if entidade:
            resumo = calcular_resumo_entidade(df_filtrado, entidade)
            
            # Grid de métricas
            col_a, col_b, col_c, col_d = st.columns(4)
            with col_a:
                st.metric("📤 Vendas", f"{resumo['total_vendas']:,.0f} FCFA")
            with col_b:
                st.metric("📥 Compras", f"{resumo['total_compras']:,.0f} FCFA")
            with col_c:
                delta_color = "normal" if resumo['saldo_liquido'] >= 0 else "inverse"
                st.metric("💼 Saldo", f"{resumo['saldo_liquido']:,.0f} FCFA", delta_color=delta_color)
            with col_d:
                total_parceiros = resumo['parceiros_unicos_vendas'] + resumo['parceiros_unicos_compras']
                st.metric("🤝 Parceiros", f"{total_parceiros}")
            
            # Transações da entidade
            transacoes_entidade = df_filtrado[
                (df_filtrado['cliente'].astype(str).str.strip() == entidade) | 
                (df_filtrado['fornecedor'].astype(str).str.strip() == entidade)
            ]
            
            st.subheader("📋 Histórico de Transações")
            st.dataframe(transacoes_entidade, width='stretch')
    
    # TAB 2: ANÁLISE DE FLUXOS
    with tab_col:
        st.subheader("📊 Matriz de Fluxos Comerciais")
        
        if 'cliente' in df_filtrado.columns and 'fornecedor' in df_filtrado.columns:
            # Criar matriz de fluxo
            fluxo_matrix = df_filtrado.groupby(['cliente', 'fornecedor'])['valor'].sum().reset_index()
            
            if not fluxo_matrix.empty:
                # Top 10 relações
                top_10 = fluxo_matrix.nlargest(10, 'valor')
                
                fig = px.bar(top_10, x='cliente', y='valor', color='fornecedor',
                            title="Top 10 Relações Comerciais",
                            labels={'valor': 'Volume (FCFA)', 'cliente': 'Cliente'},
                            text_auto='.2s')
                fig.update_layout(showlegend=True, height=500)
                st.plotly_chart(fig, width='stretch')
                
                # Heatmap das principais relações
                st.subheader("🗺️ Mapa de Calor de Transações")
                st.caption("Visualiza a densidade financeira entre os maiores clientes e fornecedores. As cores mais intensas indicam concentrações de volume que podem merecer investigação por dependência económica.")
                
                # Selecionar top N entidades para visualização
                top_n = st.slider("Número de entidades para visualizar", 5, min(20, len(all_entities)), 10)
                
                # Pegar top N entidades por volume
                top_clientes = fluxo_matrix.groupby('cliente')['valor'].sum().nlargest(top_n).index.tolist()
                top_fornecedores = fluxo_matrix.groupby('fornecedor')['valor'].sum().nlargest(top_n).index.tolist()
                
                fluxo_filtrado = fluxo_matrix[
                    fluxo_matrix['cliente'].isin(top_clientes) & 
                    fluxo_matrix['fornecedor'].isin(top_fornecedores)
                ]
                
                if not fluxo_filtrado.empty:
                    pivot = fluxo_filtrado.pivot_table(index='cliente', columns='fornecedor', 
                                                      values='valor', fill_value=0)
                    
                    fig_heat = px.imshow(pivot, 
                                        title=f"Matriz de Transações (Top {top_n} Entidades)",
                                        labels=dict(x="Fornecedor", y="Cliente", color="Valor (FCFA)"),
                                        aspect="auto",
                                        color_continuous_scale="Viridis")
                    fig_heat.update_layout(height=600)
                    st.plotly_chart(fig_heat, width='stretch')
            else:
                st.info("Nenhum dado de fluxo disponível")
    
    # TAB 3: CRUZAMENTO FISCAL
    with tab_cross:
        st.subheader("⚖️ Auditoria Fiscal Detalhada")
        st.caption("Analisa o equilíbrio entre Vendas e Compras de uma única entidade. O sistema calcula a margem presumida e estima o IVA devido com base na diferença declarada.")
        
        entidade_audit = st.selectbox("Entidade para Auditoria", all_entities, key="cross_ent")
        
        if entidade_audit:
            vendas = df_filtrado[df_filtrado['fornecedor'].astype(str).str.strip() == entidade_audit]
            compras = df_filtrado[df_filtrado['cliente'].astype(str).str.strip() == entidade_audit]
            
            # Métricas fiscais
            col_v1, col_v2, col_v3 = st.columns(3)
            
            with col_v1:
                st.markdown("### 📤 Vendas Declaradas")
                st.metric("Total", f"{vendas['valor'].sum():,.0f} FCFA")
                st.metric("N° Transações", len(vendas))
                if 'cliente' in vendas.columns:
                    st.metric("Clientes Únicos", vendas['cliente'].nunique())
            
            with col_v2:
                st.markdown("### 📥 Compras Declaradas")
                st.metric("Total", f"{compras['valor'].sum():,.0f} FCFA")
                st.metric("N° Transações", len(compras))
                if 'fornecedor' in compras.columns:
                    st.metric("Fornecedores Únicos", compras['fornecedor'].nunique())
            
            with col_v3:
                st.markdown("### ⚖️ Resultado Fiscal")
                resultado = vendas['valor'].sum() - compras['valor'].sum()
                st.metric("Base de Cálculo", f"{resultado:,.0f} FCFA")
                
                # Simulação de imposto (18%)
                iva_estimado = resultado * 0.18
                st.metric("IVA Estimado (18%)", f"{iva_estimado:,.0f} FCFA")
    
    # TAB 4: AUDITORIA BILATERAL
    with tab_bilateral:
        st.subheader("🤝 Análise Bilateral de Transações")
        st.caption("Cruza diretamente os registos entre dois contribuintes. O objetivo é validar se o que um declarou como compra é exatamente o que o outro declarou como venda, detetando omissões unilaterais.")
        
        if len(all_entities) >= 2:
            col_a, col_b = st.columns(2)
            with col_a:
                ent_a = st.selectbox("Entidade A", all_entities, key="bil_a")
            with col_b:
                ent_b = st.selectbox("Entidade B", all_entities, key="bil_b")
            
            if ent_a != ent_b:
                # Transações nos dois sentidos
                a_para_b = df_filtrado[
                    (df_filtrado['cliente'].astype(str).str.strip() == ent_a) & 
                    (df_filtrado['fornecedor'].astype(str).str.strip() == ent_b)
                ]
                b_para_a = df_filtrado[
                    (df_filtrado['cliente'].astype(str).str.strip() == ent_b) & 
                    (df_filtrado['fornecedor'].astype(str).str.strip() == ent_a)
                ]
                
                col_res1, col_res2 = st.columns(2)
                with col_res1:
                    st.metric(f"{ent_a} → {ent_b}", f"{a_para_b['valor'].sum():,.0f} FCFA")
                    st.caption(f"{len(a_para_b)} transações")
                
                with col_res2:
                    st.metric(f"{ent_b} → {ent_a}", f"{b_para_a['valor'].sum():,.0f} FCFA")
                    st.caption(f"{len(b_para_a)} transações")
                
                # Transações combinadas
                todas_transacoes = pd.concat([a_para_b, b_para_a]).copy()
                
                if not todas_transacoes.empty:
                    st.subheader("📋 Detalhamento das Transações")
                    
                    # CÁLCULO DE IMPOSTO REAL VS DECLARADO
                    tax_rate = 0.18
                    col_taxa = "taxa_aplicada" if "taxa_aplicada" in todas_transacoes.columns else None
                    
                    # Busca flexível por colunas de IVA
                    iva_liq_cols = [c for c in todas_transacoes.columns if c.startswith("iva_liquidado")]
                    iva_sup_cols = [c for c in todas_transacoes.columns if c.startswith("iva_suportado")]
                    col_iva = iva_liq_cols[0] if iva_liq_cols else (iva_sup_cols[0] if iva_sup_cols else None)
                    
                    if 'valor' in todas_transacoes.columns:
                        todas_transacoes['Imposto Real (Calculado)'] = todas_transacoes['valor'] * (todas_transacoes[col_taxa] if col_taxa else tax_rate)
                        
                        if col_iva:
                            todas_transacoes['Imposto Declarado'] = todas_transacoes[col_iva].fillna(0)
                            todas_transacoes['Diferença (Risco)'] = todas_transacoes['Imposto Declarado'] - todas_transacoes['Imposto Real (Calculado)']
                            
                            # Resumo Financeiro Bilateral
                            total_real = todas_transacoes['Imposto Real (Calculado)'].sum()
                            total_decl = todas_transacoes['Imposto Declarado'].sum()
                            desvio = total_decl - total_real
                            
                            st.markdown(f"""
                            | Descrição | Valor |
                            | :--- | :--- |
                            | **Total Transacionado** | {todas_transacoes['valor'].sum():,.2f} FCFA |
                            | **Imposto Real Esperado** | {total_real:,.2f} FCFA |
                            | **Imposto Efetivamente Declarado** | {total_decl:,.2f} FCFA |
                            | **Diferença / Desvio Fiscal** | <span style='color:{"red" if abs(desvio) > 10 else "green"}'>{desvio:,.2f} FCFA</span> |
                            """, unsafe_allow_html=True)
                            
                            # EXPOSIÇÃO DE EVIDÊNCIAS
                            st.write("#### 🚩 Evidências de Incongruência entre as Partes")
                            evidencias = todas_transacoes[abs(todas_transacoes['Diferença (Risco)']) > 1].copy()
                            
                            if not evidencias.empty:
                                st.warning(f"Foram encontradas **{len(evidencias)}** faturas com divergência entre {ent_a} e {ent_b}.")
                                cols_ev = ['fatura', 'data', 'valor', 'Imposto Declarado', 'Imposto Real (Calculado)', 'Diferença (Risco)']
                                cols_ev_exists = [c for c in cols_ev if c in evidencias.columns]
                                st.dataframe(evidencias[cols_ev_exists].sort_values(by='Diferença (Risco)', ascending=False), width='stretch')
                            else:
                                st.success("✅ Nenhuma discrepância fiscal detectada nas transações mutuais.")
                                
                    st.write("#### Todas as Transações do Par")
                    st.dataframe(todas_transacoes, width='stretch')
                else:
                    st.info(f"📭 Nenhuma transação direta entre {ent_a} e {ent_b}")
            else:
                st.warning("⚠️ Selecione entidades diferentes para análise bilateral")
        else:
            st.warning("⚠️ Necessário pelo menos 2 entidades para análise bilateral")
    
    # TAB 5: DETECÇÃO DE ANOMALIAS
    with tab_anomalias:
        st.subheader("🚨 Sistema de Detecção de Anomalias")
        st.caption("Aplica algoritmos de Z-Score e IQR (Amplitude Interquartil) para isolar transações que fogem radicalmente do padrão do grupo analisado. Foca na deteção de erros de digitação ou fraudes de alto valor.")
        
        if st.button("🔍 Executar Análise de Anomalias", width='stretch'):
            with st.spinner("Analisando transações..."):
                anomalias = detectar_anomalias_avancado(df_filtrado)
                
                if not anomalias.empty:
                    st.error(f"⚠️ {len(anomalias)} transações suspeitas detectadas!")
                    
                    # Resumo por nível de risco
                    risco_counts = anomalias['nivel_risco'].value_counts()
                    
                    col_r1, col_r2, col_r3 = st.columns(3)
                    with col_r1:
                        st.markdown('<div class="risk-high">', unsafe_allow_html=True)
                        st.metric("🔴 Alto Risco", risco_counts.get('Alto', 0))
                        st.markdown('</div>', unsafe_allow_html=True)
                    with col_r2:
                        st.markdown('<div class="risk-medium">', unsafe_allow_html=True)
                        st.metric("🟡 Médio Risco", risco_counts.get('Médio', 0))
                        st.markdown('</div>', unsafe_allow_html=True)
                    with col_r3:
                        st.markdown('<div class="risk-low">', unsafe_allow_html=True)
                        st.metric("🟢 Baixo Risco", risco_counts.get('Baixo', 0))
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Tabela de anomalias
                    st.subheader("📋 Lista de Transações Suspeitas")
                    cols_mostrar = ['cliente', 'fornecedor', 'valor', 'z_score', 'nivel_risco']
                    cols_existentes = [c for c in cols_mostrar if c in anomalias.columns]
                    st.dataframe(anomalias[cols_existentes].sort_values('z_score', ascending=False), 
                               width='stretch')
                else:
                    st.success("✅ Nenhuma anomalia significativa detectada!")
    
    # TAB 6: TENDÊNCIAS
    with tab_tendencia:
        st.subheader("📈 Análise de Tendências Temporais")
        st.caption("Estuda a evolução do faturamento ao longo do tempo. Picos súbitos ou quedas drásticas em meses específicos podem indicar sazonalidade legítima ou tentativas de ajuste fiscal de última hora.")
        
        if 'data' in df_filtrado.columns:
            # Preparar dados temporais
            df_temporal = df_filtrado.copy()
            df_temporal['data'] = pd.to_datetime(df_temporal['data'], errors='coerce')
            df_temporal = df_temporal.dropna(subset=['data'])
            
            if not df_temporal.empty:
                df_temporal['mês'] = df_temporal['data'].dt.to_period('M').astype(str)
                
                # Agregação mensal
                mensal = df_temporal.groupby('mês')['valor'].agg(['sum', 'count', 'mean']).reset_index()
                mensal.columns = ['Período', 'Volume Total', 'N° Transações', 'Ticket Médio']
                
                # Gráfico de evolução
                fig_line = px.line(mensal, x='Período', y='Volume Total',
                                  title="Evolução do Volume de Transações",
                                  markers=True)
                fig_line.update_layout(height=400)
                st.plotly_chart(fig_line, width='stretch')
                
                # Sazonalidade
                df_temporal['mês_num'] = df_temporal['data'].dt.month
                sazonal = df_temporal.groupby('mês_num')['valor'].mean().reset_index()
                
                fig_sazonal = px.bar(sazonal, x='mês_num', y='valor',
                                    title="Média por Mês (Sazonalidade)",
                                    labels={'mês_num': 'Mês', 'valor': 'Média (FCFA)'})
                st.plotly_chart(fig_sazonal, width='stretch')
            else:
                st.info("Dados de data inválidos ou insuficientes")
        else:
            st.info("💡 Para análise de tendências, adicione uma coluna 'data' ao seu arquivo")

    # TAB 7: INTELIGÊNCIA ARTIFICIAL PREDITIVA E FORENSE
    with tab_ml:
        st.subheader("🧠 Agente Forense de Inteligência Artificial")
        st.caption("Utiliza algoritmos de Machine Learning não-supervisionado (Isolation Forest) e Teoria dos Grafos para detetar fraudes complexas que escapam às regras tradicionais.")
        
        col_ml1, col_ml2 = st.columns(2)
        
        with col_ml1:
            st.markdown("### 🤖 Motor Preditivo (Mutações Comportamentais)")
            st.info("A IA analisa o comportamento financeiro multidimensional e isola contribuintes cujo padrão destoa agressivamente da 'normalidade' do grupo.")
            
            if st.button("Executar Modelo de Isolation Forest", width='stretch'):
                with st.spinner("Treinando modelo de IA com os dados em memória..."):
                    from modules.ml_engine import prever_anomalias_ml
                    anomalias_ia = prever_anomalias_ml(df_filtrado)
                    
                    if not anomalias_ia.empty:
                        st.error(f"🚨 A IA identificou **{len(anomalias_ia)}** entidades com perfil altamente suspeito!")
                        # Exibir as colunas com formatação condicional de cor
                        st.dataframe(anomalias_ia.style.background_gradient(subset=['indice_suspeita_ia'], cmap='Reds'), width='stretch')
                    else:
                        st.success("✅ A IA não encontrou nenhum padrão anómalo escondido.")
                        
        with col_ml2:
            st.markdown("### 🕸️ Ciber-Forense (Fraude Carrossel)")
            st.info("Varre a rede de transações em busca de 'Ciclos Fechados' (Ex: A vende a B, que vende a C, que vende a A), a técnica mais comum para evasão massiva de IVA.")
            
            if st.button("Executar Varredura de Redes Complexas", width='stretch'):
                with st.spinner("Mapeando direções do dinheiro (Teoria dos Grafos)..."):
                    from modules.network import detetar_fraude_carrossel
                    ciclos = detetar_fraude_carrossel(df_filtrado)
                    
                    if ciclos:
                        st.error(f"🚩 ALERTA CRÍTICO: Foram detetados **{len(ciclos)}** ciclos fechados de faturamento!")
                        for i, ciclo in enumerate(ciclos):
                            # Montar a string do ciclo: A -> B -> C -> A
                            ciclo_str = " ➔ ".join(ciclo) + f" ➔ {ciclo[0]}"
                            st.warning(f"**Esquema #{i+1}:** {ciclo_str}")
                    else:
                        st.success("✅ Nenhum indício de fraude carrossel (ciclos fechados) detetado na rede.")
                        
        st.divider()
        st.markdown("### ⏳ Inteligência Comportamental (Sinais de Lavagem)")
        st.info("Analisa a série histórica de cada contribuinte. Picos súbitos e massivos de faturamento (5x a média) que ignoram a sazonalidade normal podem ser indicativos de injeção de capital ilícito (Lavagem de Dinheiro).")
        
        if st.button("Executar Scan Comportamental", width='stretch'):
            with st.spinner("Analisando perfil temporal de todos os contribuintes..."):
                from modules.fraud import detectar_lavagem_temporal
                picos = detectar_lavagem_temporal(df_filtrado)
                
                if not picos.empty:
                    st.error(f"🚨 Detetadas **{len(picos)}** entidades com picos de faturamento anormais e extremos.")
                    st.dataframe(picos, width='stretch')
                else:
                    st.success("✅ O perfil temporal dos contribuintes analisados não apresenta picos de lavagem estruturados.")

def main():
    """Main application entry point"""
    
    # Carregar dados
    st.sidebar.markdown("### 📂 Carregar Dados")
    
    uploaded_file = st.sidebar.file_uploader(
        "Escolha um arquivo CSV ou Excel",
        type=['csv', 'xlsx', 'xls']
    )
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            investigador_inteligente(df)
            
        except Exception as e:
            st.error(f"Erro ao carregar arquivo: {str(e)}")
            st.info("Verifique o formato do arquivo e as colunas necessárias.")
    else:
        # Dados de exemplo
        st.info("👈 Carregue um arquivo CSV ou Excel para começar a análise")
        
        if st.button("📊 Carregar Dados de Exemplo"):
            sample_data = {
                'cliente': ['Empresa A', 'Empresa B', 'Empresa C', 'Empresa A', 'Empresa B'] * 20,
                'fornecedor': ['Empresa X', 'Empresa Y', 'Empresa Z', 'Empresa Y', 'Empresa X'] * 20,
                'valor': [10000, 25000, 15000, 30000, 20000] * 20,
                'fatura': [f'FT-{i}' for i in range(1, 101)],
                'data': pd.date_range('2024-01-01', periods=100, freq='D')
            }
            df_sample = pd.DataFrame(sample_data)
            investigador_inteligente(df_sample)

if __name__ == "__main__":
    main()