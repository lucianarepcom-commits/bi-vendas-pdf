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
import plotly.express as px

# lista de vendas já extraída pelo seu código
df = pd.DataFrame(dados_vendas)

if not df.empty:

    # ➤ KPIs no topo
    total_vendas = df["Valor Unitário"].apply(lambda x: float(x.replace(",", "."))).sum()
    total_clientes = df["Cliente"].nunique()
    total_itens = df["Produto"].count()

    st.metric("💰 Total vendido", f"R$ {total_vendas:,.2f}")
    st.metric("👥 Clientes únicos", total_clientes)
    st.metric("📦 Itens vendidos", total_itens)

    # ➤ Top 10 Clientes
    top_clientes = df.groupby("Cliente").size().sort_values(ascending=False).head(10).reset_index(name="Quantidade")
    fig1 = px.bar(top_clientes, x="Cliente", y="Quantidade", title="Top 10 Clientes que mais compram")
    st.plotly_chart(fig1)

    # ➤ Top 10 Produtos
    top_produtos = df.groupby("Produto").size().sort_values(ascending=False).head(10).reset_index(name="Quantidade")
    fig2 = px.bar(top_produtos, x="Produto", y="Quantidade", title="Top 10 Produtos mais vendidos")
    st.plotly_chart(fig2)

    # ➤ Vendas por período
    df["Data"] = pd.to_datetime(df["Data"])
    vendas_tempo = df.groupby(df["Data"].dt.to_period("M")).size().reset_index(name="Quantidade")
    vendas_tempo["Data"] = vendas_tempo["Data"].dt.to_timestamp()
    fig3 = px.line(vendas_tempo, x="Data", y="Quantidade", title="Vendas por mês")
    st.plotly_chart(fig3)
