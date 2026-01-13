import streamlit as st
import pdfplumber
import pandas as pd
import re

st.set_page_config(
    page_title="BI de Vendas - TAF Distribuidora",
    layout="wide"
)

# ===============================
# BARRA SUPERIOR
# ===============================
st.markdown("""
<style>
.header {
    background-color: #0E2A47;
    padding: 15px;
    border-radius: 8px;
    color: white;
    margin-bottom: 20px;
}
.header-title {
    font-size: 26px;
    font-weight: bold;
}
.header-subtitle {
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header">
    <div class="header-title">📊 BI de Vendas</div>
    <div class="header-subtitle">
        🏢 <b>Distribuidora:</b> TAF Distribuidora de Alimentos e Bebidas<br>
        👤 <b>Representante:</b> Elu Representações
    </div>
</div>
""", unsafe_allow_html=True)

# ===============================
# UPLOAD
# ===============================
st.subheader("📥 Importar PDF de Venda")

pdf_file = st.file_uploader("Selecione um PDF de venda", type=["pdf"])

if pdf_file:
    texto = ""

    with pdfplumber.open(pdf_file) as pdf:
        for pagina in pdf.pages:
            if pagina.extract_text():
                texto += pagina.extract_text() + "\n"

    st.success("PDF lido com sucesso")

    # ===============================
    # MOSTRAR TEXTO (DIAGNÓSTICO)
    # ===============================
    st.subheader("🔍 Texto extraído do PDF (diagnóstico)")
    st.text(texto[:5000])  # mostra bastante texto

