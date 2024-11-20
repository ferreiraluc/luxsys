import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from core.database import fetch_all, execute_query


def open_sales_manager():
    """Abre a janela de gerenciamento de vendas."""
    sales_window = ttk.Toplevel()
    sales_window.title("Gerenciamento de Vendas")
    sales_window.geometry("800x600")

    # Barra de Busca
    search_frame = ttk.Frame(sales_window, padding=10)
    search_frame.pack(fill=X)
    search_entry = ttk.Entry(search_frame, width=50)
    search_entry.pack(side=LEFT, padx=5)
    search_button = ttk.Button(search_frame, text="Buscar", bootstyle=PRIMARY, command=lambda: search_sales(search_entry.get()))
    search_button.pack(side=LEFT, padx=5)

    # Tabela de Vendas
    columns = ("ID", "Cliente", "Total (USD)", "Data", "Ações")
    sales_table = ttk.Treeview(sales_window, columns=columns, show="headings", height=15)
    sales_table.pack(fill=BOTH, expand=True, padx=10, pady=10)

    # Configurações das colunas
    sales_table.column("ID", anchor="center", width=50)
    sales_table.column("Cliente", anchor="w", width=150)
    sales_table.column("Total (USD)", anchor="e", width=100)
    sales_table.column("Data", anchor="center", width=150)
    sales_table.column("Ações", anchor="center", width=100)

    sales_table.heading("ID", text="ID")
    sales_table.heading("Cliente", text="Cliente")
    sales_table.heading("Total (USD)", text="Total (USD)")
    sales_table.heading("Data", text="Data")
    sales_table.heading("Ações", text="Ações")

    # Botão para Atualizar
    ttk.Button(sales_window, text="Atualizar", bootstyle=SUCCESS, command=lambda: load_sales(sales_table)).pack(pady=5)

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

        for index, row in enumerate(rows):
            tag = "evenrow" if index % 2 == 0 else "oddrow"
            sale_id = row[0]
            table.insert("", "end", values=row, tags=(tag,))
            add_action_buttons(table, sale_id)

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
        for index, row in enumerate(rows):
            tag = "evenrow" if index % 2 == 0 else "oddrow"
            sale_id = row[0]
            sales_table.insert("", "end", values=row, tags=(tag,))
            add_action_buttons(sales_table, sale_id)

    def add_action_buttons(table, sale_id):
        """Adiciona botões de editar e excluir para cada venda."""
        # Botão de Editar
        edit_button = ttk.Button(table, text="✏️", width=2, bootstyle=INFO, command=lambda: edit_sale(sale_id))
        delete_button = ttk.Button(table, text="🗑️", width=2, bootstyle=DANGER, command=lambda: delete_sale(sale_id))

        # Adiciona os botões na última coluna da tabela
        table.insert(
            "",
            "end",
            values=(sale_id, "Editar", "Excluir"),
            tags=("actions",),
        )

    def edit_sale(sale_id):
        """Editar uma venda."""
        # Abra uma nova janela para editar os dados da venda
        edit_window = ttk.Toplevel()
        edit_window.title("Editar Venda")
        edit_window.geometry("400x300")

        # Carregar dados da venda
        sale_data = fetch_all("""
            SELECT s.id, c.name, s.total_amount, s.sale_date
            FROM sales s
            LEFT JOIN clients c ON s.client_id = c.id
            WHERE s.id = ?
        """, (sale_id,))

        if sale_data:
            sale = sale_data[0]

            # Campos de edição
            ttk.Label(edit_window, text="Cliente:", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=5, sticky=W)
            client_entry = ttk.Entry(edit_window, width=30)
            client_entry.insert(0, sale[1])
            client_entry.grid(row=0, column=1, padx=10, pady=5)

            ttk.Label(edit_window, text="Total (USD):", font=("Helvetica", 12)).grid(row=1, column=0, padx=10, pady=5, sticky=W)
            total_entry = ttk.Entry(edit_window, width=30)
            total_entry.insert(0, sale[2])
            total_entry.grid(row=1, column=1, padx=10, pady=5)

            ttk.Label(edit_window, text="Data:", font=("Helvetica", 12)).grid(row=2, column=0, padx=10, pady=5, sticky=W)
            date_entry = ttk.Entry(edit_window, width=30)
            date_entry.insert(0, sale[3])
            date_entry.grid(row=2, column=1, padx=10, pady=5)

            def save_changes():
                """Salvar alterações feitas na venda."""
                new_client = client_entry.get()
                new_total = total_entry.get()
                new_date = date_entry.get()

                execute_query("""
                    UPDATE sales
                    SET total_amount = ?, sale_date = ?
                    WHERE id = ?
                """, (new_total, new_date, sale_id))

                ttk.Label(edit_window, text="Alterações salvas com sucesso!", foreground="green").grid(row=4, column=0, columnspan=2, pady=10)
                load_sales(sales_table)  # Atualiza a tabela principal

            ttk.Button(edit_window, text="Salvar Alterações", bootstyle=SUCCESS, command=save_changes).grid(row=3, column=0, columnspan=2, pady=10)

    def delete_sale(sale_id):
        """Excluir uma venda."""
        execute_query("DELETE FROM sales WHERE id = ?", (sale_id,))
        execute_query("DELETE FROM sales_products WHERE sale_id = ?", (sale_id,))
        ttk.Label(sales_window, text="Venda excluída com sucesso!", foreground="red").pack(pady=10)
        load_sales(sales_table)

    # Configuração de cores (linhas zebradas)
    sales_table.tag_configure("evenrow", background="#F0F0F0")
    sales_table.tag_configure("oddrow", background="#FFFFFF")

    load_sales(sales_table)
