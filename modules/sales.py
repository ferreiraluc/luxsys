import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from core.database import execute_query, fetch_all
from core.utils import translate
from core.database import connect_db

def open():
    """Open the sales management window."""
    sales_window = ttk.Toplevel()
    sales_window.title(translate("sales_button"))
    sales_window.geometry("800x600")

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
    client_combobox = ttk.Combobox(form_frame, state="readonly")
    client_combobox.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

    # Produto Dropdown
    ttk.Label(form_frame, text=translate("product_name"), font=("Helvetica", 12)).grid(row=1, column=0, padx=10, pady=5, sticky=W)
    product_combobox = ttk.Combobox(form_frame, state="readonly")
    product_combobox.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

    # Quantidade
    ttk.Label(form_frame, text=translate("quantity"), font=("Helvetica", 12)).grid(row=1, column=2, padx=10, pady=5, sticky=W)
    quantity_entry = ttk.Entry(form_frame)
    quantity_entry.grid(row=1, column=3, padx=10, pady=5, sticky="ew")

    # Botão Adicionar Produto
    ttk.Button(form_frame, text=translate("add_product"), command=lambda: add_product(), bootstyle=PRIMARY).grid(row=1, column=4, padx=10, pady=5)

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

    def add_product():
        """Add a product to the sale."""
        product_name = product_combobox.get()
        quantity = quantity_entry.get()

        if not product_name or not quantity.isdigit() or int(quantity) <= 0:
            ttk.Label(form_frame, text=translate("error_fill_fields"), foreground="red").grid(row=2, column=0, columnspan=4, sticky="ew")
            return

        quantity = int(quantity)
        product = fetch_all("SELECT id, name, price, quantity FROM products WHERE name = ?", (product_name,))
        if product:
            product_id, name, price, available_quantity = product[0]
            if quantity > available_quantity:
                ttk.Label(form_frame, text=translate("error_insufficient_stock"), foreground="red").grid(row=2, column=0, columnspan=4, sticky="ew")
                return

            total = price * quantity
            sale_items.append((product_id, name, quantity, price, total))

            # Adiciona à tabela
            sale_table.insert("", "end", values=(name, quantity, f"${price:.2f}", f"${total:.2f}"))
        else:
            ttk.Label(form_frame, text=translate("product_not_found"), foreground="red").grid(row=2, column=0, columnspan=4, sticky="ew")

    def save_sale():
        """Save the sale to the database."""
        client_name = client_combobox.get()
        if not client_name or not sale_items:
            ttk.Label(form_frame, text=translate("error_fill_fields"), foreground="red").grid(row=2, column=0, columnspan=4, sticky="ew")
            return

        # Busca ID do cliente
        client = fetch_all("SELECT id FROM clients WHERE name = ?", (client_name,))
        if not client:
            ttk.Label(form_frame, text=translate("client_not_found"), foreground="red").grid(row=2, column=0, columnspan=4, sticky="ew")
            return

        client_id = client[0][0]
        total_amount = sum(item[4] for item in sale_items)

        conn = connect_db()
        cursor = conn.cursor()
        try:
            # Inicia a transação
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

            # Confirma a transação
            conn.commit()
            ttk.Label(form_frame, text=translate("success_sale_registered"), foreground="green").grid(row=2, column=0, columnspan=4, sticky="ew")
            sale_items.clear()
            sale_table.delete(*sale_table.get_children())
        except Exception as e:
            # Reverte a transação em caso de erro
            conn.rollback()
            ttk.Label(form_frame, text=f"{translate('error_saving_sale')}: {str(e)}", foreground="red").grid(row=2, column=0, columnspan=4, sticky="ew")
        finally:
            conn.close()


        ttk.Label(form_frame, text=translate("success_sale_registered"), foreground="green").grid(row=2, column=0, columnspan=4, sticky="ew")
        sale_items.clear()
        sale_table.delete(*sale_table.get_children())

    ttk.Button(sales_window, text=translate("save"), command=save_sale, bootstyle=SUCCESS).grid(row=2, column=0, columnspan=4, pady=10)

    # Carrega dados para os comboboxes
    def load_data():
        clients = fetch_all("SELECT name FROM clients")
        products = fetch_all("SELECT name FROM products")
        client_combobox["values"] = [client[0] for client in clients]
        product_combobox["values"] = [product[0] for product in products]

    load_data()

    # Tornando os elementos da janela responsivos
    sales_window.rowconfigure(1, weight=1)  # Tabela de vendas expande
    sales_window.columnconfigure(0, weight=1)
