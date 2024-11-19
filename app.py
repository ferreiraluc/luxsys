import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from core.database import fetch_all
from modules import products, clients, sales, cash_register
from modules.product_manager import open_product_manager


from modules.product_manager import open_product_manager  # Importa a janela de gerenciamento de produtos

def main():
    """Initialize the application and display the main menu."""
    app = ttk.Window(themename="darkly")  # Tema moderno
    app.title("Luxsys - Sistema de Importadora")
    app.geometry("1024x768")

    # Layout Principal
    frame = ttk.Frame(app, padding=10)
    frame.pack(fill=BOTH, expand=True)

    # Título
    ttk.Label(frame, text="Luxsys - Sistema de Importadora", font=("Helvetica", 24, "bold")).pack(pady=10)

    # Divisão da tela
    content_frame = ttk.Frame(frame)
    content_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

    # Listagem de Produtos (Quadrado 1)
    product_frame = ttk.LabelFrame(content_frame, text="Produtos Disponíveis no Estoque", padding=10, bootstyle="info")
    product_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    product_table = ttk.Treeview(product_frame, columns=("ID", "Nome", "Preço (USD)", "Quantidade"), show="headings", height=10)
    product_table.pack(fill=BOTH, expand=True, padx=5, pady=5)

    for col in ("ID", "Nome", "Preço (USD)", "Quantidade"):
        product_table.heading(col, text=col)

    # Botões "Abrir" e "Atualizar"
    product_button_frame = ttk.Frame(product_frame, padding=5)
    product_button_frame.pack(fill=X, pady=5)

    ttk.Button(product_button_frame, text="Abrir Gerenciamento de Produtos", command=open_product_manager, bootstyle=PRIMARY).pack(side=LEFT, padx=5)

    def refresh_products():
        """Atualiza a tabela de produtos."""
        load_products()

    ttk.Button(product_button_frame, text="Atualizar", command=refresh_products, bootstyle=SUCCESS).pack(side=LEFT, padx=5)

    def load_products():
        """Carrega os produtos do banco de dados e exibe na tabela."""
        # Limpa a tabela antes de recarregar
        for row in product_table.get_children():
            product_table.delete(row)
        # Recarrega os dados do banco
        rows = fetch_all("SELECT id, name, price, quantity FROM products")
        for row in rows:
            product_table.insert("", "end", values=row)

    load_products()

    # Listagem de Vendas Recentes (Quadrado 2)
    sales_frame = ttk.LabelFrame(content_frame, text="Vendas Recentes", padding=10, bootstyle="info")
    sales_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    sales_table = ttk.Treeview(sales_frame, columns=("ID", "Cliente", "Total (USD)", "Data"), show="headings", height=10)
    sales_table.pack(fill=BOTH, expand=True, padx=5, pady=5)

    for col in ("ID", "Cliente", "Total (USD)", "Data"):
        sales_table.heading(col, text=col)

    def load_sales():
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

    load_sales()

    # Botões do menu principal
    button_frame = ttk.Frame(frame, padding=10)
    button_frame.pack(pady=10)

    button_style = {"bootstyle": "primary", "width": 20, "padding": 10}

    ttk.Button(button_frame, text="Cadastro de Produtos", command=products.open, **button_style).grid(row=0, column=0, padx=20, pady=10)
    ttk.Button(button_frame, text="Cadastro de Clientes", command=clients.open, **button_style).grid(row=1, column=0, padx=20, pady=10)
    ttk.Button(button_frame, text="Cadastro de Vendas", command=sales.open, **button_style).grid(row=0, column=1, padx=20, pady=10)
    ttk.Button(button_frame, text="Caixa", command=cash_register.open, **button_style).grid(row=1, column=1, padx=20, pady=10)

    # Configurações de redimensionamento
    content_frame.columnconfigure(0, weight=1)
    content_frame.columnconfigure(1, weight=1)
    content_frame.rowconfigure(0, weight=1)

    # Rodar a aplicação
    app.mainloop()


if __name__ == "__main__":
    main()
