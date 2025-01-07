import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from core.database import execute_query, fetch_all
from core.utils import translate
from tkinter import messagebox
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import webbrowser
import csv


def open():
    """Abre a janela de gerenciamento de caixa com design minimalista."""
    cash_window = ttk.Toplevel()
    cash_window.title(translate("cash_register_button"))
    cash_window.geometry("1000x700")
    cash_window.resizable(False, False)

    # Configuração de Layout Responsivo
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
    transaction_table.pack(fill=BOTH, expand=True, padx=10, pady=10)

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

    # Funções
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
        """Atualiza as métricas no dashboard."""
        rows = fetch_all("SELECT amount FROM cash_register")
        if rows:
            amounts = [row[0] for row in rows]
            total_entry = sum(amount for amount in amounts if amount > 0)
            total_exit = abs(sum(amount for amount in amounts if amount < 0))
            net_flow = total_entry - total_exit
            total_sales = len(amounts)

            total_entry_label.config(text=f"{total_entry:.2f}")
            total_exit_label.config(text=f"{total_exit:.2f}")
            net_flow_label.config(text=f"{net_flow:.2f}")
            total_sales_label.config(text=str(total_sales))

    def delete_transaction():
        """Exclui uma transação selecionada."""
        selected_item = transaction_table.selection()
        if not selected_item:
            show_toast("error", translate("select_transaction"))
            return

        trans_id = transaction_table.item(selected_item)["values"][0]
        execute_query("DELETE FROM cash_register WHERE description = ?", (trans_id,))
        load_transactions()
        update_dashboard()
        show_toast("success", translate("transaction_deleted"))

    def generate_pdf_report():
        """Gera um relatório em PDF detalhado de uma transação selecionada."""
        selected_item = transaction_table.selection()
        if not selected_item:
            show_toast("error", translate("select_transaction"))
            return

        transaction_data = transaction_table.item(selected_item)["values"]
        description, amount, date = transaction_data  # Desempacotamos os valores

        # Certifique-se de que o valor `amount` seja convertido para float antes de formatar
        try:
            amount = float(amount)
        except ValueError:
            show_toast("error", translate("invalid_amount"))
            return

        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        pdf_file = os.path.join(os.getcwd(), f"{description}_report.pdf")

        c = canvas.Canvas(pdf_file, pagesize=letter)
        c.setFont("Helvetica", 12)
        c.drawString(50, 750, "Transaction Report")
        c.drawString(50, 730, f"Description: {description}")
        c.drawString(50, 710, f"Amount: ${amount:.2f}")  # Agora funciona porque amount é float
        c.drawString(50, 690, f"Date: {date}")
        c.save()

        # Abre o PDF automaticamente no navegador padrão
        import webbrowser
        webbrowser.open(pdf_file)

        show_toast("success", translate("report_generated"))


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

        ttk.Button(transaction_window, text=translate("save"), command=save_transaction, bootstyle="success").pack(pady=10)

    def show_toast(type_, message):
        """Mostra notificações discretas."""
        toast = ttk.Label(action_frame, text=message, bootstyle=type_)
        toast.pack(side=LEFT, padx=10, pady=10)
        toast.after(3000, toast.destroy)

    load_transactions()
    update_dashboard()
