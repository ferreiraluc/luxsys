from datetime import datetime
from core.translations import translations
from core.database import fetch_all

def get_current_datetime():
    """Get the current date and time as a formatted string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

current_language = "pt"  # Idioma padrão (português)

def set_language(language):
    """Define o idioma atual."""
    global current_language
    current_language = language

def translate(key):
    """Retorna a tradução para a chave fornecida no idioma atual."""
    return translations[current_language].get(key, key)  # Retorna a chave se não houver tradução

def load_products(product_table):
    """Carrega os produtos do banco de dados e exibe na tabela."""
    product_table.delete(*product_table.get_children())
    rows = fetch_all("SELECT id, name, price, quantity, code FROM products")
    for index, row in enumerate(rows):
        tag = "evenrow" if index % 2 == 0 else "oddrow"
        product_table.insert("", "end", values=row, tags=(tag,))

    # Atualiza os cabeçalhos para o idioma atual
    product_table.heading("ID", text=translate("id"))
    product_table.heading("Nome", text=translate("name"))
    product_table.heading("Preço (USD)", text=translate("price_usd"))
    product_table.heading("Quantidade", text=translate("quantity"))
    product_table.heading("Código", text=translate("code"))

def load_sales(sales_table):
    """Carrega as vendas recentes do banco de dados e exibe na tabela."""
    sales_table.delete(*sales_table.get_children())
    rows = fetch_all("""
        SELECT s.id, c.name, s.total_amount, s.sale_date
        FROM sales s
        LEFT JOIN clients c ON s.client_id = c.id
        ORDER BY s.sale_date DESC
        LIMIT 10
    """)
    for row in rows:
        sales_table.insert("", "end", values=row)

    # Atualiza os cabeçalhos para o idioma atual
    sales_table.heading("ID", text=translate("id"))
    sales_table.heading("Cliente", text=translate("client"))
    sales_table.heading("Total (USD)", text=translate("total_usd"))
    sales_table.heading("Data", text=translate("date"))

def switch_language(language, widgets):
    """Atualiza o idioma do sistema e os textos exibidos."""
    set_language(language)

    # Atualiza textos gerais
    widgets["app"].title(translate("title"))
    widgets["title_label"].config(text=translate("title"))
    widgets["product_frame"].config(text=translate("products_available"))
    widgets["sales_frame"].config(text=translate("recent_sales"))

    # Atualiza botões
    widgets["open_management_button"].config(text=translate("open_management"))
    widgets["refresh_button"].config(text=translate("refresh"))
    widgets["products_button"].config(text=translate("products_button"))
    widgets["clients_button"].config(text=translate("clients_button"))
    widgets["sales_button"].config(text=translate("sales_button"))
    widgets["cash_register_button"].config(text=translate("cash_register_button"))
    widgets["sales_refresh_button"].config(text=translate("refresh"))
    widgets["sales_management_button"].config(text=translate("sales_management"))

    # Atualiza tabelas
    load_products(widgets["product_table"])
    load_sales(widgets["sales_table"])
