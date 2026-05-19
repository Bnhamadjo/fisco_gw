import pandas as pd
import io
import streamlit as st

def exportar_csv(df):
    """Retorna o CSV como bytes"""
    return df.to_csv(index=False).encode('utf-8')

def exportar_excel(df):
    """Retorna o Excel como bytes"""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Relatorio')
    return output.getvalue()

def exportar_pdf(df, titulo="Relatório Fiscal DGCI"):
    """
    Gera um PDF profissional da tabela em modo paisagem.
    """
    try:
        from fpdf import FPDF
        
        class PDF(FPDF):
            def header(self):
                # Logo fictício ou Texto de Cabeçalho
                self.set_font('Helvetica', 'B', 16)
                self.set_text_color(102, 126, 234) # Cor azulada premium
                self.cell(0, 10, "FISCO_GW - INTELIGÊNCIA FISCAL", 0, 1, 'L')
                
                self.set_font('Helvetica', 'B', 12)
                self.set_text_color(100, 100, 100)
                self.cell(0, 10, titulo, 0, 1, 'L')
                
                self.set_draw_color(200, 200, 200)
                self.line(10, 32, 287, 32) # Linha horizontal (Landscape A4 tem ~297mm)
                self.ln(10)

            def footer(self):
                self.set_y(-15)
                self.set_font('Helvetica', 'I', 8)
                self.set_text_color(150, 150, 150)
                self.cell(0, 10, f'Relatório Automático FISCO_GW | Página {self.page_no()}', 0, 0, 'C')

        # Usar LANDSCAPE (L) para caber mais dados
        pdf = PDF(orientation='L', unit='mm', format='A4')
        pdf.add_page()
        pdf.set_font("Helvetica", size=9)
        
        # Selecionar colunas relevantes e limitar para evitar overflow mesmo em landscape
        cols = df.columns.tolist()[:10]
        
        # Calcular larguras proporcionais (NIF e Valor costumam ser menores, Nome maior)
        total_w = 277 # Largura útil em Landscape A4 (297 - 20)
        col_widths = []
        for col in cols:
            c_low = col.lower()
            if 'cliente' in c_low or 'fornecedor' in c_low:
                col_widths.append(total_w * 0.25) # 25% para nomes
            elif 'nif' in c_low or 'data' in c_low:
                col_widths.append(total_w * 0.12) # 12% para IDs/Datas
            else:
                col_widths.append(total_w * 0.08) # Resto
        
        # Ajustar para que a soma seja exatamente total_w
        scale = total_w / sum(col_widths)
        col_widths = [w * scale for w in col_widths]

        # Cabeçalho da Tabela
        pdf.set_fill_color(240, 242, 246)
        pdf.set_text_color(50, 50, 50)
        pdf.set_font('Helvetica', 'B', 9)
        
        for i, col in enumerate(cols):
            pdf.cell(col_widths[i], 10, str(col).upper(), border=1, fill=True, align='C')
        pdf.ln()
        
        # Dados da Tabela
        pdf.set_font('Helvetica', '', 8)
        pdf.set_text_color(80, 80, 80)
        
        # Alternar cores de linha (Zebra style)
        fill = False
        for _, row in df.head(150).iterrows():
            pdf.set_fill_color(250, 250, 250)
            
            # Verificar se cabe na página atual, se não, adiciona página
            if pdf.get_y() > 180:
                pdf.add_page()
                # Repetir cabeçalho
                pdf.set_font('Helvetica', 'B', 9)
                for i, col in enumerate(cols):
                    pdf.cell(col_widths[i], 10, str(col).upper(), border=1, fill=True, align='C')
                pdf.ln()
                pdf.set_font('Helvetica', '', 8)

            for i, col in enumerate(cols):
                val = str(row[col])
                # Truncar texto para não transbordar a célula
                if len(val) > 30: val = val[:27] + "..."
                pdf.cell(col_widths[i], 8, val, border=1, fill=fill)
            
            pdf.ln()
            fill = not fill # Alternar cor da próxima linha
            
        return bytes(pdf.output())
    except Exception as e:
        st.error(f"Erro no PDF: {str(e)}")
        return None

def download_buttons(df, filename="relatorio", key_prefix=""):
    """Cria botões de download para CSV e Excel (PDF se possível)"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="📥 Baixar CSV",
            data=exportar_csv(df),
            file_name=f"{filename}.csv",
            mime='text/csv',
            width='stretch',
            key=f"{key_prefix}_csv"
        )
        
    with col2:
        try:
            excel_data = exportar_excel(df)
            st.download_button(
                label="📥 Baixar Excel",
                data=excel_data,
                file_name=f"{filename}.xlsx",
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                width='stretch',
                key=f"{key_prefix}_excel"
            )
        except Exception as e:
            st.error("Instale 'xlsxwriter' para exportar Excel.")

    # PDF é opcional e pesado, mostrar apenas se o usuário pedir ou em expander
    with st.expander("📄 Exportar como PDF"):
        st.info("O PDF será gerado com as primeiras 8 colunas e 100 linhas para garantir legibilidade.")
        if st.button("Gerar PDF", key=f"{key_prefix}_pdf_gen"):
            pdf_data = exportar_pdf(df, titulo=f"Relatório: {filename}")
            if pdf_data:
                st.download_button(
                    label="📥 Baixar PDF",
                    data=pdf_data,
                    file_name=f"{filename}.pdf",
                    mime='application/pdf',
                    width='stretch',
                    key=f"{key_prefix}_pdf_down"
                )
            else:
                st.warning("Biblioteca 'fpdf' não encontrada. Instale-a com 'pip install fpdf2'.")
