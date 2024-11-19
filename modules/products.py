import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from core.database import execute_query, fetch_all

def open():
    """Open the product management window."""
    product_window = ttk.Toplevel()
    product_window.title("Cadastro de Produtos")
    product_window.geometry("600x400")

    # Input fields
    ttk.Label(product_window, text="Nome do Produto:").grid(row=0, column=0, padx=10, pady=5)
    name_entry = ttk.Entry(product_window)
    name_entry.grid(row=0, column=1, padx=10, pady=5)

    ttk.Label(product_window, text="Valor em dólares:").grid(row=1, column=0, padx=10, pady=5)
    price_entry = ttk.Entry(product_window)
    price_entry.grid(row=1, column=1, padx=10, pady=5)

    ttk.Label(product_window, text="Descrição:").grid(row=2, column=0, padx=10, pady=5)
    description_entry = ttk.Entry(product_window)
    description_entry.grid(row=2, column=1, padx=10, pady=5)

    ttk.Label(product_window, text="Quantidade:").grid(row=3, column=0, padx=10, pady=5)
    quantity_entry = ttk.Entry(product_window)
    quantity_entry.grid(row=3, column=1, padx=10, pady=5)

    # Save button
    def save_product():
        """Save the product to the database."""
        name = name_entry.get()
        price = float(price_entry.get())
        description = description_entry.get()
        quantity = int(quantity_entry.get())

        execute_query("""
            INSERT INTO products (name, price, description, quantity)
            VALUES (?, ?, ?, ?)
        """, (name, price, description, quantity))

        # Confirmation message
        ttk.Label(product_window, text="Produto salvo com sucesso!", foreground="green").grid(row=5, column=0, columnspan=2, pady=10)

    ttk.Button(product_window, text="Salvar", command=save_product, bootstyle=SUCCESS).grid(row=4, column=0, columnspan=2, pady=20)

    # Display all products
    def show_products():
        """Display all products in the database."""
        rows = fetch_all("SELECT * FROM products")
        for i, row in enumerate(rows, start=6):
            ttk.Label(product_window, text=f"{row[0]}: {row[1]} - ${row[2]} - Qtd: {row[4]}").grid(row=i, column=0, columnspan=2, pady=2)

    show_products()
