TIPOS_DECLARACAO = {
    "IVA": ["iva", "liquidado", "suportado", "dedutivel", "nif", "valor_iva", "3.7 iva", "4.7 iva", "5.7 iva"],
    "DIVA": ["diva", "venda", "taxa", "liquido", "nome do declarante", "01.nif", "3.1 nif"],
    "DECIRF": ["rendimento", "retencao", "irf", "beneficiario", "fonte"],
    "LISTAGEM_CLIENTES": ["cliente", "fatura", "data", "nif cliente"]
}

def detectar_tipo_declaracao(df):
    """
    Detecta automaticamente o tipo de declaração fiscal com base nas colunas.
    """
    cols = [str(c).lower() for c in df.columns]
    
    melhor_tipo = "GENERICO"
    maior_score = 0
    
    for tipo, keywords in TIPOS_DECLARACAO.items():
        score = sum(1 for k in keywords if any(k in col for col in cols))
        
        if score > maior_score:
            maior_score = score
            melhor_tipo = tipo
            
    # Critério de confiança mínima
    if maior_score < 2:
        return "GENERICO"
        
    return melhor_tipo
