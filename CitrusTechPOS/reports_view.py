import tkinter as tk
from tkinter import ttk, messagebox
import database
import json
from datetime import date, timedelta

class ReportsView(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # --- Frame de filtros de fecha ---
        filter_frame = ttk.LabelFrame(self, text="Filtro de Reporte")
        filter_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(filter_frame, text="Fecha Inicio (YYYY-MM-DD):").grid(row=0, column=0, padx=5, pady=5)
        self.start_date_entry = ttk.Entry(filter_frame)
        self.start_date_entry.grid(row=0, column=1, padx=5, pady=5)
        self.start_date_entry.insert(0, (date.today() - timedelta(days=7)).strftime('%Y-%m-%d'))

        ttk.Label(filter_frame, text="Fecha Fin (YYYY-MM-DD):").grid(row=0, column=2, padx=5, pady=5)
        self.end_date_entry = ttk.Entry(filter_frame)
        self.end_date_entry.grid(row=0, column=3, padx=5, pady=5)
        self.end_date_entry.insert(0, date.today().strftime('%Y-%m-%d'))

        ttk.Button(filter_frame, text="Generar Reporte", command=self.generar_reporte, style="Accent.TButton").grid(row=0, column=4, padx=10, pady=5)

        # --- Frame del reporte ---
        report_frame = ttk.LabelFrame(self, text="Resultados del Reporte")
        report_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.tree = ttk.Treeview(report_frame, columns=("id", "fecha", "usuario", "total"), show='headings')
        self.tree.heading("id", text="ID Venta")
        self.tree.heading("fecha", text="Fecha y Hora")
        self.tree.heading("usuario", text="Vendedor")
        self.tree.heading("total", text="Total Venta")
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.mostrar_detalles_venta)

        # --- Frame de detalles de la venta ---
        details_frame = ttk.Frame(report_frame, width=250)
        details_frame.pack(side="right", fill="y", padx=5)

        ttk.Label(details_frame, text="Detalles de la Venta", font=("Segoe UI", 12, "bold")).pack(pady=5)
        self.details_text = tk.Text(details_frame, height=10, width=40, state="disabled", font=("Courier New", 9))
        self.details_text.pack(fill="both", expand=True)

        self.total_label = ttk.Label(self, text="Ingresos Totales en Periodo: $0.00", font=("Segoe UI", 12, "bold"))
        self.total_label.pack(anchor="e", padx=10, pady=5)

    def generar_reporte(self):
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()

        if not start_date or not end_date:
            messagebox.showerror("Error", "Ambas fechas son requeridas.", parent=self)
            return

        for i in self.tree.get_children():
            self.tree.delete(i)

        ventas = database.obtener_ventas_por_fecha(start_date, end_date)
        total_periodo = 0
        for v in ventas:
            total_periodo += v[3]
            self.tree.insert("", "end", values=(v[0], v[1], v[2], f"${v[3]:.2f}"), iid=v[0]) # Usamos el ID de venta como IID

        self.total_label.config(text=f"Ingresos Totales en Periodo: ${total_periodo:.2f}")
        self.details_text.config(state="normal")
        self.details_text.delete(1.0, tk.END)
        self.details_text.config(state="disabled")

    def mostrar_detalles_venta(self, event):
        selected_item = self.tree.focus()
        if not selected_item: return

        # Encontrar la venta completa en los datos originales
        venta_id = int(selected_item)
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()
        ventas = database.obtener_ventas_por_fecha(start_date, end_date)
        venta_seleccionada = next((v for v in ventas if v[0] == venta_id), None)

        if venta_seleccionada:
            detalles_json = venta_seleccionada[4]
            detalles_lista = json.loads(detalles_json)

            texto_detalles = ""
            for item in detalles_lista:
                texto_detalles += f"Producto: {item['nombre']}\n"
                texto_detalles += f"  SKU: {item['sku']}\n"
                texto_detalles += f"  Cant: {item['cantidad']} x ${item['precio']:.2f}\n"
                texto_detalles += "--------------------\n"

            self.details_text.config(state="normal")
            self.details_text.delete(1.0, tk.END)
            self.details_text.insert(1.0, texto_detalles)
            self.details_text.config(state="disabled")