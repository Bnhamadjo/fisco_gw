import re

def limpar_texto(texto):
    """
    Limpa e normaliza descrições de transações.
    """
    if not isinstance(texto, str): return ""
    return texto.lower().strip()

def extrair_entidades_texto(texto):
    """
    Tenta extrair NIFs ou códigos de fatura de uma descrição longa.
    """
    # Regex para NIF (exemplo: 9 dígitos)
    nifs = re.findall(r'\b\d{9}\b', texto)
    
    # Regex para Faturas (exemplo: FT/2024/001)
    faturas = re.findall(r'[A-Z]{2}/\d{4}/\d+', texto)
    
    return {
        "nifs": nifs,
        "faturas": faturas
    }

def analisar_sentimento_fiscal(texto):
    """
    Identifica palavras-chave de risco em descrições.
    """
    keywords_alerta = ["ajuste", "correcao", "cancelado", "estorno", "manual", "divergencia"]
    t = limpar_texto(texto)
    for kw in keywords_alerta:
        if kw in t:
            return "ALERTA"
    return "NORMAL"
