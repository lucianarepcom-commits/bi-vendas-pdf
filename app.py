import streamlit as st
import pdfplumber
import pandas as pd
import re

st.set_page_config(page_title="BI de Vendas", layout="wide")

st.title("📊 BI de Vendas - Importação de PDFs")

st.write("Faça upload dos PDFs de vendas. PDFs com ORÇAMENTO ou BONIFICAÇÃO serão ignorados.")

uploaded_files = st.file_uploader(
    "Selecione os arquivos PDF",
    type="pdf",
    accept_multiple_files=True
)

palavras_proibidas = ["ORÇAMENTO", "ORCAMENTO", "BONIFICAÇÃO", "BONIFICACAO"]

dados_vendas = []

def extrair_cliente(texto):
    linhas = texto.split("\n")
    for linha in linhas:
        if "CLIENTE" in linha.upper():
            return linha.strip()
    return "Cliente não identificado"

def extrair_itens(texto):
    itens = []
    linhas = texto.split("\n")

    for linha in linhas:
        # Exemplo simples: PRODUTO  10  25,90
        numeros = re.findall(r"\d+,\d{2}", linha)
        if numeros:
            partes = linha.split()
            if len(partes) >= 3:
                produto = " ".join(partes[:-2])
                quantidade = partes[-2]
                valor = partes[-1]
                itens.append({
                    "Produto": produto,
                    "Quantidade": quantidade,
                    "Valor Unitário": valor
                })
    return itens

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

        cliente = extrair_cliente(texto)
        itens = extrair_itens(texto)

        for item in itens:
            dados_vendas.append({
                "Arquivo": file.name,
                "Cliente": cliente,
                "Produto": item["Produto"],
                "Quantidade": item["Quantidade"],
                "Valor Unitário": item["Valor Unitário"]
            })

    if dados_vendas:
        df = pd.DataFrame(dados_vendas)

        st.success("✅ Dados extraídos com sucesso!")
        st.dataframe(df)
