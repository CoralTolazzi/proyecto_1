import customtkinter as ctk
from tkinter import ttk, messagebox
import repository as db
from datetime import datetime


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
            self.tree_detalle.insert("", "end", values=(d["producto"], d["cantidad"], d["precio_unitario"], d["subtotal"]))

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

        if messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Seguro que querés eliminar la factura #{factura_id}?."
        ):
            try:
                # ✅ Llamamos a la función de repository que maneja todo (detalle + stock)
                db.delete_factura(factura_id)

                messagebox.showinfo(
                    "Éxito",
                    f"Factura #{factura_id} eliminada correctamente."
                )
                self.cargar_facturas()
            except Exception as e:
                messagebox.showerror(
                    "Error",
                    f"Ocurrió un problema al eliminar la factura:\n{e}"
                )

            
    def cargar_detalles_factura(self, id_factura):
        detalles = db.get_detalles_por_factura(id_factura)
        self.tree.delete(*self.tree.get_children())  # limpia antes de cargar

        for det in detalles:
            producto = det["producto_nombre"]
            cantidad = det["cantidad"]
            precio_unit = det["precio_unitario"]
            subtotal = cantidad * precio_unit

        # Mostrar los valores en la tabla
            self.tree.insert("", "end", values=(
                producto,
                cantidad,
                f"${precio_unit:,.2f}",
                f"${subtotal:,.2f}",
                "🗑️"
            ))

        self.actualizar_total()


    def on_tree_click(self, event):
        item = self.tree.identify_row(event.y)
        column = self.tree.identify_column(event.x)
        if column == "#5":  # la columna de "Acción"
            if item:
                self.tree.delete(item)
                self.actualizar_total()

# =============================
# FORMULARIO DE FACTURA (POPUP)
# =============================

