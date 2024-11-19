import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from core.database import execute_query, fetch_all

def open():
    """Open the cash register management window."""
    cash_window = ttk.Toplevel()
    cash_window.title("Gerenciamento de Caixa")
    cash_window.geometry("600x400")

    # Entrada de descrição
    ttk.Label(cash_window, text="Descrição:", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=5, sticky=W)
    description_entry = ttk.Entry(cash_window)
    description_entry.grid(row=0, column=1, padx=10, pady=5)

    # Entrada de valor
    ttk.Label(cash_window, text="Valor:", font=("Helvetica", 12)).grid(row=1, column=0, padx=10, pady=5, sticky=W)
    amount_entry = ttk.Entry(cash_window)
    amount_entry.grid(row=1, column=1, padx=10, pady=5)

    # Tipo de transação
    ttk.Label(cash_window, text="Tipo:", font=("Helvetica", 12)).grid(row=2, column=0, padx=10, pady=5, sticky=W)
    transaction_type = ttk.Combobox(cash_window, state="readonly", values=["Entrada", "Saída"])
    transaction_type.grid(row=2, column=1, padx=10, pady=5)

    def register_transaction():
        """Register a financial transaction."""
        description = description_entry.get()
        amount = float(amount_entry.get())
        t_type = transaction_type.get()

        if not description or not amount or not t_type:
            ttk.Label(cash_window, text="Preencha todos os campos.", foreground="red").grid(row=4, column=0, columnspan=2)
            return

        # Ajusta o valor para saída
        if t_type == "Saída":
            amount = -abs(amount)

        # Salva no banco
        execute_query("INSERT INTO cash_register (description, amount, transaction_date) VALUES (?, ?, datetime('now'))", (description, amount))
        ttk.Label(cash_window, text="Transação registrada com sucesso!", foreground="green").grid(row=4, column=0, columnspan=2)

    ttk.Button(cash_window, text="Registrar Transação", command=register_transaction, bootstyle=PRIMARY).grid(row=3, column=0, columnspan=2, pady=10)

    # Exibe transações recentes
    columns = ("Descrição", "Valor", "Data")
    transaction_table = ttk.Treeview(cash_window, columns=columns, show="headings", height=10)
    transaction_table.grid(row=5, column=0, columnspan=2, padx=10, pady=20)

    for col in columns:
        transaction_table.heading(col, text=col)

    def load_transactions():
        """Load recent transactions into the table."""
        rows = fetch_all("SELECT description, amount, transaction_date FROM cash_register ORDER BY transaction_date DESC LIMIT 10")
        for row in rows:
            transaction_table.insert("", "end", values=row)

    load_transactions()
