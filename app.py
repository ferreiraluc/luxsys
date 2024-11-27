import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from core.utils import (
    translate,
    load_products,
    load_sales,
    switch_language
)
from modules import products, clients, sales, cash_register
from modules.product_manager import open_product_manager
from modules.sales_manager import open_sales_manager


def apply_zoom(app, scale_factor):
    """Aplica zoom a toda a aplicação alterando tamanhos de fontes e widgets."""
    default_font = ttk.Style().lookup("TButton", "font")
    base_size = int(default_font.split()[-1]) if default_font else 12
    new_size = max(8, min(30, int(base_size * scale_factor)))

    # Atualiza estilos globais
    ttk.Style().configure(".", font=("Helvetica", new_size))
    for widget in app.winfo_children():
        widget.configure(font=("Helvetica", new_size))

def adjust_window_to_screen(app):
    """Ajusta a janela ao tamanho da tela e centraliza a posição."""
    screen_width = app.winfo_screenwidth()  # Largura da tela
    screen_height = app.winfo_screenheight()  # Altura da tela

    # Define o tamanho da janela proporcional à resolução
    if screen_width > 1920 and screen_height > 1080:  # Para telas grandes (2K ou superiores)
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
    else:  # Para resoluções padrão (Full HD ou menores)
        window_width = 1280
        window_height = 768

    # Calcula a posição central
    position_x = (screen_width - window_width) // 2
    position_y = (screen_height - window_height) // 2

    # Aplica as dimensões e a posição da janela
    app.geometry(f"{window_width}x{window_height}+{position_x}+{position_y}")


def main():
    """Initialize the application and display the main menu."""
    app = ttk.Window(themename="darkly")
    app.title(translate("title"))
    adjust_window_to_screen(app)

    # Configuração do layout principal
    frame = ttk.Frame(app, padding=10)
    frame.grid(row=0, column=0, sticky="nsew")
    app.rowconfigure(0, weight=1)
    app.columnconfigure(0, weight=1)

    # Barra de Zoom
    zoom_frame = ttk.Frame(app)
    zoom_frame.grid(row=0, column=1, sticky="e", padx=10, pady=10)

    zoom_in_button = ttk.Button(zoom_frame, text="+", command=lambda: apply_zoom(app, 1.2))
    zoom_in_button.pack(side="left", padx=5)

    zoom_out_button = ttk.Button(zoom_frame, text="-", command=lambda: apply_zoom(app, 0.8))
    zoom_out_button.pack(side="left", padx=5)

    # Botões de Idioma no canto superior esquerdo
    language_frame = ttk.Frame(frame, padding=10)
    language_frame.grid(row=0, column=0, sticky="w", padx=5)
    ttk.Button(
        language_frame, text="🇧🇷", bootstyle="success",
        command=lambda: switch_language("pt", get_widgets(app, title_label, product_frame, product_table, sales_frame, sales_table))
    ).pack(side=LEFT, padx=5)
    ttk.Button(
        language_frame, text="🇺🇸", bootstyle="info",
        command=lambda: switch_language("en", get_widgets(app, title_label, product_frame, product_table, sales_frame, sales_table))
    ).pack(side=LEFT, padx=5)
    ttk.Button(
        language_frame, text="🇪🇸", bootstyle="warning",
        command=lambda: switch_language("es", get_widgets(app, title_label, product_frame, product_table, sales_frame, sales_table))
    ).pack(side=LEFT, padx=5)

    # Título
    title_label = ttk.Label(frame, text=translate("title"), font=("Helvetica", 24, "bold"))
    title_label.grid(row=1, column=0, columnspan=2, pady=10, sticky="n")

    # Divisão da tela (frames para produtos e vendas)
    product_frame, product_table = create_product_frame(frame)
    sales_frame, sales_table = create_sales_frame(frame)

    # Botões principais
    button_frame = ttk.Frame(frame, padding=10)
    button_frame.grid(row=3, column=0, columnspan=2, pady=20, sticky="n")
    create_main_buttons(button_frame)

    # Configuração de redimensionamento dos frames
    frame.rowconfigure(2, weight=1)
    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(1, weight=1)

    app.mainloop()


