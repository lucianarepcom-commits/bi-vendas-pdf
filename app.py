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

def extrair_itens_por_texto(texto):
    itens = []

    linhas = texto.split("\n")

    for linha in linhas:
        # Exemplo esperado:
        # ARROZ TIPO 1  10  25,90  259,00
        padrao = re.search(r"(.+?)\s+(\d+)\s+(\d+,\d{2})\s+(\d+,\d{2})", linha)

        if padrao:
            produto = padrao.group(1).strip()
            quantidade = padrao.group(2)
            valor_unit = padrao.group(3)
            valor_final = padrao.group(4)

            itens.append({
                "Produto": produto,
                "Quantidade": quantidade,
                "Valor Unitário": valor_unit,
                "Valor Final": valor_final
            })

    return itens

def extrair_itens(pdf, texto):
    itens = []

    # 1️⃣ tenta como tabela
    for page in pdf.pages:
        tabelas = page.extract_tables()
        for tabela in tabelas:
            for linha in tabela:
                if linha and len(linha) >= 4:
                    produto, quantidade, valor_unit, valor_final = linha[:4]
                    if produto and quantidade and valor_final:
                        itens.append({
                            "Produto": str(produto).strip(),
                            "Quantidade": quantidade,
                            "Valor Unitário": valor_unit,
                            "Valor Final": valor_final
                        })

    # 2️⃣ se não encontrou nada, tenta por texto
    if not itens:
        itens = extrair_itens_por_texto(texto)

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
            itens = extrair_itens(pdf, texto_completo)

        if not itens:
            st.error(f"❌ Não foi possível identificar itens em {file.name}")
            continue

        total_cliente = 0

        for item in itens:
            try:
                valor_final = float(item["Valor Final"].replace(".", "").replace(",", "."))
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
        df = pd.DataFrame(linhas_bi)

        st.success("✅ Dados extraídos com sucesso!")
        st.dataframe(df, use_container_width=True)


        st.success("✅ Dados extraídos com sucesso!")

        st.subheader("📋 Detalhamento por Cliente e Produto")
        st.dataframe(df, use_container_width=True)
