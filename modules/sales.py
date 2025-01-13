import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from core.database import execute_query, fetch_all
from core.utils import translate
from core.database import connect_db

def setup_autocomplete_combobox(combobox, items):
    """Configura um Combobox para autocompletar enquanto o usuário digita."""
    def on_key_release(event):
        value = combobox.get().lower()
        filtered_items = [item for item in items if item.lower().startswith(value)]
        combobox["values"] = filtered_items
        if value and filtered_items:
            combobox.event_generate("<Down>")
    
    combobox.bind("<KeyRelease>", on_key_release)

def open():
    """Open the sales management window."""
    sales_window = ttk.Toplevel()
    sales_window.title(translate("sales_button"))
    sales_window.geometry("800x700")

    # Configuração de Layout Responsivo
    sales_window.rowconfigure(0, weight=1)  # Frame superior (formulários)
    sales_window.rowconfigure(1, weight=3)  # Tabela
    sales_window.columnconfigure(0, weight=1)

    # Frame Superior (Formulários)
    form_frame = ttk.Frame(sales_window, padding=10)
    form_frame.grid(row=0, column=0, sticky="nsew")

    form_frame.columnconfigure(0, weight=1)
    form_frame.columnconfigure(1, weight=2)
    form_frame.columnconfigure(2, weight=1)
    form_frame.columnconfigure(3, weight=1)

    # Cliente Dropdown
    ttk.Label(form_frame, text=translate("client_name"), font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=5, sticky=W)
    client_combobox = ttk.Combobox(form_frame)
    client_combobox.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

    # Código do Produto
    ttk.Label(form_frame, text=translate("product_code"), font=("Helvetica", 12)).grid(row=1, column=0, padx=10, pady=5, sticky=W)
    product_code_entry = ttk.Entry(form_frame)
    product_code_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

    # Produto Dropdown
    ttk.Label(form_frame, text=translate("product_name"), font=("Helvetica", 12)).grid(row=2, column=0, padx=10, pady=5, sticky=W)
    product_combobox = ttk.Combobox(form_frame)
    product_combobox.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

    # Quantidade
    ttk.Label(form_frame, text=translate("quantity"), font=("Helvetica", 12)).grid(row=3, column=0, padx=10, pady=5, sticky=W)
    quantity_entry = ttk.Entry(form_frame)
    quantity_entry.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

    # Botão Adicionar Produto
    ttk.Button(form_frame, text=translate("add_product"), command=lambda: add_product(), bootstyle=PRIMARY).grid(row=4, column=1, padx=10, pady=10, sticky="ew")

    # Produtos adicionados à venda
    columns = (translate("name"), translate("quantity"), translate("price_usd"), translate("total_usd"))
    sale_table = ttk.Treeview(sales_window, columns=columns, show="headings", height=10)
    sale_table.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    sale_table.column(translate("name"), anchor="w", width=150)
    sale_table.column(translate("quantity"), anchor="center", width=100)
    sale_table.column(translate("price_usd"), anchor="e", width=100)
    sale_table.column(translate("total_usd"), anchor="e", width=120)

    for col in columns:
        sale_table.heading(col, text=col)

    # Lista de itens da venda
    sale_items = []

    def populate_product_name(event=None):
        """Populate product name when a valid product code is entered."""
        product_code = product_code_entry.get().strip()
        if product_code:
            product = fetch_all("SELECT name FROM products WHERE code = ?", (product_code,))
            if product:
                product_combobox.set(product[0][0])  # Preenche o nome do produto correspondente ao código
            else:
                product_combobox.set("")  # Limpa o campo se o código não for válido

    product_code_entry.bind("<KeyRelease>", populate_product_name)

    def add_product():
        """Add a product to the sale."""
        product_name = product_combobox.get()
        product_code = product_code_entry.get().strip()
        quantity = quantity_entry.get()

        if not product_name or not quantity.isdigit() or int(quantity) <= 0:
            ttk.Label(form_frame, text=translate("error_fill_fields"), foreground="red").grid(row=4, column=0, columnspan=4, sticky="ew")
            return

        quantity = int(quantity)
        product = fetch_all("SELECT id, name, price, quantity FROM products WHERE name = ? OR code = ?", (product_name, product_code))
        if product:
            product_id, name, price, available_quantity = product[0]
            if quantity > available_quantity:
                ttk.Label(form_frame, text=translate("error_insufficient_stock"), foreground="red").grid(row=4, column=0, columnspan=4, sticky="ew")
                return

            total = price * quantity
            sale_items.append((product_id, name, quantity, price, total))

            # Adiciona à tabela
            sale_table.insert("", "end", values=(name, quantity, f"${price:.2f}", f"${total:.2f}"))
        else:
            ttk.Label(form_frame, text=translate("product_not_found"), foreground="red").grid(row=4, column=0, columnspan=4, sticky="ew")

    def save_sale():
        """Save the sale to the database."""
        client_name = client_combobox.get()
        if not client_name or not sale_items:
            ttk.Label(form_frame, text=translate("error_fill_fields"), foreground="red").grid(row=4, column=0, columnspan=4, sticky="ew")
            return

        # Busca ID do cliente
        client = fetch_all("SELECT id FROM clients WHERE name = ?", (client_name,))
        if not client:
            ttk.Label(form_frame, text=translate("client_not_found"), foreground="red").grid(row=4, column=0, columnspan=4, sticky="ew")
            return

        client_id = client[0][0]
        total_amount = sum(item[4] for item in sale_items)

        conn = connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("BEGIN TRANSACTION")

            # Insere a venda
            cursor.execute(
                "INSERT INTO sales (client_id, total_amount, sale_date) VALUES (?, ?, datetime('now'))",
                (client_id, total_amount)
            )
            sale_id = cursor.lastrowid

            # Insere os produtos na venda
            for item in sale_items:
                product_id, _, quantity, _, _ = item
                cursor.execute(
                    "INSERT INTO sales_products (sale_id, product_id, quantity) VALUES (?, ?, ?)",
                    (sale_id, product_id, quantity)
                )
                # Atualiza o estoque
                cursor.execute(
                    "UPDATE products SET quantity = quantity - ? WHERE id = ?",
                    (quantity, product_id)
                )

            cursor.execute(
                "INSERT INTO cash_register (description, amount, transaction_date) VALUES (?, ?, datetime('now'))",
                (translate("sale_registered"), total_amount)
            )

            conn.commit()
            ttk.Label(form_frame, text=translate("success_sale_registered"), foreground="green").grid(row=6, column=0, columnspan=4, sticky="ew")
            sale_items.clear()
            sale_table.delete(*sale_table.get_children())
        except Exception as e:
            conn.rollback()
            ttk.Label(form_frame, text=f"{translate('error_saving_sale')}: {str(e)}", foreground="red").grid(row=4, column=0, columnspan=4, sticky="ew")
        finally:
            conn.close()

    ttk.Button(sales_window, text=translate("save"), command=save_sale, bootstyle=SUCCESS).grid(row=2, column=0, columnspan=4, pady=10)

    # Carrega dados para os comboboxes
    def load_data():
        clients = fetch_all("SELECT name FROM clients")
        products = fetch_all("SELECT name, code FROM products")
        client_names = [client[0] for client in clients]
        product_names = [product[0] for product in products]
        product_codes = [product[1] for product in products]

        client_combobox["values"] = client_names
        product_combobox["values"] = product_names

        # Configurar autocomplete
        setup_autocomplete_combobox(client_combobox, client_names)
        setup_autocomplete_combobox(product_combobox, product_names)

    load_data()

    # Tornando os elementos da janela responsivos
    sales_window.rowconfigure(1, weight=1)
    sales_window.columnconfigure(0, weight=1)
