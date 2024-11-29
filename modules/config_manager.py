import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from core.utils import apply_zoom, switch_language, translate


def open_config_manager(app):
    """Abre a janela de configurações."""
    config_window = ttk.Toplevel(app)
    config_window.title(translate("settings"))
    config_window.geometry("400x300")

    # Zoom Config
    zoom_frame = ttk.LabelFrame(config_window, text=translate("zoom_settings"), padding=10)
    zoom_frame.pack(fill="x", padx=10, pady=10)

    ttk.Button(zoom_frame, text="+", command=lambda: apply_zoom(app, 1.2)).pack(side=LEFT, padx=5)
    ttk.Button(zoom_frame, text="-", command=lambda: apply_zoom(app, 0.8)).pack(side=LEFT, padx=5)

    # Language Config
    language_frame = ttk.LabelFrame(config_window, text=translate("language_settings"), padding=10)
    language_frame.pack(fill="x", padx=10, pady=10)

    ttk.Button(
        language_frame, text="🇧🇷", bootstyle="success",
        command=lambda: switch_language("pt", {"app": app})
    ).pack(side=LEFT, padx=5)
    ttk.Button(
        language_frame, text="🇺🇸", bootstyle="info",
        command=lambda: switch_language("en", {"app": app})
    ).pack(side=LEFT, padx=5)
    ttk.Button(
        language_frame, text="🇪🇸", bootstyle="warning",
        command=lambda: switch_language("es", {"app": app})
    ).pack(side=LEFT, padx=5)
