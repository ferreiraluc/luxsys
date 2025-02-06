import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from core.database import execute_query, fetch_all
from core.utils import translate
from tkinter import messagebox
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import webbrowser

def open():
    """Abre a janela de gerenciamento de caixa com design minimalista e novas funcionalidades."""
    cash_window = ttk.Toplevel()
    cash_window.title(translate("cash_register_button"))
    cash_window.geometry("1000x700")
    cash_window.resizable(False, False)

    # Layout: Dashboard, Tabela de Transações, Menu de Ações
    cash_window.rowconfigure(0, weight=1)  # Dashboard
    cash_window.rowconfigure(1, weight=5)  # Tabela
    cash_window.rowconfigure(2, weight=1)  # Menu de ações
    cash_window.columnconfigure(0, weight=1)

    # Dashboard
    dashboard_frame = ttk.Frame(cash_window, padding=10)
    dashboard_frame.grid(row=0, column=0, sticky="nsew")

    def create_dashboard_metric(parent, title, value):
        """Cria uma métrica no dashboard."""
        card = ttk.Frame(parent, padding=10)
        card.pack(side=LEFT, padx=15, pady=10, fill="none", expand=True)
        ttk.Label(card, text=title, font=("Helvetica", 14, "bold"), anchor="center").pack(anchor="center", pady=5)
        value_label = ttk.Label(card, text=value, font=("Helvetica", 24, "bold"), anchor="center")
        value_label.pack(anchor="center", pady=5)
        return value_label

    total_entry_label = create_dashboard_metric(dashboard_frame, translate("Total entry"), "0.00")
    total_exit_label = create_dashboard_metric(dashboard_frame, translate("Total exit"), "0.00")
    net_flow_label = create_dashboard_metric(dashboard_frame, translate("Net flow"), "0.00")
    total_sales_label = create_dashboard_metric(dashboard_frame, translate("Total sales"), "0")

    # Tabela de Transações
    transaction_frame = ttk.Frame(cash_window, padding=10)
    transaction_frame.grid(row=1, column=0, sticky="nsew")

    columns = (translate("description"), translate("amount"), translate("date"))
    transaction_table = ttk.Treeview(transaction_frame, columns=columns, show="headings", height=15)
    transaction_table.pack(fill="both", expand=True, padx=10, pady=10)
    transaction_table.column(translate("description"), anchor="w", width=300)
    transaction_table.column(translate("amount"), anchor="e", width=100)
    transaction_table.column(translate("date"), anchor="center", width=200)
    for col in columns:
        transaction_table.heading(col, text=col)

    # Menu de Ações
    action_frame = ttk.Frame(cash_window, padding=10)
    action_frame.grid(row=2, column=0, sticky="nsew")
    ttk.Button(action_frame, text=translate("register_transaction"), command=lambda: open_transaction_window(), bootstyle="success").pack(side=LEFT, padx=5)
    ttk.Button(action_frame, text=translate("generate_report"), command=lambda: generate_pdf_report(), bootstyle="info").pack(side=LEFT, padx=5)
    ttk.Button(action_frame, text=translate("delete_transaction"), command=lambda: delete_transaction(), bootstyle="danger").pack(side=LEFT, padx=5)
    # Novo botão para relatório geral de vendas
    ttk.Button(action_frame, text=translate("general_sales_report"), command=lambda: open_general_sales_report(), bootstyle="primary").pack(side=LEFT, padx=5)

    # Função para carregar transações
    def load_transactions():
        """Carrega transações recentes na tabela."""
        for row in transaction_table.get_children():
            transaction_table.delete(row)
        rows = fetch_all(
            "SELECT description, amount, transaction_date FROM cash_register ORDER BY transaction_date DESC"
        )
        for row in rows:
            transaction_table.insert("", "end", values=row)

    def update_dashboard():
        """Atualiza as métricas do dashboard."""
        rows = fetch_all("SELECT amount FROM cash_register")
        if rows:
            amounts = [row[0] for row in rows]
            total_entry = sum(amount for amount in amounts if amount > 0)
            total_exit = abs(sum(amount for amount in amounts if amount < 0))
            net_flow = total_entry - total_exit
            total_sales = sum(1 for amount in amounts if amount > 0)
            total_entry_label.config(text=f"{total_entry:.2f}")
            total_exit_label.config(text=f"{total_exit:.2f}")
            net_flow_label.config(text=f"{net_flow:.2f}")
            total_sales_label.config(text=str(total_sales))

    def delete_transaction():
        """Exclui uma transação selecionada com proteção por senha."""
        selected_item = transaction_table.selection()
        if not selected_item:
            show_toast("error", translate("select_transaction"))
            return

        def check_password():
            if password_entry.get() == "1974":
                trans_desc = transaction_table.item(selected_item)["values"][0]
                execute_query("DELETE FROM cash_register WHERE description = ?", (trans_desc,))
                load_transactions()
                update_dashboard()
                show_toast("success", translate("transaction_deleted"))
                password_window.destroy()
            else:
                messagebox.showerror(translate("error"), translate("incorrect_password"))
                password_window.destroy()

        password_window = ttk.Toplevel(cash_window)
        password_window.title(translate("password_prompt"))
        password_window.geometry("300x150")
        ttk.Label(password_window, text=translate("enter_password"), font=("Helvetica", 12)).pack(pady=10)
        password_entry = ttk.Entry(password_window, show="*")
        password_entry.pack(pady=10)
        ttk.Button(password_window, text=translate("submit"), command=check_password, bootstyle="success").pack(pady=10)

    def generate_pdf_report():
        """Gera um relatório em PDF de uma transação com os produtos da venda (como um cupom fiscal)."""
        selected_item = transaction_table.selection()
        if not selected_item:
            # Exibe aviso se nenhuma transação for selecionada
            messagebox.showwarning("Aviso", translate("select_transaction"))
            return

        # Obtém os dados da transação selecionada
        transaction_data = transaction_table.item(selected_item)["values"]
        if not transaction_data or len(transaction_data) < 3:
            messagebox.showerror("Erro", "Dados insuficientes na transação.")
            return

        description, amount, date = transaction_data

        # Variável para armazenar os detalhes da venda e os itens
        sale_data = None
        product_rows = []

        # Se a descrição indicar uma venda, assumindo o formato "Venda: <sale_id>"
        if description.startswith("Venda:"):
            try:
                sale_id = int(description.split("Venda:")[1].strip())
            except Exception as e:
                messagebox.showerror("Erro", "Formato de venda inválido.")
                return

            # Consultar os detalhes da venda
            sale_data_list = fetch_all("""
                SELECT s.id, c.name, c.phone, c.city, s.total_amount, s.sale_date
                FROM sales s
                JOIN clients c ON s.client_id = c.id
                WHERE s.id = ?
            """, (sale_id,))
            if not sale_data_list:
                messagebox.showerror("Erro", translate("sale_not_found"))
                return
            sale_data = sale_data_list[0]

            # Consultar os produtos vendidos nessa venda
            product_rows = fetch_all("""
                SELECT p.name, sp.quantity, (sp.quantity * p.price) as total_price
                FROM sales_products sp
                JOIN products p ON sp.product_id = p.id
                WHERE sp.sale_id = ?
            """, (sale_id,))
        else:
            # Se não for uma venda, gera um relatório simples com os dados disponíveis
            sale_data = (None, "", "", "", float(amount), date)
            product_rows = []

        try:
            pdf_file = os.path.join(os.getcwd(), f"{description}_report.pdf")
            c = canvas.Canvas(pdf_file, pagesize=letter)
            c.setFont("Helvetica", 12)
            c.drawString(50, 750, "Cupom Fiscal")
            c.drawString(50, 730, f"Venda ID: {sale_data[0] if sale_data[0] is not None else 'N/D'}")
            c.drawString(50, 710, f"Cliente: {sale_data[1]}")
            c.drawString(50, 690, f"Telefone: {sale_data[2]}")
            c.drawString(50, 670, f"Cidade: {sale_data[3]}")
            c.drawString(50, 650, f"Total: ${float(sale_data[4]):.2f}")
            c.drawString(50, 630, f"Data: {sale_data[5]}")
            c.drawString(50, 600, "Produtos:")
            y = 580
            for product in product_rows:
                c.drawString(50, y, product[0])
                c.drawString(250, y, f"Qtd: {product[1]}")
                c.drawString(350, y, f"Total: ${float(product[2]):.2f}")
                y -= 20
            c.save()
            webbrowser.open(pdf_file)
            show_toast("success", translate("report_generated"))
        except Exception as ex:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {ex}")

    def open_transaction_details(sale_id):
        """Abre uma janela interna exibindo os detalhes da venda (sem gerar PDF)."""
        details_window = ttk.Toplevel()
        details_window.title(translate("sale_details"))
        details_window.geometry("600x600")

        sale_data = fetch_all("""
            SELECT s.id, c.name, c.phone, c.city, s.total_amount, s.sale_date
            FROM sales s
            JOIN clients c ON s.client_id = c.id
            WHERE s.id = ?
        """, (sale_id,))
        if not sale_data:
            ttk.Label(details_window, text=translate("sale_not_found"), foreground="red").pack(pady=10)
            return
        sale_data = sale_data[0]

        ttk.Label(details_window, text=f"{translate('client_name')}: {sale_data[1]}", font=("Helvetica", 12)).pack(anchor="w", padx=10, pady=5)
        ttk.Label(details_window, text=f"{translate('phone')}: {sale_data[2]}", font=("Helvetica", 12)).pack(anchor="w", padx=10, pady=5)
        ttk.Label(details_window, text=f"{translate('city')}: {sale_data[3]}", font=("Helvetica", 12)).pack(anchor="w", padx=10, pady=5)
        ttk.Label(details_window, text=f"{translate('total_usd')}: ${sale_data[4]:.2f}", font=("Helvetica", 12)).pack(anchor="w", padx=10, pady=5)
        ttk.Label(details_window, text=f"{translate('date')}: {sale_data[5]}", font=("Helvetica", 12)).pack(anchor="w", padx=10, pady=5)

        ttk.Label(details_window, text=translate("products_sold"), font=("Helvetica", 14, "bold")).pack(anchor="w", padx=10, pady=10)
        products_table = ttk.Treeview(details_window, columns=("Produto", "Quantidade", "Total"), show="headings", height=8)
        products_table.pack(fill=BOTH, expand=True, padx=10, pady=10)
        products_table.column("Produto", anchor="w", width=200)
        products_table.column("Quantidade", anchor="center", width=100)
        products_table.column("Total", anchor="e", width=100)
        products_table.heading("Produto", text=translate("product_name"))
        products_table.heading("Quantidade", text=translate("quantity"))
        products_table.heading("Total", text=translate("total"))
        product_rows = fetch_all("""
            SELECT p.name, sp.quantity, (sp.quantity * p.price) as total_price
            FROM sales_products sp
            JOIN products p ON sp.product_id = p.id
            WHERE sp.sale_id = ?
        """, (sale_id,))
        if not product_rows:
            ttk.Label(details_window, text=translate("no_products_found"), foreground="red").pack(pady=10)
        for row in product_rows:
            products_table.insert("", "end", values=row)

    def open_transaction_window():
        """Abre uma janela para registrar uma nova transação."""
        transaction_window = ttk.Toplevel(cash_window)
        transaction_window.title(translate("register_transaction"))
        transaction_window.geometry("400x300")
        ttk.Label(transaction_window, text=translate("description")).pack(pady=5)
        description_entry = ttk.Entry(transaction_window)
        description_entry.pack(fill=X, padx=10)
        ttk.Label(transaction_window, text=translate("amount")).pack(pady=5)
        amount_entry = ttk.Entry(transaction_window)
        amount_entry.pack(fill=X, padx=10)
        ttk.Label(transaction_window, text=translate("transaction_type")).pack(pady=5)
        transaction_type = ttk.Combobox(transaction_window, state="readonly", values=[translate("entry"), translate("exit")])
        transaction_type.pack(fill=X, padx=10)

        def save_transaction():
            """Salva a nova transação no banco de dados."""
            description = description_entry.get()
            amount = amount_entry.get()
            t_type = transaction_type.get()
            if not description or not amount or not t_type:
                show_toast("error", translate("error_fill_fields"))
                return
            try:
                amount = float(amount)
                if t_type == translate("exit"):
                    amount = -abs(amount)
                execute_query("INSERT INTO cash_register (description, amount, transaction_date) VALUES (?, ?, datetime('now'))", (description, amount))
                load_transactions()
                update_dashboard()
                transaction_window.destroy()
                show_toast("success", translate("transaction_saved"))
            except ValueError:
                show_toast("error", translate("amount_invalid"))
        ttk.Button(transaction_window, text=translate("save"), command=save_transaction, bootstyle=SUCCESS).pack(pady=10)

    def open_general_sales_report():
        """Abre uma janela de relatório geral de vendas com cruzamentos e filtros avançados."""
        report_window = ttk.Toplevel()
        report_window.title(translate("general_sales_report"))
        report_window.geometry("800x600")
        # Exemplo de cruzamento de dados
        # Produto mais vendido
        prod_result = fetch_all("""
            SELECT p.name, SUM(sp.quantity) as total_sold
            FROM sales_products sp
            JOIN products p ON sp.product_id = p.id
            GROUP BY p.name
            ORDER BY total_sold DESC
            LIMIT 1
        """)
        prod_text = f"Produto mais vendido: {prod_result[0][0]} ({prod_result[0][1]} unidades)" if prod_result else "N/D"

        # Cliente que mais comprou
        client_result = fetch_all("""
            SELECT c.name, COUNT(s.id) as num_sales
            FROM sales s
            JOIN clients c ON s.client_id = c.id
            GROUP BY c.name
            ORDER BY num_sales DESC
            LIMIT 1
        """)
        client_text = f"Cliente que mais comprou: {client_result[0][0]} ({client_result[0][1]} vendas)" if client_result else "N/D"

        # Maior venda
        sale_result = fetch_all("""
            SELECT id, total_amount
            FROM sales
            ORDER BY total_amount DESC
            LIMIT 1
        """)
        sale_text = f"Maior venda: ID {sale_result[0][0]} - ${sale_result[0][1]:.2f}" if sale_result else "N/D"

        # Horários com mais vendas
        hour_result = fetch_all("""
            SELECT strftime('%H', sale_date) as hour, COUNT(*) as num_sales
            FROM sales
            GROUP BY hour
            ORDER BY num_sales DESC
            LIMIT 1
        """)
        hour_text = f"Horário com mais vendas: {hour_result[0][0]}h ({hour_result[0][1]} vendas)" if hour_result else "N/D"

        # Exibe os dados em Labels
        ttk.Label(report_window, text=prod_text, font=("Helvetica", 14)).pack(pady=10, anchor="w", padx=10)
        ttk.Label(report_window, text=client_text, font=("Helvetica", 14)).pack(pady=10, anchor="w", padx=10)
        ttk.Label(report_window, text=sale_text, font=("Helvetica", 14)).pack(pady=10, anchor="w", padx=10)
        ttk.Label(report_window, text=hour_text, font=("Helvetica", 14)).pack(pady=10, anchor="w", padx=10)
        # Você pode expandir essa janela com mais filtros e gráficos, se desejar.

    def show_toast(type_, message):
        """Mostra notificações discretas."""
        toast = ttk.Label(action_frame, text=message, bootstyle=type_)
        toast.pack(side=LEFT, padx=10, pady=10)
        toast.after(3000, toast.destroy)

    # Atualiza os dados
    load_transactions()
    update_dashboard()

    # Vincula duplo clique na tabela de transações para abrir os detalhes da venda (internamente)
    def on_transaction_double_click(event):
        selected_item = transaction_table.selection()
        if selected_item:
            transaction_data = transaction_table.item(selected_item)["values"]
            description = transaction_data[0]
            # Se o description indicar uma venda, assumindo o formato "Venda: <sale_id>"
            if description.startswith("Venda:"):
                try:
                    sale_id = int(description.split("Venda:")[1].strip())
                    open_transaction_details(sale_id)
                except Exception as e:
                    show_toast("error", "Formato de venda inválido.")
    transaction_table.bind("<Double-1>", on_transaction_double_click)

    cash_window.mainloop()
