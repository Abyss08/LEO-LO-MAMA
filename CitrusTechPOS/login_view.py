import tkinter as tk
from tkinter import ttk, messagebox
import database

class LoginView(tk.Toplevel):
    def __init__(self, app_controller):
        super().__init__()
        self.app_controller = app_controller
        self.title("Citrus Tech - Iniciar Sesión")
        self.geometry("350x250")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.master = app_controller
        self.master.eval(f'tk::PlaceWindow {str(self)} center')

        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="Iniciar Sesión", font=("Segoe UI", 16, "bold")).pack(pady=(0, 20))

        ttk.Label(main_frame, text="Nombre de Usuario:").pack(anchor="w")
        self.user_entry = ttk.Entry(main_frame)
        self.user_entry.pack(fill="x", pady=(0, 10))

        ttk.Label(main_frame, text="Contraseña:").pack(anchor="w")
        self.pass_entry = ttk.Entry(main_frame, show="*")
        self.pass_entry.pack(fill="x", pady=(0, 20))
        self.pass_entry.bind("<Return>", self.intentar_login)

        ttk.Button(main_frame, text="Ingresar", command=self.intentar_login, style="Accent.TButton").pack(fill="x")

    def intentar_login(self, event=None):
        username = self.user_entry.get()
        password = self.pass_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Todos los campos son requeridos.", parent=self)
            return

        user_info = database.verificar_usuario(username, password)

        if user_info:
            self.destroy()
            self.app_controller.mostrar_vista_principal(user_info)
        else:
            messagebox.showerror("Error de Autenticación", "Usuario o contraseña incorrectos.", parent=self)

    def on_closing(self):
        self.app_controller.destroy()