import streamlit as st
import pandas as pd

# CONFIG (Deve ser o primeiro comando Streamlit)
st.set_page_config(page_title="Inteligência Fiscal DGCI", layout="wide")

# =========================
# MODULES
# =========================
from modules.uploader import load_file, get_excel_sheets
from modules.cleaner import normalize_columns
from modules.parser_engine import interpretar_ficheiro_inteligente
from modules.exporter import download_buttons
from modules.analyzer import calcular_volume_negocio, resumo_clientes, resumo_fornecedores
from modules.relationships import relacoes
from modules.fiscal import calcular_imposto
from components.charts import grafico_clientes, grafico_risco
from modules.risk import calcular_score_risco
from modules.network import criar_grafo
from modules.mapper import extrair_entidades
from modules.db_insert import inserir_contribuintes
from modules.db_read import listar_contribuintes

from components.time_analysis import analise_temporal
from components.fiscal_compare import cruzamento_fiscal

from modules.auditoria import (
    detectar_valores_invalidos,
    top_suspeitos,
    detectar_anomalias,
    gerar_alertas
)

# =========================
# COMPONENTS
# =========================
from components.charts import grafico_clientes, grafico_risco
from components.filters import aplicar_filtros
from components.network_chart import visualizar_grafo
from components.query_builder import query_builder
from components.contributor_view import analisar_contribuinte
from components.entity_relationship import analisar_relacao
from components.investigador_view import investigador_inteligente

from modules.fraud import (
    benford_analysis,
    detect_statistical_outliers,
    find_duplicate_transactions,
    suspicious_round_values
)

# =========================
# UTILS
# =========================
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# =========================
# CONFIG
# =========================
load_css("assets/style.css")

st.markdown('<h1 class="main-header">📊 Inteligência Fiscal - DGCI 🇬🇼</h1>', unsafe_allow_html=True)

# =========================
# SIDEBAR
# =========================
st.sidebar.title("📌 Navegação")

pagina = st.sidebar.radio(
    "Escolha uma opção",
    [
        "📊 Análise Fiscal",
        "🔎 Investigador Inteligente",
        "🧾 Sistema MER",
        "🕸️ Investigação"
    ]
)

# =========================
# UPLOAD
# =========================
uploaded_files = st.file_uploader(
    "📤 Carregar ficheiros",
    type=["csv", "xlsx", "xlsm", "pdf"],
    accept_multiple_files=True
)

dfs = []
df = None

# =========================
# LOAD DATA
# =========================
if uploaded_files:
    for file in uploaded_files:
        sheets = get_excel_sheets(file)
        if sheets:
            st.sidebar.markdown(f"📖 **{file.name}**")
            selected_sheets = st.sidebar.multiselect(
                f"Folhas de {file.name}",
                sheets,
                default=[sheets[0]],
                key=f"sheets_{file.name}"
            )
            for sheet in selected_sheets:
                df_temp = load_file(file, sheet_name=sheet)
                if df_temp is not None:
                    df_temp, tipo = interpretar_ficheiro_inteligente(df_temp)
                    st.sidebar.success(f"✅ {sheet}: **{tipo}**")
                    dfs.append(df_temp)
        else:
            df_temp = load_file(file)
            if df_temp is not None:
                # Motor Inteligente
                df_temp, tipo = interpretar_ficheiro_inteligente(df_temp)
                st.sidebar.info(f"📂 {file.name}\n📋 Tipo: **{tipo}**")
                dfs.append(df_temp)

    if dfs:
        df = dfs[0]

        # Opção para inverter papéis caso o mapeamento automático tenha trocado
        st.sidebar.divider()
        if st.sidebar.checkbox("🔄 Inverter Papéis (Cliente ↔ Fornecedor)"):
            mapping_swap = {}
            if 'cliente' in df.columns and 'fornecedor' in df.columns:
                mapping_swap['cliente'] = 'fornecedor'
                mapping_swap['fornecedor'] = 'cliente'
            if 'nif_cliente' in df.columns and 'nif_fornecedor' in df.columns:
                mapping_swap['nif_cliente'] = 'nif_fornecedor'
                mapping_swap['nif_fornecedor'] = 'nif_cliente'
            
            if mapping_swap:
                # Usar um mapeamento temporário para evitar sobreposição
                temp_map = {k: f"temp_{v}" for k, v in mapping_swap.items()}
                df = df.rename(columns=temp_map)
                final_swap = {f"temp_{v}": v for k, v in mapping_swap.items()}
                df = df.rename(columns=final_swap)
                st.sidebar.success("✅ Papéis Invertidos")

        entidades = extrair_entidades(df)
        st.session_state["entidades"] = entidades
        inserir_contribuintes(entidades)