def get_widgets(app, title_label, product_frame, product_table, sales_frame, sales_table):
    return {
        "app": app,
        "title_label": title_label,
        "product_frame": product_frame,
        "sales_frame": sales_frame,
        "product_table": product_table,
        "sales_table": sales_table,
        # Botões
        "open_management_button": open_management_button,
        "refresh_button": refresh_button,
        "sales_refresh_button": sales_refresh_button,
        "sales_management_button": sales_management_button,
        "products_button": products_button,
        "clients_button": clients_button,
        "sales_button": sales_button,
        "cash_register_button": cash_register_button,
    }


def create_product_frame(parent):
    """Cria o frame e a tabela de produtos."""
    product_frame = ttk.LabelFrame(parent, text=translate("products_available"), padding=10, bootstyle="info")
    product_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

    product_table = ttk.Treeview(
        product_frame,
        columns=("ID", "Nome", "Preço (USD)", "Quantidade", "Código"),
        show="headings",
        height=10
    )
    product_table.pack(fill=BOTH, expand=True, padx=5, pady=5)

    product_table.column("ID", anchor="center", width=50)
    product_table.column("Código", anchor="center", width=120)
    product_table.column("Nome", anchor="center", width=100)
    product_table.column("Preço (USD)", anchor="center", width=100)
    product_table.column("Quantidade", anchor="center", width=80)

    product_table.heading("ID", text="ID")
    product_table.heading("Código", text="Código")
    product_table.heading("Nome", text="Nome")
    product_table.heading("Preço (USD)", text="Preço (USD)")
    product_table.heading("Quantidade", text="Quantidade")

    # Botões
    button_frame = ttk.Frame(product_frame)
    button_frame.pack(fill=X, pady=5)

    global open_management_button, refresh_button
    open_management_button = ttk.Button(button_frame, text=translate("open_management"), command=open_product_manager, bootstyle=PRIMARY)
    open_management_button.pack(side=LEFT, padx=5)

    refresh_button = ttk.Button(button_frame, text=translate("refresh"), command=lambda: load_products(product_table), bootstyle=SUCCESS)
    refresh_button.pack(side=LEFT, padx=5)

    load_products(product_table)
    return product_frame, product_table



def create_sales_frame(parent):
    """Cria o frame e a tabela de vendas recentes."""
    sales_frame = ttk.LabelFrame(parent, text=translate("recent_sales"), padding=10, bootstyle="info")
    sales_frame.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")

    sales_table = ttk.Treeview(sales_frame, columns=("ID", "Cliente", "Total (USD)", "Data"), show="headings", height=10)
    sales_table.pack(fill=BOTH, expand=True, padx=5, pady=5)

    sales_table.column("ID", anchor="center", width=50)
    sales_table.column("Cliente", anchor="w", width=100)
    sales_table.column("Total (USD)", anchor="e", width=100)
    sales_table.column("Data", anchor="center", width=120)

    sales_table.heading("ID", text="ID")
    sales_table.heading("Cliente", text="Cliente")
    sales_table.heading("Total (USD)", text="Total (USD)")
    sales_table.heading("Data", text="Data")

    # Botões
    global sales_refresh_button, sales_management_button
    sales_management_button = ttk.Button(sales_frame, text=translate("sales_management"), bootstyle=PRIMARY, command=open_sales_manager)
    sales_management_button.pack(side=LEFT, padx=5)
    sales_refresh_button = ttk.Button(sales_frame, text=translate("refresh"), bootstyle=SUCCESS, command=lambda: load_sales(sales_table))
    sales_refresh_button.pack(side=LEFT, padx=5)

    load_sales(sales_table)
    return sales_frame, sales_table


def create_main_buttons(parent):
    """Cria os botões principais do menu."""
    global products_button, clients_button, sales_button, cash_register_button
    button_style = {"bootstyle": "primary", "width": 20, "padding": 10}

    products_button = ttk.Button(parent, text=translate("products_button"), command=products.open, **button_style)
    products_button.grid(row=0, column=0, padx=20, pady=10)

    clients_button = ttk.Button(parent, text=translate("clients_button"), command=clients.open, **button_style)
    clients_button.grid(row=1, column=0, padx=20, pady=10)

    sales_button = ttk.Button(parent, text=translate("sales_button"), command=sales.open, **button_style)
    sales_button.grid(row=0, column=1, padx=20, pady=10)

    cash_register_button = ttk.Button(parent, text=translate("cash_register_button"), command=cash_register.open, **button_style)
    cash_register_button.grid(row=1, column=1, padx=20, pady=10)


if __name__ == "__main__":
    main()
