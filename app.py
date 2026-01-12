import streamlit as st
import os
import sqlite3
from processar_pdf import processar_pdf
import pandas as pd

st.set_page_config(
    page_title="BI de Vendas",
    layout="wide"
)

st.title("📊 BI de Vendas - Importação de PDFs")

st.write("Faça upload dos PDFs de venda. Os dados serão salvos automaticamente no histórico.")

# Pasta temporária para salvar PDFs
os.makedirs("pdfs", exist_ok=True)

uploaded_files = st.file_uploader(
    "Selecione os arquivos PDF",
    type="pdf",
    accept_multiple_files=True
)

if uploaded_files:
    for file in uploaded_files:
        caminho = f"pdfs/{file.name}"
        with open(caminho, "wb") as f:
            f.write(file.read())

        processar_pdf(caminho)

    st.success("✅ PDFs processados e salvos com sucesso!")

# ===== DASHBOARD =====

st.divider()
st.subheader("📈 Histórico de Vendas")

conn = sqlite3.connect("bi_vendas.db")

df_itens = pd.read_sql("""
SELECT
    c.nome_cliente AS Cliente,
    i.codigo_produto AS Cod_Produto,
    i.nome_produto AS Produto,
    i.quantidade AS Quantidade,
    i.valor_unit AS Valor_Unit,
    i.valor_total AS Valor_Total,
    p.data AS Data_Pedido
FROM itens_pedido i
JOIN pedidos p ON i.id_pedido = p.id_pedido
JOIN clientes c ON p.codigo_cliente = c.codigo_cliente
""", conn)

conn.close()

if not df_itens.empty:
    col1, col2, col3 = st.columns(3)

    col1.metric("Clientes Ativos", df_itens["Cliente"].nunique())
    col2.metric("Produtos Vendidos", df_itens["Produto"].nunique())
    col3.metric("Faturamento Total", f"R$ {df_itens['Valor_Total'].sum():,.2f}")

    st.subheader("📋 Detalhamento das Vendas")
    st.dataframe(df_itens, use_container_width=True)

    st.subheader("🏆 Top 10 Produtos Mais Vendidos")
    top_prod = (
        df_itens.groupby("Produto")["Quantidade"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )
    st.bar_chart(top_prod)

    st.subheader("🏆 Top 10 Clientes por Faturamento")
    top_cli = (
        df_itens.groupby("Cliente")["Valor_Total"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
    )
    st.bar_chart(top_cli)

else:
    st.info("Nenhum dado ainda. Faça upload de PDFs para iniciar.")

