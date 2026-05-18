import networkx as nx

def criar_grafo(df):

    if "cliente" not in df.columns or "fornecedor" not in df.columns:
        return None

    G = nx.Graph()

    for _, row in df.iterrows():
        fornecedor = str(row["fornecedor"])
        cliente = str(row["cliente"])

        if fornecedor and cliente and fornecedor != "nan" and cliente != "nan":
            G.add_edge(fornecedor, cliente)

    return G

def detetar_fraude_carrossel(df):
    """
    Ciber-Forense: Constrói um grafo direcionado e pesquisa por ciclos fechados
    (Ex: A -> B -> C -> A), que é a assinatura clássica da Fraude Carrossel do IVA.
    """
    if "cliente" not in df.columns or "fornecedor" not in df.columns:
        return []

    # Criar um Grafo Direcionado (DiGraph) porque a direção do dinheiro importa
    DG = nx.DiGraph()

    for _, row in df.iterrows():
        fornecedor = str(row.get("fornecedor", "")).strip()
        cliente = str(row.get("cliente", "")).strip()

        if fornecedor and cliente and fornecedor != "nan" and cliente != "nan":
            # Adicionar peso (valor) se existir para uso futuro, mas a aresta é o mais importante
            DG.add_edge(fornecedor, cliente)

    # Detetar ciclos simples no grafo
    ciclos = list(nx.simple_cycles(DG))
    
    # Filtrar ciclos significativos (ignoramos ciclos de 2 entidades pois é apenas compra/venda mútua, 
    # queremos focar em ciclos estruturados de 3 ou mais entidades, ex: A->B->C->A)
    ciclos_carrossel = [c for c in ciclos if len(c) >= 3]
    
    return ciclos_carrossel