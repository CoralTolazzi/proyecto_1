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


def execute_query(query, params=(), fetch=False):
    import sqlite3
    connection = sqlite3.connect("coral_tech.db")
    cursor = connection.cursor()
    try:
        cursor.execute(query, params)
        if fetch:
            result = cursor.fetchall()
        else:
            result = None
        connection.commit()  # 🔥 importante, sin esto no guarda los INSERT
        return result
    except sqlite3.Error as e:
        print(f"[DB ERROR] {e}")
        return None
    finally:
        connection.close()



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


def create_product(descripcion: str, precio: float, rubro_nombre: str, stock: int):
    id_rubro = get_rubro_id_by_name(rubro_nombre)
    execute_query("""
        INSERT INTO producto (descripcion, precio, id_rubro, stock)
        VALUES (?, ?, ?, ?)
    """, (descripcion, precio, id_rubro, stock), commit=True)


def update_product(id_producto: int, descripcion: str, precio: float, stock: int, rubro_nombre: str):
    id_rubro = get_rubro_id_by_name(rubro_nombre)
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
        SELECT c.id_cliente, c.nombre, p.nombre_provincia, c.domicilio, c.telefono, c.email
        FROM cliente AS c
        JOIN provincia AS p ON c.id_provincia = p.id_provincia
        ORDER BY c.id_cliente
    """, fetch="all")

def create_client(nombre, id_provincia, domicilio, telefono, email):
    execute_query("""
        INSERT INTO cliente (nombre, id_provincia, domicilio, telefono, email)
        VALUES (?, ?, ?, ?, ?)
    """, (nombre, id_provincia, domicilio, telefono, email))
    print(f"[OK] Cliente agregado: {nombre}")


def update_client(id_cliente: int, nombre: str, id_provincia: int, domicilio: str, telefono: str, email: str):
    execute_query("""
        UPDATE cliente
        SET nombre = ?, id_provincia = ?, domicilio = ?, telefono = ?, email = ?
        WHERE id_cliente = ?
    """, (nombre, id_provincia, domicilio, telefono, email, id_cliente), commit=True)


def get_client_by_id(id_cliente: int):
    return execute_query("""
        SELECT c.id_cliente, c.nombre, p.nombre_provincia, c.domicilio
        FROM cliente AS c
        JOIN provincia AS p ON c.id_provincia = p.id_provincia
        WHERE c.id_cliente = ?
    """, (id_cliente,), fetch="one")


def delete_client(id_cliente):
    execute_query("DELETE FROM cliente WHERE id_cliente = ?", (id_cliente,))
    print(f"[OK] Cliente con ID {id_cliente} eliminado.")


# --------------- Facturas ---------------

def get_invoices():
    """
    Devuelve todas las facturas con el nombre del cliente y el total calculado.
    Hace JOIN entre factura y cliente.
    """
    query = """
        SELECT 
            f.id_factura AS id,
            c.nombre AS cliente,
            f.fecha AS fecha,
            COALESCE(SUM(df.cantidad * df.precio_unitario), 0) AS total
        FROM factura AS f
        JOIN cliente AS c ON f.id_cliente = c.id_cliente
        LEFT JOIN detalle_factura AS df ON f.id_factura = df.id_factura
        GROUP BY f.id_factura, c.nombre, f.fecha
        ORDER BY f.id_factura;
    """
    rows = execute_query(query, fetch="all")

    # Convertimos cada fila a un dict para la UI
    facturas = [
        {"id": row[0], "cliente": row[1], "fecha": row[2], "total": row[3]}
        for row in rows
    ]
    return facturas


def get_invoice_details(factura_id: int):
    """
    Devuelve el detalle de una factura: producto, cantidad, precio unitario, subtotal, id_producto.
    Hace JOIN entre detalle_factura y producto.
    """
    query = """
        SELECT 
            p.id_producto,
            p.descripcion AS producto,
            df.cantidad,
            df.precio_unitario,
            (df.cantidad * df.precio_unitario) AS subtotal
        FROM detalle_factura AS df
        JOIN producto AS p ON df.id_producto = p.id_producto
        WHERE df.id_factura = ?
        ORDER BY p.descripcion;
    """
    rows = execute_query(query, (factura_id,), fetch="all")

    detalles = [
        {
            "id_producto": row[0],
            "producto": row[1],
            "cantidad": row[2],
            "precio_unitario": row[3],
            "subtotal": row[4],
        }
        for row in rows
    ]
    return detalles

def get_detalles_por_factura(id_factura):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                p.id_producto,
                p.descripcion AS producto_nombre,
                df.cantidad,
                df.precio_unitario
            FROM detalle_factura AS df
            JOIN producto AS p ON df.id_producto = p.id_producto
            WHERE df.id_factura = ?
        """, (id_factura,))
        result = [
            {
                "id_producto": row[0],
                "producto_nombre": row[1],
                "cantidad": row[2],
                "precio_unitario": row[3]
            }
            for row in cursor.fetchall()
        ]
    return result



# -------------- Rubros ------------
def get_rubros():
    return execute_query("SELECT id_rubro, nombre_rubro FROM rubro ORDER BY id_rubro", fetch="all")

def get_rubro_id_by_name(nombre_rubro: str):
    """Devuelve el id_rubro a partir del nombre del rubro"""
    result = execute_query("SELECT id_rubro FROM rubro WHERE nombre_rubro = ?", (nombre_rubro,), fetch="one")
    return result[0] if result else None


def create_rubro(nombre_rubro: str):
    execute_query("INSERT INTO rubro (nombre_rubro) VALUES (?)", (nombre_rubro,), commit=True)

def update_rubro(id_rubro: int, nombre_rubro: str):
    execute_query("UPDATE rubro SET nombre_rubro = ? WHERE id_rubro = ?", (nombre_rubro, id_rubro), commit=True)

def delete_rubro(id_rubro: int):
    execute_query("DELETE FROM rubro WHERE id_rubro = ?", (id_rubro,), commit=True)

# --------------- Operaciones sobre detalle_factura ---------------

def add_invoice_product(id_factura: int, id_producto: int, cantidad: int, precio_unitario: float):
    """
    Agrega un producto a una factura en detalle_factura.
    """
    execute_query("""
        INSERT INTO detalle_factura (id_factura, id_producto, cantidad, precio_unitario)
        VALUES (?, ?, ?, ?)
    """, (id_factura, id_producto, cantidad, precio_unitario), commit=True)


def delete_invoice_product(id_factura: int, id_producto: int):
    """
    Elimina un producto específico del detalle de una factura.
    """
    execute_query("""
        DELETE FROM detalle_factura
        WHERE id_factura = ? AND id_producto = ?
    """, (id_factura, id_producto), commit=True)
