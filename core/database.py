import sqlite3

DB_NAME = "luxsys.db"

def connect_db():
    """Connect to the SQLite database and return the connection object."""
    conn = sqlite3.connect(DB_NAME)
    return conn

def create_tables():
    """Create necessary tables if they don't already exist."""
    conn = connect_db()
    cursor = conn.cursor()

    # Table for Products
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        description TEXT,
        quantity INTEGER NOT NULL
        
        
    )
    """)

    # Table for Clients
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT NOT NULL,
        city TEXT
    )
    """)

    # Table for Sales
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        total_amount REAL NOT NULL,
        sale_date TEXT NOT NULL,
        FOREIGN KEY (client_id) REFERENCES clients (id)
    )
    """)

    # Table for Sales Products
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

    # Table for Cash Register
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cash_register (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        transaction_date TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


def execute_query(query, params=()):
    """Execute a given query with optional parameters."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def fetch_all(query, params=()):
    """Fetch all results for a given query with optional parameters."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return results


# Ensure tables are created when this module is imported
create_tables()
