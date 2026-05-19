import unicodedata
import re
import difflib

def normalize_columns(df):
    """
    Normaliza os nomes das colunas de forma inteligente usando busca por similaridade
    e mapeamento de palavras-chave com sistema de pontuação avançado.
    """
    
    def clean_str(s):
        if not isinstance(s, str):
            return str(s)
        s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
        s = s.lower().strip()
        s = re.sub(r'[^a-z0-9\s]', ' ', s)
        return ' '.join(s.split())

    original_cols = list(df.columns)
    normalized_cols = [clean_str(col) for col in original_cols]
    
    # 2. Definição de Alvos e Palavras-Chave (Prioridade: NIFs e Valores primeiro)
    target_mapping = {
        "nif_cliente": ["nif do declarante", "nif cliente", "nif do cliente", "nif comprador", "nif", "01.nif", "01 nif"],
        "nif_fornecedor": ["nif do fornecedor", "nif fornecedor", "nif prestador", "3.1 nif do fornecedor", "3 1 nif do fornecedor"],
        "iva_suportado": ["iva suportado", "iva dedutivel", "iva debito", "3.7 iva suportado", "4.7 iva suportado", "5.7 iva suportado", "iva suportado e retido"],
        "iva_liquidado": ["iva liquidado", "iva credito"],
        "iva_retido": ["iva retido"],
        "data": ["data da fatura", "data da factura", "data de emissao", "data emissao", "data"],
        "fatura": ["numero de fatura", "numero fatura", "fatura numero", "fatura n", "doc n", "fatura"],
        "valor": ["base tributavel", "valor total", "total base", "valor sem iva", "montante liquido", "valor", "valor da fatura"],
        "cliente": ["nome do declarante", "nome cliente", "cliente name", "cliente", "comprador", "entidade"],
        "fornecedor": ["nome do fornecedor", "nome fornecedor", "fornecedor name", "fornecedor", "prestador"],
    }

    final_mapping = {}
    used_indices = set()

    # 3. Lógica de Mapeamento com Pontuação e Bloqueio de Conflitos
    for internal_name, keywords in target_mapping.items():
        best_idx = -1
        max_score = 0
        
        for idx, col in enumerate(normalized_cols):
            if idx in used_indices: continue
            
            for kw in keywords:
                clean_kw = clean_str(kw)
                
                # Penalizar se a coluna contém "nif" mas estamos buscando "cliente" (nome)
                is_nif_col = "nif" in col
                is_searching_name = internal_name in ["cliente", "fornecedor"]
                
                # Pontuação Base
                if col == clean_kw:
                    score = 100
                elif clean_kw in col:
                    score = 85 + (len(clean_kw) / len(col)) * 10
                else:
                    similarity = difflib.SequenceMatcher(None, clean_kw, col).ratio()
                    score = similarity * 80
                
                # Ajustes de contexto
                if is_searching_name and is_nif_col:
                    score -= 40 # Forte penalização para não confundir NIF com Nome
                
                # Bônus por posição (colunas iniciais costumam ser mais importantes)
                score += (1 - (idx / len(normalized_cols))) * 5

                if score > max_score and score > 70:
                    max_score = score
                    best_idx = idx

        if best_idx != -1:
            final_mapping[original_cols[best_idx]] = internal_name
            used_indices.add(best_idx)

    # 4. Aplicar o Renomeamento
    df = df.rename(columns=final_mapping)
    
    # 5. Normalizar o restante
    remaining_cols = {}
    for idx, col in enumerate(original_cols):
        if idx not in used_indices:
            remaining_cols[col] = normalized_cols[idx]
    
    df = df.rename(columns=remaining_cols)

    # 6. DEDUPLICAÇÃO DE COLUNAS (Evitar crash no Streamlit/Arrow)
    cols = list(df.columns)
    new_cols = []
    seen = {}
    for col in cols:
        if col in seen:
            seen[col] += 1
            new_cols.append(f"{col}_{seen[col]}")
        else:
            seen[col] = 0
            new_cols.append(col)
    df.columns = new_cols

    # 7. FORMATAÇÃO DE NIFs (Remover espaços, vírgulas e garantir formato numérico limpo)
    for col in df.columns:
        if 'nif' in col.lower():
            # Converter para string, remover .0 (se veio de float), remover espaços e vírgulas
            df[col] = df[col].astype(str).str.replace(r'\.0$', '', regex=True)
            df[col] = df[col].str.replace(r'[\s,\.]', '', regex=True)
            # Garantir que se for 'nan' ou vazio fique limpo
            df[col] = df[col].apply(lambda x: "" if isinstance(x, str) and x.lower() == 'nan' else x)

    # 8. PREVENÇÃO DE ERROS DO PYARROW (Garantir que colunas com texto sejam string pura e não tipo misto object)
    for col in df.columns:
        if df[col].dtype == 'object':
            # Se a coluna contém strings, converte para string pura para o Arrow não engasgar
            has_str = df[col].apply(lambda x: isinstance(x, str)).any()
            if has_str:
                df[col] = df[col].fillna('').astype(str).str.strip()

    return df

def clean_for_arrow(df):
    """
    Garante que o DataFrame seja totalmente Arrow-compatível e livre de conflitos de timezone/tipos.
    """
    import pandas as pd
    if df is None or df.empty:
        return df
        
    # 1. PREVENÇÃO DE ERROS DO PYARROW (Garantir que colunas com texto sejam string pura e não tipo misto object)
    for col in df.columns:
        if df[col].dtype == 'object':
            # Se a coluna contém strings, converte para string pura para o Arrow não engasgar
            has_str = df[col].apply(lambda x: isinstance(x, str)).any()
            if has_str:
                df[col] = df[col].fillna('').astype(str).str.strip()

    # 2. NORMALIZAÇÃO DE TIMEZONES (Evitar erros de comparação datetime64[us, UTC] com Timestamp)
    for col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[col]):
            if hasattr(df[col].dt, 'tz') and df[col].dt.tz is not None:
                df[col] = df[col].dt.tz_localize(None)

    return df
