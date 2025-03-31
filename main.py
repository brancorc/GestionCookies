import atexit
from database.db_manager import DatabaseManager
from gui.main_window import MainWindow

def main():
    # Inicializar el gestor de base de datos
    db_manager = DatabaseManager()
    
    # Registrar el cierre de la base de datos al salir
    atexit.register(db_manager.close)
    
    # Crear y ejecutar la ventana principal
    app = MainWindow(db_manager)
    app.run()

if __name__ == "__main__":
    main() 