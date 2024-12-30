import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from core.database import authenticate_user
from app import main as open_main_app  # Importa a função principal do app

def open_login():
    """Abre a janela de login."""
    login_window = ttk.Window(themename="darkly")
    login_window.title("Login")
    login_window.geometry("400x300")
    login_window.resizable(False, False)

    # Labels e Entradas
    ttk.Label(login_window, text="Usuário:", font=("Helvetica", 12)).pack(pady=10)
    username_entry = ttk.Entry(login_window, width=30)
    username_entry.pack(pady=5)

    ttk.Label(login_window, text="Senha:", font=("Helvetica", 12)).pack(pady=10)
    password_entry = ttk.Entry(login_window, width=30, show="*")
    password_entry.pack(pady=5)

    def handle_login():
        """Lida com a autenticação do usuário."""
        username = username_entry.get().strip()
        password = password_entry.get().strip()

        if authenticate_user(username, password):
            messagebox.showinfo("Sucesso", "Login realizado com sucesso!")
            login_window.destroy()  # Fecha a janela de login
            open_main_app()  # Abre o app principal
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos!")

    ttk.Button(login_window, text="Entrar", command=handle_login, bootstyle=SUCCESS).pack(pady=20)

    login_window.mainloop()
