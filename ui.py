import customtkinter as ctk
from tkinter import ttk
from PIL import Image
import repository as db
import tab
from factura_tab import FacturaTab
from provincia import Provincia
from dashboard import DashboardWindow
from dashboard import abrir_dashboard


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

        for name in ["Productos", "Clientes", "Rubros"]:
            self.tab_view.add(name)

        self._setup_treeview_style()

        # --- Productos ---
        self.product_tab = tab.EntityTab(
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
            dropdowns={"Rubro": self.reload_rubros()}
        )

        # --- Clientes ---
        tab.EntityTab(
            self,
            "Clientes",
            ("ID", "Nombre", "Provincia", "Domicilio", "Teléfono", "Mail"),
            db.get_clients,
            db.create_client,
            db.update_client,
            db.delete_client,
            {
                "Nombre": str,
                "Provincia": str,
                "Domicilio": str,
                "Teléfono": int,  # <- ahora validará solo números
                "Mail": str
            },
            dropdowns={"Provincia": [p.value for p in Provincia]}
        )

        # --- Rubros ---
        def _create_rubro_and_refresh(nombre_rubro):
            db.create_rubro(nombre_rubro)
            self._refresh_rubro_data()

        def _delete_rubro_and_refresh(id_rubro):
            db.delete_rubro(id_rubro)
            self._refresh_rubro_data()

        rubros_tab = tab.EntityTab(
            self,
            "Rubros",
            ("ID", "Nombre Rubro"),
            db.get_rubros,
            _create_rubro_and_refresh,
            db.update_rubro,
            _delete_rubro_and_refresh,
            {"Nombre Rubro": str}
        )
        self.rubros_tab = rubros_tab  # para acceder desde el método _refresh_rubro_data

        # --- Facturas ---
        FacturaTab(self.tab_view)

        # --- Dashboard ---
        dashboard_button = ctk.CTkButton(
            self,
            text="📊 Ver Dashboard",
            command=lambda: abrir_dashboard(self),
            fg_color="#272f35",
            hover_color="#6D8799"
        )
        dashboard_button.pack(pady=10)

    # --- Recarga la lista de rubros desde la base de datos ---
    def reload_rubros(self):
        rubros = db.get_rubros()
        return [r[1] for r in rubros] if rubros else []

    def _refresh_rubro_data(self):
        """Recarga rubros desde la BD y actualiza el combo en Productos y la tabla Rubros."""
        nuevos_rubros = self.reload_rubros()
        self.product_tab.update_dropdown_options("Rubro", nuevos_rubros)
        self.rubros_tab._refresh()

    # --- Estilo visual de la tabla ---
    def _setup_treeview_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Treeview",
            background="#2b2b2b",
            foreground="white",
            fieldbackground="#2b2b2b",
            rowheight=25
        )
        style.map(
            "Treeview",
            background=[("selected", "#414447")],
            foreground=[("selected", "white")]
        )


def run_ui():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    run_ui()