import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from core.database import execute_query, fetch_all
from core.utils import translate  # Importa função de tradução

def open():
    """Open the product management window."""
    product_window = ttk.Toplevel()
    product_window.title(translate("product_management"))  # Título traduzido
    product_window.geometry("600x400")
    product_window.rowconfigure(7, weight=1)  # Configuração para tornar a tabela responsiva
    product_window.columnconfigure(0, weight=1)
    product_window.columnconfigure(1, weight=1)

    # Input fields
    ttk.Label(product_window, text=translate("product_code")).grid(row=0, column=0, padx=10, pady=5, sticky=W)
    code_entry = ttk.Entry(product_window, width=30)
    code_entry.grid(row=0, column=1, padx=10, pady=5, sticky=EW)

    ttk.Label(product_window, text=translate("product_name")).grid(row=1, column=0, padx=10, pady=5, sticky=W)
    name_entry = ttk.Entry(product_window, width=30)
    name_entry.grid(row=1, column=1, padx=10, pady=5, sticky=EW)

    ttk.Label(product_window, text=translate("product_price")).grid(row=2, column=0, padx=10, pady=5, sticky=W)
    price_entry = ttk.Entry(product_window, width=30)
    price_entry.grid(row=2, column=1, padx=10, pady=5, sticky=EW)

    ttk.Label(product_window, text=translate("description")).grid(row=3, column=0, padx=10, pady=5, sticky=W)
    description_entry = ttk.Entry(product_window, width=30)
    description_entry.grid(row=3, column=1, padx=10, pady=5, sticky=EW)

    ttk.Label(product_window, text=translate("quantity")).grid(row=4, column=0, padx=10, pady=5, sticky=W)
    quantity_entry = ttk.Entry(product_window, width=30)
    quantity_entry.grid(row=4, column=1, padx=10, pady=5, sticky=EW)

    message_label = ttk.Label(product_window, text="", foreground="red")
    message_label.grid(row=6, column=0, columnspan=2, pady=10)

    # Save button
    def save_product():
        """Save the product to the database."""
        code = code_entry.get().strip() or None
        name = name_entry.get().strip()
        price = price_entry.get().strip()
        description = description_entry.get().strip()
        quantity = quantity_entry.get().strip()

        if not code or not name or not price or not quantity:
            message_label.config(text=translate("error_fill_fields"), foreground="red")
            return

        try:
            price = float(price)
            quantity = int(quantity)
        except ValueError:
            message_label.config(text=translate("error_price_quantity"), foreground="red")
            return

        # Verificar duplicação no banco de dados
        existing_code = fetch_all("SELECT 1 FROM products WHERE code = ?", (code,))
        existing_name = fetch_all("SELECT 1 FROM products WHERE name = ?", (name,))

        if existing_code:
            message_label.config(text=translate("error_duplicate_code"), foreground="red")
            return

        if existing_name:
            message_label.config(text=translate("error_duplicate_name"), foreground="red")
            return

        # Inserir o produto no banco de dados
        execute_query("""
            INSERT INTO products (code, name, price, description, quantity)
            VALUES (?, ?, ?, ?, ?)
        """, (code, name, price, description, quantity))

        # Mensagem de sucesso
        message_label.config(text=translate("success_product_saved"), foreground="green")
        load_products()

    ttk.Button(product_window, text=translate("save"), command=save_product, bootstyle=SUCCESS).grid(row=5, column=0, columnspan=2, pady=10)

    # Product table
    columns = (translate("code"), translate("name"), translate("price_usd"), translate("quantity"))
    product_table = ttk.Treeview(product_window, columns=columns, show="headings")
    product_table.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky=NSEW)  # Tornar a tabela expansível

    # Configuração do Scrollbar
    scrollbar = ttk.Scrollbar(product_window, orient=VERTICAL, command=product_table.yview)
    product_table.configure(yscroll=scrollbar.set)
    scrollbar.grid(row=7, column=2, sticky=NS)

    for col in columns:
        product_table.heading(col, text=col)
        product_table.column(col, anchor="center", stretch=True)

    def load_products():
        """Display all products in the database."""
        for row in product_table.get_children():
            product_table.delete(row)

        # Alinhe a ordem dos campos no SELECT com as colunas da tabela
        rows = fetch_all("SELECT code, name, price, quantity FROM products ORDER BY id DESC")
        for row in rows:
            # Insere os valores na ordem correta das colunas
            product_table.insert("", "end", values=row)

    # Load products at the start
    load_products()

    # Fazer a tabela expandir com a janela
    product_window.rowconfigure(7, weight=1)  # Linha da tabela
    product_window.columnconfigure(0, weight=1)  # Ajustar as colunas principais
