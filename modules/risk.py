import pandas as pd

def calcular_score_risco(df):

    if "cliente" not in df.columns or "valor" not in df.columns:
        return None

    resultado = df.groupby("cliente").agg({
        "valor": ["sum", "count"]
    })

    resultado.columns = ["total_valor", "num_transacoes"]
    resultado = resultado.reset_index()

    media_valor = resultado["total_valor"].mean()

    def calcular_score(row):
        score = 0

        # volume muito alto
        if row["total_valor"] > media_valor * 3:
            score += 40

        # muitas transações
        if row["num_transacoes"] > 50:
            score += 30

        # valores baixos suspeitos
        if row["total_valor"] < 1000:
            score += 10

        return score

    resultado["score_risco"] = resultado.apply(calcular_score, axis=1)

    # classificação
    def classificar(score):
        if score >= 60:
            return "🔴 Alto Risco"
        elif score >= 30:
            return "🟡 Médio Risco"
        else:
            return "🟢 Baixo Risco"

    resultado["nivel_risco"] = resultado["score_risco"].apply(classificar)

    return resultado