import customtkinter as ctk
from tkinter import ttk
from PIL import Image
import repository as db
import tab
from factura_tab import FacturaTab
from rubro import Rubro
from provincia import Provincia


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CORAL TECH")
        self.geometry("900x650")

        # --- LOGO PRINCIPAL ---
        logo_img = ctk.CTkImage(light_image=Image.open("logo_coraltech.jpg"), size=(250, 90))
        logo_label = ctk.CTkLabel(self, image=logo_img, text="")
        logo_label.pack(pady=10)

        # --- TABS ---
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(expand=True, fill="both")

        for name in ["Productos", "Clientes", "Facturas", "Rubros"]:
            self.tab_view.add(name)

        self._setup_treeview_style()

        # --- Productos ---
        tab.EntityTab(
            self,
            "Productos",
            ("ID", "Descripción", "Precio", "Stock", "Rubro"),
            db.get_products,
            db.create_product,
            db.update_product,
            db.delete_product,
            {
                "Descripción": str,
                "Precio": float,
                "Stock": int,
                "Rubro": str
            },
            dropdowns={
                "Rubro": [r.name.replace("_", " ").title() for r in Rubro]
            }
        )

        # --- Clientes ---
        tab.EntityTab(
            self,
            "Clientes",
            ("ID", "Nombre", "Provincia", "Domicilio"),
            db.get_clients,
            db.create_client,
            db.update_client,
            db.delete_client,
            {
                "Nombre": str,
                "Provincia": str,
                "Domicilio": str
            },
            dropdowns={"Provincia": [p.value for p in Provincia]}
        )

        # --- Rubros ---
        tab.EntityTab(
            self,
            "Rubros",
            ("ID", "Nombre Rubro"),
            db.get_rubros,
            db.create_rubro,
            db.update_rubro,
            db.delete_rubro,
            {"Nombre Rubro": str}
        )

        # --- Facturas ---
        FacturaTab(self, self.tab_view)

    def _setup_treeview_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#2b2b2b",
                        foreground="white",
                        fieldbackground="#2b2b2b",
                        rowheight=25)
        style.map("Treeview",
                  background=[("selected", "#1f6aa5")],
                  foreground=[("selected", "white")])


def run_ui():
    app = App()
    app.mainloop()
