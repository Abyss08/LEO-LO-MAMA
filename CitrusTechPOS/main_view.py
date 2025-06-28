import tkinter as tk
from tkinter import ttk
from sales_view import SalesView
from inventory_view import InventoryView
from reports_view import ReportsView

class MainView(tk.Frame):
    def __init__(self, parent, user_info):
        super().__init__(parent)
        self.parent = parent
        self.user_info = user_info

        notebook = ttk.Notebook(self)
        notebook.pack(pady=10, padx=10, fill="both", expand=True)

        sales_frame = SalesView(notebook, self.user_info)
        notebook.add(sales_frame, text='   Punto de Venta   ')

        if self.user_info[2] == 'admin':
            inventory_frame = InventoryView(notebook)
            reports_frame = ReportsView(notebook)
            notebook.add(inventory_frame, text='   Gestión de Inventario   ')
            notebook.add(reports_frame, text='   Reportes de Ventas   ')

        status_bar = ttk.Label(self, text=f"Usuario: {self.user_info[1]} | Privilegio: {self.user_info[2].capitalize()}", relief=tk.SUNKEN, anchor=tk.W, padding=5)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)