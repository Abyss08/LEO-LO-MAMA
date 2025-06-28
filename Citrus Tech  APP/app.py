import tkinter as tk
from tkinter import ttk
from login_view import LoginView
from main_view import MainView

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Citrus Tech POS")
        self.withdraw()

        self.user_info = None
        self.mostrar_login()

    def mostrar_login(self):
        login_window = LoginView(self)
        login_window.grab_set()

    def mostrar_vista_principal(self, user_info):
        self.user_info = user_info
        self.deiconify()

        # Aplicar estilo
        style = ttk.Style(self)
        style.theme_use("clam") # Un tema moderno
        style.configure("Accent.TButton", foreground="white", background="#0078D7")
        style.configure("Delete.TButton", foreground="white", background="#E81123")

        self.main_view = MainView(self, user_info)
        self.main_view.pack(fill="both", expand=True)
        self.geometry("1100x700")
        self.state('zoomed')