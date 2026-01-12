import streamlit as st
import pdfplumber
import pandas as pd

st.set_page_config(page_title="BI de Vendas", layout="wide")

st.title("📊 BI de Vendas - Importação de PDFs")

st.write("Faça upload dos PDFs de vendas. PDFs com ORÇAMENTO ou BONIFICAÇÃO serão ignorados.")

uploaded_files = st.file_uploader(
    "Selecione os arquivos PDF",
    type="pdf",
    accept_multiple_files=True
)

palavras_proibidas = ["ORÇAMENTO", "ORCAMENTO", "BONIFICAÇÃO", "BONIFICACAO"]

dados = []

if uploaded_files:
    for file in uploaded_files:
        with pdfplumber.open(file) as pdf:
            texto = ""
            for page in pdf.pages:
                texto += page.extract_text() or ""

        texto_maiusculo = texto.upper()

        if any(p in texto_maiusculo for p in palavras_proibidas):
            st.warning(f"⛔ {file.name} ignorado (Orçamento/Bonificação)")
            continue

        dados.append({
            "Arquivo": file.name,
            "Texto (prévia)": texto[:300]
        })

    if dados:
        df = pd.DataFrame(dados)

        st.success("✅ PDFs válidos importados com sucesso!")
        st.dataframe(df)
