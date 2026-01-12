import pdfplumber
import sqlite3
import re
from datetime import datetime

conn = sqlite3.connect("bi_vendas.db")
cursor = conn.cursor()

# ===== TABELAS =====
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
    numero_pedido TEXT,
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

# ===== FUNÇÃO PRINCIPAL =====
def processar_pdf(caminho_pdf):
    with pdfplumber.open(caminho_pdf) as pdf:
        texto = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())

    # IGNORAR ORÇAMENTO / BONIFICAÇÃO
    texto_upper = texto.upper()
    if "ORÇAMENTO" in texto_upper or "BONIFICAÇÃO" in texto_upper:
        print("PDF ignorado (Orçamento/Bonificação)")
        return

    # ===== PEDIDO =====
    pedido_match = re.search(r"Pedido.*?\n(\d+)", texto)
    numero_pedido = pedido_match.group(1) if pedido_match else "N/A"

    # ===== DATA =====
    data_match = re.search(r"(\d{2}/\d{2}/\d{4})", texto)
    data_pedido = data_match.group(1) if data_match else datetime.now().strftime("%d/%m/%Y")

    # ===== CLIENTE =====
    cliente_match = re.search(r"(\d+)\s-\s([A-Z0-9\s]+LTDA)", texto)
    if not cliente_match:
        print("Cliente não identificado")
        return

    codigo_cliente = cliente_match.group(1)
    nome_cliente = cliente_match.group(2).strip()

    cursor.execute(
        "INSERT OR IGNORE INTO clientes VALUES (?, ?, ?)",
        (codigo_cliente, nome_cliente, None)
    )

    # ===== TOTAL PEDIDO =====
    total_match = re.search(r"Total Itens:\s([\d,]+)", texto)
    valor_total_pedido = float(total_match.group(1).replace(".", "").replace(",", ".")) if total_match else 0

    cursor.execute("""
        INSERT INTO pedidos (numero_pedido, codigo_cliente, data, valor_total)
        VALUES (?, ?, ?, ?)
    """, (numero_pedido, codigo_cliente, data_pedido, valor_total_pedido))

    id_pedido = cursor.lastrowid

    # ===== PRODUTOS =====
    for linha in texto.split("\n"):
        produto_match = re.match(
            r"(\d+)\s-\s(.+?)\s+\d+\s+(\d+)\s+([\d,]+)\s+0,00\s+\w+\s+\d+\s+([\d,]+)",
            linha
        )

        if produto_match:
            codigo_produto = produto_match.group(1)
            nome_produto = produto_match.group(2).strip()
            quantidade = int(produto_match.group(3))
            valor_unit = float(produto_match.group(4).replace(",", "."))
            valor_total = float(produto_match.group(5).replace(",", "."))

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
    print("PDF processado corretamente")

