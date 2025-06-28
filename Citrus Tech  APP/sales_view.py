import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import database

class SalesView(ttk.Frame):
    def __init__(self, parent, user_info):
        super().__init__(parent)
        self.user_info = user_info
        self.carrito = []
        self.total_venta = 0.0

        # --- Layout principal con PanedWindow ---
        paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # --- Panel Izquierdo: Lista de productos ---
        products_panel = ttk.Frame(paned_window, width=300)
        paned_window.add(products_panel, weight=1)

        search_frame = ttk.LabelFrame(products_panel, text="Productos Disponibles")
        search_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filtrar_productos_tree)
        ttk.Entry(search_frame, textvariable=self.search_var).pack(fill="x", padx=5, pady=5)

        self.products_tree = ttk.Treeview(search_frame, columns=("sku", "nombre", "precio", "stock"), show='headings')
        self.products_tree.heading("sku", text="SKU")
        self.products_tree.heading("nombre", text="Producto")
        self.products_tree.heading("precio", text="Precio")
        self.products_tree.heading("stock", text="Stock")
        self.products_tree.column("sku", width=80)
        self.products_tree.column("precio", width=60, anchor='e')
        self.products_tree.column("stock", width=50, anchor='center')
        self.products_tree.pack(fill="both", expand=True)
        self.products_tree.bind("<Double-1>", self.anadir_al_carrito_desde_lista)
        self.cargar_productos_tree()

        # --- Panel Derecho: Carrito de Compra ---
        cart_panel = ttk.Frame(paned_window)
        paned_window.add(cart_panel, weight=2)

        cart_frame = ttk.LabelFrame(cart_panel, text="Carrito de Compra")
        cart_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.cart_tree = ttk.Treeview(cart_frame, columns=("sku", "nombre", "cantidad", "precio", "subtotal"), show='headings')
        self.cart_tree.heading("sku", text="SKU")
        self.cart_tree.heading("nombre", text="Producto")
        self.cart_tree.heading("cantidad", text="Cant.")
        self.cart_tree.heading("precio", text="Precio Unit.")
        self.cart_tree.heading("subtotal", text="Subtotal")
        self.cart_tree.column("cantidad", width=50, anchor='center')
        self.cart_tree.pack(fill="both", expand=True)

        checkout_frame = ttk.Frame(cart_panel)
        checkout_frame.pack(fill="x", padx=10, pady=10)

        self.total_label = ttk.Label(checkout_frame, text="TOTAL: $0.00", font=("Segoe UI", 18, "bold"))
        self.total_label.pack(side="left", expand=True)

        ttk.Button(checkout_frame, text="Finalizar Venta", command=self.finalizar_venta, style="Accent.TButton", padding=10).pack(side="right")
        ttk.Button(checkout_frame, text="Cancelar", command=self.limpiar_carrito, padding=10).pack(side="right", padx=10)

    def cargar_productos_tree(self):
        for i in self.products_tree.get_children():
            self.products_tree.delete(i)
        productos = database.obtener_productos()
        for p in productos:
            self.products_tree.insert("", "end", values=(p[0], p[1], f"${p[3]:.2f}", p[4]))

    def filtrar_productos_tree(self, *args):
        query = self.search_var.get()
        for i in self.products_tree.get_children():
            self.products_tree.delete(i)
        productos = database.obtener_productos(query)
        for p in productos:
            self.products_tree.insert("", "end", values=(p[0], p[1], f"${p[3]:.2f}", p[4]))

    def anadir_al_carrito_desde_lista(self, event):
        selected_item = self.products_tree.focus()
        if not selected_item: return

        item_values = self.products_tree.item(selected_item, 'values')
        sku, nombre, precio_str, stock = item_values
        precio = float(precio_str.replace('$', ''))

        if int(stock) <= 0:
            messagebox.showerror("Sin Stock", f"El producto '{nombre}' está agotado.", parent=self)
            return

        cantidad = simpledialog.askinteger("Cantidad", f"¿Cuántas unidades de '{nombre}'?", parent=self, minvalue=1, initialvalue=1)
        if cantidad is None: return

        item_existente_en_carrito = next((item for item in self.carrito if item['sku'] == sku), None)

        if item_existente_en_carrito:
            item_existente_en_carrito['cantidad'] += cantidad
        else:
            self.carrito.append({'sku': sku, 'nombre': nombre, 'cantidad': cantidad, 'precio': precio})

        self.actualizar_vista_carrito()

    def actualizar_vista_carrito(self):
        for i in self.cart_tree.get_children():
            self.cart_tree.delete(i)

        self.total_venta = 0.0
        for item in self.carrito:
            subtotal = item['cantidad'] * item['precio']
            self.cart_tree.insert("", "end", values=(item['sku'], item['nombre'], item['cantidad'], f"${item['precio']:.2f}", f"${subtotal:.2f}"))
            self.total_venta += subtotal

        self.total_label.config(text=f"TOTAL: ${self.total_venta:.2f}")

    def limpiar_carrito(self):
        if messagebox.askyesno("Cancelar Venta", "¿Está seguro de que desea vaciar el carrito?", parent=self):
            self.carrito = []
            self.actualizar_vista_carrito()

    def finalizar_venta(self):
        if not self.carrito:
            messagebox.showinfo("Carrito Vacío", "No hay productos en el carrito para vender.", parent=self)
            return

        confirm = messagebox.askyesno("Confirmar Venta", f"El total de la venta es ${self.total_venta:.2f}. ¿Desea continuar?", parent=self)
        if confirm:
            database.registrar_venta(self.user_info[0], self.total_venta, self.carrito)
            messagebox.showinfo("Venta Exitosa", "La venta se ha registrado correctamente.", parent=self)
            self.limpiar_carrito()
            self.cargar_productos_tree() # Recargar la lista de productos para ver el stock actualizado