import streamlit as st
import os
import sqlite3
import pandas as pd
from processar_pdf import processar_pdf

# ================= CONFIGURAÇÃO =================
st.set_page_config(page_title="BI de Vendas", layout="wide")

# ================= BANCO =================
def inicializar_banco():
    conn = sqlite3.connect("bi_vendas.db")
    cursor = conn.cursor()

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS representante ("
        "codigo TEXT PRIMARY KEY, "
        "nome TEXT)"
    )

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS clientes ("
        "codigo_cliente TEXT PRIMARY KEY, "
        "nome_cliente TEXT, "
        "perfil TEXT)"
    )

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS pedidos ("
        "id_pedido INTEGER PRIMARY KEY AUTOINCREMENT, "
        "numero_pedido TEXT UNIQUE, "
        "codigo_cliente TEXT, "
        "data TEXT, "
        "valor_total REAL)"
    )

    cursor.execute(
        "CREATE TABLE IF NOT EXISTS itens_pedido ("
        "id_pedido INTEGER, "
        "codigo_produto TEXT, "
        "nome_produto TEXT, "
        "quantidade INTEGER, "
        "valor_unit REAL, "
        "valor_total REAL)"
    )

    conn.commit()
    conn.close()

inicializar_banco()

# ================= REPRESENTANTE =================
conn = sqlite3.connect("bi_vendas.db")
cursor = conn.cursor()

try:
    cursor.execute("SELECT nome FROM representante LIMIT 1")
    rep = cursor.fetchone()
    representante_nome = rep[0] if rep else "Representante não identificado"
except:
    representante_nome = "Representante não identificado"

st.markdown(
    "<div style='background-color:#f5f7fa;padding:15px;border-radius:10px;margin-bottom:20px'>"
    "<h3>👤 Representante: " + representante_nome + "</h3>"
    "</div>",
    unsafe_allow_html=True
)

st.title("📊 BI de Vendas")
st.write("Importe PDFs de venda. Pedidos duplicados são ignorados automaticamente.")

# ================= UPLOAD =================
os.makedirs("pdfs", exist_ok=True)

uploaded_files = st.file_uploader(
    "Selecionar arquivos PDF",
    type="pdf",
    accept_multiple_files=True
)

if uploaded_files:
    for file in uploaded_files:
        caminho = "pdfs/" + file.name

        with open(caminho, "wb") as f:
            f.write(file.read())

        try:
            resultado = processar_pdf(caminho)

            if resultado is None:
                st.warning(file.name + ": PDF ignorado")
            elif "já importado" in resultado.lower():
                st.warning(resultado)
            elif "sucesso" in resultado.lower():
                st.success(resultado)
            else:
                st.info(resultado)

        except Exception as e:
            st.error("Erro ao processar " + file.name + ": " + str(e))

# ================= DASHBOARD =================
st.divider()
st.subheader("📈 Histórico de Vendas")

conn = sqlite3.connect("bi_vendas.db")

try:
    df = pd.read_sql(
        "SELECT "
        "p.numero_pedido AS Pedido, "
        "p.data AS Data, "
        "c.nome_cliente AS Cliente, "
        "i.codigo_produto AS Cod_Produto, "
        "i.nome_produto AS Produto, "
        "i.quantidade AS Quantidade, "
        "i.valor_unit AS Valor_Unitario, "
        "i.valor_total AS Valor_Total "
        "FROM itens_pedido i "
        "JOIN pedidos p ON i.id_pedido = p.id_pedido "
        "JOIN clientes c ON p.codigo_cliente = c.codigo_cliente "
        "ORDER BY p.data DESC",
        conn
    )
except:
    df = pd.DataFrame()

conn.close()

if df.empty:
    st.info("Nenhum dado disponível ainda. Faça upload de PDFs para iniciar.")
else:
    col1, col2, col3 = st.columns(3)

    cliente_sel = col1.selectbox("Cliente", ["Todos"] + sorted(df["Cliente"].unique()))
    data_sel = col2.selectbox("Data", ["Todas"] + sorted(df["Data"].unique(), reverse=True))
    produto_sel = col3.selectbox("Produto", ["Todos"] + sorted(df["Produto"].unique()))

    df_filtro = df.copy()

    if cliente_sel != "Todos":
        df_filtro = df_filtro[df_filtro["Cliente"] == cliente_sel]

    if data_sel != "Todas":
        df_filtro = df_filtro[df_filtro["Data"] == data_sel]

    if produto_sel != "Todos":
        df_filtro = df_filtro[df_filtro["Produto"] == produto_sel]

    k1, k2, k3 = st.columns(3)
    k1.metric("Pedidos", df_filtro["Pedido"].nunique())
    k2.metric("Clientes", df_filtro["Cliente"].nunique())
    k3.metric("Faturamento", "R$ {:,.2f}".format(df_filtro["Valor_Total"].sum()))

    st.subheader("📋 Detalhamento das Vendas")
    st.dataframe(df_filtro, use_container_width=True)

    st.subheader("🏆 Top 10 Produtos")
    st.bar_chart(
        df_filtro.groupby("Produto")["Quantidade"].sum().sort_values(ascending=False).head(10)
    )

    st.subheader("🏆 Top Clientes por Faturamento")
    st.bar_chart(
        df_filtro.groupby("Cliente")["Valor_Total"].sum().sort_values(ascending=False).head(10)
    )



