import customtkinter as ctk
from tkinter import ttk, messagebox
import repository as db


class FacturaTab:
    def __init__(self, tabview):
        # ✅ Crear una nueva pestaña dentro del TabView
        self.frame = tabview.add("Facturas")

        # --- Título ---
        ctk.CTkLabel(self.frame, text="Gestión de Facturas", font=("Arial", 18, "bold")).pack(pady=10)

        # --- Tabla de facturas ---
        self.tree_facturas = ttk.Treeview(
            self.frame,
            columns=("id", "cliente", "fecha", "total"),
            show="headings",
            height=8
        )
        self.tree_facturas.heading("id", text="ID")
        self.tree_facturas.heading("cliente", text="Cliente")
        self.tree_facturas.heading("fecha", text="Fecha")
        self.tree_facturas.heading("total", text="Total")
        self.tree_facturas.pack(fill="x", pady=5)

        self.tree_facturas.bind("<<TreeviewSelect>>", self.on_factura_select)

        # --- Botones CRUD ---
        btn_frame = ctk.CTkFrame(self.frame)
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="➕ Nueva Factura", command=self.agregar_factura).grid(row=0, column=0, padx=5)
        ctk.CTkButton(btn_frame, text="✏️ Editar Factura", command=self.editar_factura).grid(row=0, column=1, padx=5)
        ctk.CTkButton(btn_frame, text="🗑️ Eliminar Factura", fg_color="red", command=self.eliminar_factura).grid(row=0, column=2, padx=5)
        ctk.CTkButton(btn_frame, text="🔄 Actualizar", command=self.cargar_facturas).grid(row=0, column=3, padx=5)

        # --- Detalle de factura ---
        ttk.Label(
            self.frame,
            text="Detalle de la factura seleccionada:",
            background="#1c1c1c",
            foreground="white"
        ).pack(pady=(10, 2))

        self.tree_detalle = ttk.Treeview(
            self.frame,
            columns=("producto", "cantidad", "precio", "subtotal"),
            show="headings",
            height=6
        )
        for col, text in zip(("producto", "cantidad", "precio", "subtotal"),
                             ("Producto", "Cantidad", "Precio Unit.", "Subtotal")):
            self.tree_detalle.heading(col, text=text)
        self.tree_detalle.pack(fill="x", pady=5)

        # Cargar los datos al iniciar
        self.cargar_facturas()

    # =====================
    # FUNCIONES PRINCIPALES
    # =====================

    def cargar_facturas(self):
        """Recarga las facturas desde la base de datos."""
        for row in self.tree_facturas.get_children():
            self.tree_facturas.delete(row)

        facturas = db.get_invoices()
        for f in facturas:
            self.tree_facturas.insert("", "end", values=(f["id"], f["cliente"], f["fecha"], f["total"]))

        for row in self.tree_detalle.get_children():
            self.tree_detalle.delete(row)

    def on_factura_select(self, event):
        """Cuando seleccionás una factura, se carga su detalle."""
        selected = self.tree_facturas.selection()
        if not selected:
            return
        factura_id = self.tree_facturas.item(selected[0])["values"][0]

        detalles = db.get_invoice_details(factura_id)

        for row in self.tree_detalle.get_children():
            self.tree_detalle.delete(row)

        for d in detalles:
            self.tree_detalle.insert("", "end", values=(d["producto"], d["cantidad"], d["precio_unit"], d["subtotal"]))

    # =====================
    # CRUD DE FACTURAS
    # =====================

    def agregar_factura(self):
        win = FacturaForm(self.frame, modo="crear", callback=self.cargar_facturas)
        win.top.focus()

    def editar_factura(self):
        selected = self.tree_facturas.selection()
        if not selected:
            messagebox.showwarning("Atención", "Seleccioná una factura para editar.")
            return
        factura_id = self.tree_facturas.item(selected[0])["values"][0]
        win = FacturaForm(self.frame, modo="editar", factura_id=factura_id, callback=self.cargar_facturas)
        win.top.focus()

    def eliminar_factura(self):
        selected = self.tree_facturas.selection()
        if not selected:
            messagebox.showwarning("Atención", "Seleccioná una factura para eliminar.")
            return
        factura_id = self.tree_facturas.item(selected[0])["values"][0]

        if messagebox.askyesno("Confirmar", f"¿Eliminar la factura #{factura_id}?"):
            db.execute_query("DELETE FROM factura WHERE id_factura = ?", (factura_id,), commit=True)
            db.execute_query("DELETE FROM detalle_factura WHERE id_factura = ?", (factura_id,), commit=True)
            messagebox.showinfo("Éxito", f"Factura #{factura_id} eliminada.")
            self.cargar_facturas()


# =============================
# FORMULARIO DE FACTURA (POPUP)
# =============================

class FacturaForm:
    def __init__(self, parent, modo="crear", factura_id=None, callback=None):
        self.modo = modo
        self.factura_id = factura_id
        self.callback = callback

        self.top = ctk.CTkToplevel(parent)
        self.top.title("Factura")
        self.top.geometry("400x350")

        ctk.CTkLabel(self.top, text="Cliente:").pack(pady=5)
        self.cliente_cb = ctk.CTkComboBox(self.top, values=[c[1] for c in db.get_clients()])
        self.cliente_cb.pack(pady=5)

        ctk.CTkLabel(self.top, text="Fecha (YYYY-MM-DD):").pack(pady=5)
        self.fecha_entry = ctk.CTkEntry(self.top)
        self.fecha_entry.pack(pady=5)

        if self.modo == "editar" and self.factura_id:
            data = db.execute_query(
                "SELECT id_cliente, fecha FROM factura WHERE id_factura = ?",
                (self.factura_id,),
                fetch="one"
            )
            if data:
                cliente = db.execute_query(
                    "SELECT nombre FROM cliente WHERE id_cliente = ?",
                    (data[0],),
                    fetch="one"
                )[0]
                self.cliente_cb.set(cliente)
                self.fecha_entry.insert(0, data[1])

        ctk.CTkButton(self.top, text="💾 Guardar", command=self.guardar).pack(pady=15)

    def guardar(self):
        cliente_nombre = self.cliente_cb.get()
        fecha = self.fecha_entry.get().strip()

        if not cliente_nombre or not fecha:
            messagebox.showwarning("Error", "Completá todos los campos.")
            return

        id_cliente = db.execute_query(
            "SELECT id_cliente FROM cliente WHERE nombre = ?",
            (cliente_nombre,),
            fetch="one"
        )[0]

        if self.modo == "crear":
            db.execute_query(
                "INSERT INTO factura (id_cliente, fecha) VALUES (?, ?)",
                (id_cliente, fecha),
                commit=True
            )
            messagebox.showinfo("Éxito", "Factura creada correctamente.")
        else:
            db.execute_query(
                "UPDATE factura SET id_cliente = ?, fecha = ? WHERE id_factura = ?",
                (id_cliente, fecha, self.factura_id),
                commit=True
            )
            messagebox.showinfo("Éxito", "Factura actualizada correctamente.")

        self.top.destroy()
        if self.callback:
            self.callback()
