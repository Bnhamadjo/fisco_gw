from sqlalchemy import create_engine, text
import streamlit as st
import os
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Usar variáveis de ambiente com fallback
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:123456@localhost:5432/fiscal_db"
)

def get_engine():
    """
    Cria engine SQLAlchemy com fallback para SQLite se PostgreSQL falhar.
    """
    try:
        # Tentar PostgreSQL primeiro
        engine = create_engine(DATABASE_URL, echo=False)
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✓ PostgreSQL conectado com sucesso")
        return engine
    except Exception as e:
        logger.warning(f"PostgreSQL falhou: {e}")
        logger.info("Usando SQLite como fallback...")
        
        # Fallback para SQLite
        try:
            sqlite_url = "sqlite:///fiscal_db.db"
            engine = create_engine(sqlite_url, echo=False)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("✓ SQLite (fallback) conectado com sucesso")
            return engine
        except Exception as e_sqlite:
            logger.error(f"Falha em ambas conexões: {e_sqlite}")
            return None

engine = get_engine()

if engine is None:
    # Mostrar aviso no Streamlit se estiver no contexto do app
    try:
        st.sidebar.error("⚠️ Falha na ligação ao PostgreSQL e SQLite. O sistema MER funcionará apenas em memória.")
    except:
        logger.error("Sistema rodando em memória (sem base de dados)")