import streamlit as st
import os
import sqlite3
import pandas as pd
from processar_pdf import processar_pdf

# ================= CONFIGURAÇÃO DA PÁGINA =================
st.set_page_config(
    page_title="BI de Vendas",
    layout="wide"
)

# ================= BANCO DE DADOS =================
def inicializar_banco():
    conn = sqlite3.connect("bi_vendas.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS representante (
        codigo TEXT PRIMARY KEY,
        nome TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        codigo_cliente TEXT PRIMARY KEY,
        nome_cliente TEXT,
        perfil TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pedidos (
        id_pedido INTEGER PRIMARY KEY AUTOINCREMENT,



