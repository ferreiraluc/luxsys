import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from core.database import execute_query, fetch_all
from core.utils import translate

def open():
    """Abre a janela de gerenciamento de clientes."""
    client_window = ttk.Toplevel()
    client_window.title(translate("clients_button"))
    client_window.geometry("500x300")

    # Campos de entrada
    ttk.Label(client_window, text=translate("client_name")).grid(row=0, column=0, padx=10, pady=5)
    name_entry = ttk.Entry(client_window)
    name_entry.grid(row=0, column=1, padx=10, pady=5)

    ttk.Label(client_window, text=translate("phone")).grid(row=1, column=0, padx=10, pady=5)
    phone_entry = ttk.Entry(client_window)
    phone_entry.grid(row=1, column=1, padx=10, pady=5)

    ttk.Label(client_window, text=translate("city")).grid(row=2, column=0, padx=10, pady=5)
    city_entry = ttk.Entry(client_window)
    city_entry.grid(row=2, column=1, padx=10, pady=5)

    # Botão de salvar cliente
    def save_client():
        """Salva o cliente no banco de dados."""
        name = name_entry.get().strip()
        phone = phone_entry.get().strip()
        city = city_entry.get().strip()

        if not name or not phone or not city:
            confirmation_label.config(text=translate("error_fill_fields"), foreground="red")
            return

        execute_query("""
            INSERT INTO clients (name, phone, city)
            VALUES (?, ?, ?)
        """, (name, phone, city))

        # Mensagem de confirmação
        confirmation_label.config(text=translate("success_client_saved"), foreground="green")
        name_entry.delete(0, 'end')
        phone_entry.delete(0, 'end')
        city_entry.delete(0, 'end')
        show_clients()

    ttk.Button(client_window, text=translate("save"), command=save_client, bootstyle=SUCCESS).grid(row=3, column=0, columnspan=2, pady=10)

    # Mensagem de confirmação
    confirmation_label = ttk.Label(client_window, text="", foreground="green")
    confirmation_label.grid(row=4, column=0, columnspan=2, pady=5)

    # Exibir todos os clientes cadastrados
    def show_clients():
        """Exibe todos os clientes no banco de dados."""
        for widget in client_list_frame.winfo_children():
            widget.destroy()

        rows = fetch_all("SELECT id, name, phone, city FROM clients ORDER BY id DESC")
        for row in rows:
            ttk.Label(client_list_frame, text=f"{row[0]}: {row[1]} - {row[2]} - {row[3]}").pack(anchor="w", pady=2)

    # Frame para lista de clientes
    client_list_frame = ttk.Frame(client_window)
    client_list_frame.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

    # Carregar clientes ao iniciar
    show_clients()
