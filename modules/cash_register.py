import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from core.database import execute_query, fetch_all
from core.utils import translate

def open():
    """Abre a janela de gerenciamento de caixa."""
    cash_window = ttk.Toplevel()
    cash_window.title(translate("cash_register_button"))
    cash_window.geometry("800x600")

    # Configuração de Layout Responsivo
    cash_window.rowconfigure(0, weight=1)  # Frame superior (formulários)
    cash_window.rowconfigure(1, weight=3)  # Tabela
    cash_window.columnconfigure(0, weight=1)

    # Frame Superior (Formulários)
    form_frame = ttk.Frame(cash_window, padding=10)
    form_frame.grid(row=0, column=0, sticky="nsew")

    form_frame.columnconfigure(0, weight=1)
    form_frame.columnconfigure(1, weight=2)

    # Entrada de descrição
    ttk.Label(form_frame, text=translate("description"), font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=5, sticky=W)
    description_entry = ttk.Entry(form_frame)
    description_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

    # Entrada de valor
    ttk.Label(form_frame, text=translate("amount"), font=("Helvetica", 12)).grid(row=1, column=0, padx=10, pady=5, sticky=W)
    amount_entry = ttk.Entry(form_frame)
    amount_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

    # Tipo de transação
    ttk.Label(form_frame, text=translate("transaction_type"), font=("Helvetica", 12)).grid(row=2, column=0, padx=10, pady=5, sticky=W)
    transaction_type = ttk.Combobox(form_frame, state="readonly", values=[translate("entry"), translate("exit")])
    transaction_type.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

    # Mensagem de validação
    validation_label = ttk.Label(form_frame, text="", foreground="red")
    validation_label.grid(row=4, column=0, columnspan=2)

    # Botão Registrar Transação
    def register_transaction():
        """Registra uma transação financeira."""
        description = description_entry.get().strip()
        amount = amount_entry.get().strip()
        t_type = transaction_type.get()

        if not description or not amount or not t_type:
            validation_label.config(text=translate("error_fill_fields"), foreground="red")
            return

        try:
            amount = float(amount)
        except ValueError:
            validation_label.config(text=translate("amount_invalid"), foreground="red")
            return

        # Ajusta o valor para saída
        if t_type == translate("exit"):
            amount = -abs(amount)

        # Salva no banco
        execute_query(
            "INSERT INTO cash_register (description, amount, transaction_date) VALUES (?, ?, datetime('now'))",
            (description, amount)
        )
        validation_label.config(text=translate("transaction_saved"), foreground="green")
        load_transactions()

        # Limpa os campos após salvar
        description_entry.delete(0, 'end')
        amount_entry.delete(0, 'end')
        transaction_type.set("")

    ttk.Button(
        form_frame,
        text=translate("register_transaction"),
        command=register_transaction,
        bootstyle=PRIMARY
    ).grid(row=3, column=0, columnspan=2, pady=10)

    # Tabela de Transações
    columns = (translate("description"), translate("amount"), translate("date"))
    transaction_table = ttk.Treeview(cash_window, columns=columns, show="headings", height=10)
    transaction_table.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    # Configurações das colunas
    transaction_table.column(translate("description"), anchor="w", width=300)
    transaction_table.column(translate("amount"), anchor="e", width=100)
    transaction_table.column(translate("date"), anchor="center", width=200)

    for col in columns:
        transaction_table.heading(col, text=col)

    # Carregar Transações
    def load_transactions():
        """Carrega transações recentes na tabela."""
        for row in transaction_table.get_children():
            transaction_table.delete(row)

        rows = fetch_all("SELECT description, amount, transaction_date FROM cash_register ORDER BY transaction_date DESC LIMIT 10")
        for row in rows:
            transaction_table.insert("", "end", values=row)

    load_transactions()

    # Tornando a tabela responsiva
    cash_window.rowconfigure(1, weight=1)
    cash_window.columnconfigure(0, weight=1)
