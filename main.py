import repository as db
import ui
import os
import pandas as pd
import json

def export_all_to_csv():
    """Exporta todas las tablas de la base de datos a archivos CSV en una carpeta 'export_csv'."""
    export_dir = "export_csv"
    os.makedirs(export_dir, exist_ok=True)

    try:
        tables = db.get_all_data(return_data=True)
        if not tables or all(df.empty for df in tables.values()):
            print("⚠️ No hay datos en la base de datos para exportar.")
            return

        for name, df in tables.items():
            path = os.path.join(export_dir, f"{name}.csv")
            df.to_csv(path, index=False, encoding="utf-8-sig")
            print(f"✅ Exportado: {path}")

        print("\n📁 Todos los datos fueron exportados correctamente en formato CSV (carpeta 'export_csv').")
    except Exception as e:
        print(f"❌ Error al exportar los datos a CSV: {e}")

def export_all_to_json():
    """Exporta todas las tablas de la base de datos a archivos JSON individuales en una carpeta 'export_json'."""
    export_dir = "export_json"
    os.makedirs(export_dir, exist_ok=True)

    try:
        tables = db.get_all_data(return_data=True)
        if not tables or all(df.empty for df in tables.values()):
            print("⚠️ No hay datos en la base de datos para exportar.")
            return

        for name, df in tables.items():
            path = os.path.join(export_dir, f"{name}.json")
            df.to_json(path, orient="records", indent=4, force_ascii=False)
            print(f"✅ Exportado: {path}")

        print("\n📁 Todos los datos fueron exportados correctamente en formato JSON (carpeta 'export_json').")
    except Exception as e:
        print(f"❌ Error al exportar los datos a JSON: {e}")

def verificar_base_creada():
    """Verifica si la base de datos existe."""
    return os.path.exists("coral_tech.db")

def verificar_datos_cargados():
    """Verifica si hay datos en la base."""
    try:
        tablas = db.get_all_data(return_data=True)
        if tablas and any(not df.empty for df in tablas.values()):
            return True
        return False
    except Exception:
        return False

def main():
    while True:
        print("\n" + "=" * 60)
        print("💻  CORAL TECH - PANEL PRINCIPAL")
        print("=" * 60)
        print("1️⃣  Crear base de datos")
        print("2️⃣  Cargar datos desde CSV")
        print("3️⃣  Mostrar todos los datos")
        print("4️⃣  Eliminar base de datos")
        print("5️⃣  Ejecutar interfaz gráfica (UI)")
        print("6️⃣  Exportar todos los datos (CSV o JSON) 📤")
        print("0️⃣  Salir")
        print("=" * 60)

        opcion = input("👉 Elige una opción: ").strip()

        match opcion:
            case "1":
                print("🔧 Creando base de datos...")
                db.create_db()

            case "2":
                if not verificar_base_creada():
                    print("❌ Error: No existe una base de datos. Crea una antes de cargar datos (opción 1).")
                else:
                    print("📂 Cargando datos desde CSV...")
                    db.load_csv_data()

            case "3":
                if not verificar_base_creada():
                    print("❌ Error: No hay base de datos creada. Usa la opción 1 para crearla primero.")
                elif not verificar_datos_cargados():
                    print("⚠️ No hay datos cargados en la base de datos todavía.")
                else:
                    print("📊 Mostrando todos los datos...")
                    db.get_all_data()

            case "4":
                if not verificar_base_creada():
                    print("⚠️ No hay ninguna base de datos para eliminar.")
                else:
                    print("⚠️  Eliminando base de datos...")
                    db.delete_db()

            case "5":
                if not verificar_base_creada():
                    print("❌ Error: No hay base de datos creada. Crea una antes de ejecutar la interfaz.")
                else:
                    print("🖥️  Abriendo interfaz gráfica...")
                    ui.run_ui()

            case "6":
                if not verificar_base_creada():
                    print("❌ Error: No hay base de datos creada. Crea una antes de exportar datos.")
                else:
                    print("\n📤 ¿En qué formato querés exportar los datos?")
                    print("1️⃣  Exportar como CSV (archivos separados en 'export_csv')")
                    print("2️⃣  Exportar como JSON (archivos separados en 'export_json')")
                    formato = input("👉 Elige una opción (1 o 2): ").strip()

                    if formato == "1":
                        export_all_to_csv()
                    elif formato == "2":
                        export_all_to_json()
                    else:
                        print("❌ Opción inválida. Volviendo al menú principal...")

            case "0":
                print("👋 Cerrando el sistema Coral Tech... ¡Hasta luego!")
                break

            case _:
                print("❌ Opción no válida. Intenta nuevamente.")


if __name__ == '__main__':
    main()
