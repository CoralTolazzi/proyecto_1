import customtkinter as ctk
from tkinter import ttk, messagebox

from provincia import Provincia
from rubro import Rubro


class EntityTab:
    """Generic tab handler for CRUD operations on any entity (Product, Client, etc.)"""
    def __init__(self, parent, title, columns, get_all_fn, create_fn, update_fn, delete_fn, form_fields, dropdowns=None):
        self.parent = parent
        self.tab = parent.tab_view.tab(title)
        self.columns = columns
        self.get_all_fn = get_all_fn
        self.create_fn = create_fn
        self.update_fn = update_fn
        self.delete_fn = delete_fn
        self.form_fields = form_fields
        self.dropdowns = dropdowns or {}
        self.tree = None
        self._setup_ui()


    def _setup_ui(self):
        btn_frame = ctk.CTkFrame(self.tab)
        btn_frame.pack(pady=10)

        add_btn = ctk.CTkButton(btn_frame, text="➕ Añadir", fg_color="green", command=self._open_add_window)
        add_btn.pack(side="left", padx=5)

        edit_btn = ctk.CTkButton(btn_frame, text="✏️ Editar", fg_color="blue", command=self._open_selected_edit)
        edit_btn.pack(side="left", padx=5)

        delete_btn = ctk.CTkButton(btn_frame, text="🗑️Eliminar", fg_color="red", command=self._delete_selected)
        delete_btn.pack(side="left", padx=5)

        refresh_btn = ctk.CTkButton(btn_frame, text="🔄 Actualizar", command=self._refresh)
        refresh_btn.pack(side="left", padx=5)

        self.tree = ttk.Treeview(self.tab, columns=self.columns, show="headings")
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")
        self.tree.pack(expand=True, fill="both", padx=20, pady=10)

        self._refresh()

    def _refresh(self):
        self.tree.delete(*self.tree.get_children())  # limpia
        rows = self.get_all_fn()  # devuelve lista de tuplas (ID, col1, col2,...)

        if not rows:
            return

        for i, row in enumerate(rows):
            # Convertimos solo None a ""
            display_row = [str(r) if r is not None else "" for r in row]
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.insert("", "end", values=display_row, tags=(tag,))

        self.tree.tag_configure("even", background="#2b2b2b")
        self.tree.tag_configure("odd", background="#3c3f41")
        self.tree.bind("<Double-1>", self._on_double_click)

    def _on_double_click(self, event):
        item = self.tree.selection()
        if not item:
            return
        values = self.tree.item(item, "values")
        self._open_edit_window(values)


    def _open_add_window(self):
        self._open_form_window("Agregar", self.create_fn)


    def _open_edit_window(self, values):
        entity_id = values[0]
        self._open_form_window("Editar", lambda *args: self.update_fn(entity_id, *args), values)

    def _open_form_window(self, action, submit_fn, current_values=None):
        modal = ctk.CTkToplevel(self.parent)
        modal.title(f"{action} registro")
        modal.geometry("400x450")
        modal.grab_set()

        entries = {}

        def _numeric_validate(entry_type):
            def validator(p):
                if p == "":
                    return True
                try:
                    if entry_type == int:
                        return p.isdigit()
                    elif entry_type == float:
                        float(p)
                        return True
                except ValueError:
                    return False
                return True

            return validator

        for label, field_type in self.form_fields.items():
            ctk.CTkLabel(modal, text=f"{label}:").pack(pady=5)

            if label in self.dropdowns:  # Dropdown (ComboBox)
                combo = ctk.CTkComboBox(modal, values=self.dropdowns[label], width=250, state="readonly")
                combo.pack(pady=5)
                entries[label] = combo
            else:  # Entry normal
                entry = ctk.CTkEntry(modal, width=250)
                if field_type in [int, float]:
                    vcmd = (modal.register(_numeric_validate(field_type)), "%P")
                    entry.configure(validate="key", validatecommand=vcmd)
                entry.pack(pady=5)
                entries[label] = entry

        # Precargar valores si es edición
        if current_values:
            for (label, field_type), value in zip(self.form_fields.items(), current_values[1:]):  # omitimos ID
                widget = entries[label]
                if isinstance(widget, ctk.CTkComboBox):
                    widget.set(value)
                else:
                    widget.insert(0, str(value))

        def submit():
            new_values = []
            for f_label, f_type in self.form_fields.items():
                w = entries[f_label]
                val = w.get().strip()
                if not val:
                    messagebox.showerror("Error", "Todos los campos son obligatorios")
                    return

                # --- 🔁 Mapeo especial para dropdowns ---
                if f_label == "Provincia":
                    # Convertir nombre → id (posición en Enum + 1)
                    provincia_id = list(Provincia).index(Provincia[val.upper().replace(" ", "_")]) + 1 \
                        if val else None
                    val = provincia_id
                elif f_label == "Rubro":
                    # Convertir nombre mostrado → id del Enum Rubro, tolerando acentos
                    import unicodedata

                    def normalize_enum_key(s: str):
                        # Quita tildes y normaliza a mayúsculas con _
                        nfkd = unicodedata.normalize('NFKD', s)
                        return ''.join([c for c in nfkd if not unicodedata.combining(c)]).upper().replace(" ", "_")

                    nombre_enum = normalize_enum_key(val)
                    try:
                        val = Rubro[nombre_enum].value
                    except KeyError:
                        messagebox.showerror("Error", f"Rubro '{val}' no reconocido.")
                        return


                # --- Validación numérica si aplica ---
                elif f_type == int:
                    try:
                        val = int(val)
                    except ValueError:
                        messagebox.showerror("Error", f"El campo {f_label} debe ser un número entero")
                        return
                elif f_type == float:
                    try:
                        val = float(val)
                    except ValueError:
                        messagebox.showerror("Error", f"El campo {f_label} debe ser un número")
                        return

                new_values.append(val)

            # Ejecutar create o update
            if action == "Editar":
                try:
                    entity_id_typed = int(current_values[0])
                except ValueError:
                    entity_id_typed = current_values[0]
                self.update_fn(entity_id_typed, *new_values)
            else:
                self.create_fn(*new_values)

            modal.destroy()
            self._refresh()

        ctk.CTkButton(
            modal,
            text=action,
            command=submit,
            fg_color="blue" if action == "Editar" else "green"
        ).pack(pady=20)

    def _confirm_delete(self, entity_id):
        confirm = messagebox.askyesno("Confirmar", "¿Seguro que desea eliminar este registro?")
        if confirm:
            self.delete_fn(entity_id)
            self._refresh()


    def _open_selected_edit(self):
        """Open edit window for the currently selected item."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Atención", "Seleccione un registro para editar.")
            return
        values = self.tree.item(selected, "values")
        self._open_edit_window(values)


    def _delete_selected(self):
        """Delete the selected item after confirmation."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Atención", "Seleccione un registro para eliminar.")
            return
        values = self.tree.item(selected, "values")
        entity_id = values[0]
        self._confirm_delete(entity_id)
