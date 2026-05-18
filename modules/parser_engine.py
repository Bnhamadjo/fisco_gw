from modules.schema_detector import detectar_tipo_declaracao
from modules.cleaner import normalize_columns
from modules.tax_engine import calcular_imposto_inteligente

def interpretar_ficheiro_inteligente(df):
    """
    Motor principal que interpreta, normaliza e processa qualquer ficheiro fiscal.
    """
    if df is None or df.empty:
        return None, "GENERICO"
        
    # 1. Identificar o Tipo de Declaração
    tipo = detectar_tipo_declaracao(df)
    
    # 2. Normalizar colunas (usando a lógica inteligente já existente no cleaner)
    df = normalize_columns(df)
    
    # Adicionar metadados do tipo
    df['tipo_declaracao'] = tipo
    
    # 3. Aplicar Cálculos Fiscais baseados no tipo ou inferência
    df = calcular_imposto_inteligente(df)
    
    return df, tipo

def processar_especifico(df, tipo):
    """
    Lógica adicional para tipos específicos (IVA, DECIRF, etc).
    """
    if tipo == "DECIRF":
        # Lógica para retenções na fonte
        pass
    elif tipo == "IVA":
        # Lógica para saldo devedor/credor
        pass
        
    return df
