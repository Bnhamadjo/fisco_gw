import pandas as pd
import streamlit as st
import pdfplumber
import io

@st.cache_data
def load_file(uploaded_file, sheet_name=0):
    """
    Carrega ficheiros CSV, Excel ou PDF e retorna um DataFrame.
    """
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xlsx') or uploaded_file.name.endswith('.xlsm'):
            df = pd.read_excel(uploaded_file, sheet_name=sheet_name)
        elif uploaded_file.name.endswith('.pdf'):
            df = extract_from_pdf(uploaded_file)
        else:
            st.error(f"Formato {uploaded_file.name} não suportado.")
            return None
        return df
    except Exception as e:
        st.error(f"Erro ao ler {uploaded_file.name}: {str(e)}")
        return None

def get_excel_sheets(uploaded_file):
    """
    Retorna a lista de nomes das folhas (sheets) de um ficheiro Excel.
    """
    if uploaded_file.name.endswith('.xlsx') or uploaded_file.name.endswith('.xlsm'):
        try:
            xl = pd.ExcelFile(uploaded_file)
            return xl.sheet_names
        except:
            return []
    return []

def extract_from_pdf(uploaded_file):
    """
    Tenta extrair tabelas de um ficheiro PDF.
    """
    with pdfplumber.open(uploaded_file) as pdf:
        all_data = []
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                all_data.extend(table)
        
        if not all_data:
            st.warning("⚠️ Nenhuma tabela detectada no PDF. Tentando extrair texto...")
            return pd.DataFrame()
            
        # Converter para DataFrame usando a primeira linha como cabeçalho
        df = pd.DataFrame(all_data[1:], columns=all_data[0])
        return df