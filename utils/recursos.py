"""Acha os arquivos de assets tanto no script quanto dentro do .exe."""
import os
import sys

import customtkinter as ctk
from PIL import Image

_cache = {}


def caminho_recurso(*partes):
    # No .exe (PyInstaller) os arquivos ficam numa pasta temporária (_MEIPASS).
    base = getattr(sys, "_MEIPASS", None)
    if not base:
        base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, *partes)


def carregar_icone(pasta, nome, tamanho):
    """Carrega assets/<pasta>/<nome> como CTkImage. Retorna None se faltar o arquivo."""
    chave = (pasta, nome, tamanho)
    if chave not in _cache:  # guardar evita que o Tk descarte a imagem
        try:
            img = Image.open(caminho_recurso("assets", pasta, nome))
            img.load()
            _cache[chave] = ctk.CTkImage(
                light_image=img, dark_image=img, size=(tamanho, tamanho)
            )
        except (OSError, FileNotFoundError):
            _cache[chave] = None
    return _cache[chave]
