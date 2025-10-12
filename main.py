import repository as db
import ui
import os
import pandas as pd

def export_all_to_csv():
    """Exporta todas las tablas de la base de datos a archivos CSV en una carpeta 'exports'."""
    export_dir = "exports"
    os.makedirs(export_dir, exist_ok=True)

    try:
        tables = db.get_all_data(return_data=True)  # 🔥 modificaremos get_all_data() para que devuelva DataFrames
        for name, df in tables.items():
            path = os.path.join(export_dir, f"{name}.csv")
            df.to_csv(path, index=False, encoding="utf-8-sig")
            print(f"✅ Exportado: {path}")
        print("\n📁 Todos los datos fueron exportados correctamente a la carpeta 'exports/'")
    except Exception as e:
        print(f"❌ Error al exportar los datos: {e}")

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
        print("6️⃣  Exportar todos los datos a CSV 📤")
        print("0️⃣  Salir")
        print("=" * 60)

        opcion = input("👉 Elige una opción: ")

        match opcion:
            case "1":
                print("🔧 Creando base de datos...")
                db.create_db()

            case "2":
                print("📂 Cargando datos desde CSV...")
                db.load_csv_data()

            case "3":
                print("📊 Mostrando todos los datos...")
                db.get_all_data()

            case "4":
                print("⚠️  Eliminando base de datos...")
                db.delete_db()

            case "5":
                print("🖥️  Abriendo interfaz gráfica...")
                ui.run_ui()

            case "6":
                print("📤 Exportando todos los datos a CSV...")
                export_all_to_csv()

            case "0":
                print("👋 Cerrando el sistema Coral Tech... ¡Hasta luego!")
                break

            case _:
                print("❌ Opción no válida. Intenta nuevamente.")


if __name__ == '__main__':
    main()
