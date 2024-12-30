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
        """Abre uma janela com os detalhes da venda selecionada."""
        details_window = ttk.Toplevel(sales_window)
        details_window.title(translate("sale_details"))
        details_window.geometry("600x400")

        # Carregar dados da venda
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

        # Exibir informações do cliente
        ttk.Label(details_window, text=f"{translate('client_name')}: {client_name}", font=("Helvetica", 12)).pack(anchor="w", padx=10, pady=5)
        ttk.Label(details_window, text=f"{translate('phone')}: {phone}", font=("Helvetica", 12)).pack(anchor="w", padx=10, pady=5)
        ttk.Label(details_window, text=f"{translate('city')}: {city}", font=("Helvetica", 12)).pack(anchor="w", padx=10, pady=5)
        ttk.Label(details_window, text=f"{translate('total_usd')}: ${total_amount:.2f}", font=("Helvetica", 12)).pack(anchor="w", padx=10, pady=5)
        ttk.Label(details_window, text=f"{translate('date')}: {sale_date}", font=("Helvetica", 12)).pack(anchor="w", padx=10, pady=5)

        # Produtos vendidos
        ttk.Label(details_window, text=translate("products_sold"), font=("Helvetica", 14, "bold")).pack(anchor="w", padx=10, pady=10)
        products_table = ttk.Treeview(details_window, columns=("Produto", "Quantidade", "Preço"), show="headings", height=8)
        products_table.pack(fill=BOTH, expand=True, padx=10, pady=10)

        products_table.column("Produto", anchor="w", width=200)
        products_table.column("Quantidade", anchor="center", width=100)
        products_table.column("Preço", anchor="e", width=100)

        products_table.heading("Produto", text=translate("product_name"))
        products_table.heading("Quantidade", text=translate("quantity"))
        products_table.heading("Preço", text=translate("price"))

        products_query = """
            SELECT p.name, sp.quantity, sp.quantity * p.price
            FROM sales_products sp
            LEFT JOIN products p ON sp.product_id = p.id
            WHERE sp.sale_id = ?
        """
        product_rows = fetch_all(products_query, (sale_id,))
        for row in product_rows:
            products_table.insert("", "end", values=row)

        # Botões para ações
        actions_frame = ttk.Frame(details_window, padding=10)
        actions_frame.pack(fill=X, pady=10)

        def cancel_sale():
            """Anula a venda e atualiza o banco de dados."""
            execute_query("DELETE FROM sales_products WHERE sale_id = ?", (sale_id,))
            execute_query("DELETE FROM sales WHERE id = ?", (sale_id,))
            details_window.destroy()
            load_sales(sales_table)

        ttk.Button(actions_frame, text=translate("cancel_sale"), command=cancel_sale, bootstyle="danger").pack(side=LEFT, padx=5)

        def add_notes():
            """Abre um campo para adicionar informações adicionais."""
            notes_window = ttk.Toplevel(details_window)
            notes_window.title(translate("add_notes"))
            notes_window.geometry("400x200")

            ttk.Label(notes_window, text=translate("additional_notes")).pack(pady=10)
            notes_entry = ttk.Text(notes_window, height=5)
            notes_entry.pack(fill=BOTH, expand=True, padx=10, pady=10)

            def save_notes():
                notes = notes_entry.get("1.0", END).strip()
                execute_query("INSERT INTO sale_notes (sale_id, notes) VALUES (?, ?)", (sale_id, notes))
                notes_window.destroy()

            ttk.Button(notes_window, text=translate("save"), command=save_notes, bootstyle="success").pack(pady=10)

        ttk.Button(actions_frame, text=translate("add_notes"), command=add_notes, bootstyle="info").pack(side=LEFT, padx=5)

    def on_sale_select(event):
        """Abre a janela de detalhes ao clicar em uma venda."""
        selected_item = sales_table.selection()
        if selected_item:
            sale_id = sales_table.item(selected_item[0])["values"][0]
            open_sale_details(sale_id)

    sales_table.bind("<Double-1>", on_sale_select)

    # Carregar vendas ao iniciar
    load_sales(sales_table)
