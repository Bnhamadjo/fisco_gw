import pandas as pd
from modules.db import engine

def listar_contribuintes():
    if engine is None:
        return pd.DataFrame()
        
    query = "SELECT * FROM contribuinte"
    try:
        return pd.read_sql(query, engine)
    except Exception:
        return pd.DataFrame()