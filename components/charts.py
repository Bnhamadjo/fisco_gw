import plotly.express as px
import pandas as pd

def grafico_clientes(df):
    if "cliente" not in df.columns or "valor" not in df.columns:
        return px.bar(title="Dados insuficientes para gerar gráfico")
        
    resumo = df.groupby("cliente")["valor"].sum().reset_index()
    fig = px.bar(resumo, x="cliente", y="valor", title="Volume por Cliente",
                 color_discrete_sequence=['#00d2ff'])
    return fig


def grafico_risco(df):
    if "cliente" not in df.columns or "score_risco" not in df.columns:
        return px.bar(title="Dados de risco insuficientes")
        
    fig = px.bar(
        df.sort_values(by="score_risco", ascending=False).head(10),
        x="cliente",
        y="score_risco",
        color="nivel_risco",
        title="Top 10 Contribuintes por Risco",
        color_discrete_map={
            "🔴 Alto Risco": "#ef4444",
            "🟡 Médio Risco": "#f59e0b",
            "🟢 Baixo Risco": "#10b981"
        }
    )
    return fig
