import streamlit as st

def mostrar_metodologia():
    with st.expander("📖 Guia de Interpretação e Metodologia de Risco"):
        st.markdown("""
        ### 🧠 Como o Sistema Toma Decisões
        Para garantir a transparência da auditoria, abaixo explicamos os critérios usados para classificar cada transação:

        #### 🔴 ALTO RISCO (Evidência Forte de Irregularidade)
        *   **Outliers Estatísticos (Z-Score > 3)**: Transações com valores que fogem completamente do padrão matemático do contribuinte ou do ficheiro.
        *   **Datas Futuras**: Faturas com data de emissão posterior à data de hoje (indicação clara de erro ou fraude).
        *   **Desvio de Cruzamento > 5%**: Quando o imposto declarado difere significativamente do cálculo fiscal real esperado para o montante.

        #### 🟡 MÉDIO RISCO (Necessita de Verificação)
        *   **Valores Suspeitamente Redondos**: Faturas com valores exatos (ex: 1.000.000) que não possuem centavos/frações, comum em lançamentos fictícios.
        *   **Transações Duplicadas**: Registros com o mesmo Cliente, Fornecedor e Valor no mesmo ficheiro.
        *   **Anomalias de Média**: Valores que são 5x superiores à média aritmética de todas as transações do documento.

        #### 🟢 BAIXO RISCO / NORMAL
        *   Transações que seguem a **Lei de Benford** (distribuição natural de dígitos).
        *   Valores dentro do desvio padrão esperado para o setor económico da empresa.

        #### ❌ VALORES INVÁLIDOS
        *   **Valor Zero ou Negativo**: Lançamentos que anulam a base tributável ou que não possuem conteúdo económico real.

        #### 🏆 CRITÉRIOS DO TOP 10 POR RISCO
        O ranking de risco dos contribuintes é calculado através de um sistema de pontuação acumulada:
        *   **Volume Financeiro (40 pts)**: Atribuído se o volume total de transações da entidade for 3x superior à média do ficheiro.
        *   **Frequência Atípica (30 pts)**: Atribuído se a entidade possuir mais de 50 transações no período analisado (possível fracionamento de faturas).
        *   **Suspeita de Omissão (10 pts)**: Atribuído se houver transações com valores extremamente baixos que sugerem evasão fiscal.
        
        ---
        *Nota: Esta lógica foi desenhada para atuar como um filtro inicial, permitindo que o auditor foque nos casos de maior impacto fiscal.*
        """)
