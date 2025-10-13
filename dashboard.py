import customtkinter as ctk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import pandas as pd
import repository as db

# apariencia matplotlib para fondo oscuro
plt.rcParams["figure.facecolor"] = "#1e1e1e"
plt.rcParams["axes.facecolor"] = "#1e1e1e"
plt.rcParams["text.color"] = "white"
plt.rcParams["xtick.color"] = "white"
plt.rcParams["ytick.color"] = "white"
plt.rcParams["axes.labelcolor"] = "white"
plt.rcParams["axes.titlecolor"] = "white"


class DashboardWindow(ctk.CTkToplevel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.title("📊 Dashboard de Ventas - Coral Tech")
        self.geometry("1200x750")
        self.configure(fg_color="#1e1e1e")

        ttk.Label(self, text="📈 Dashboard de Ventas", font=("Arial", 20, "bold")).pack(pady=12)

        frame = ctk.CTkFrame(self)
        frame.pack(expand=True, fill="both", padx=12, pady=12)

        # --- obtener datos ---
        detalles = db.get_all_detalle_factura()  # espera (id_factura, id_producto, cantidad, precio_unitario)
        productos = db.get_products()            # puede variar la estructura; lo manejamos abajo
        rubros = db.get_rubros()                 # (id_rubro, nombre_rubro)

        # debug console (útil si algo sale mal)
        print("DEBUG dashboard: primeras filas")
        print("detalles:", detalles[:5])
        print("productos:", productos[:5])
        print("rubros:", rubros[:5])

        # --- crear dataframes defensivamente ---
        df_det = pd.DataFrame(detalles)
        if df_det.shape[1] == 4:
            df_det.columns = ["id_factura", "id_producto", "cantidad", "precio_unitario"]
        else:
            # si la estructura es distinta, intentar inferir
            raise RuntimeError("Formato inesperado de detalle_factura; debe tener 4 columnas.")

        df_prod = pd.DataFrame(productos)
        # heurística: si tiene 5 cols, probamos asignar (id_producto, descripcion, precio, id_rubro, stock)
        if df_prod.shape[1] == 5:
            df_prod.columns = ["id_producto", "descripcion", "precio", "id_rubro_or_stock", "maybe_rubro_or_stock"]
        elif df_prod.shape[1] == 4:
            # posible formato (id, descripcion, precio, id_rubro) o (id, descripcion, precio, stock)
            df_prod.columns = ["id_producto", "descripcion", "precio", "id_rubro_or_stock"]
            df_prod["maybe_rubro_or_stock"] = None
        else:
            # columna inesperada -> nombramos genericos
            df_prod.columns = [f"p{i}" for i in range(df_prod.shape[1])]
            # intentar continuar pero será más inseguro

        df_rub = pd.DataFrame(rubros)
        if df_rub.shape[1] == 2:
            df_rub.columns = ["id_rubro", "nombre_rubro"]
        else:
            df_rub.columns = [f"r{i}" for i in range(df_rub.shape[1])]

        # --- detectar cuál columna de producto es realmente id_rubro / stock / nombre_rubro ---
        # convertimos a strings temporalmente para inspección
        df_prod_preview = df_prod.astype(str).head(20)
        # Buscar si alguno de los valores de la columna 4 coincide con un nombre de rubro conocido
        known_rubros = [str(r[1]).strip().lower() for r in rubros]
        col4_matches_rubro = df_prod_preview["maybe_rubro_or_stock"].str.strip().str.lower().isin(known_rubros).sum() if "maybe_rubro_or_stock" in df_prod_preview else 0
        col4_numeric = pd.to_numeric(df_prod_preview["maybe_rubro_or_stock"], errors="coerce").notna().sum() if "maybe_rubro_or_stock" in df_prod_preview else 0
        col3_numeric = pd.to_numeric(df_prod_preview["id_rubro_or_stock"], errors="coerce").notna().sum()

        # Inicializar columnas limpias en df_prod_clean:
        df_prod_clean = pd.DataFrame()
        df_prod_clean["id_producto"] = df_prod["id_producto"].astype(str).str.strip()
        df_prod_clean["descripcion"] = df_prod["descripcion"].astype(str).str.strip()

        # decidir id_rubro y nombre_rubro
        if "maybe_rubro_or_stock" in df_prod.columns and col4_matches_rubro > 0:
            # la columna maybe contiene los nombres de rubro
            df_prod_clean["nombre_rubro"] = df_prod["maybe_rubro_or_stock"].astype(str).str.strip()
            # la otra columna probablemente sea stock -> intentar parsear int
            df_prod_clean["stock"] = pd.to_numeric(df_prod["id_rubro_or_stock"], errors="coerce").fillna(0).astype(int)
            df_prod_clean["id_rubro"] = pd.NA
        elif col3_numeric > col4_numeric:
            # la columna 3 (id_rubro_or_stock) parece numérica -> la tratamos como id_rubro
            df_prod_clean["id_rubro"] = pd.to_numeric(df_prod["id_rubro_or_stock"], errors="coerce").astype('Int64')
            # maybe_rubro_or_stock puede ser nombre de rubro (si es string)
            if "maybe_rubro_or_stock" in df_prod.columns:
                # si coincide con known_rubros lo guardamos
                df_prod_clean["nombre_rubro"] = df_prod["maybe_rubro_or_stock"].where(df_prod["maybe_rubro_or_stock"].astype(str).str.strip().str.lower().isin(known_rubros), pd.NA)
            else:
                df_prod_clean["nombre_rubro"] = pd.NA
            # stock probablemente está en maybe_rubro_or_stock cuando col3 es id, intentar leer
            df_prod_clean["stock"] = pd.to_numeric(df_prod["maybe_rubro_or_stock"], errors="coerce").fillna(0).astype(int) if "maybe_rubro_or_stock" in df_prod else 0
        else:
            # fallback: interpretar columna 3 como stock y 4 como rubro-nombre
            df_prod_clean["stock"] = pd.to_numeric(df_prod["id_rubro_or_stock"], errors="coerce").fillna(0).astype(int)
            df_prod_clean["nombre_rubro"] = df_prod["maybe_rubro_or_stock"].astype(str).str.strip() if "maybe_rubro_or_stock" in df_prod else pd.NA
            # intentar extraer id_rubro buscando coincidencias en df_rub por nombre
            df_prod_clean["id_rubro"] = pd.NA
            # mas abajo intentaremos mapear nombre_rubro -> id_rubro con df_rub

        # precio
        df_prod_clean["precio"] = pd.to_numeric(df_prod["precio"], errors="coerce").fillna(0.0)

        # normalizar columnas como strings para merge por descripcion
        df_det["id_producto_str"] = df_det["id_producto"].astype(str).str.strip()
        df_prod_clean["id_producto_str"] = df_prod_clean["id_producto"].astype(str).str.strip()
        df_prod_clean["descripcion_str"] = df_prod_clean["descripcion"].astype(str).str.strip()
        # nombre_rubro columna si existe
        if "nombre_rubro" in df_prod_clean.columns:
            df_prod_clean["nombre_rubro"] = df_prod_clean["nombre_rubro"].astype(str).replace("None", pd.NA).str.strip()

        # --- intentar relacionar detalle con producto ---
        merged_by_id = df_det.merge(df_prod_clean, left_on="id_producto_str", right_on="id_producto_str", how="left", suffixes=("_det", "_prod"))
        matches_by_id = merged_by_id["descripcion_str"].notna().sum()
        print("DEBUG matches_by_id:", matches_by_id)

        if matches_by_id > 0:
            df_for_top = merged_by_id
        else:
            # fallback: si en detalle vienen descripciones (como en tu caso), merge por descripcion
            df_det["descripcion_guess"] = df_det["id_producto_str"]
            merged_by_desc = df_det.merge(df_prod_clean, left_on="descripcion_guess", right_on="descripcion_str", how="left", suffixes=("_det", "_prod"))
            matches_by_desc = merged_by_desc["descripcion_str"].notna().sum()
            print("DEBUG matches_by_desc:", matches_by_desc)
            df_for_top = merged_by_desc

        if df_for_top["descripcion_str"].isna().all():
            ctk.CTkLabel(frame, text="⚠️ No se pudieron relacionar detalle ↔ producto.", text_color="red").pack(pady=8)
            return

        # --- Top 5 productos (por cantidad) ---
        top_prod = (
            df_for_top.groupby("descripcion_str")["cantidad"]
            .sum()
            .reset_index()
            .rename(columns={"cantidad": "cantidad_total", "descripcion_str": "descripcion"})
            .sort_values("cantidad_total", ascending=False)
            .head(5)
        )

        if top_prod.empty:
            ctk.CTkLabel(frame, text="⚠️ No hay ventas para mostrar en Top productos.", text_color="red").pack()
        else:
            fig1, ax1 = plt.subplots(figsize=(6, 4))
            ax1.barh(top_prod["descripcion"], top_prod["cantidad_total"], color="#4CAF50")
            ax1.set_title("Top 5 Productos más Vendidos", fontsize=13)
            ax1.set_xlabel("Cantidad Vendida")
            ax1.tick_params(axis="x", colors="white")
            ax1.tick_params(axis="y", colors="white")
            fig1.tight_layout()
            canvas1 = FigureCanvasTkAgg(fig1, master=frame)
            canvas1.draw()
            canvas1.get_tk_widget().pack(side="left", padx=16, pady=16)

        # --- Top 3 rubros ---
        # si ya tenemos nombre_rubro en df_prod_clean lo usamos; si no, intentamos mapear id_rubro -> nombre_rubro usando df_rub
        # normalizar df_rub id a string también
        df_rub["id_rubro_str"] = df_rub["id_rubro"].astype(str).str.strip()
        df_rub["nombre_rubro_str"] = df_rub["nombre_rubro"].astype(str).str.strip()

        # si df_prod_clean tiene nombre_rubro rellena ok; si no intentamos mapear por id_rubro (int)
        if df_prod_clean.get("nombre_rubro").isna().all():
            # mapear id_rubro (Int) -> nombre_rubro
            # aseguremos id_rubro_str en df_prod_clean
            if "id_rubro" in df_prod_clean.columns:
                df_prod_clean["id_rubro_str"] = df_prod_clean["id_rubro"].astype(str).replace("<NA>", "").str.strip()
            else:
                df_prod_clean["id_rubro_str"] = ""
        else:
            # ya hay nombre_rubro en df_prod_clean, aseguramos columna id si existe
            if "id_rubro" not in df_prod_clean.columns:
                df_prod_clean["id_rubro_str"] = ""
            else:
                df_prod_clean["id_rubro_str"] = df_prod_clean["id_rubro"].astype(str).replace("<NA>", "").str.strip()

        # unir la info usada (df_for_top ya contiene las columnas de producto)
        # asegurarnos de tener columna id_rubro_str y nombre_rubro_str en df_for_top
        if "id_rubro_str" not in df_for_top.columns:
            df_for_top["id_rubro_str"] = df_for_top["id_rubro"].astype(str).replace("nan", "").replace("<NA>", "") if "id_rubro" in df_for_top else ""
        if "nombre_rubro" not in df_for_top.columns:
            df_for_top["nombre_rubro"] = df_for_top.get("nombre_rubro", pd.NA)

        # si nombre_rubro está vacío, intentar obtenerlo desde df_rub por id
        # construir tabla de ventas por rubro
        # prioridad: usar nombre_rubro (producto) si existe, sino mapear id_rubro -> nombre_rubro
        # crear columna rubro_key que contenga el nombre final
        df_for_top["rubro_name_candidate"] = df_for_top["nombre_rubro"].where(df_for_top["nombre_rubro"].notna() & (df_for_top["nombre_rubro"] != "None"), pd.NA)
        # map id->nombre para filas que no tienen nombre
        mask_no_name = df_for_top["rubro_name_candidate"].isna()
        if mask_no_name.any():
            # intentar merge por id_rubro_str
            left = df_for_top.loc[mask_no_name, :].copy()
            left["id_rubro_str"] = left.get("id_rubro", "").astype(str).str.strip()
            tmp = left.merge(df_rub[["id_rubro_str", "nombre_rubro_str"]], left_on="id_rubro_str", right_on="id_rubro_str", how="left")
            df_for_top.loc[mask_no_name, "rubro_name_candidate"] = tmp["nombre_rubro_str"].values

        # ahora agrupar por rubro_name_candidate
        rubro_ventas = (
            df_for_top.groupby("rubro_name_candidate")["cantidad"]
            .sum()
            .reset_index()
            .rename(columns={"rubro_name_candidate": "nombre_rubro", "cantidad": "cantidad_total"})
            .sort_values("cantidad_total", ascending=False)
            .head(3)
        )

        if rubro_ventas.empty or rubro_ventas["cantidad_total"].sum() == 0:
            ctk.CTkLabel(frame, text="⚠️ No hay datos de rubros para mostrar.", text_color="red").pack(pady=8)
            return

        fig2, ax2 = plt.subplots(figsize=(6, 4))
        ax2.barh(rubro_ventas["nombre_rubro"], rubro_ventas["cantidad_total"], color="#2196F3")
        ax2.set_title("Top 3 Rubros con más Ventas", fontsize=13)
        ax2.set_xlabel("Cantidad Vendida")
        ax2.tick_params(axis="x", colors="white")
        ax2.tick_params(axis="y", colors="white")
        fig2.tight_layout()
        canvas2 = FigureCanvasTkAgg(fig2, master=frame)
        canvas2.draw()
        canvas2.get_tk_widget().pack(side="left", padx=16, pady=16)


def abrir_dashboard(parent=None):
    DashboardWindow(parent)
