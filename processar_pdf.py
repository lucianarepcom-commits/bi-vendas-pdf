import pdfplumber
import sqlite3
import re
from datetime import datetime

conn = sqlite3.connect("bi_vendas.db", check_same_thread=False)
cursor = conn.cursor()

# ===== TABELAS =====
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
    numero_pedido TEXT UNIQUE,
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
        texto = "\n".join(
            page.extract_text() for page in pdf.pages if page.extract_text()
        )

    texto_upper = texto.upper()

    # IGNORAR ORÇAMENTO / BONIFICAÇÃO
    if "ORÇAMENTO" in texto_upper or "BONIFICAÇÃO" in texto_upper:
        return "PDF ignorado (Orçamento/Bonificação)"

    # ===== REPRESENTANTE =====
    rep_match = re.search(r"REPRESENTANTE:\s*(\d+)\s-\s(.+)", texto_upper)
    if rep_match:
        cursor.execute(
            "INSERT OR IGNORE INTO representante VALUES (?, ?)",
            (rep_match.group(1), rep_match.group(2).strip())
        )

    # ===== PEDIDO =====
    pedido_match = re.search(r"PEDIDO:\s*(\d+)", texto_upper)
    if not pedido_match:
        return "Número do pedido não identificado"

    numero_pedido = pedido_match.group(1)

    # 🔴 EVITAR DUPLICIDADE
    cursor.execute(
        "SELECT 1 FROM pedidos WHERE numero_pedido = ?",
        (numero_pedido,)
    )
    if cursor.fetchone():
        return f"Pedido {numero_pedido} já importado"

    # ===== DATA =====
    data_match = re.search(r"(\d{2}/\d{2}/\d{4})", texto)
    data_pedido = data_match.group(1) if data_match else datetime.now().strftime("%d/%m/%Y")

    # ===== CLIENTE (EXPLÍCITO) =====
    cliente_match = re.search(r"CLIENTE:\s*(\d+)\s-\s(.+)", texto_upper)
    if not cliente_match:
        return "Cliente não identificado"

    codigo_cliente = cliente_match.group(1)
    nome_cliente = cliente_match.group(2).strip()

    cursor.execute(
        "INSERT OR IGNORE INTO clientes VALUES (?, ?, ?)",
        (codigo_cliente, nome_cliente, None)
    )

    # ===== TOTAL =====
    total_match = re.search(r"TOTAL ITENS:\s*([\d,]+)", texto_upper)
    valor_total = float(
        total_match.group(1).replace(".", "").replace(",", ".")
    ) if total_match else 0

    cursor.execute("""
        INSERT INTO pedidos (numero_pedido, codigo_cliente, data, valor_total)
        VALUES (?, ?, ?, ?)
    """, (numero_pedido, codigo_cliente, data_pedido, valor_total))

    id_pedido = cursor.lastrowid

    # ===== PRODUTOS =====
    for linha in texto.split("\n"):
        prod = re.match(
            r"(\d+)\s-\s(.+?)\s+\d+\s+(\d+)\s+([\d,]+)\s+0,00\s+\w+\s+\d+\s+([\d,]+)",
            linha
        )

        if prod:
            cursor.execute("""
                INSERT INTO itens_pedido
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                id_pedido,
                prod.group(1),
                prod.group(2).strip(),
                int(prod.group(3)),
                float(prod.group(4).replace(",", ".")),
                float(prod.group(5).replace(",", "."))
            ))

    conn.commit()
    return f"Pedido {numero_pedido} importado com sucesso"
