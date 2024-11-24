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
    ttk.Label(search_frame, text="Buscar por Nome ou Código:").pack(side=LEFT, padx=5)
    search_entry = ttk.Entry(search_frame, width=50)
    search_entry.pack(side=LEFT, padx=5)
    search_button = ttk.Button(
        search_frame, text="Buscar", bootstyle=PRIMARY,
        command=lambda: search_products(search_entry.get())
    )
    search_button.pack(side=LEFT, padx=5)

    # Listagem de Produtos
    columns = ("ID", "Código", "Nome", "Preço (USD)", "Quantidade", "Editar")
    product_table = ttk.Treeview(product_window, columns=columns, show="headings", height=15)
    product_table.pack(fill=BOTH, expand=True, padx=10, pady=10)

    for col in columns:
        product_table.heading(col, text=col, command=lambda c=col: sort_column(product_table, c, False))
        product_table.column(col, anchor="center" if col in ("ID", "Código", "Preço (USD)", "Quantidade") else "w", width=120)

    def load_products():
        """Carrega todos os produtos no Treeview."""
        for row in product_table.get_children():
            product_table.delete(row)

        rows = fetch_all("SELECT id, code, name, price, quantity FROM products ORDER BY id DESC")
        for row in rows:
            product_table.insert("", "end", values=row + ("Editar",))

    def sort_column(treeview, col, reverse):
        """Ordena a tabela ao clicar no cabeçalho."""
        data = [(treeview.set(child, col), child) for child in treeview.get_children()]
        data.sort(reverse=reverse, key=lambda x: (float(x[0]) if col in ("ID", "Preço (USD)", "Quantidade") else x[0]))
        for index, (_, child) in enumerate(data):
            treeview.move(child, '', index)
        treeview.heading(col, command=lambda: sort_column(treeview, col, not reverse))

    def search_products(search_term):
        """Busca produtos com base no nome ou código."""
        query = """
            SELECT id, code, name, price, quantity
            FROM products
            WHERE name LIKE ? OR code LIKE ?
            ORDER BY id DESC
        """
        rows = fetch_all(query, (f"%{search_term}%", f"%{search_term}%"))
        for row in product_table.get_children():
            product_table.delete(row)
        for row in rows:
            product_table.insert("", "end", values=row + ("Editar",))

    def edit_product(product_id):
        """Abre uma janela para editar o produto."""
        edit_window = ttk.Toplevel()
        edit_window.title("Editar Produto")
        edit_window.geometry("300x350")

        product = fetch_all("SELECT id, code, name, price, quantity FROM products WHERE id = ?", (product_id,))
        if not product:
            ttk.Label(edit_window, text="Produto não encontrado.", foreground="red").pack(pady=10)
            return

        product = product[0]

        # Campos de edição
        ttk.Label(edit_window, text="Código:").pack(pady=5)
        code_entry = ttk.Entry(edit_window, width=30)
        code_entry.insert(0, product[1])
        code_entry.pack(pady=5)

        ttk.Label(edit_window, text="Nome:").pack(pady=5)
        name_entry = ttk.Entry(edit_window, width=30)
        name_entry.insert(0, product[2])
        name_entry.pack(pady=5)

        ttk.Label(edit_window, text="Preço:").pack(pady=5)
        price_entry = ttk.Entry(edit_window, width=30)
        price_entry.insert(0, product[3])
        price_entry.pack(pady=5)

        ttk.Label(edit_window, text="Quantidade:").pack(pady=5)
        quantity_entry = ttk.Entry(edit_window, width=30)
        quantity_entry.insert(0, product[4])
        quantity_entry.pack(pady=5)

        def save_changes():
            """Salva as alterações no banco de dados."""
            code = code_entry.get().strip()
            name = name_entry.get().strip()
            price = float(price_entry.get().strip())
            quantity = int(quantity_entry.get().strip())

            execute_query(
                "UPDATE products SET code = ?, name = ?, price = ?, quantity = ? WHERE id = ?",
                (code, name, price, quantity, product_id)
            )
            ttk.Label(edit_window, text="Alterações salvas com sucesso!", foreground="green").pack(pady=10)
            load_products()

        ttk.Button(edit_window, text="Salvar Alterações", bootstyle=SUCCESS, command=save_changes).pack(pady=10)

    def add_product(code, name, price, quantity):
        """Adiciona um novo produto ao banco de dados."""
        if not code.get() or not name.get() or not price.get() or not quantity.get():
            ttk.Label(product_window, text="Preencha todos os campos.", foreground="red").pack(pady=10)
            return

        execute_query(
            "INSERT INTO products (code, name, price, quantity) VALUES (?, ?, ?, ?)",
            (code.get().strip(), name.get().strip(), float(price.get()), int(quantity.get()))
        )
        load_products()

    # Adicionar Novo Produto
    new_product_frame = ttk.Frame(product_window, padding=10)
    new_product_frame.pack(fill=X, pady=10)

    ttk.Label(new_product_frame, text="Código:").pack(side=LEFT, padx=5)
    code_entry = ttk.Entry(new_product_frame, width=10)
    code_entry.pack(side=LEFT, padx=5)

    ttk.Label(new_product_frame, text="Nome:").pack(side=LEFT, padx=5)
    name_entry = ttk.Entry(new_product_frame, width=20)
    name_entry.pack(side=LEFT, padx=5)

    ttk.Label(new_product_frame, text="Preço:").pack(side=LEFT, padx=5)
    price_entry = ttk.Entry(new_product_frame, width=10)
    price_entry.pack(side=LEFT, padx=5)

    ttk.Label(new_product_frame, text="Quantidade:").pack(side=LEFT, padx=5)
    quantity_entry = ttk.Entry(new_product_frame, width=10)
    quantity_entry.pack(side=LEFT, padx=5)

    add_button = ttk.Button(new_product_frame, text="Adicionar Produto", bootstyle=SUCCESS, command=lambda: add_product(code_entry, name_entry, price_entry, quantity_entry))
    add_button.pack(side=LEFT, padx=5)

    # Adiciona botões de edição na tabela
    def on_item_double_click(event):
        """Abre o editor ao clicar duas vezes em uma linha."""
        selected_item = product_table.selection()
        if selected_item:
            product_id = product_table.item(selected_item[0], "values")[0]
            edit_product(product_id)

    product_table.bind("<Double-1>", on_item_double_click)

    # Carregar produtos ao iniciar
    load_products()
