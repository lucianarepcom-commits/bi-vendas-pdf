import streamlit as st
import pdfplumber

st.set_page_config(page_title="BI de Vendas - PDF", layout="wide")

st.title("📊 BI de Vendas (PDF)")
st.write("Passo 3: Leitura do conteúdo do PDF")

pdf_file = st.file_uploader(
    "Selecione um PDF de venda",
    type=["pdf"]
)

if pdf_file:
    texto_completo = ""

    with pdfplumber.open(pdf_file) as pdf:
        for pagina in pdf.pages:
            if pagina.extract_text():
                texto_completo += pagina.extract_text() + "\n"

    st.subheader("📄 Texto extraído do PDF")
    st.text(texto_completo[:4000])  # mostra só o começo
