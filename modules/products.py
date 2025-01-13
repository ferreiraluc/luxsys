import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from core.database import execute_query, fetch_all
from core.utils import translate  # Importa função de tradução


def open():
    """Open the product management window."""
    product_window = ttk.Toplevel()
    product_window.title(translate("product_register"))  # Título traduzido
    product_window.geometry("800x500")
    product_window.columnconfigure(0, weight=1)
    product_window.rowconfigure(6, weight=1)  # Configuração para tornar a tabela responsiva

    # Frame para organizar os campos
    input_frame = ttk.Frame(product_window, padding=10)
    input_frame.grid(row=0, column=0, sticky=EW)
    input_frame.columnconfigure(0, weight=1)
    input_frame.columnconfigure(1, weight=2)

    # Input fields
    ttk.Label(input_frame, text=translate("product_code")).grid(row=0, column=0, padx=5, pady=5, sticky=W)
    code_entry = ttk.Entry(input_frame, width=40)
    code_entry.grid(row=0, column=1, padx=5, pady=5, sticky=EW)

    ttk.Label(input_frame, text=translate("product_name")).grid(row=1, column=0, padx=5, pady=5, sticky=W)
    name_entry = ttk.Entry(input_frame, width=40)
    name_entry.grid(row=1, column=1, padx=5, pady=5, sticky=EW)

    ttk.Label(input_frame, text=translate("product_price")).grid(row=2, column=0, padx=5, pady=5, sticky=W)
    price_entry = ttk.Entry(input_frame, width=40)
    price_entry.grid(row=2, column=1, padx=5, pady=5, sticky=EW)

    ttk.Label(input_frame, text=translate("description")).grid(row=3, column=0, padx=5, pady=5, sticky=W)
    description_entry = ttk.Entry(input_frame, width=40)
    description_entry.grid(row=3, column=1, padx=5, pady=5, sticky=EW)

    ttk.Label(input_frame, text=translate("quantity")).grid(row=4, column=0, padx=5, pady=5, sticky=W)
    quantity_entry = ttk.Entry(input_frame, width=40)
    quantity_entry.grid(row=4, column=1, padx=5, pady=5, sticky=EW)

    # Save button
    save_button = ttk.Button(input_frame, text=translate("save"), bootstyle=SUCCESS, command=lambda: save_product())
    save_button.grid(row=5, column=0, columnspan=2, pady=10, sticky=EW)

    message_label = ttk.Label(input_frame, text="", foreground="red")
    message_label.grid(row=6, column=0, columnspan=2, pady=5)

    # Product table
    columns = (translate("code"), translate("name"), translate("price_usd"), translate("quantity"), "Editar", "Excluir")
    product_table = ttk.Treeview(product_window, columns=columns, show="headings")
    product_table.grid(row=1, column=0, padx=10, pady=10, sticky=NSEW)

    for col in columns:
        product_table.heading(col, text=col)
        product_table.column(col, anchor="center", stretch=True)

    # Configuração do Scrollbar
    scrollbar = ttk.Scrollbar(product_window, orient=VERTICAL, command=product_table.yview)
    product_table.configure(yscroll=scrollbar.set)
    scrollbar.grid(row=1, column=1, sticky=NS)

    def save_product():
        """Save the product to the database."""
        code = code_entry.get().strip()
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

        existing_code = fetch_all("SELECT 1 FROM products WHERE code = ?", (code,))
        existing_name = fetch_all("SELECT 1 FROM products WHERE name = ?", (name,))

        if existing_code:
            message_label.config(text=translate("error_duplicate_code"), foreground="red")
            return

        if existing_name:
            message_label.config(text=translate("error_duplicate_name"), foreground="red")
            return

        execute_query("""
            INSERT INTO products (code, name, price, description, quantity)
            VALUES (?, ?, ?, ?, ?)
        """, (code, name, price, description, quantity))

        message_label.config(text=translate("success_product_saved"), foreground="green")
        load_products()

    def load_products():
        """Display all products in the database."""
        for row in product_table.get_children():
            product_table.delete(row)

        rows = fetch_all("SELECT id, code, name, price, quantity FROM products ORDER BY id DESC")
        for product in rows:
            product_table.insert("", "end", values=product[1:] + ("Editar", "Excluir"))

    def edit_product(product_id):
        """Open a window to edit a product."""
        product = fetch_all("SELECT code, name, price, description, quantity FROM products WHERE id = ?", (product_id,))
        if product:
            code, name, price, description, quantity = product[0]

            edit_window = ttk.Toplevel()
            edit_window.title(translate("edit_product"))
            edit_window.geometry("400x300")

            ttk.Label(edit_window, text=translate("product_code")).pack(pady=5)
            code_entry = ttk.Entry(edit_window, width=30)
            code_entry.insert(0, code)
            code_entry.pack(pady=5)

            ttk.Label(edit_window, text=translate("product_name")).pack(pady=5)
            name_entry = ttk.Entry(edit_window, width=30)
            name_entry.insert(0, name)
            name_entry.pack(pady=5)

            ttk.Label(edit_window, text=translate("product_price")).pack(pady=5)
            price_entry = ttk.Entry(edit_window, width=30)
            price_entry.insert(0, str(price))
            price_entry.pack(pady=5)

            ttk.Label(edit_window, text=translate("quantity")).pack(pady=5)
            quantity_entry = ttk.Entry(edit_window, width=30)
            quantity_entry.insert(0, str(quantity))
            quantity_entry.pack(pady=5)

            def save_changes():
                """Save product changes to the database."""
                new_code = code_entry.get()
                new_name = name_entry.get()
                new_price = price_entry.get()
                new_quantity = quantity_entry.get()

                execute_query("""
                    UPDATE products
                    SET code = ?, name = ?, price = ?, quantity = ?
                    WHERE id = ?
                """, (new_code, new_name, float(new_price), int(new_quantity), product_id))
                edit_window.destroy()
                load_products()

            ttk.Button(edit_window, text=translate("save"), command=save_changes, bootstyle=SUCCESS).pack(pady=10)

    def delete_product(product_id):
        """Delete a product from the database."""
        execute_query("DELETE FROM products WHERE id = ?", (product_id,))
        load_products()

    def on_action(event):
        """Handle edit and delete actions."""
        item = product_table.selection()
        if item:
            values = product_table.item(item, "values")
            product_id = fetch_all("SELECT id FROM products WHERE code = ?", (values[0],))[0][0]
            column = product_table.identify_column(event.x)
            if column == "#5":  # Editar
                edit_product(product_id)
            elif column == "#6":  # Excluir
                delete_product(product_id)

    product_table.bind("<ButtonRelease-1>", on_action)
    load_products()
