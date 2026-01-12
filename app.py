import streamlit as st
import pdfplumber
import pandas as pd
import re

st.set_page_config(page_title="BI de Vendas", layout="wide")
st.title("📊 BI de Vendas - Importação de PDFs")

st.write("Importe PDFs de vendas. Arquivos com ORÇAMENTO ou BONIFICAÇÃO serão ignorados.")

uploaded_files = st.file_uploader(
    "Selecione os arquivos PDF",
    type="pdf",
    accept_multiple_files=True
)

palavras_proibidas = ["ORÇAMENTO", "ORCAMENTO", "BONIFICAÇÃO", "BONIFICACAO"]

linhas_bi = []

def identificar_cliente(texto):
    for linha in texto.split("\n"):
        if "CLIENTE" in linha.upper():
            return linha.replace("CLIENTE", "").strip()
    return "Cliente não identificado"

def extrair_itens_tabela(pdf):
    itens = []

    for page in pdf.pages:
        tabelas = page.extract_tables()

        for tabela in tabelas:
            for linha in tabela:
                if not linha or len(linha) < 4:
                    continue

                produto = linha[0]
                quantidade = linha[1]
                valor_unit = linha[2]
                valor_final = linha[3]

                if produto and re.search(r"\d", str(quantidade)):
                    itens.append({
                        "Produto": produto.strip(),
                        "Quantidade": quantidade,
                        "Valor Unitário": valor_unit,
                        "Valor Final": valor_final
                    })

    return itens

if uploaded_files:
    for file in uploaded_files:
        with pdfplumber.open(file) as pdf:
            texto_completo = ""
            for page in pdf.pages:
                texto_completo += page.extract_text() or ""

        texto_maiusculo = texto_completo.upper()

        if any(p in texto_maiusculo for p in palavras_proibidas):
            st.warning(f"⛔ {file.name} ignorado (Orçamento/Bonificação)")
            continue

        cliente = identificar_cliente(texto_completo)

        with pdfplumber.open(file) as pdf:
            itens = extrair_itens_tabela(pdf)

        if not itens:
            st.warning(f"⚠️ Nenhum item identificado em {file.name}")
            continue

        total_cliente = 0

        for item in itens:
            try:
                valor_final = float(str(item["Valor Final"]).replace(".", "").replace(",", "."))
            except:
                valor_final = 0

            total_cliente += valor_final

            linhas_bi.append({
                "Cliente": cliente,
                "Produto": item["Produto"],
                "Quantidade": item["Quantidade"],
                "Valor Unitário": item["Valor Unitário"],
                "Valor Final": valor_final,
                "Total Cliente": total_cliente
            })

    if linhas_bi:
        d
