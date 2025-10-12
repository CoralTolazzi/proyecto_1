import repository as db
import ui

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

            case "0":
                print("👋 Cerrando el sistema Coral Tech... ¡Hasta luego!")
                break

            case _:
                print("❌ Opción no válida. Intenta nuevamente.")


if __name__ == '__main__':
    main()
