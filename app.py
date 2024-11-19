import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from core.utils import set_language, translate
from core.database import fetch_all
from modules import products, clients, sales, cash_register
from modules.product_manager import open_product_manager


def main():
    """Initialize the application and display the main menu."""
    app = ttk.Window(themename="darkly")
    app.title(translate("title"))
    app.geometry("1024x768")

    # Layout Principal
    frame = ttk.Frame(app, padding=10)
    frame.pack(fill=BOTH, expand=True)

    # Título
    title_label = ttk.Label(frame, text=translate("title"), font=("Helvetica", 24, "bold"))
    title_label.pack(pady=10)

    # Botões de Idioma
    language_frame = ttk.Frame(frame, padding=10)
    language_frame.pack(fill=X, pady=10)
    ttk.Button(language_frame, text="🇧🇷", bootstyle="success", command=lambda: switch_language("pt")).pack(side=LEFT, padx=5)
    ttk.Button(language_frame, text="🇺🇸", bootstyle="info", command=lambda: switch_language("en")).pack(side=LEFT, padx=5)

    # Divisão da tela
    content_frame = ttk.Frame(frame)
    content_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    # Listagem de Produtos (Quadrado 1)
    product_frame = ttk.LabelFrame(content_frame, text=translate("products_available"), padding=10, bootstyle="info")
    product_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    product_table = ttk.Treeview(product_frame, columns=("ID", "Nome", "Preço (USD)", "Quantidade"), show="headings", height=10)
    product_table.pack(fill=BOTH, expand=True, padx=5, pady=5)

    for col in ("ID", "Nome", "Preço (USD)", "Quantidade"):
        product_table.heading(col, text=col)

    # Botões "Abrir" e "Atualizar"
    product_button_frame = ttk.Frame(product_frame, padding=5)
    product_button_frame.pack(fill=X, pady=5)

    open_management_button = ttk.Button(product_button_frame, text=translate("open_management"), command=open_product_manager, bootstyle=PRIMARY)
    open_management_button.pack(side=LEFT, padx=5)

    refresh_button = ttk.Button(product_button_frame, text=translate("refresh"), command=lambda: load_products(product_table), bootstyle=SUCCESS)
    refresh_button.pack(side=LEFT, padx=5)

    load_products(product_table)

    # Listagem de Vendas Recentes (Quadrado 2)
    sales_frame = ttk.LabelFrame(content_frame, text=translate("recent_sales"), padding=10, bootstyle="info")
    sales_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    sales_table = ttk.Treeview(sales_frame, columns=("ID", "Cliente", "Total (USD)", "Data"), show="headings", height=10)
    sales_table.pack(fill=BOTH, expand=True, padx=5, pady=5)

    for col in ("ID", "Cliente", "Total (USD)", "Data"):
        sales_table.heading(col, text=col)

    load_sales(sales_table)

    # Botões do menu principal
    button_frame = ttk.Frame(frame, padding=10)
    button_frame.pack(pady=10)

    products_button = ttk.Button(button_frame, text=translate("products_button"), command=products.open, bootstyle=PRIMARY, width=20, padding=10)
    products_button.grid(row=0, column=0, padx=20, pady=10)

    clients_button = ttk.Button(button_frame, text=translate("clients_button"), command=clients.open, bootstyle=PRIMARY, width=20, padding=10)
    clients_button.grid(row=1, column=0, padx=20, pady=10)

    sales_button = ttk.Button(button_frame, text=translate("sales_button"), command=sales.open, bootstyle=PRIMARY, width=20, padding=10)
    sales_button.grid(row=0, column=1, padx=20, pady=10)

    cash_register_button = ttk.Button(button_frame, text=translate("cash_register_button"), command=cash_register.open, bootstyle=PRIMARY, width=20, padding=10)
    cash_register_button.grid(row=1, column=1, padx=20, pady=10)

    # Configurações de redimensionamento
    content_frame.columnconfigure(0, weight=1)
    content_frame.columnconfigure(1, weight=1)
    content_frame.rowconfigure(0, weight=1)

    def switch_language(language):
        """Altera o idioma do sistema e atualiza todos os textos."""
        set_language(language)
        app.title(translate("title"))
        title_label.config(text=translate("title"))
        product_frame.config(text=translate("products_available"))
        sales_frame.config(text=translate("recent_sales"))
        open_management_button.config(text=translate("open_management"))
        refresh_button.config(text=translate("refresh"))
        products_button.config(text=translate("products_button"))
        clients_button.config(text=translate("clients_button"))
        sales_button.config(text=translate("sales_button"))
        cash_register_button.config(text=translate("cash_register_button"))

    app.mainloop()


def load_products(product_table):
    """Carrega os produtos do banco de dados e exibe na tabela."""
    # Limpa a tabela antes de recarregar
    for row in product_table.get_children():
        product_table.delete(row)
    # Recarrega os dados do banco
    rows = fetch_all("SELECT id, name, price, quantity FROM products")
    for row in rows:
        product_table.insert("", "end", values=row)


def load_sales(sales_table):
    """Carrega as vendas recentes do banco de dados e exibe na tabela."""
    # Limpa a tabela antes de recarregar
    for row in sales_table.get_children():
        sales_table.delete(row)
    # Recarrega os dados do banco
    rows = fetch_all("""
        SELECT s.id, c.name, s.total_amount, s.sale_date
        FROM sales s
        LEFT JOIN clients c ON s.client_id = c.id
        ORDER BY s.sale_date DESC
        LIMIT 10
    """)
    for row in rows:
        sales_table.insert("", "end", values=row)


if __name__ == "__main__":
    main()
