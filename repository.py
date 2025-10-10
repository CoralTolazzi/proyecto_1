import sqlite3
import pandas as pd
import os

DB_NAME = "coral_tech.db"
SQL_FILE = "init.sql"
CSV_FOLDER = "data"


def create_db():
    if os.path.exists(DB_NAME):
        print(f"Database '{DB_NAME}' already exists. Skipping creation.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    print(f"Creating database '{DB_NAME}'...")

    with open(SQL_FILE, "r", encoding="utf-8") as f:
        sql_script = f.read()
    cursor.executescript(sql_script)
    conn.commit()

    print("Base tables and initial data created successfully.")
    conn.close()


def load_csv_data():
    conn = sqlite3.connect(DB_NAME)

    # Map of table_name -> csv_filename
    csv_map = {
        "cliente": "cliente.csv",
        "rubro": "rubro.csv",
        "producto": "producto.csv",
        "factura": "factura.csv",
        "detalle_factura": "detalle_factura.csv"
    }

    for table, filename in csv_map.items():
        path = os.path.join(CSV_FOLDER, filename)
        if not os.path.exists(path):
            print(f"⚠️  CSV file not found for table '{table}': {path}")
            continue

        print(f"Loading '{filename}' into table '{table}'...")
        df = pd.read_csv(path)
        df.to_sql(table, conn, if_exists="append", index=False)

    conn.close()
    print("CSV data loaded successfully.")


def get_all_data(db_name="coral_tech.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    print("\n📂 Tables in database:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

    tables = cursor.fetchall().copy()

    for table in tables:
        print("  -", table[0])

    for table in tables:
        print("\n🧱 Table", table[0], ":")
        cursor.execute(f"SELECT * FROM {table[0]} LIMIT 20;")
        for row in cursor.fetchall():
            print(row)

    conn.close()


def delete_db():
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print(f"Database '{DB_NAME}' has been deleted.")
    else:
        print(f"Database '{DB_NAME}' does not exist.")


def delete_table(table_name):
    if not os.path.exists(DB_NAME):
        print(f"Database '{DB_NAME}' does not exist.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute(f"DROP TABLE IF EXISTS {table_name};")
        conn.commit()
        print(f"Table '{table_name}' has been deleted.")
    except sqlite3.Error as e:
        print("Error deleting table:", e)
    finally:
        conn.close()


def execute_query(query: str, params: tuple = (), fetch: str = None, commit: bool = False):
    """Helper to execute SQL queries safely"""
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)

        if commit:
            conn.commit()

        if fetch == "one":
            return cursor.fetchone()
        elif fetch == "all":
            return cursor.fetchall()
        return None


# --------------- Products ---------------

def get_products():
    return execute_query("""
        SELECT p.id_producto, p.descripcion, p.precio, p.stock, r.nombre_rubro
        FROM producto AS p
        JOIN rubro AS r ON p.id_rubro = r.id_rubro
        ORDER BY p.id_producto
    """, fetch="all")


def get_product_by_id(id_producto: int):
    return execute_query("""
        SELECT p.id_producto, p.descripcion, p.precio, p.stock, r.nombre_rubro
        FROM producto AS p
        JOIN rubro AS r ON p.id_rubro = r.id_rubro
        WHERE p.id_producto = ?
    """, (id_producto,), fetch="one")


def create_product(descripcion: str, precio: float, id_rubro: int, stock: int):
    execute_query("""
        INSERT INTO producto (descripcion, precio, id_rubro, stock)
        VALUES (?, ?, ?, ?)
    """, (descripcion, precio, id_rubro, stock), commit=True)


def update_product(id_producto: int, descripcion: str, precio: float, stock: int, id_rubro: int):
    execute_query("""
        UPDATE producto
        SET descripcion = ?, precio = ?, stock = ?, id_rubro = ?
        WHERE id_producto = ?
    """, (descripcion, precio, stock, id_rubro, id_producto), commit=True)


def delete_product(id_producto: int):
    execute_query("DELETE FROM producto WHERE id_producto = ?", (id_producto,), commit=True)



# --------------- Clients ---------------


def get_clients():
    return execute_query("""
        SELECT c.id_cliente, c.nombre, p.nombre_provincia, c.domicilio
        FROM cliente AS c
        JOIN provincia AS p ON c.id_provincia = p.id_provincia
        ORDER BY c.id_cliente
    """, fetch="all")


def get_client_by_id(id_cliente: int):
    return execute_query("""
        SELECT c.id_cliente, c.nombre, p.nombre_provincia, c.domicilio
        FROM cliente AS c
        JOIN provincia AS p ON c.id_provincia = p.id_provincia
        WHERE c.id_cliente = ?
    """, (id_cliente,), fetch="one")


def create_client(nombre: str, domicilio: str, id_provincia: int):
    execute_query("""
        INSERT INTO cliente (nombre, domicilio, id_provincia)
        VALUES (?, ?, ?)
    """, (nombre, domicilio, id_provincia), commit=True)


def update_client(id_cliente: int, nombre: str, id_provincia: int, domicilio: str):
    execute_query("""
        UPDATE cliente
        SET nombre = ?, id_provincia = ?, domicilio = ?
        WHERE id_cliente = ?
    """, (nombre, id_provincia, domicilio, id_cliente), commit=True)



def delete_client(id_cliente: int):
    execute_query("DELETE FROM cliente WHERE id_cliente = ?", (id_cliente,), commit=True)


# --------------- Facturas ---------------

def get_invoices():
    return [
        {"id": 1, "cliente": "Ana Gómez", "fecha": "2025-09-30", "total": 15500.0},
        {"id": 2, "cliente": "Luis Martínez", "fecha": "2025-10-01", "total": 9800.0},
    ]

def get_invoice_details(factura_id):
    if factura_id == 1:
        return [
            {"producto": "Notebook Lenovo", "cantidad": 1, "precio_unit": 15000.0, "subtotal": 15000.0},
            {"producto": "Mouse Logitech", "cantidad": 1, "precio_unit": 500.0, "subtotal": 500.0},
        ]
    elif factura_id == 2:
        return [
            {"producto": "Teclado Redragon", "cantidad": 2, "precio_unit": 4900.0, "subtotal": 9800.0},
        ]
    else:
        return []


# -------------- Rubros ------------
def get_rubros():
    return execute_query("SELECT id_rubro, nombre_rubro FROM rubro ORDER BY id_rubro", fetch="all")

def create_rubro(nombre_rubro: str):
    execute_query("INSERT INTO rubro (nombre_rubro) VALUES (?)", (nombre_rubro,), commit=True)

def update_rubro(id_rubro: int, nombre_rubro: str):
    execute_query("UPDATE rubro SET nombre_rubro = ? WHERE id_rubro = ?", (nombre_rubro, id_rubro), commit=True)

def delete_rubro(id_rubro: int):
    execute_query("DELETE FROM rubro WHERE id_rubro = ?", (id_rubro,), commit=True)


