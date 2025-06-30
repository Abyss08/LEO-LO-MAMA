import tkinter as tk
from tkinter import ttk, messagebox
import database

class InventoryView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # --- Frame de controles ---
        control_frame = ttk.LabelFrame(self, text="Controles de Inventario")
        control_frame.pack(fill="x", padx=10, pady=10)

        ttk.Button(control_frame, text="Añadir Nuevo Producto", command=self.abrir_dialogo_producto).pack(side="left", padx=5, pady=5)
        ttk.Button(control_frame, text="Editar Producto Seleccionado", command=self.editar_producto_seleccionado).pack(side="left", padx=5, pady=5)
        ttk.Button(control_frame, text="Eliminar Producto", command=self.eliminar_producto_seleccionado, style="Delete.TButton").pack(side="left", padx=5, pady=5)

        # --- Frame de la lista de productos ---
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.tree = ttk.Treeview(
            self, 
            columns=("id_producto", "sku", "nombre", "descripcion", "precio", "stock"), 
            show="headings")
        self.tree.heading("id_producto", text="ID")
        self.tree.heading("sku", text="SKU")
        self.tree.heading("nombre", text="Nombre")
        self.tree.heading("descripcion", text="Descripción")
        self.tree.heading("precio", text="Precio")
        self.tree.heading("stock", text="Stock")

        self.tree.column("sku", width=100)
        self.tree.column("nombre", width=300)
        self.tree.column("descripcion", width=400)
        self.tree.column("precio", width=100, anchor='e')
        self.tree.column("stock", width=80, anchor='center')

        self.tree.pack(fill="both", expand=True)
        self.cargar_productos()

    def cargar_productos(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        productos = database.obtener_productos()
        for p in productos:
            # p[0]=id_producto, p[1]=sku, p[2]=nombre, p[3]=descripcion, p[4]=precio, p[5]=stock
            self.tree.insert(
                "", "end", 
                values=(p[0], p[1], p[2], p[3], f"${p[4]:.2f}", p[5]))

    def abrir_dialogo_producto(self, producto_a_editar=None):
        dialog = ProductDialog(self, producto_a_editar)
        dialog.wait_window()
        self.cargar_productos()

    def editar_producto_seleccionado(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Sin Selección", "Por favor, seleccione un producto para editar.", parent=self)
            return

        item_values = self.tree.item(selected_item, 'values')
        # item_values: (id_producto, sku, nombre, descripcion, precio, stock)
        producto_a_editar = (
            item_values[0],  # id_producto
            item_values[1],  # sku
            item_values[2],  # nombre
            item_values[3],  # descripcion
            float(item_values[4].replace('$', '')),  # precio (elimina el $ si existe)
            int(item_values[5])  # stock
        )
        self.abrir_dialogo_producto(producto_a_editar)

    def eliminar_producto_seleccionado(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Sin Selección", "Por favor, seleccione un producto para eliminar.", parent=self)
            return

        id_producto = self.tree.item(selected_item, 'values')[0]  # Ahora es el ID
        nombre = self.tree.item(selected_item, 'values')[2]
        
        if messagebox.askyesno("Confirmar Eliminación", f"¿Está seguro de que desea eliminar '{nombre}' (ID: {id_producto}) del inventario?", parent=self):
            database.eliminar_producto_por_id(id_producto)
            self.cargar_productos()
            messagebox.showinfo("Éxito", "Producto eliminado correctamente.", parent=self)


class ProductDialog(tk.Toplevel):
    def __init__(self, parent, producto=None):
        super().__init__(parent)
        self.transient(parent)
        self.grab_set()
        self.producto = producto
        self.is_edit_mode = producto is not None

        self.title("Editar Producto" if self.is_edit_mode else "Añadir Nuevo Producto")

        frame = ttk.Frame(self, padding="20")
        frame.pack(fill="both", expand=True)

        # --- Formulario ---
        fields = ["Nombre", "Descripción", "Precio Venta", "Stock"]
        self.entries = {}
        for i, field in enumerate(fields):
            ttk.Label(frame, text=f"{field}:").grid(row=i, column=0, sticky="w", pady=2)
            entry = ttk.Entry(frame, width=40)
            entry.grid(row=i, column=1, sticky="ew", pady=2)
            self.entries[field] = entry

        if self.is_edit_mode:
            self.entries["Nombre"].insert(0, self.producto[2])
            self.entries["Descripción"].insert(0, self.producto[3])
            self.entries["Precio Venta"].insert(0, self.producto[4])
            self.entries["Stock"].insert(0, self.producto[5])

        # --- Botones ---
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Guardar", command=self.guardar).pack(side="left", padx=5)

    def guardar(self):
        nombre = self.entries["Nombre"].get()
        descripcion = self.entries["Descripción"].get()
        precio = float(self.entries["Precio Venta"].get())
        stock = int(self.entries["Stock"].get())
        # Llama la función sin SKU
        database.agregar_producto(nombre, descripcion, precio, stock)
        self.destroy()