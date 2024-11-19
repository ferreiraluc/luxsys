from datetime import datetime
from core.translations import translations


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