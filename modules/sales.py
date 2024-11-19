import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from core.database import execute_query, fetch_all

def open():
    """Open the sales management window."""
    sales_window = ttk.Toplevel()
    sales_window.title("Cadastro de Vendas")
    sales_window.geometry("800x600")

    # Cliente Dropdown
    ttk.Label(sales_window, text="Selecione o Cliente:", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=5, sticky=W)
    client_combobox = ttk.Combobox(sales_window, state="readonly")
    client_combobox.grid(row=0, column=1, padx=10, pady=5, sticky=W)

    # Produto Dropdown
    ttk.Label(sales_window, text="Selecione o Produto:", font=("Helvetica", 12)).grid(row=1, column=0, padx=10, pady=5, sticky=W)
    product_combobox = ttk.Combobox(sales_window, state="readonly")
    product_combobox.grid(row=1, column=1, padx=10, pady=5, sticky=W)

    # Quantidade
    ttk.Label(sales_window, text="Quantidade:", font=("Helvetica", 12)).grid(row=1, column=2, padx=10, pady=5, sticky=W)
    quantity_entry = ttk.Entry(sales_window)
    quantity_entry.grid(row=1, column=3, padx=10, pady=5, sticky=W)

    # Produtos adicionados à venda
    columns = ("Produto", "Quantidade", "Preço Unitário", "Total")
    sale_table = ttk.Treeview(sales_window, columns=columns, show="headings", height=10)
    sale_table.grid(row=2, column=0, columnspan=4, padx=10, pady=20)

    for col in columns:
        sale_table.heading(col, text=col)

    # Lista de itens da venda
    sale_items = []

    def add_product():
        """Add a product to the sale."""
        product_name = product_combobox.get()
        quantity = int(quantity_entry.get())

        if not product_name or quantity <= 0:
            ttk.Label(sales_window, text="Por favor, selecione um produto e insira uma quantidade válida.", foreground="red").grid(row=3, column=0, columnspan=4)
            return

        # Busca detalhes do produto no banco
        product = fetch_all("SELECT id, name, price FROM products WHERE name = ?", (product_name,))
        if product:
            product_id, name, price = product[0]
            total = price * quantity
            sale_items.append((product_id, name, quantity, price, total))

            # Adiciona à tabela
            sale_table.insert("", "end", values=(name, quantity, f"${price:.2f}", f"${total:.2f}"))

    ttk.Button(sales_window, text="Adicionar Produto", command=add_product, bootstyle=PRIMARY).grid(row=1, column=4, padx=10, pady=5)

    def save_sale():
        """Save the sale to the database."""
        client_name = client_combobox.get()
        if not client_name or not sale_items:
            ttk.Label(sales_window, text="Por favor, selecione um cliente e adicione produtos.", foreground="red").grid(row=4, column=0, columnspan=4)
            return

        # Busca ID do cliente
        client = fetch_all("SELECT id FROM clients WHERE name = ?", (client_name,))
        if not client:
            ttk.Label(sales_window, text="Cliente não encontrado.", foreground="red").grid(row=4, column=0, columnspan=4)
            return

        client_id = client[0][0]
        total_amount = sum(item[4] for item in sale_items)

        # Insere venda no banco
        execute_query("INSERT INTO sales (client_id, total_amount, sale_date) VALUES (?, ?, datetime('now'))", (client_id, total_amount))
        sale_id = fetch_all("SELECT last_insert_rowid()")[0][0]

        # Insere itens da venda
        for item in sale_items:
            execute_query("INSERT INTO sales_products (sale_id, product_id, quantity) VALUES (?, ?, ?)", (sale_id, item[0], item[2]))

        ttk.Label(sales_window, text="Venda registrada com sucesso!", foreground="green").grid(row=4, column=0, columnspan=4)
        sale_items.clear()
        sale_table.delete(*sale_table.get_children())

    ttk.Button(sales_window, text="Finalizar Venda", command=save_sale, bootstyle=SUCCESS).grid(row=5, column=0, columnspan=4, pady=20)

    # Carrega dados para os comboboxes
    def load_data():
        clients = fetch_all("SELECT name FROM clients")
        products = fetch_all("SELECT name FROM products")
        client_combobox["values"] = [client[0] for client in clients]
        product_combobox["values"] = [product[0] for product in products]

    load_data()
