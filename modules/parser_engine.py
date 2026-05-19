from modules.schema_detector import detectar_tipo_declaracao
from modules.cleaner import normalize_columns, clean_for_arrow
from modules.tax_engine import calcular_imposto_inteligente
from modules.field_adapter import create_field_adapter

def interpretar_ficheiro_inteligente(df):
    """
    Motor principal que interpreta, normaliza e processa qualquer ficheiro fiscal.
    Agora com adaptação inteligente de campos.
    """
    if df is None or df.empty:
        return None, "GENERICO", None
        
    # 1. Criar adaptador de campos (detecta automaticamente)
    adapter = create_field_adapter(df)
    
    # 2. Identificar o Tipo de Declaração
    tipo = detectar_tipo_declaracao(df)
    
    # 3. Normalizar colunas (usando a lógica inteligente já existente no cleaner)
    df = normalize_columns(df)
    
    # 4. Adaptar dataframe (renomear campos detectados)
    df = adapter.adapt_dataframe()
    
    # 4.5. Higienizar tipos e fusos horários para compatibilidade total com o PyArrow do Streamlit Cloud
    df = clean_for_arrow(df)
    
    # Adicionar metadados
    df['tipo_declaracao'] = tipo
    df.attrs['field_adapter'] = adapter
    
    # 5. Aplicar Cálculos Fiscais baseados no tipo ou inferência
    df = calcular_imposto_inteligente(df)
    
    return df, tipo, adapter

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
