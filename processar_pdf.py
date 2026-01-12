import pdfplumber
import sqlite3
import re
from datetime import datetime

# Conexão com banco (arquivo será criado automaticamente)
conn = sqlite3.connect("bi_vendas.db")
cursor = conn.cursor()

# Criar tabelas
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
    codigo_cliente TEXT,
    data TEXT,
    valor_total REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS itens_pedido (
    id_pedido INTEGER,
    codigo_produto TEXT,
    nome_produto TEXT,
    quantidade INTEGER,
    valor_unit REAL,
    valor_total REAL
)
""")

conn.commit()

def processar_pdf(caminho_pdf):
    with pdfplumber.open(caminho_pdf) as pdf:
        texto = ""
        for page in pdf.pages:
            texto += page.extract_text() + "\n"

    # CLIENTE
    cliente_match = re.search(r"(\d+)\s-\s(.+LTDA)", texto)
    if not cliente_match:
        print("Cliente não identificado")
        return

    codigo_cliente = cliente_match.group(1)
    nome_cliente = cliente_match.group(2)

    cursor.execute("""
    INSERT OR IGNORE INTO clientes VALUES (?, ?, ?)
    """, (codigo_cliente, nome_cliente, None))

    # TOTAL DO PEDIDO
    total_match = re.search(r"Total Pedido:\s([\d,]+)", texto)
    if not total_match:
        print("Total do pedido não encontrado")
        return

    valor_total_pedido = float(total_match.group(1).replace(",", "."))

    data_pedido = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
    INSERT INTO pedidos (codigo_cliente, data, valor_total)
    VALUES (?, ?, ?)
    """, (codigo_cliente, data_pedido, valor_total_pedido))

    id_pedido = cursor.lastrowid

    # PRODUTOS
    for linha in texto.split("\n"):
        prod = re.search(r"(\d+)\s-\s(.+?)\s", linha)
        if prod:
            codigo_produto = prod.group(1)
            nome_produto = prod.group(2)

            numeros = re.findall(r"([\d,]+)", linha)
            if len(numeros) >= 2:
                valor_unit = float(numeros[-2].replace(",", "."))
                valor_total = float(numeros[-1].replace(",", "."))

                quantidade = int(valor_total / valor_unit)

                cursor.execute("""
                INSERT INTO itens_pedido
                VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    id_pedido,
                    codigo_produto,
                    nome_produto,
                    quantidade,
                    valor_unit,
                    valor_total
                ))

    conn.commit()
    print("PDF processado com sucesso")
