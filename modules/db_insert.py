import pandas as pd
from modules.db import engine

def inserir_contribuintes(entidades):

    dados = entidades.get("contribuintes", [])

    if not dados:
        return

    df = pd.DataFrame({"razao_social": dados})

    if engine is None:
        return

    df.to_sql(
        "contribuinte",
        engine,
        if_exists="append",
        index=False
    )