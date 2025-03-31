import sqlite3
import os
from config.settings import DB_NAME

class DatabaseManager:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.init_db()

    def init_db(self):
        """Inicializa la conexión a la BD y crea las tablas si no existen."""
        db_exists = os.path.exists(DB_NAME)
        self.conn = sqlite3.connect(DB_NAME)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        print("Conectado a la base de datos.")

        if not db_exists:
            print("Creando tablas...")
            self._create_tables()
            print("Tablas creadas.")
        else:
            self.conn.execute("PRAGMA foreign_keys = ON")
            print("Tablas existentes cargadas.")

    def _create_tables(self):
        """Crea las tablas necesarias en la base de datos."""
        # Tabla de Pedidos principales
        self.cursor.execute('''
            CREATE TABLE pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dia TEXT NOT NULL,
                nombre TEXT NOT NULL,
                precio_pedido REAL NOT NULL,
                precio_envio REAL DEFAULT 0.0,
                direccion TEXT,
                horario TEXT,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Tabla de Items de cada Pedido
        self.cursor.execute('''
            CREATE TABLE pedido_items (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                pedido_id INTEGER NOT NULL,
                sabor TEXT NOT NULL,
                cantidad INTEGER NOT NULL,
                FOREIGN KEY (pedido_id) REFERENCES pedidos (id) ON DELETE CASCADE
            )
        ''')
        # Índice para búsquedas rápidas
        self.cursor.execute('CREATE INDEX idx_pedido_id ON pedido_items (pedido_id)')
        self.conn.commit()

    def close(self):
        """Cierra la conexión a la base de datos."""
        if self.conn:
            self.conn.close()
            print("Conexión a la base de datos cerrada.")

    def cargar_pedidos(self):
        """Carga todos los pedidos y sus items de la base de datos."""
        if not self.cursor:
            return []
        try:
            self.cursor.execute("SELECT * FROM pedidos ORDER BY dia, fecha_registro")
            pedidos_db = self.cursor.fetchall()
            pedidos_completos = []
            for pedido_row in pedidos_db:
                pedido_dict = dict(pedido_row)
                self.cursor.execute("SELECT sabor, cantidad FROM pedido_items WHERE pedido_id = ?", (pedido_dict['id'],))
                items_db = self.cursor.fetchall()
                pedido_dict['items'] = [dict(item) for item in items_db]
                pedidos_completos.append(pedido_dict)
            return pedidos_completos
        except sqlite3.Error as e:
            raise Exception(f"No se pudieron cargar los pedidos: {e}")

    def agregar_pedido(self, dia, nombre, precio_pedido, precio_envio, direccion, horario, items):
        """Agrega un nuevo pedido a la base de datos."""
        try:
            self.cursor.execute("BEGIN TRANSACTION")

            # Insertar en tabla pedidos
            sql_pedido = """
                INSERT INTO pedidos (dia, nombre, precio_pedido, precio_envio, direccion, horario)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            self.cursor.execute(sql_pedido, (dia, nombre, precio_pedido, precio_envio, direccion, horario))
            pedido_id = self.cursor.lastrowid

            # Insertar items
            sql_item = "INSERT INTO pedido_items (pedido_id, sabor, cantidad) VALUES (?, ?, ?)"
            for item in items:
                self.cursor.execute(sql_item, (pedido_id, item['sabor'], item['cantidad']))

            self.conn.commit()
            return pedido_id
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"No se pudo guardar el pedido: {e}")

    def eliminar_pedido(self, pedido_id):
        """Elimina un pedido y sus items de la base de datos."""
        try:
            self.cursor.execute("DELETE FROM pedidos WHERE id = ?", (pedido_id,))
            self.conn.commit()
            return self.cursor.rowcount > 0
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"No se pudo eliminar el pedido: {e}")

    def actualizar_pedido(self, pedido_id, dia, nombre, precio_pedido, precio_envio, direccion, horario, items):
        """Actualiza un pedido existente y sus items."""
        try:
            self.cursor.execute("BEGIN TRANSACTION")

            # Actualizar datos generales
            sql_update_pedido = """
                UPDATE pedidos
                SET dia = ?, nombre = ?, precio_pedido = ?, precio_envio = ?, direccion = ?, horario = ?
                WHERE id = ?
            """
            self.cursor.execute(sql_update_pedido, (dia, nombre, precio_pedido, precio_envio, direccion, horario, pedido_id))

            # Eliminar items antiguos
            self.cursor.execute("DELETE FROM pedido_items WHERE pedido_id = ?", (pedido_id,))

            # Insertar nuevos items
            sql_insert_item = "INSERT INTO pedido_items (pedido_id, sabor, cantidad) VALUES (?, ?, ?)"
            for item in items:
                self.cursor.execute(sql_insert_item, (pedido_id, item['sabor'], item['cantidad']))

            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            raise Exception(f"No se pudo actualizar el pedido: {e}")

    def obtener_pedido(self, pedido_id):
        """Obtiene un pedido específico y sus items."""
        try:
            self.cursor.execute("SELECT * FROM pedidos WHERE id = ?", (pedido_id,))
            pedido_row = self.cursor.fetchone()
            if not pedido_row:
                return None

            pedido_dict = dict(pedido_row)
            self.cursor.execute("SELECT sabor, cantidad FROM pedido_items WHERE pedido_id = ?", (pedido_id,))
            items_db = self.cursor.fetchall()
            pedido_dict['items'] = [dict(item) for item in items_db]
            return pedido_dict
        except sqlite3.Error as e:
            raise Exception(f"No se pudo obtener el pedido: {e}") 