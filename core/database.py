import sqlite3
import hashlib

DB_NAME = "luxsys.db"

    
def connect_db():
    """Estabelece conexão com o banco de dados SQLite."""
    return sqlite3.connect(DB_NAME)

def create_tables():
    """Cria tabelas no banco de dados, se ainda não existirem."""
    conn = connect_db()
    cursor = conn.cursor()

    # Tabela para produtos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        quantity INTEGER NOT NULL
    )
    """)

    # Tabela para clientes
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        city TEXT
    )
    """)

    # Tabela para vendas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        total_amount REAL NOT NULL,
        sale_date TEXT NOT NULL,
        FOREIGN KEY (client_id) REFERENCES clients (id)
    )
    """)

    # Tabela para itens das vendas
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales_products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        FOREIGN KEY (sale_id) REFERENCES sales (id),
        FOREIGN KEY (product_id) REFERENCES products (id)
    )
    """)

    # Tabela para o registro do caixa
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cash_register (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        transaction_date TEXT NOT NULL
    )
    """)

    # Tabela para usuários (login)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL
    )
    """)

    # Adiciona usuários pré-definidos, se ainda não existirem
    users = [
        ("lucas", hashlib.sha256("091974".encode()).hexdigest()),
        ("adriana", hashlib.sha256("171601".encode()).hexdigest()),
        ("debora", hashlib.sha256("0121".encode()).hexdigest())
    ]

    cursor.executemany("""
    INSERT OR IGNORE INTO users (username, password_hash) VALUES (?, ?)
    """, users)

    conn.commit()
    conn.close()

def execute_query(query, params=()):
    """Executa uma consulta no banco de dados."""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Erro ao executar query: {e}")
    finally:
        conn.close()

def fetch_all(query, params=()):
    """Busca todos os resultados de uma consulta."""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(query, params)
        return cursor.fetchall()
    except Exception as e:
        print(f"Erro ao buscar dados: {e}")
        return []
    finally:
        conn.close()

def authenticate_user(username, password):
    """Autentica um usuário verificando o hash da senha."""
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    user = fetch_all("SELECT id FROM users WHERE username = ? AND password_hash = ?", (username, password_hash))
    return len(user) > 0

# Inicializa as tabelas ao importar o módulo
create_tables()
