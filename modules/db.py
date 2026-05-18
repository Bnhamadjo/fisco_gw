from sqlalchemy import create_engine
import streamlit as st

DATABASE_URL = "postgresql://postgres:123456@localhost:5432/fiscal_db"

def get_engine():
    try:
        engine = create_engine(DATABASE_URL)
        # Test connection
        with engine.connect() as conn:
            pass
        return engine
    except Exception as e:
        # Fallback ou log
        return None

engine = get_engine()

if engine is None:
    # Opcionalmente, mostrar um aviso no Streamlit se estiver no contexto do app
    try:
        st.sidebar.error("⚠️ Falha na ligação ao PostgreSQL. O sistema MER funcionará apenas em memória.")
    except:
        pass