class FacturaForm:
    def __init__(self, parent, modo="crear", factura_id=None, callback=None):
        self.modo = modo
        self.factura_id = factura_id
        self.callback = callback
        self.items = []  # (id_prod, nombre, cantidad, precio, subtotal)

        self.top = ctk.CTkToplevel(parent)
        self.top.title("Factura")
        self.top.geometry("600x600")

        # --- Cliente y fecha ---
        ctk.CTkLabel(self.top, text="Cliente:").pack(pady=5)
        self.cliente_cb = ctk.CTkComboBox(self.top, values=[c[1] for c in db.get_clients()])
        self.cliente_cb.pack(pady=5)

        ctk.CTkLabel(self.top, text="Fecha (YYYY-MM-DD):").pack(pady=5)
        self.fecha_entry = ctk.CTkEntry(self.top)
        self.fecha_entry.pack(pady=5)

        # --- Sección productos ---
        ctk.CTkLabel(self.top, text="Agregar productos:").pack(pady=(15, 5))
        productos = db.get_products()
        # productos: (id_producto, descripcion, precio, stock, nombre_rubro)
        self.productos_dict = {p[1]: (p[0], p[3], p[2]) for p in productos}  # nombre -> (id, stock, precio)

        prod_frame = ctk.CTkFrame(self.top)
        prod_frame.pack(pady=5)

        self.producto_cb = ctk.CTkComboBox(prod_frame, values=list(self.productos_dict.keys()), width=180)
        self.producto_cb.grid(row=0, column=0, padx=5)

        self.cantidad_entry = ctk.CTkEntry(prod_frame, placeholder_text="Cantidad", width=100)
        self.cantidad_entry.grid(row=0, column=1, padx=5)

        ctk.CTkButton(prod_frame, text="➕ Agregar", command=self.agregar_producto).grid(row=0, column=2, padx=5)

        # --- Tabla temporal: ahora con columna 'accion' para eliminar ---
        self.tree_items = ttk.Treeview(
            self.top,
            columns=("producto", "cantidad", "precio", "subtotal", "accion"),
            show="headings",
            height=6
        )
        for col, text in zip(("producto", "cantidad", "precio", "subtotal", "accion"),
                             ("Producto", "Cant.", "Precio Unit.", "Subtotal", "Eliminar")):
            self.tree_items.heading(col, text=text)
            self.tree_items.column(col, width=110, anchor="center")

        self.tree_items.pack(pady=10)
        self.tree_items.bind("<Button-1>", self.on_tree_click)  # clic para eliminar

        # --- Total ---
        self.total_label = ctk.CTkLabel(self.top, text="Total: $0.00", font=("Arial", 14, "bold"))
        self.total_label.pack(pady=10)

        # --- Botón Guardar ---
        ctk.CTkButton(self.top, text="💾 Guardar", command=self.guardar).pack(pady=15)

        # Si estamos en modo editar → cargar datos existentes
        if self.modo == "editar" and self.factura_id:
            self.cargar_datos_factura()

    # -----------------------
    # cargar datos / UI
    # -----------------------
    def cargar_datos_factura(self):
        """Carga cabecera y detalle en modo editar."""
        factura = db.execute_query(
            "SELECT f.fecha, c.nombre FROM factura f "
            "JOIN cliente c ON f.id_cliente = c.id_cliente "
            "WHERE f.id_factura = ?", (self.factura_id,), fetch="one"
        )
        if not factura:
            messagebox.showerror("Error", "No se encontró la factura.")
            return

        fecha, cliente = factura
        self.cliente_cb.set(cliente)
        self.fecha_entry.insert(0, fecha)

        # Cargar detalle desde repository (asegurate de tener get_detalles_por_factura correcto)
        detalles = db.get_detalles_por_factura(self.factura_id)
        for d in detalles:
            # d debe contener: id_producto, producto_nombre, cantidad, precio_unitario
            id_prod = d.get("id_producto")
            nombre = d.get("producto_nombre")
            cantidad = d.get("cantidad")
            precio_unit = d.get("precio_unitario")
            subtotal = cantidad * precio_unit
            self.items.append((id_prod, nombre, cantidad, precio_unit, subtotal))
            self.tree_items.insert("", "end", values=(nombre, cantidad, f"{precio_unit:.2f}", f"{subtotal:.2f}", "🗑"))
        self.actualizar_total()

    # -----------------------
    # agregar / eliminar fila
    # -----------------------
    def agregar_producto(self):
        nombre = self.producto_cb.get()
        cantidad_str = self.cantidad_entry.get().strip()

        if not nombre:
            messagebox.showwarning("Error", "Seleccioná un producto.")
            return
        if not cantidad_str.isdigit() or int(cantidad_str) <= 0:
            messagebox.showwarning("Error", "La cantidad debe ser un número entero positivo.")
            return

        cantidad = int(cantidad_str)
        id_prod, stock, precio = self.productos_dict[nombre]

        if cantidad > stock:
            messagebox.showwarning("Error", f"No hay stock suficiente ({stock} disponibles).")
            return

        subtotal = precio * cantidad
        self.items.append((id_prod, nombre, cantidad, precio, subtotal))
        self.tree_items.insert("", "end", values=(nombre, cantidad, f"{precio:.2f}", f"{subtotal:.2f}", "🗑"))
        self.actualizar_total()
        self.cantidad_entry.delete(0, "end")

    def on_tree_click(self, event):
        """Detecta clics en la columna de eliminar y borra la fila (lista items también)."""
        region = self.tree_items.identify("region", event.x, event.y)
        if region != "cell":
            return

        column = self.tree_items.identify_column(event.x)
        # la columna 5 corresponde a "accion" (Eliminar)
        if column == "#5":
            item_id = self.tree_items.identify_row(event.y)
            if not item_id:
                return
            idx = self.tree_items.index(item_id)
            # si está en modo editar: no borramos de la BD todavía, solo quitamos de la lista y tabla;
            # al guardar la edición se sobrescribirá todo el detalle (véase guardar()).
            del self.items[idx]
            self.tree_items.delete(item_id)
            self.actualizar_total()

    def actualizar_total(self):
        total = sum(item[4] for item in self.items)
        self.total_label.configure(text=f"Total: ${total:.2f}")

    # -----------------------
    # guardar: crear o editar
    # -----------------------
    def guardar(self):
        # --- validar fecha ---
        fecha_text = self.fecha_entry.get().strip()
        try:
            # permite solo YYYY-MM-DD
            datetime.strptime(fecha_text, "%Y-%m-%d")
        except Exception:
            messagebox.showwarning("Error", "La fecha debe tener formato YYYY-MM-DD (ej: 2025-10-04).")
            return

        # validar cliente y items
        cliente_nombre = self.cliente_cb.get()
        if not cliente_nombre:
            messagebox.showwarning("Error", "Seleccioná un cliente.")
            return
        if not self.items:
            messagebox.showwarning("Error", "Agregá al menos un producto.")
            return

        # obtener id_cliente
        id_cliente_row = db.execute_query(
            "SELECT id_cliente FROM cliente WHERE nombre = ?", (cliente_nombre,), fetch="one"
        )
        if not id_cliente_row:
            messagebox.showerror("Error", "Cliente no encontrado.")
            return
        id_cliente = id_cliente_row[0]

        # --- manejo stock y detalles en modo editar ---
        if self.modo == "editar":
            factura_id = self.factura_id

            # 1) restaurar stock antiguo (sumar atrás las cantidades antiguas)
            prev_detalles = db.get_detalles_por_factura(factura_id)  # devuelve id_producto, producto_nombre, cantidad, precio_unitario
            for pd in prev_detalles:
                id_prod_prev = pd["id_producto"]
                cant_prev = pd["cantidad"] or 0
                # devolver stock (sumar la cantidad anterior)
                db.execute_query("UPDATE producto SET stock = stock + ? WHERE id_producto = ?", (cant_prev, id_prod_prev), commit=True)

            # 2) actualizar cabecera
            db.execute_query(
                "UPDATE factura SET id_cliente = ?, fecha = ? WHERE id_factura = ?",
                (id_cliente, fecha_text, factura_id),
                commit=True
            )
            # 3) borrar detalles previos (vamos a insertar los nuevos abajo)
            db.execute_query("DELETE FROM detalle_factura WHERE id_factura = ?", (factura_id,), commit=True)

        else:
            # crear nueva factura
            db.execute_query("INSERT INTO factura (id_cliente, fecha) VALUES (?, ?)", (id_cliente, fecha_text), commit=True)
            factura_row = db.execute_query("SELECT MAX(id_factura) FROM factura", fetch="one")
            factura_id = factura_row[0]

        # --- insertar nuevos detalles y actualizar stock (restar) ---
        for id_prod, _, cantidad, precio, _ in self.items:
            db.execute_query(
                "INSERT INTO detalle_factura (id_factura, id_producto, cantidad, precio_unitario) VALUES (?, ?, ?, ?)",
                (factura_id, id_prod, cantidad, precio),
                commit=True
            )
            # restar stock
            db.execute_query("UPDATE producto SET stock = stock - ? WHERE id_producto = ?", (cantidad, id_prod), commit=True)

        # opcional: podrías actualizar un campo 'monto' en tabla factura si lo deseas:
        total = sum(item[4] for item in self.items)
        # si querés guardar el total en la tabla factura (si existe columna 'monto'), descomentá:
        # db.execute_query("UPDATE factura SET monto = ? WHERE id_factura = ?", (total, factura_id), commit=True)

        messagebox.showinfo("Éxito", "Factura actualizada correctamente." if self.modo == "editar" else "Factura guardada correctamente.")
        self.top.destroy()
        if self.callback:
            self.callback()
