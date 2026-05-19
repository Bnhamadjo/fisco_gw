"""
Analysis Fallbacks - Análises adaptadas que funcionam com campos faltando
=========================================================================
Versões robustas de funções de análise que não falham quando campos são omitidos.
"""

import pandas as pd
import numpy as np
from typing import Optional, Tuple

def safe_top_suspicious(df: pd.DataFrame, n: int = 10) -> Optional[pd.DataFrame]:
    """
    Encontra top N valores suspeitos (maiores valores).
    Funciona mesmo sem campo 'cliente'.
    """
    if df is None or df.empty:
        return None
    
    # Procurar por campo de valor
    valor_col = None
    for col in ['valor', 'Valor', 'VALOR', 'montante', 'amount']:
        if col in df.columns:
            valor_col = col
            break
    
    if valor_col is None:
        return None
    
    try:
        # Converter para numérico
        df_temp = df.copy()
        df_temp[valor_col] = pd.to_numeric(df_temp[valor_col], errors='coerce')
        
        # Top N maiores valores
        top = df_temp.nlargest(n, valor_col)
        
        # Se houver cliente, incluir. Se não, apenas mostrar valor
        if 'cliente' in top.columns:
            return top[['cliente', valor_col]].reset_index(drop=True)
        else:
            return top[[valor_col]].reset_index(drop=True)
    except Exception as e:
        return None


def safe_statistical_outliers(df: pd.DataFrame, z_threshold: float = 3) -> Optional[pd.DataFrame]:
    """
    Detecta outliers estatísticos usando Z-score.
    Funciona mesmo sem metadados de cliente.
    """
    if df is None or df.empty:
        return None
    
    # Procurar por campo de valor
    valor_col = None
    for col in ['valor', 'Valor', 'VALOR', 'montante', 'amount']:
        if col in df.columns:
            valor_col = col
            break
    
    if valor_col is None:
        return None
    
    try:
        df_temp = df.copy()
        df_temp[valor_col] = pd.to_numeric(df_temp[valor_col], errors='coerce')
        df_temp = df_temp.dropna(subset=[valor_col])
        
        if len(df_temp) < 3:
            return None
        
        # Calcular Z-score
        mean = df_temp[valor_col].mean()
        std = df_temp[valor_col].std()
        
        if std == 0:
            return None
        
        df_temp['z_score'] = np.abs((df_temp[valor_col] - mean) / std)
        
        # Filtrar outliers
        outliers = df_temp[df_temp['z_score'] > z_threshold]
        
        if outliers.empty:
            return None
        
        if 'cliente' in outliers.columns:
            return outliers[['cliente', valor_col, 'z_score']].sort_values('z_score', ascending=False)
        else:
            return outliers[[valor_col, 'z_score']].sort_values('z_score', ascending=False)
    except Exception as e:
        return None


def safe_detect_duplicates(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """
    Detecta transações duplicadas.
    Funciona com diferentes combinações de campos.
    """
    if df is None or df.empty:
        return None
    
    try:
        df_temp = df.copy()
        
        # Tentar diferentes combinações de chaves de duplicação
        duplicate_keys = [
            ['cliente', 'fornecedor', 'valor'],
            ['cliente', 'valor'],
            ['valor'],
        ]
        
        for keys in duplicate_keys:
            available_keys = [k for k in keys if k in df_temp.columns]
            if available_keys:
                # Encontrar duplicatas
                duplicates = df_temp[df_temp.duplicated(subset=available_keys, keep=False)]
                
                if not duplicates.empty:
                    cols_to_show = available_keys + [c for c in ['data', 'fatura'] if c in duplicates.columns]
                    return duplicates[cols_to_show].sort_values(by=available_keys)
        
        return None
    except Exception as e:
        return None


def safe_invalid_values(df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """
    Detecta valores inválidos (<= 0).
    """
    if df is None or df.empty:
        return None
    
    valor_col = None
    for col in ['valor', 'Valor', 'VALOR', 'montante', 'amount']:
        if col in df.columns:
            valor_col = col
            break
    
    if valor_col is None:
        return None
    
    try:
        df_temp = df.copy()
        df_temp[valor_col] = pd.to_numeric(df_temp[valor_col], errors='coerce')
        
        invalidos = df_temp[df_temp[valor_col] <= 0]
        
        if invalidos.empty:
            return None
        
        cols_to_show = [c for c in ['cliente', valor_col, 'data'] if c in invalidos.columns]
        return invalidos[cols_to_show]
    except Exception as e:
        return None


def safe_temporal_analysis(df: pd.DataFrame) -> Tuple[bool, Optional[pd.DataFrame]]:
    """
    Realiza análise temporal se campo 'data' estiver disponível.
    Retorna (pode_analisar, dados_agregados)
    """
    if df is None or df.empty:
        return False, None
    
    if 'data' not in df.columns:
        return False, None
    
    valor_col = None
    for col in ['valor', 'Valor', 'VALOR', 'montante', 'amount']:
        if col in df.columns:
            valor_col = col
            break
    
    if valor_col is None:
        return False, None
    
    try:
        df_temp = df.copy()
        df_temp['data'] = pd.to_datetime(df_temp['data'], errors='coerce')
        df_temp = df_temp.dropna(subset=['data'])
        
        if df_temp.empty:
            return False, None
        
        df_temp[valor_col] = pd.to_numeric(df_temp[valor_col], errors='coerce')
        df_temp['mês'] = df_temp['data'].dt.to_period('M').astype(str)
        
        # Agregação mensal
        mensal = df_temp.groupby('mês')[valor_col].agg(['sum', 'count', 'mean']).reset_index()
        mensal.columns = ['Período', 'Volume Total', 'N° Transações', 'Ticket Médio']
        
        return True, mensal
    except Exception as e:
        return False, None


def get_valor_column(df: pd.DataFrame) -> Optional[str]:
    """
    Detecta qual coluna contém valores monetários.
    """
    if df is None:
        return None
    
    for col in ['valor', 'Valor', 'VALOR', 'montante', 'amount', 'base tributavel']:
        if col in df.columns:
            return col
    
    return None


def get_entity_columns(df: pd.DataFrame) -> Tuple[Optional[str], Optional[str]]:
    """
    Detecta colunas de cliente e fornecedor.
    Retorna (cliente_col, fornecedor_col)
    """
    cliente_col = None
    fornecedor_col = None
    
    for col in df.columns:
        col_lower = col.lower()
        if 'cliente' in col_lower or 'comprador' in col_lower:
            cliente_col = col
        elif 'fornecedor' in col_lower or 'prestador' in col_lower or 'vendedor' in col_lower:
            fornecedor_col = col
    
    return cliente_col, fornecedor_col


def safe_column_access(df: pd.DataFrame, field_name: str, alternatives: list = None) -> Optional[str]:
    """
    Acessa uma coluna com fallbacks automáticos.
    
    Returns:
        Nome da coluna ou None se não encontrada
    """
    if alternatives is None:
        alternatives = []
    
    alternatives = [field_name] + alternatives
    
    for col in alternatives:
        if col in df.columns:
            return col
    
    return None
