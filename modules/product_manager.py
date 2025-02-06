import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from core.database import execute_query, fetch_all
# Certifique-se de que as funções translate e sort_column estejam definidas ou importadas corretamente
from core.utils import translate

def open_product_manager(product_id=None):
    """Abre a aba de gerenciamento de produtos."""
    product_window = ttk.Toplevel()
    product_window.title("Gerenciamento de Produtos")
    product_window.geometry("1024x768")

    # Barra de busca
    search_frame = ttk.Frame(product_window, padding=10)
    search_frame.pack(fill=X)
    ttk.Label(search_frame, text="Buscar por Nome ou Código:").pack(side=LEFT, padx=5)
    search_entry = ttk.Entry(search_frame, width=50)
    search_entry.pack(side=LEFT, padx=5)
    search_button = ttk.Button(
        search_frame, text="Buscar", bootstyle=PRIMARY,
        command=lambda: search_products(search_entry.get())
    )
    search_button.pack(side=LEFT, padx=5)

    # Listagem de Produtos
    columns = ("ID", "Código", "Nome", "Preço (USD)", "Quantidade", "Editar", "Excluir")
    product_table = ttk.Treeview(product_window, columns=columns, show="headings", height=15)
    product_table.pack(fill=BOTH, expand=True, padx=10, pady=10)

    for col in columns:
        # A função sort_column deve estar definida (veja abaixo)
        product_table.heading(col, text=col, command=lambda c=col: sort_column(product_table, c, False))
        product_table.column(col, anchor="center", width=120)

    def load_products():
        """Carrega todos os produtos no Treeview."""
        for row in product_table.get_children():
            product_table.delete(row)
        rows = fetch_all("SELECT id, code, name, price, quantity FROM products ORDER BY id DESC")
        for row in rows:
            product_table.insert("", "end", values=row + ("Editar", "Excluir"))

    def sort_column(treeview, col, reverse):
        """Ordena a tabela ao clicar no cabeçalho."""
        data = [(treeview.set(child, col), child) for child in treeview.get_children()]
        # Para colunas numéricas, tenta converter o valor para float
        data.sort(reverse=reverse, key=lambda x: float(x[0]) if col in ("ID", "Preço (USD)", "Quantidade") and x[0] != "" else x[0])
        for index, (_, child) in enumerate(data):
            treeview.move(child, '', index)
        treeview.heading(col, command=lambda: sort_column(treeview, col, not reverse))

    def search_products(search_term):
        """Busca produtos com base no nome ou código."""
        query = """
            SELECT id, code, name, price, quantity
            FROM products
            WHERE name LIKE ? OR code LIKE ?
            ORDER BY id DESC
        """
        rows = fetch_all(query, (f"%{search_term}%", f"%{search_term}%"))
        for row in product_table.get_children():
            product_table.delete(row)
        for row in rows:
            product_table.insert("", "end", values=row + ("Editar", "Excluir"))

    def confirm_delete(product_id):
        """Exibe um pop-up para confirmação de exclusão."""
        confirm_window = ttk.Toplevel()
        confirm_window.title("Confirmar Exclusão")
        confirm_window.geometry("250x150")
        ttk.Label(confirm_window, text="Tem certeza que deseja excluir este produto?", wraplength=250).pack(pady=10)

        def delete_product():
            execute_query("DELETE FROM products WHERE id = ?", (product_id,))
            load_products()
            confirm_window.destroy()

        ttk.Button(confirm_window, text="Sim", bootstyle=DANGER, command=delete_product).pack(pady=10)
        ttk.Button(confirm_window, text="Não", bootstyle=SUCCESS, command=confirm_window.destroy).pack(pady=10)

    def edit_product(product_id):
        """Abre uma janela para editar o produto e ver seu histórico de compras."""
        edit_window = ttk.Toplevel()
        edit_window.title("Editar Produto")
        edit_window.geometry("500x500")

        product = fetch_all("SELECT id, code, name, price, quantity FROM products WHERE id = ?", (product_id,))
        if not product:
            ttk.Label(edit_window, text="Produto não encontrado.", foreground="red").pack(pady=10)
            return
        product = product[0]

        # Campos de edição
        ttk.Label(edit_window, text="Código:").pack(pady=5)
        code_entry = ttk.Entry(edit_window, width=30)
        code_entry.insert(0, product[1])
        code_entry.pack(pady=5)

        ttk.Label(edit_window, text="Nome:").pack(pady=5)
        name_entry = ttk.Entry(edit_window, width=30)
        name_entry.insert(0, product[2])
        name_entry.pack(pady=5)

        ttk.Label(edit_window, text="Preço:").pack(pady=5)
        price_entry = ttk.Entry(edit_window, width=30)
        price_entry.insert(0, product[3])
        price_entry.pack(pady=5)

        ttk.Label(edit_window, text="Quantidade:").pack(pady=5)
        quantity_entry = ttk.Entry(edit_window, width=30)
        quantity_entry.insert(0, product[4])
        quantity_entry.pack(pady=5)

        def save_changes():
            """Salva as alterações no banco de dados."""
            code = code_entry.get().strip()
            name = name_entry.get().strip()
            price = float(price_entry.get().strip())
            quantity = int(quantity_entry.get().strip())
            execute_query(
                "UPDATE products SET code = ?, name = ?, price = ?, quantity = ? WHERE id = ?",
                (code, name, price, quantity, product_id)
            )
            ttk.Label(edit_window, text="Alterações salvas com sucesso!", foreground="green").pack(pady=10)
            load_products()

        ttk.Button(edit_window, text="Salvar Alterações", bootstyle=SUCCESS, command=save_changes).pack(pady=10)

        # Botão para ver histórico de compras do produto
        ttk.Button(edit_window, text="Ver Histórico de Compras", bootstyle=INFO,
                   command=lambda: view_product_history(product_id)).pack(pady=10)

    def view_product_history(product_id):
        """Abre uma janela exibindo o histórico de compras do produto."""
        history_window = ttk.Toplevel()
        history_window.title("Histórico de Compras")
        history_window.geometry("600x400")
        columns = ("Venda ID", "Cliente", "Quantidade", "Data", "Total (USD)")
        history_table = ttk.Treeview(history_window, columns=columns, show="headings", height=10)
        history_table.pack(fill="both", expand=True, padx=10, pady=10)
        for col in columns:
            history_table.heading(col, text=col)
            history_table.column(col, anchor="center", width=100)
        # Consulta que une as tabelas de vendas, itens de venda, clientes e produtos
        query = """
            SELECT s.id, c.name, sp.quantity, s.sale_date, (sp.quantity * p.price) as total
            FROM sales_products sp
            JOIN sales s ON sp.sale_id = s.id
            JOIN clients c ON s.client_id = c.id
            JOIN products p ON sp.product_id = p.id
            WHERE p.id = ?
            ORDER BY s.sale_date DESC
        """
        rows = fetch_all(query, (product_id,))
        for row in rows:
            history_table.insert("", "end", values=row)

    def on_action(event):
        """Determina a ação (editar ou excluir) ao clicar em uma célula da tabela."""
        selected_item = product_table.selection()
        if selected_item:
            item_values = product_table.item(selected_item[0], "values")
            action = product_table.identify_column(event.x).replace("#", "")
            if action == "6":  # Editar
                edit_product(item_values[0])
            elif action == "7":  # Excluir
                confirm_delete(item_values[0])

    product_table.bind("<ButtonRelease-1>", on_action)

    # Adicionar Novo Produto no Rodapé
    add_frame = ttk.Frame(product_window, padding=10)
    add_frame.pack(fill=X, pady=10)

    ttk.Label(add_frame, text="Código:").pack(side=LEFT, padx=5)
    code_entry = ttk.Entry(add_frame, width=10)
    code_entry.pack(side=LEFT, padx=5)

    ttk.Label(add_frame, text="Nome:").pack(side=LEFT, padx=5)
    name_entry = ttk.Entry(add_frame, width=20)
    name_entry.pack(side=LEFT, padx=5)

    ttk.Label(add_frame, text="Preço:").pack(side=LEFT, padx=5)
    price_entry = ttk.Entry(add_frame, width=10)
    price_entry.pack(side=LEFT, padx=5)

    ttk.Label(add_frame, text="Quantidade:").pack(side=LEFT, padx=5)
    quantity_entry = ttk.Entry(add_frame, width=10)
    quantity_entry.pack(side=LEFT, padx=5)

    def add_product():
        """Adiciona um novo produto ao banco de dados."""
        if not code_entry.get() or not name_entry.get() or not price_entry.get() or not quantity_entry.get():
            return
        execute_query(
            "INSERT INTO products (code, name, price, quantity) VALUES (?, ?, ?, ?)",
            (code_entry.get().strip(), name_entry.get().strip(), float(price_entry.get()), int(quantity_entry.get()))
        )
        load_products()

    ttk.Button(add_frame, text="Adicionar Produto", bootstyle=SUCCESS, command=add_product).pack(side=LEFT, padx=5)

    # Carregar produtos ao iniciar
    load_products()

# Para testes, se executado diretamente:
if __name__ == "__main__":
    open_product_manager()
