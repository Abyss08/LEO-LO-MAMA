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

        self.tree = ttk.Treeview(tree_frame, columns=("sku", "nombre", "descripcion", "precio", "stock"), show='headings')
        self.tree.heading("sku", text="SKU")
        self.tree.heading("nombre", text="Nombre del Producto")
        self.tree.heading("descripcion", text="Descripción")
        self.tree.heading("precio", text="Precio Venta")
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
            self.tree.insert("", "end", values=(p[0], p[1], p[2], f"${p[3]:.2f}", p[4]))

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
        self.abrir_dialogo_producto(item_values)

    def eliminar_producto_seleccionado(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Sin Selección", "Por favor, seleccione un producto para eliminar.", parent=self)
            return

        sku = self.tree.item(selected_item, 'values')[0]
        nombre = self.tree.item(selected_item, 'values')[1]

        if messagebox.askyesno("Confirmar Eliminación", f"¿Está seguro de que desea eliminar '{nombre}' (SKU: {sku}) del inventario?", parent=self):
            database.eliminar_producto(sku)
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
        fields = ["SKU", "Nombre", "Descripción", "Precio Venta", "Stock"]
        self.entries = {}
        for i, field in enumerate(fields):
            ttk.Label(frame, text=f"{field}:").grid(row=i, column=0, sticky="w", pady=2)
            entry = ttk.Entry(frame, width=40)
            entry.grid(row=i, column=1, sticky="ew", pady=2)
            self.entries[field] = entry

        if self.is_edit_mode:
            self.entries["SKU"].insert(0, self.producto[0])
            self.entries["SKU"].config(state="readonly")
            self.entries["Nombre"].insert(0, self.producto[1])
            self.entries["Descripción"].insert(0, self.producto[2])
            self.entries["Precio Venta"].insert(0, self.producto[3].replace('$', ''))
            self.entries["Stock"].insert(0, self.producto[4])

        # --- Botones ---
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Guardar", command=self.guardar).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self.destroy).pack(side="left", padx=5)

    def guardar(self):
        try:
            sku = self.entries["SKU"].get()
            nombre = self.entries["Nombre"].get()
            descripcion = self.entries["Descripción"].get()
            precio = float(self.entries["Precio Venta"].get())
            stock = int(self.entries["Stock"].get())

            if not all([sku, nombre, precio, stock]):
                messagebox.showerror("Campos Vacíos", "SKU, Nombre, Precio y Stock son requeridos.", parent=self)
                return
        except ValueError:
            messagebox.showerror("Dato Inválido", "Precio y Stock deben ser números válidos.", parent=self)
            return

        if self.is_edit_mode:
            database.actualizar_producto(sku, nombre, descripcion, precio, stock)
            messagebox.showinfo("Éxito", "Producto actualizado correctamente.", parent=self.master)
        else:
            if database.agregar_producto(sku, nombre, descripcion, precio, stock):
                messagebox.showinfo("Éxito", "Producto añadido correctamente.", parent=self.master)
            else:
                messagebox.showerror("Error", "El SKU ya existe. Por favor, use uno diferente.", parent=self)
                return # No cerrar la ventana si hay error

        self.destroy()