import streamlit as st
import pdfplumber
import pandas as pd
import re
from datetime import datetime

# ===============================
# CONFIGURAÇÃO DA PÁGINA
# ===============================
st.set_page_config(
    page_title="BI de Vendas - TAF Distribuidora",
    layout="wide"
)

# ===============================
# ESTADO DA APLICAÇÃO
# ===============================
if "texto_pdf" not in st.session_state:
    st.session_state.texto_pdf = None

if "dados_processados" not in st.session_state:
    st.session_state.dados_processados = None

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

if pdf_file and st.session_state.texto_pdf is None:
    texto = ""

    with pdfplumber.open(pdf_file) as pdf:
        for pagina in pdf.pages:
            if pagina.extract_text():
                texto += pagina.extract_text() + "\n"

    st.session_state.texto_pdf = texto
    st.success("PDF carregado e armazenado com sucesso")

# ===============================
# PROCESSAMENTO
# ===============================
if st.session_state.texto_pdf and st.session_state.dados_processados is None:
    texto = st.session_state.texto_pdf
    linhas = texto.split("\n")

    # 🔹 Pedido
    numero_pedido = ""
    for linha in linhas:
        match = re.search(r"(\d{8,})\s+\d+\s-\s", linha)
        if match:
            numero_pedido = match.group(1)
            break

    # 🔹 Data
    data_match = re.search(r"(\d{1,2}\s+de\s+\w+\s+de\s+\d{4})", texto)
    data_pedido = data_match.group(1) if data_match else datetime.now().strftime("%d/%m/%Y")

    # 🔹 Cliente
    codigo_cliente = ""
    nome_cliente = ""

    for linha in linhas:
        if re.match(r"\d+\s-\s[A-Z]", linha):
            partes = linha.split(" - ", 1)
            codigo_cliente = partes[0].strip()
            nome_cliente = partes[1].strip()
            break

    # 🔹 Produtos
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

    st.session_state.dados_processados = {
        "pedido": numero_pedido,
        "data": data_pedido,
        "codigo_cliente": codigo_cliente,
        "nome_cliente": nome_cliente,
        "produtos": produtos
    }

# ===============================
# EXIBIÇÃO
# ===============================
if st.session_state.dados_processados:
    dados = st.session_state.dados_processados

    st.markdown("### 📄 Dados do Pedido")
    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Pedido", dados["pedido"] or "Não identificado")
    col2.metric("Data", dados["data"])
    col3.metric("Código Cliente", dados["codigo_cliente"])
    col4.metric("Cliente", dados["nome_cliente"])

    if dados["produtos"]:
        df = pd.DataFrame(dados["produtos"])

        st.markdown("### 🛒 Itens do Pedido")
        st.dataframe(df, use_container_width=True)

        st.markdown("### 💰 Resumo")
        st.metric(
            "Total do Pedido (R$)",
            f"{df['Valor Total'].sum():,.2f}"
        )
    else:
        st.warning("Nenhum produto identificado.")
