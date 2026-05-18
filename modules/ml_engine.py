import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
import warnings

def prever_anomalias_ml(df):
    """
    Motor Preditivo: Utiliza Machine Learning (Isolation Forest) para detetar
    anomalias multidimensionais que escapam às regras estáticas.
    """
    if "valor" not in df.columns or "cliente" not in df.columns or "fornecedor" not in df.columns:
        return pd.DataFrame()

    df_ml = df.copy()

    # Preencher nulos no valor
    df_ml['valor'] = pd.to_numeric(df_ml['valor'], errors='coerce').fillna(0)
    
    # Feature Engineering (Criar variáveis para a IA)
    # 1. Agrupar por Entidade (vamos analisar os fornecedores como 'foco' da possível fraude)
    perfil = df_ml.groupby("fornecedor").agg(
        total_valor=("valor", "sum"),
        num_transacoes=("valor", "count"),
        ticket_medio=("valor", "mean"),
        desvio_valor=("valor", "std")
    ).fillna(0).reset_index()

    # Se houver muito poucos dados, o ML não funciona bem
    if len(perfil) < 5:
        return pd.DataFrame()

    # Selecionar as features para o modelo
    X = perfil[['total_valor', 'num_transacoes', 'ticket_medio', 'desvio_valor']]

    # Configurar o modelo (contamination = proporção esperada de fraudes, ex: 5%)
    # Usamos random_state para garantir que a análise seja determinística (reproduzível)
    modelo = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
    
    # Ignorar avisos do scikit-learn temporariamente
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        # Treinar o modelo e prever
        perfil['ml_outlier'] = modelo.fit_predict(X)
        # Pontuação da anomalia (quanto mais negativo, mais anômalo)
        perfil['ml_score'] = modelo.decision_function(X)

    # Filtrar apenas as entidades que a IA considerou anómalas (outlier = -1)
    anomalias_ml = perfil[perfil['ml_outlier'] == -1].copy()
    
    # Normalizar o score para um Índice de Suspeita (0 a 100)
    if not anomalias_ml.empty:
        min_score = anomalias_ml['ml_score'].min()
        max_score = anomalias_ml['ml_score'].max()
        
        # Inverter e escalar (menor score original = maior suspeita)
        if min_score != max_score:
            anomalias_ml['indice_suspeita_ia'] = 100 - ((anomalias_ml['ml_score'] - min_score) / (max_score - min_score) * 100)
        else:
            anomalias_ml['indice_suspeita_ia'] = 99.0
            
        anomalias_ml = anomalias_ml.sort_values('indice_suspeita_ia', ascending=False)
        anomalias_ml['motivo_ia'] = "Padrão Transacional Anómalo Detetado pela IA"
        
    return anomalias_ml[['fornecedor', 'total_valor', 'num_transacoes', 'indice_suspeita_ia', 'motivo_ia']]
