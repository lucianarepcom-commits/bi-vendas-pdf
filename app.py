import streamlit as st
import os
import sqlite3
import pandas as pd
from processar_pdf import processar_pdf

st.set_page_config(
    page_title="BI de Vendas",
    layout="wide"
)

# ================== TOPO ==================
conn = sqlite3.connect("bi_vendas.db")
cursor = conn.cursor()

cursor.execute("SELECT nome FROM representante LIMIT 1")
rep = cursor.fetchone()
representante_nome = rep[0] if rep else "Representante não identificado"

st.markdown(
    f"""
    <div style='background-color:#f0f2f6;padding:15px;border-radius:10px'>
        <h3>👤 Representante: {representante_nome}</h3>
    </div>
    """,
    unsafe_allow_html=True
)

st.title("📊 BI de Vendas")

st.write("Importe os PDFs de venda. O sistema ignora pedidos duplicados automaticamente.")

# ================== UPLOAD ==================
os.makedirs("pdfs", exist_ok=True)

uploaded_files = st.file_uploader(
    "Selecionar arquivos PDF",
    type="pdf",
    accept_multiple_files=True
)

if uploaded_files:
    for file in uploaded_files:
        caminho = f"pdfs/{file.name}"
        with open(caminho, "wb") as f:
            f.write(file.read())

        resultado = processar_pdf(caminho)

        if "já importado" in resultado:
            st.warning(resultado)
        elif "ignorado" in resultado:
            st.info(resultado)
        elif "sucesso" in resultado:
            st.success(resultado)
        else:
            st.error(resultado)

# ================== DASHBOARD ==================
st.divider()
st.subheader("📈 Histórico de Vendas")

df = pd.read_sql("""
SELECT
    p.numero_pedido AS Pedido,
    p.data AS Data,
    c.nome_cliente AS Cliente,
    i.codigo_produto AS Cod_Produto,
    i.nome_produto AS Produto,
    i.quantidade AS Quantidade,
    i.valor_unit AS Valor_Unitário,
    i.valor_total AS Valor_Total
FROM itens_pedido i
JOIN pedidos p ON i.id_pedido = p.id_pedido
JOIN clientes c ON p.codigo_cliente = c.codigo_cliente
ORDER BY p.data DESC
""", conn)

conn.close()

if df.empty:
    st.info("Nenhum dado disponível. Faça upload de PDFs para começar.")
else:
    # ===== FILTROS =====
    col1, col2, col3 = st.columns(3)

    clientes = ["Todos"] + sorted(df["Cliente"].unique())
    cliente_sel = col1.selectbox("Cliente", clientes)

    datas = ["Todas"] + sorted(df["Data"].unique(), reverse=True)
    data_sel = col2.selectbox("Data", datas)

    produtos = ["Todos"] + sorted(df["Produto"].unique())
    produto_sel = col3.selectbox("Produto", produtos)

    df_filtrado = df.copy()

    if cliente_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Cliente"] == cliente_sel]

    if data_sel != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Data"] == data_sel]

    if produto_sel != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Produto"] == produto_sel]

    # ===== KPIs =====
    k1, k2, k3 = st.columns(3)
    k1.metric("Pedidos", df_filtrado_