# =========================
# 📊 ANÁLISE FISCAL
# =========================
if pagina == "📊 Análise Fiscal":

    if df is None:
        st.warning("⚠️ Carregue ficheiros primeiro.")
        st.stop()

    st.success("✅ Dados carregados com sucesso.")

    df_filtrado = aplicar_filtros(df)

    abas = st.tabs([
        "📊 Dashboard",
        "🔎 Auditoria",
        "📂 Dados",
        "🕸️ Rede",
        "🔍 Explorar",
        "👤 Contribuinte / Relação",
        "📅 Análise Temporal"
    ])

    # DASHBOARD
    with abas[0]:
        st.subheader("🚀 Indicadores de Performance")
        
        volume = calcular_volume_negocio(df_filtrado)
        num_transacoes = len(df_filtrado)
        
        # Usar imposto calculado pelo motor inteligente se disponível
        if 'imposto_calculado' in df_filtrado.columns:
            imposto_total = df_filtrado['imposto_calculado'].sum()
            label_imposto = "⚖️ Imposto Inteligente"
        else:
            imposto_total = calcular_imposto(volume, volume * 0.3)
            label_imposto = "⚖️ Imposto Estimado"
            
        ticket_medio = volume / num_transacoes if num_transacoes > 0 else 0

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("💰 Volume Total", f"{volume:,.2f} FCFA")
        m2.metric(label_imposto, f"{imposto_total:,.2f} FCFA")
        m3.metric("📈 Transações", f"{num_transacoes:,}")
        m4.metric("🎫 Ticket Médio", f"{ticket_medio:,.2f} FCFA")

        st.divider()

        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            if "cliente" in df_filtrado.columns and "valor" in df_filtrado.columns:
                st.plotly_chart(grafico_clientes(df_filtrado), use_container_width=True)
            else:
                st.warning("⚠️ Colunas 'cliente' ou 'valor' não encontradas para o gráfico.")
        
        with col_right:
            st.info("💡 **Dica Fiscal:** O volume de negócio acumulado representa a base de cálculo para o imposto estimado de 30% sobre a margem presumida.")

    # AUDITORIA
    with abas[1]:
        with st.expander("📖 Guia de Metodologia e Legendas"):
            st.markdown("""
            **Como calculamos cada seção:**
            
            *   **🚨 Suspeitos (Top Valores):** Identifica as 10 maiores transações por valor absoluto. Valores extremamente altos são os primeiros pontos de verificação em auditorias fiscais.
            *   **📉 Anomalias Estatísticas (Z-Score):** Usa o cálculo de Desvio Padrão. Transações com *Z-Score > 3* são consideradas anomalias estatísticas (outliers), pois estão muito distantes da média do grupo.
            *   **📊 Análise de Benford:** Baseia-se na lei estatística de que o dígito '1' aparece como primeiro dígito em ~30% das vezes. Desvios significativos nesta curva sugerem que os dados podem ter sido inventados ou manipulados.
            *   **⚠️ Valores Inválidos (<= 0):** Filtra transações com valores negativos ou zerados, que podem indicar erros de lançamento ou tentativas de anular faturas indevidamente.
            *   **🔄 Transações Duplicadas Suspeitas:** Procura por registros que tenham o mesmo *Cliente*, *Fornecedor* e *Valor* exatos. Pode indicar faturamento duplo ou erros de importação.
            """)

        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🚨 Suspeitos (Top Valores)")
            st.caption("Filtra as 10 faturas com os montantes mais elevados. Estes registos representam o maior impacto financeiro potencial em caso de erro ou omissão.")
            suspeitos = top_suspeitos(df_filtrado)
            if suspeitos is not None:
                st.dataframe(suspeitos, use_container_width=True)

        with col2:
            st.subheader("📉 Anomalias Estatísticas (Z-Score)")
            st.caption("Identifica valores que estão a mais de 3 desvios padrão da média. Matematicamente, estas transações são exceções raras e altamente suspeitas.")
            outliers = detect_statistical_outliers(df_filtrado)
            if outliers is not None:
                st.dataframe(outliers, use_container_width=True)

        st.divider()
        
        st.subheader("🔢 Análise de Benford")
        st.caption("Compara a frequência do primeiro dígito dos valores com a distribuição natural esperada. Desvios na curva sugerem que os dados podem não ter sido gerados organicamente.")
        fig_benford, mae = benford_analysis(df_filtrado)
        if fig_benford:
            st.plotly_chart(fig_benford, use_container_width=True)
            st.info(f"**Desvio Médio Absoluto (MAE):** {mae:.4f}")
            if mae > 0.05:
                st.warning("⚠️ O desvio da Lei de Benford é elevado, sugerindo possível manipulação de dados.")

        st.divider()

        col3, col4 = st.columns(2)
        with col3:
            st.subheader("⚠️ Valores Inválidos (<= 0)")
            st.caption("Lista registos com valores negativos ou zero. Estas entradas anulam a base tributável e podem indicar erros graves de processamento.")
            invalidos = detectar_valores_invalidos(df_filtrado)
            if invalidos is not None:
                st.dataframe(invalidos, use_container_width=True)

        with col4:
            st.subheader("🔄 Transações Duplicadas Suspeitas")
            st.caption("Procura por faturas idênticas (mesmo cliente, fornecedor e valor). Pode sinalizar faturamento duplo para inflar custos ou erros de importação.")
            duplicados = find_duplicate_transactions(df_filtrado)
            if duplicados is not None:
                st.dataframe(duplicados, use_container_width=True)

        st.divider()
        
        st.subheader("🚩 Alertas de Risco")
        for alerta in gerar_alertas(df_filtrado):
            st.warning(alerta)

        st.subheader("📊 Score de Risco por Contribuinte")
        st.caption("Pontuação acumulada baseada em volume financeiro (40pts), frequência atípica (30pts) e desvios estatísticos. Quanto maior o score, maior a prioridade de fiscalização.")
        risk_df = calcular_score_risco(df_filtrado)
        if risk_df is not None:
            st.dataframe(risk_df, use_container_width=True)
            st.plotly_chart(grafico_risco(risk_df), use_container_width=True)

    # DADOS
    with abas[2]:
        st.dataframe(df_filtrado)

        clientes = resumo_clientes(df_filtrado)
        fornecedores = resumo_fornecedores(df_filtrado)

        if clientes is not None:
            st.dataframe(clientes)

        if fornecedores is not None:
            st.dataframe(fornecedores)

        if {"cliente", "fornecedor"}.issubset(df_filtrado.columns):
            st.dataframe(relacoes(df_filtrado))

    # REDE
    with abas[3]:
        grafo = criar_grafo(df_filtrado)

        if grafo is not None:
            html = visualizar_grafo(grafo)
            with open(html, "r", encoding="utf-8") as f:
                st.components.v1.html(f.read(), height=650)

    # EXPLORAR
    with abas[4]:
        query_builder(df_filtrado)

    # CONTRIBUINTE + RELAÇÃO
    with abas[5]:
        st.subheader("👤 Contribuinte")
        analisar_contribuinte(df_filtrado)

        st.divider()

        st.subheader("🔗 Relações")
        analisar_relacao(df_filtrado)

    # ANÁLISE TEMPORAL
    with abas[6]:
        analise_temporal(df_filtrado)

        st.divider()

        cruzamento_fiscal(df_filtrado)

    # COMPARAÇÃO
    if len(dfs) >= 2:
        df1, df2 = dfs[:2]
        colunas = list(set(df1.columns) & set(df2.columns))

        if len(colunas) >= 2:
            st.subheader("🔍 Comparação")
            # Garantir que as colunas de merge tenham o mesmo tipo para evitar erro de 'object' vs 'float'
            df1_comp = df1.copy()
            df2_comp = df2.copy()
            for col in colunas:
                df1_comp[col] = df1_comp[col].astype(str)
                df2_comp[col] = df2_comp[col].astype(str)
                
            st.dataframe(df1_comp.merge(df2_comp, on=colunas, how="outer").head())

    st.divider()
    st.subheader("📥 Exportar Resultados")
    download_buttons(df_filtrado, filename="relatorio_fiscal_geral", key_prefix="main_audit")

