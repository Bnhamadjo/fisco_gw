import re

# Dicionário de treinamento base (Keywords -> Regime)
TRAINING_DATA = {
    "IVA_ESPECIAL": ["hotel", "pousada", "resort", "restaurante", "bar", "cafe", "pasteleria", "alojamento"],
    "IVA_REDUZIDO": ["arroz", "leite", "pao", "farinha", "medicamento", "farmacia", "clinica", "hospital"],
    "ISENTA": ["ong", "associacao", "embaixada", "consulado", "estado", "ministerio"],
    "RETENCAO": ["advogado", "consultor", "engenheiro", "medico", "servico profissional", "honorarios"],
    "IVA_NORMAL": ["lda", "sa", "su", "comercio", "servicos", "vendas", "import"]
}

def prever_regime_fiscal(nome_empresa):
    """
    IA de Classificação: Prediz o regime fiscal com base no nome e termos da empresa.
    """
    if not nome_empresa or not isinstance(nome_empresa, str):
        return "IVA_NORMAL"
        
    nome = nome_empresa.lower()
    
    scores = {regime: 0 for regime in TRAINING_DATA.keys()}
    
    for regime, keywords in TRAINING_DATA.items():
        for kw in keywords:
            if kw in nome:
                # Termos no início ou fim valem mais
                if nome.startswith(kw) or nome.endswith(kw):
                    scores[regime] += 2
                else:
                    scores[regime] += 1
                    
    # Retornar o regime com maior score
    melhor_regime = max(scores, key=scores.get)
    
    if scores[melhor_regime] == 0:
        return "IVA_NORMAL"
        
    return melhor_regime

def classificar_setor(nome_empresa):
    """
    Classifica a empresa em um setor econômico.
    """
    setores = {
        "Turismo/Lazer": ["hotel", "resort", "viagens"],
        "Alimentação": ["restaurante", "supermercado", "comida"],
        "Saúde": ["hospital", "clinica", "farmacia"],
        "Educação": ["escola", "universidade", "colegio"],
        "Serviços Profissionais": ["consultoria", "advocacia", "contabilidade"]
    }
    
    nome = str(nome_empresa).lower()
    for setor, keywords in setores.items():
        if any(kw in nome for kw in keywords):
            return setor
    return "Outros Serviços"
