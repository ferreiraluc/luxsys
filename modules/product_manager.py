import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from core.database import execute_query, fetch_all

def open_product_manager(product_id=None):
    """Abre a aba de gerenciamento de produtos."""
    product_window = ttk.Toplevel()
    product_window.title("Gerenciamento de Produtos")
    product_window.geometry("1024x768")

    # Barra de busca
    search_frame = ttk.Frame(product_window, padding=10)
    search_frame.pack(fill=X)
    search_entry = ttk.Entry(search_frame, width=50)
    search_entry.pack(side=LEFT, padx=5)
    search_button = ttk.Button(search_frame, text="Buscar", bootstyle=PRIMARY, command=lambda: search_products(search_entry.get()))
    search_button.pack(side=LEFT, padx=5)

    # Filtros
    filter_frame = ttk.Frame(product_window, padding=10)
    filter_frame.pack(fill=X)
    ttk.Label(filter_frame, text="Ordenar por:").pack(side=LEFT, padx=5)
    filter_combobox = ttk.Combobox(filter_frame, state="readonly", values=["Preço: Mais Caro", "Preço: Mais Barato", "Quantidade", "Nome (A-Z)"])
    filter_combobox.pack(side=LEFT, padx=5)
    filter_button = ttk.Button(filter_frame, text="Filtrar", bootstyle=PRIMARY, command=lambda: apply_filter(filter_combobox.get()))
    filter_button.pack(side=LEFT, padx=5)

    # Listagem de Produtos
    product_table = ttk.Treeview(product_window, columns=("ID", "Nome", "Preço", "Quantidade"), show="headings", height=15)
    product_table.pack(fill=BOTH, expand=True, padx=10, pady=10)
    for col in ("ID", "Nome", "Preço", "Quantidade"):
        product_table.heading(col, text=col)

    def load_products():
        """Carrega todos os produtos no Treeview."""
        rows = fetch_all("SELECT id, name, price, quantity FROM products")
        update_table(rows)

    def update_table(rows):
        """Atualiza a tabela com os produtos fornecidos."""
        for row in product_table.get_children():
            product_table.delete(row)
        for row in rows:
            product_table.insert("", "end", values=row)

    def search_products(search_term):
        """Busca produtos com base no termo."""
        query = f"SELECT id, name, price, quantity FROM products WHERE name LIKE ?"
        rows = fetch_all(query, (f"%{search_term}%",))
        update_table(rows)

    def apply_filter(filter_option):
        """Aplica o filtro escolhido."""
        if filter_option == "Preço: Mais Caro":
            query = "SELECT id, name, price, quantity FROM products ORDER BY price DESC"
        elif filter_option == "Preço: Mais Barato":
            query = "SELECT id, name, price, quantity FROM products ORDER BY price ASC"
        elif filter_option == "Quantidade":
            query = "SELECT id, name, price, quantity FROM products ORDER BY quantity DESC"
        elif filter_option == "Nome (A-Z)":
            query = "SELECT id, name, price, quantity FROM products ORDER BY name ASC"
        else:
            return
        rows = fetch_all(query)
        update_table(rows)

    # Adicionar Novo Produto
    new_product_frame = ttk.Frame(product_window, padding=10)
    new_product_frame.pack(fill=X, pady=10)

    ttk.Label(new_product_frame, text="Nome:").pack(side=LEFT, padx=5)
    name_entry = ttk.Entry(new_product_frame, width=20)
    name_entry.pack(side=LEFT, padx=5)

    ttk.Label(new_product_frame, text="Preço:").pack(side=LEFT, padx=5)
    price_entry = ttk.Entry(new_product_frame, width=10)
    price_entry.pack(side=LEFT, padx=5)

    ttk.Label(new_product_frame, text="Quantidade:").pack(side=LEFT, padx=5)
    quantity_entry = ttk.Entry(new_product_frame, width=10)
    quantity_entry.pack(side=LEFT, padx=5)

    add_button = ttk.Button(new_product_frame, text="Adicionar Produto", bootstyle=SUCCESS, command=lambda: add_product(name_entry, price_entry, quantity_entry))
    add_button.pack(side=LEFT, padx=5)

    def add_product(name, price, quantity):
        """Adiciona um novo produto ao banco de dados."""
        if not name.get() or not price.get() or not quantity.get():
            return  # Não adiciona se algum campo estiver vazio
        execute_query(
            "INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)",
            (name.get(), float(price.get()), int(quantity.get()))
        )
        load_products()

    # Carregar produtos ao iniciar
    load_products()