# =========================
# 🔎 INVESTIGADOR INTELIGENTE
# =========================
elif pagina == "🔎 Investigador Inteligente":
    if df is None:
        st.warning("⚠️ Carregue ficheiros primeiro")
        st.stop()
    
    investigador_inteligente(df)

# =========================
# 🧾 SISTEMA MER
# =========================
elif pagina == "🧾 Sistema MER":

    entidades = st.session_state.get("entidades")

    if not entidades:
        st.warning("⚠️ Carregar ficheiros primeiro")
        st.stop()

    tab1, tab2 = st.tabs(["Contribuintes", "Relações"])

    with tab1:
        dados = list(set(entidades["contribuintes"] + entidades["fornecedores"]))
        st.dataframe(pd.DataFrame(dados, columns=["Nome"]))

        st.subheader("Base de Dados")
        st.dataframe(listar_contribuintes())

    with tab2:
        rel = entidades.get("relacoes")

        if rel is not None:
            st.dataframe(rel.head())

# =========================
# 🕸️ INVESTIGAÇÃO GLOBAL
# =========================
elif pagina == "🕸️ Investigação":

    if df is None:
        st.warning("⚠️ Carregue ficheiros primeiro")
        st.stop()

    grafo = criar_grafo(df)

    if grafo is not None:
        html = visualizar_grafo(grafo)
        with open(html, "r", encoding="utf-8") as f:
            st.components.v1.html(f.read(), height=650)