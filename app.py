import streamlit as st
import pdfplumber
import pandas as pd
import re

# ===============================
# CONFIGURAÇÃO DA PÁGINA
# ===============================
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
pdf_file = st.file_uploader("Selecione um PDF", type=["pdf"])

if pdf_file:
    texto = ""

    with pdfplumber.open(pdf_file) as pdf:
        for pagina in pdf.pages:
            if pagina.extract_text():
                texto += pagina.extract_text() + "\n"

    linhas = texto.split("\n")

    # ===============================
    # PEDIDO
    # ===============================
    numero_pedido = ""
    for linha in linhas:
        if linha.strip().isdigit() and len(linha.strip()) >= 8:
            numero_pedido = linha.strip()
            break

    # ===============================
    # CLIENTE
    # ===============================
    codigo_cliente = ""
    nome_cliente = ""

    for linha in linhas:
        if re.match(r"\d+\s-\s[A-Z]", linha):
            partes = linha.split(" - ", 1)
            codigo_cliente = partes[0].strip()
            nome_cliente = partes[1].strip()
            break

    # ===============================
    # PRODUTOS
    # ===============================
    produtos = []

    for linha in linhas:
        if re.match(r"\d+\s-\s", linha):
            partes = linha.split()
            try:
                codigo = partes[0]
                nome = " ".join(partes[2:-8])
                quantidade = int(partes[-7])
                valor_unit = float(partes[-6].replace(",", "."))
                valor_total = float(partes[-1].replace(",", "."))

                produtos.append({
                    "Código Produto": codigo,
                    "Produto": nome,
                    "Quantidade": quantidade,
                    "Valor Unitário (R$)": valor_unit,
                    "Valor Total (R$)": valor_total
                })
            except:
                pass

    # ===============================
    # EXIBIÇÃO
    # ===============================
    st.markdown("### 📄 Dados do Pedido")

    col1, col2, col3 = st.columns(3)
    col1.metric("Pedido", numero_pedido or "Não identificado")
    col2.metric("Código do Cliente", codigo_cliente)
    col3.metric("Cliente", nome_cliente)

    if produtos:
        df = pd.DataFrame(produtos)
        st.markdown("### 🛒 Itens do Pedido")
        st.dataframe(df, use_container_width=True)

        st.markdown("### 💰 Resumo")
        st.metric("Total do Pedido (R$)", f"{df['Valor Total (R$)'].sum():,.2f}")
    else:
        st.warning("Nenhum produto identificado.")

