import streamlit as st

st.set_page_config(page_title="BI de Vendas - PDF", layout="wide")

st.title("📊 BI de Vendas (PDF)")
st.write("Passo 2: Upload de PDF")

pdf_file = st.file_uploader(
    "Selecione um PDF de venda",
    type=["pdf"]
)

if pdf_file:
    st.success(f"Arquivo '{pdf_file.name}' carregado com sucesso!")

