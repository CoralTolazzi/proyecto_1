import customtkinter as ctk
from tkinter import ttk
import repository as db


class FacturaTab:
    def __init__(self, master, tab_view):
        self.master = master
        self.frame = tab_view.tab("Facturas")

        # --- Layout ---
        self.frame.columnconfigure(0, weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.frame.rowconfigure(1, weight=1)

        # --- Tabla de facturas ---
        self.tree_facturas = ttk.Treeview(
            self.frame,
            columns=("ID", "Cliente", "Fecha", "Total"),
            show="headings",
            height=8
        )
        for col in ("ID", "Cliente", "Fecha", "Total"):
            self.tree_facturas.heading(col, text=col)
            self.tree_facturas.column(col, anchor="center")

        self.tree_facturas.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))
        self.tree_facturas.bind("<<TreeviewSelect>>", self._on_select_factura)

        # --- Tabla de detalles ---
        self.tree_detalles = ttk.Treeview(
            self.frame,
            columns=("Producto", "Cantidad", "Precio Unit.", "Subtotal"),
            show="headings",
            height=8
        )
        for col in ("Producto", "Cantidad", "Precio Unit.", "Subtotal"):
            self.tree_detalles.heading(col, text=col)
            self.tree_detalles.column(col, anchor="center")

        self.tree_detalles.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))

        # --- Botón de refresco ---
        self.btn_refresh = ctk.CTkButton(self.frame, text="🔄 Actualizar", command=self.load_facturas)
        self.btn_refresh.grid(row=2, column=0, pady=(0, 10))

        # --- Inicial ---
        self.load_facturas()


    def load_facturas(self):
        """Carga todas las facturas desde la base de datos."""
        for item in self.tree_facturas.get_children():
            self.tree_facturas.delete(item)

        facturas = db.get_invoices()
        for f in facturas:
            self.tree_facturas.insert("", "end", values=(f["id"], f["cliente"], f["fecha"], f["total"]))

        # Limpia detalles
        for item in self.tree_detalles.get_children():
            self.tree_detalles.delete(item)


    def _on_select_factura(self, event):
        """Cuando se selecciona una factura, muestra sus detalles."""
        selected = self.tree_facturas.selection()
        if not selected:
            return

        factura_id = self.tree_facturas.item(selected[0], "values")[0]
        detalles = db.get_invoice_details(factura_id)

        # Limpiar tabla anterior
        for item in self.tree_detalles.get_children():
            self.tree_detalles.delete(item)

        # Insertar nuevos
        for d in detalles:
            self.tree_detalles.insert("", "end", values=(d["producto"], d["cantidad"], d["precio_unit"], d["subtotal"]))
