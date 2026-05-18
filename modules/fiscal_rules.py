REGRAS_FISCAIS = {
    "IVA_NORMAL": {
        "taxa": 0.19,
        "descricao": "IVA Regime Geral (19%)"
    },
    "IVA_REDUZIDO": {
        "taxa": 0.05,
        "descricao": "IVA Reduzido (5%)"
    },
    "IVA_ESPECIAL": {
        "taxa": 0.18,
        "descricao": "IVA Especial / Hotelaria (18%)"
    },
    "RETENCAO": {
        "taxa": 0.25,
        "descricao": "Retenção na Fonte (25%)"
    },
    "ISENTA": {
        "taxa": 0.0,
        "descricao": "Isento de Imposto"
    }
}

SETORES_MAP = {
    "hotelaria": "IVA_ESPECIAL",
    "restauracao": "IVA_ESPECIAL",
    "saude": "ISENTA",
    "alimentacao": "IVA_REDUZIDO",
    "geral": "IVA_NORMAL"
}

def inferir_regime_por_setor(texto):
    """
    Tenta inferir o regime fiscal com base no nome da empresa ou descrição do setor.
    """
    texto = str(texto).lower()
    for setor, regime in SETORES_MAP.items():
        if setor in texto:
            return regime
    return "IVA_NORMAL"
