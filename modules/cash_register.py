import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from core.database import execute_query, fetch_all

def open():
    """Open the cash register management window."""
    cash_window = ttk.Toplevel()
    cash_window.title("Gerenciamento de Caixa")
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
    ttk.Label(form_frame, text="Descrição:", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=5, sticky=W)
    description_entry = ttk.Entry(form_frame)
    description_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

    # Entrada de valor
    ttk.Label(form_frame, text="Valor:", font=("Helvetica", 12)).grid(row=1, column=0, padx=10, pady=5, sticky=W)
    amount_entry = ttk.Entry(form_frame)
    amount_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

    # Tipo de transação
    ttk.Label(form_frame, text="Tipo:", font=("Helvetica", 12)).grid(row=2, column=0, padx=10, pady=5, sticky=W)
    transaction_type = ttk.Combobox(form_frame, state="readonly", values=["Entrada", "Saída"])
    transaction_type.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

    # Botão Registrar Transação
    def register_transaction():
        """Register a financial transaction."""
        description = description_entry.get()
        amount = float(amount_entry.get())
        t_type = transaction_type.get()

        if not description or not amount or not t_type:
            ttk.Label(form_frame, text="Preencha todos os campos.", foreground="red").grid(row=4, column=0, columnspan=2)
            return

        # Ajusta o valor para saída
        if t_type == "Saída":
            amount = -abs(amount)

        # Salva no banco
        execute_query("INSERT INTO cash_register (description, amount, transaction_date) VALUES (?, ?, datetime('now'))", (description, amount))
        ttk.Label(form_frame, text="Transação registrada com sucesso!", foreground="green").grid(row=4, column=0, columnspan=2)
        load_transactions()

    ttk.Button(form_frame, text="Registrar Transação", command=register_transaction, bootstyle=PRIMARY).grid(row=3, column=0, columnspan=2, pady=10)

    # Tabela de Transações
    columns = ("Descrição", "Valor", "Data")
    transaction_table = ttk.Treeview(cash_window, columns=columns, show="headings", height=10)
    transaction_table.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    # Configurações das colunas
    transaction_table.column("Descrição", anchor="w", width=300)
    transaction_table.column("Valor", anchor="e", width=100)
    transaction_table.column("Data", anchor="center", width=200)

    transaction_table.heading("Descrição", text="Descrição")
    transaction_table.heading("Valor", text="Valor")
    transaction_table.heading("Data", text="Data")

    # Carregar Transações
    def load_transactions():
        """Load recent transactions into the table."""
        for row in transaction_table.get_children():
            transaction_table.delete(row)

        rows = fetch_all("SELECT description, amount, transaction_date FROM cash_register ORDER BY transaction_date DESC LIMIT 10")
        for row in rows:
            transaction_table.insert("", "end", values=row)

    load_transactions()

    # Tornando a tabela responsiva
    cash_window.rowconfigure(1, weight=1)
    cash_window.columnconfigure(0, weight=1)
