import pandas as pd
import numpy as np
import plotly.express as px

def benford_analysis(df, column="valor"):
    """
    Realiza a análise da Lei de Benford no primeiro dígito dos valores.
    """
    if column not in df.columns:
        return None, None
    
    # Extrair primeiro dígito (ignorando 0 e negativos)
    data = df[df[column] > 0][column].astype(str).str.extract(r'([1-9])')[0].astype(int)
    
    if data.empty:
        return None, None
    
    counts = data.value_counts(normalize=True).sort_index()
    
    # Distribuição teórica de Benford
    benford = pd.Series({d: np.log10(1 + 1/d) for d in range(1, 10)})
    
    comparison = pd.DataFrame({
        'Dígito': benford.index,
        'Esperado (Benford)': benford.values,
        'Observado': counts.reindex(range(1, 10), fill_value=0).values
    })
    
    fig = px.bar(comparison, x='Dígito', y=['Esperado (Benford)', 'Observado'],
                 barmode='group', title="Análise de Benford (Primeiro Dígito)",
                 color_discrete_sequence=['#94a3b8', '#00d2ff'])
    
    # Calcular desvio (MAE)
    mae = np.abs(comparison['Esperado (Benford)'] - comparison['Observado']).mean()
    
    return fig, mae

def detect_statistical_outliers(df, column="valor", threshold=3):
    """
    Detecta anomalias usando Z-Score.
    """
    if column not in df.columns:
        return None
    
    mean = df[column].mean()
    std = df[column].std()
    
    if std == 0:
        return None
    
    df_outliers = df.copy()
    df_outliers['z_score'] = (df_outliers[column] - mean) / std
    
    outliers = df_outliers[np.abs(df_outliers['z_score']) > threshold].copy()
    outliers['motivo_anomalia'] = outliers['z_score'].apply(lambda x: f"Valor Extremamente Alto (Outlier Z-Score: {x:.2f})" if x > 0 else f"Valor Extremamente Baixo (Outlier Z-Score: {x:.2f})")
    return outliers

def find_duplicate_transactions(df):
    """
    Detecta transações suspeitas com mesmos valores entre as mesmas entidades.
    """
    cols = ['cliente', 'fornecedor', 'valor']
    if not all(c in df.columns for c in cols):
        return None
    
    duplicates = df[df.duplicated(subset=cols, keep=False)].copy()
    duplicates['motivo_anomalia'] = "Transação Duplicada (Mesmo Cliente, Fornecedor e Valor)"
    return duplicates.sort_values(by=cols)

def suspicious_round_values(df, column="valor"):
    """
    Detecta valores suspeitosamente redondos (múltiplos de 1000, etc).
    """
    if column not in df.columns:
        return None
    
    # Exemplo: valores > 1000 que são múltiplos de 1000
    round_mask = (df[column] >= 1000) & (df[column] % 1000 == 0)
    round_values = df[round_mask].copy()
    round_values['motivo_anomalia'] = round_values[column].apply(lambda x: f"Valor Suspeitamente Redondo (Múltiplo de {1000 if x < 10000 else 10000})")
    return round_values

def detectar_lavagem_temporal(df, date_col="data", val_col="valor"):
    """
    Inteligência Comportamental: Deteta picos anómalos de faturamento que não 
    condizem com o histórico da empresa (assinatura de injeção de capital/lavagem).
    """
    if date_col not in df.columns or val_col not in df.columns or "fornecedor" not in df.columns:
        return pd.DataFrame()
        
    df_temp = df.copy()
    df_temp[date_col] = pd.to_datetime(df_temp[date_col], errors='coerce')
    df_temp = df_temp.dropna(subset=[date_col])
    
    if df_temp.empty:
        return pd.DataFrame()
        
    # Agrupar faturamento por fornecedor e por mês
    df_temp['mes_ano'] = df_temp[date_col].dt.to_period('M')
    faturamento_mensal = df_temp.groupby(['fornecedor', 'mes_ano'])[val_col].sum().reset_index()
    
    # Calcular média e desvio padrão mensal por fornecedor
    stats_fornecedor = faturamento_mensal.groupby('fornecedor')[val_col].agg(['mean', 'std', 'max']).reset_index()
    stats_fornecedor['std'] = stats_fornecedor['std'].fillna(0)
    
    # Identificar picos: O mês máximo é 5 vezes superior à média e desvio padrão é muito alto
    # (Indica que não é um negócio linear, mas tem injeções pontuais maciças)
    suspeitos = stats_fornecedor[
        (stats_fornecedor['max'] > stats_fornecedor['mean'] * 5) & 
        (stats_fornecedor['mean'] > 0) &
        (stats_fornecedor['max'] > 100000) # Ignorar microempresas com variações pequenas em valor absoluto
    ].copy()
    
    if not suspeitos.empty:
        suspeitos['motivo_anomalia'] = "Pico de Faturamento Extremo (Possível Injeção de Capital/Lavagem)"
        suspeitos = suspeitos.sort_values(by='max', ascending=False)
        
    return suspeitos

