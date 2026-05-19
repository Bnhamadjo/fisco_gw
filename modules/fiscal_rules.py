REGRAS_FISCAIS = {
    "IVA_NORMAL": {
        "taxa": 0.18,
        "descricao": "IVA Regime Geral (18%)"
    },
    "IVA_REDUZIDO": {
        "taxa": 0.10,
        "descricao": "IVA Reduzido (10%)"
    },
    "IVA_ZERO": {
        "taxa": 0.0,
        "descricao": "Taxa Zero / Exportações"
    },
    "IVA_ESPECIAL": {
        "taxa": 0.18,
        "descricao": "IVA Especial / Hotelaria (18%)"
    },
    "RETENCAO": {
        "taxa": 0.25,
        "descricao": "Retenção na Fonte genérica (confirmar tipo de rendimento)"
    },
    "RETENCAO_SERVICOS": {
        "taxa": 0.25,
        "descricao": "Retenção na Fonte (serviços profissionais)"
    },
    "RETENCAO_VARIAVEL": {
        "taxa": None,
        "descricao": "Retenção na Fonte variável, requer verificação manual"
    },
    "ISENTA": {
        "taxa": 0.0,
        "descricao": "Isento de IVA"
    }
}

SETORES_MAP = {
    "hotelaria": "IVA_ESPECIAL",
    "saude": "ISENTA",
    "educacao": "ISENTA",
    "alimentacao_basica": "IVA_REDUZIDO",
    "exportacao": "IVA_ZERO",
    "geral": "IVA_NORMAL"
}

def inferir_regime_por_setor(texto):
    """
    Tenta inferir o regime fiscal com base no nome da empresa ou descrição do setor.
    O algoritmo é propositalmente conservador: usa fallback seguro e evita classificações excessivamente amplas.
    """
    texto = str(texto).lower()
    for setor, regime in SETORES_MAP.items():
        if setor in texto:
            return regime
    return "IVA_NORMAL"
