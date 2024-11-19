import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from core.database import execute_query, fetch_all

def open():
    """Open the client management window."""
    client_window = ttk.Toplevel()
    client_window.title("Cadastro de Clientes")
    client_window.geometry("500x300")

    # Input fields
    ttk.Label(client_window, text="Nome do Cliente:").grid(row=0, column=0, padx=10, pady=5)
    name_entry = ttk.Entry(client_window)
    name_entry.grid(row=0, column=1, padx=10, pady=5)

    ttk.Label(client_window, text="Telefone:").grid(row=1, column=0, padx=10, pady=5)
    phone_entry = ttk.Entry(client_window)
    phone_entry.grid(row=1, column=1, padx=10, pady=5)

    ttk.Label(client_window, text="Cidade:").grid(row=2, column=0, padx=10, pady=5)
    city_entry = ttk.Entry(client_window)
    city_entry.grid(row=2, column=1, padx=10, pady=5)

    # Save button
    def save_client():
        """Save the client to the database."""
        name = name_entry.get()
        phone = phone_entry.get()
        city = city_entry.get()

        execute_query("""
            INSERT INTO clients (name, phone, city)
            VALUES (?, ?, ?)
        """, (name, phone, city))

        # Confirmation message
        ttk.Label(client_window, text="Cliente salvo com sucesso!", foreground="green").grid(row=4, column=0, columnspan=2, pady=10)

    ttk.Button(client_window, text="Salvar", command=save_client, bootstyle=SUCCESS).grid(row=3, column=0, columnspan=2, pady=20)

    # Display all clients
    def show_clients():
        """Display all clients in the database."""
        rows = fetch_all("SELECT * FROM clients")
        for i, row in enumerate(rows, start=6):
            ttk.Label(client_window, text=f"{row[0]}: {row[1]} - {row[2]} - {row[3]}").grid(row=i, column=0, columnspan=2, pady=2)

    show_clients()
