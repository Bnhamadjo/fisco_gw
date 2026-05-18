from modules.fiscal_rules import REGRAS_FISCAIS
from modules.ai_classifier import prever_regime_fiscal

def calcular_imposto_inteligente(df):
    """
    Aplica regras fiscais dinâmicas e usa IA para classificar regimes desconhecidos.
    """
    if 'valor' not in df.columns:
        return df
        
    # Garantir que 'valor' seja numérico para evitar erro de multiplicação por string
    import pandas as pd
    df['valor'] = pd.to_numeric(df['valor'], errors='coerce').fillna(0)
        
    # Usar IA para prever regime se não houver coluna de taxa ou se for genérico
    if 'regime' not in df.columns:
        if 'fornecedor' in df.columns:
            # IA decide o regime com base no nome do fornecedor
            df['regime'] = df['fornecedor'].apply(prever_regime_fiscal)
        else:
            df['regime'] = "IVA_NORMAL"
            
    def get_tax(regime):
        return REGRAS_FISCAIS.get(regime, REGRAS_FISCAIS["IVA_NORMAL"])["taxa"]
        
    df['taxa_aplicada'] = df['regime'].apply(get_tax)
    df['imposto_calculado'] = df['valor'] * df['taxa_aplicada']
    
    return df

def aplicar_penalidade_risco(df):
    """
    Exemplo de lógica de risco: se imposto pago for muito baixo em relação ao volume.
    """
    if 'valor' in df.columns and 'imposto' in df.columns:
        df['alerta_evasao'] = df.apply(
            lambda x: x['imposto'] < (x['valor'] * 0.03) if x['valor'] > 0 else False, 
            axis=1
        )
    return df
