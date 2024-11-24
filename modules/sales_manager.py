import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from core.database import fetch_all, execute_query


def open_sales_manager():
    """Abre a janela de gerenciamento de vendas."""
    sales_window = ttk.Toplevel()
    sales_window.title("Gerenciamento de Vendas")
    sales_window.geometry("800x600")
    sales_window.rowconfigure(1, weight=1)
    sales_window.columnconfigure(0, weight=1)

    # Barra de Busca
    search_frame = ttk.Frame(sales_window, padding=10)
    search_frame.grid(row=0, column=0, sticky="ew")
    search_frame.columnconfigure(0, weight=1)

    search_entry = ttk.Entry(search_frame, width=50)
    search_entry.grid(row=0, column=0, padx=5, sticky="ew")

    search_button = ttk.Button(search_frame, text="Buscar", bootstyle=PRIMARY, command=lambda: search_sales(search_entry.get()))
    search_button.grid(row=0, column=1, padx=5, sticky="w")

    # Tabela de Vendas
    columns = ("ID", "Cliente", "Total (USD)", "Data")
    sales_table = ttk.Treeview(sales_window, columns=columns, show="headings", height=15)
    sales_table.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    # Configurações das colunas
    sales_table.column("ID", anchor="center", width=50)
    sales_table.column("Cliente", anchor="w", width=150)
    sales_table.column("Total (USD)", anchor="e", width=100)
    sales_table.column("Data", anchor="center", width=150)

    sales_table.heading("ID", text="ID")
    sales_table.heading("Cliente", text="Cliente")
    sales_table.heading("Total (USD)", text="Total (USD)")
    sales_table.heading("Data", text="Data")

    # Botão para Atualizar
    update_button = ttk.Button(sales_window, text="Atualizar", bootstyle=SUCCESS, command=lambda: load_sales(sales_table))
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

    # Carregar vendas ao iniciar
    load_sales(sales_table)
