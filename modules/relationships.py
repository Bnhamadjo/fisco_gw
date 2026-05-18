def relacoes(df):
    if "valor" not in df.columns or "fornecedor" not in df.columns or "cliente" not in df.columns:
        return df
        
    rel = df.groupby(["fornecedor", "cliente"]).agg({
        "valor": ["sum", "count"]
    }).reset_index()
    
    rel.columns = ["fornecedor", "cliente", "volume_total", "num_transacoes"]
    return rel
