import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from core.database import execute_query, fetch_all
from core.utils import translate

def open():
    """Abre a janela de gerenciamento de clientes."""
    client_window = ttk.Toplevel()
    client_window.title(translate("clients_button"))
    client_window.geometry("800x700")
    client_window.rowconfigure(7, weight=1)  # Tornar a tabela responsiva
    client_window.columnconfigure(0, weight=1)
    client_window.columnconfigure(1, weight=1)

    # Campos de entrada
    ttk.Label(client_window, text=translate("client_name")).grid(row=0, column=0, padx=10, pady=5, sticky=W)
    name_entry = ttk.Entry(client_window, width=30)
    name_entry.grid(row=0, column=1, padx=10, pady=5, sticky=EW)

    ttk.Label(client_window, text=translate("phone")).grid(row=1, column=0, padx=10, pady=5, sticky=W)
    phone_entry = ttk.Entry(client_window, width=30)
    phone_entry.grid(row=1, column=1, padx=10, pady=5, sticky=EW)

    ttk.Label(client_window, text=translate("city")).grid(row=2, column=0, padx=10, pady=5, sticky=W)
    city_entry = ttk.Entry(client_window, width=30)
    city_entry.grid(row=2, column=1, padx=10, pady=5, sticky=EW)

    # Mensagem de confirmação
    confirmation_label = ttk.Label(client_window, text="", foreground="green")
    confirmation_label.grid(row=3, column=0, columnspan=2, pady=5)

    # Botão de salvar cliente
    def save_client():
        """Salva o cliente no banco de dados."""
        name = name_entry.get().strip()
        phone = phone_entry.get().strip()
        city = city_entry.get().strip()

        if not name or not phone or not city:
            confirmation_label.config(text=translate("error_fill_fields"), foreground="red")
            return

        if "selected_client_id" in globals() and selected_client_id is not None:
            # Editar cliente existente
            execute_query("""
                UPDATE clients SET name = ?, phone = ?, city = ?
                WHERE id = ?
            """, (name, phone, city, selected_client_id))
            confirmation_label.config(text=translate("success_client_updated"), foreground="green")
        else:
            # Inserir novo cliente
            execute_query("""
                INSERT INTO clients (name, phone, city)
                VALUES (?, ?, ?)
            """, (name, phone, city))
            confirmation_label.config(text=translate("success_client_saved"), foreground="green")

        clear_form()
        load_clients()

    save_button = ttk.Button(client_window, text=translate("save"), command=save_client, bootstyle=SUCCESS)
    save_button.grid(row=4, column=1, padx=10, pady=10, sticky=EW)

    # Configuração da tabela de clientes
    columns = (translate("id"), translate("client_name"), translate("phone"), translate("city"))
    client_table = ttk.Treeview(client_window, columns=columns, show="headings", height=10)
    client_table.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky=NSEW)

    client_table.column(translate("id"), anchor="center", width=50)
    client_table.column(translate("client_name"), anchor="w", width=200)
    client_table.column(translate("phone"), anchor="center", width=150)
    client_table.column(translate("city"), anchor="w", width=150)

    for col in columns:
        client_table.heading(col, text=col)

    # Configuração do Scrollbar
    scrollbar = ttk.Scrollbar(client_window, orient=VERTICAL, command=client_table.yview)
    client_table.configure(yscroll=scrollbar.set)
    scrollbar.grid(row=5, column=2, sticky=NS)

    # Função para carregar os clientes
    def load_clients():
        """Carrega todos os clientes na tabela."""
        for row in client_table.get_children():
            client_table.delete(row)

        rows = fetch_all("SELECT id, name, phone, city FROM clients ORDER BY id DESC")
        for row in rows:
            client_table.insert("", "end", values=row)

    # Função para preencher o formulário com os dados do cliente selecionado
    def edit_client():
        """Preenche os campos de entrada para edição de cliente."""
        global selected_client_id
        selected_item = client_table.selection()
        if not selected_item:
            confirmation_label.config(text=translate("error_select_client"), foreground="red")
            return

        client_data = client_table.item(selected_item, "values")
        selected_client_id = client_data[0]  # ID do cliente
        name_entry.delete(0, 'end')
        name_entry.insert(0, client_data[1])
        phone_entry.delete(0, 'end')
        phone_entry.insert(0, client_data[2])
        city_entry.delete(0, 'end')
        city_entry.insert(0, client_data[3])
        confirmation_label.config(text=translate("editing_client"), foreground="blue")

    # Função para limpar o formulário
    def clear_form():
        """Limpa os campos de entrada e reseta a seleção."""
        global selected_client_id
        selected_client_id = None
        name_entry.delete(0, 'end')
        phone_entry.delete(0, 'end')
        city_entry.delete(0, 'end')
        confirmation_label.config(text="", foreground="green")

    # Botão para editar cliente
    ttk.Button(client_window, text=translate("edit_client"), command=edit_client, bootstyle=INFO, width=20).grid(row=6, column=0, pady=10, padx=5, sticky=EW)

    # Botão para deletar cliente
    def delete_client():
        """Exclui o cliente selecionado."""
        selected_item = client_table.selection()
        if not selected_item:
            confirmation_label.config(text=translate("error_select_client"), foreground="red")
            return

        client_id = client_table.item(selected_item, "values")[0]
        execute_query("DELETE FROM clients WHERE id = ?", (client_id,))
        confirmation_label.config(text=translate("success_client_deleted"), foreground="green")
        load_clients()

    ttk.Button(client_window, text=translate("delete_client"), command=delete_client, bootstyle=DANGER, width=20).grid(row=6, column=1, pady=10, padx=5, sticky=EW)

    # Carregar clientes ao abrir a janela
    load_clients()
