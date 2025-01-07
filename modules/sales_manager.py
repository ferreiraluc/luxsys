import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from core.database import fetch_all, execute_query
from core.utils import translate

def open_sales_manager():
    """Abre a janela de gerenciamento de vendas."""
    sales_window = ttk.Toplevel()
    sales_window.title(translate("sales_management"))
    sales_window.geometry("800x600")
    sales_window.rowconfigure(1, weight=1)
    sales_window.columnconfigure(0, weight=1)

    # Barra de Busca
    search_frame = ttk.Frame(sales_window, padding=10)
    search_frame.grid(row=0, column=0, sticky="ew")
    search_frame.columnconfigure(0, weight=1)

    search_entry = ttk.Entry(search_frame, width=50)
    search_entry.grid(row=0, column=0, padx=5, sticky="ew")

    search_button = ttk.Button(search_frame, text=translate("search"), bootstyle=PRIMARY,
                               command=lambda: search_sales(search_entry.get()))
    search_button.grid(row=0, column=1, padx=5, sticky="w")

    # Tabela de Vendas
    columns = (translate("id"), translate("client"), translate("total_usd"), translate("date"))
    sales_table = ttk.Treeview(sales_window, columns=columns, show="headings", height=15)
    sales_table.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    # Configurações das colunas
    sales_table.column(translate("id"), anchor="center", width=50)
    sales_table.column(translate("client"), anchor="w", width=150)
    sales_table.column(translate("total_usd"), anchor="e", width=100)
    sales_table.column(translate("date"), anchor="center", width=150)

    for col in columns:
        sales_table.heading(col, text=col)

    # Botão para Atualizar
    update_button = ttk.Button(sales_window, text=translate("refresh"), bootstyle=SUCCESS,
                               command=lambda: load_sales(sales_table))
    update_button.grid(row=2, column=0, pady=5)

    def load_sales(table):
        """Carrega as vendas no Treeview."""
        for row in table.get_children():
            table.delete(row)

        rows = fetch_all("""
            SELECT s.id, c.name, s.total_amount, s.sale_date
            FROM sales s
            LEFT JOIN clients c ON s.client_id = c.id
            ORDER BY s.sale_date DESC
        """)

        for row in rows:
            table.insert("", "end", values=row)

    def search_sales(term):
        """Busca vendas pelo nome do cliente."""
        query = """
            SELECT s.id, c.name, s.total_amount, s.sale_date
            FROM sales s
            LEFT JOIN clients c ON s.client_id = c.id
            WHERE c.name LIKE ?
            ORDER BY s.sale_date DESC
        """
        rows = fetch_all(query, (f"%{term}%",))
        for row in sales_table.get_children():
            sales_table.delete(row)
        for row in rows:
            sales_table.insert("", "end", values=row)

    def open_sale_details(sale_id):
        """Open a window showing the details of a selected sale."""
        details_window = ttk.Toplevel()
        details_window.title(translate("sale_details"))
        details_window.geometry("600x400")

        # Busca dados da venda
        sale_query = """
            SELECT s.id, c.name, c.phone, c.city, s.total_amount, s.sale_date
            FROM sales s
            LEFT JOIN clients c ON s.client_id = c.id
            WHERE s.id = ?
        """
        sale_data = fetch_all(sale_query, (sale_id,))
        if not sale_data:
            ttk.Label(details_window, text=translate("sale_not_found"), foreground="red").pack(pady=10)
            return

        sale_id, client_name, phone, city, total_amount, sale_date = sale_data[0]

        # Exibir detalhes do cliente
        ttk.Label(details_window, text=f"{translate('client_name')}: {client_name}", font=("Helvetica", 12)).pack(anchor="w", padx=10, pady=5)
        ttk.Label(details_window, text=f"{translate('phone')}: {phone}", font=("Helvetica", 12)).pack(anchor="w", padx=10, pady=5)
        ttk.Label(details_window, text=f"{translate('city')}: {city}", font=("Helvetica", 12)).pack(anchor="w", padx=10, pady=5)
        ttk.Label(details_window, text=f"{translate('total_usd')}: ${total_amount:.2f}", font=("Helvetica", 12)).pack(anchor="w", padx=10, pady=5)
        ttk.Label(details_window, text=f"{translate('date')}: {sale_date}", font=("Helvetica", 12)).pack(anchor="w", padx=10, pady=5)

        # Exibir produtos vendidos
        ttk.Label(details_window, text=translate("products_sold"), font=("Helvetica", 14, "bold")).pack(anchor="w", padx=10, pady=10)
        products_table = ttk.Treeview(details_window, columns=("Produto", "Quantidade", "Total"), show="headings", height=8)
        products_table.pack(fill=BOTH, expand=True, padx=10, pady=10)

        products_table.column("Produto", anchor="w", width=200)
        products_table.column("Quantidade", anchor="center", width=100)
        products_table.column("Total", anchor="e", width=100)

        products_table.heading("Produto", text=translate("product_name"))
        products_table.heading("Quantidade", text=translate("quantity"))
        products_table.heading("Total", text=translate("total"))

        # Buscar produtos relacionados à venda
        products_query = """
            SELECT p.name, sp.quantity, (sp.quantity * p.price) AS total_price
            FROM sales_products sp
            JOIN products p ON sp.product_id = p.id
            WHERE sp.sale_id = ?
        """
        product_rows = fetch_all(products_query, (sale_id,))
        if not product_rows:
            ttk.Label(details_window, text=translate("no_products_found"), foreground="red").pack(pady=10)

        for row in product_rows:
            products_table.insert("", "end", values=row)

        # Cancelar venda
        def cancel_sale():
            """Cancela a venda e restaura o estoque."""
            execute_query("BEGIN TRANSACTION")
            try:
                for product in product_rows:
                    product_name, quantity, _ = product
                    execute_query(
                        "UPDATE products SET quantity = quantity + ? WHERE name = ?",
                        (quantity, product_name)
                    )
                execute_query("DELETE FROM sales_products WHERE sale_id = ?", (sale_id,))
                execute_query("DELETE FROM sales WHERE id = ?", (sale_id,))
                execute_query("COMMIT")
                details_window.destroy()
                load_sales(sales_table)
            except Exception as e:
                execute_query("ROLLBACK")
                ttk.Label(details_window, text=f"{translate('error_canceling_sale')}: {str(e)}", foreground="red").pack(pady=5)

        ttk.Button(details_window, text=translate("cancel_sale"), command=cancel_sale, bootstyle="danger").pack(anchor="w", padx=10, pady=5)


    def on_sale_select(event):
        """Abre a janela de detalhes ao clicar em uma venda."""
        selected_item = sales_table.selection()
        if selected_item:
            sale_id = sales_table.item(selected_item[0])["values"][0]
            open_sale_details(sale_id)

    sales_table.bind("<Double-1>", on_sale_select)

    # Carregar vendas ao iniciar
    load_sales(sales_table)
