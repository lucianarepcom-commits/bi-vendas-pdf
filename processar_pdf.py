def conectar_banco():
    conn = sqlite3.connect("bi_vendas.db", check_same_thread=False)
    cursor = conn.cursor()

    # 🔍 Verifica estrutura da tabela pedidos
    cursor.execute("PRAGMA table_info(pedidos)")
    colunas = [col[1] for col in cursor.fetchall()]

    if "numero_pedido" not in colunas and colunas:
        # Estrutura antiga detectada → recria tudo
        cursor.execute("DROP TABLE IF EXISTS itens_pedido")
        cursor.execute("DROP TABLE IF EXISTS pedidos")
        cursor.execute("DROP TABLE IF EXISTS clientes")
        cursor.execute("DROP TABLE IF EXISTS representante")
        conn.commit()

    # Criação correta das tabelas
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
    return conn, cursor

