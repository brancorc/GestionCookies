import tkinter as tk
from tkinter import ttk, messagebox
from config.settings import SABORES_VALIDOS
from utils.validators import validar_numero

class EditWindow:
    def __init__(self, parent, db_manager, pedido, callback_actualizar):
        self.parent = parent
        self.db_manager = db_manager
        self.pedido = pedido
        self.callback_actualizar = callback_actualizar
        self.items_edit_actual = pedido.get('items', []).copy()

        # Crear ventana
        self.win = tk.Toplevel(parent)
        self.win.title(f"Editar Pedido #{pedido['id']}")
        self.win.state('zoomed')
        self.win.grab_set()

        self._setup_ui()

    def _setup_ui(self):
        """Configura la interfaz de la ventana de edición."""
        frame_edit = ttk.Frame(self.win, padding="10")
        frame_edit.pack(expand=True, fill=tk.BOTH)

        # Frame para datos generales
        self._setup_datos_generales(frame_edit)
        # Frame para items
        self._setup_items_frame(frame_edit)
        # Frame para botones
        self._setup_buttons(frame_edit)

    def _setup_datos_generales(self, parent):
        """Configura el frame de datos generales."""
        frame_datos_generales = ttk.LabelFrame(parent, text="Datos Generales", padding="10")
        frame_datos_generales.pack(pady=5, fill=tk.X)

        # Campos de entrada
        self.edit_entry_dia = self._create_entry_field(frame_datos_generales, "Día Entrega:", 0)
        self.edit_entry_nombre = self._create_entry_field(frame_datos_generales, "Nombre Cliente:", 1)
        self.edit_entry_precio_pedido = self._create_entry_field(frame_datos_generales, "Precio Pedido ($):", 2)
        self.edit_entry_precio_envio = self._create_entry_field(frame_datos_generales, "Precio Envío ($):", 3)
        self.edit_entry_direccion = self._create_entry_field(frame_datos_generales, "Dirección:", 4)
        self.edit_entry_horario = self._create_entry_field(frame_datos_generales, "Horario Entrega:", 5)

        # Llenar campos con datos actuales
        self.edit_entry_dia.insert(0, self.pedido.get('dia', ''))
        self.edit_entry_nombre.insert(0, self.pedido.get('nombre', ''))
        self.edit_entry_precio_pedido.insert(0, str(self.pedido.get('precio_pedido', '')))
        self.edit_entry_precio_envio.insert(0, str(self.pedido.get('precio_envio', '')))
        self.edit_entry_direccion.insert(0, self.pedido.get('direccion', ''))
        self.edit_entry_horario.insert(0, self.pedido.get('horario', ''))

    def _create_entry_field(self, parent, label_text, row):
        """Crea un campo de entrada con su etiqueta."""
        ttk.Label(parent, text=label_text).grid(row=row, column=0, padx=5, pady=5, sticky=tk.W)
        entry = ttk.Entry(parent, width=30)
        entry.grid(row=row, column=1, padx=5, pady=5)
        return entry

    def _setup_items_frame(self, parent):
        """Configura el frame para los items del pedido."""
        frame_items_edit = ttk.LabelFrame(parent, text="Items del Pedido", padding="10")
        frame_items_edit.pack(pady=10, fill=tk.BOTH, expand=True)

        # Frame para agregar items
        frame_add_item_edit = ttk.Frame(frame_items_edit)
        frame_add_item_edit.pack(pady=5, fill=tk.X)

        ttk.Label(frame_add_item_edit, text="Sabor:").pack(side=tk.LEFT, padx=5)
        self.edit_combo_sabor_item = ttk.Combobox(frame_add_item_edit, values=SABORES_VALIDOS, width=15, state='readonly')
        self.edit_combo_sabor_item.pack(side=tk.LEFT, padx=5)

        ttk.Label(frame_add_item_edit, text="Cantidad:").pack(side=tk.LEFT, padx=5)
        self.edit_entry_cantidad_item = ttk.Entry(frame_add_item_edit, width=8)
        self.edit_entry_cantidad_item.pack(side=tk.LEFT, padx=5)

        ttk.Button(frame_add_item_edit, text="Añadir Item", command=self.agregar_item_edit).pack(side=tk.LEFT, padx=10)

        # Treeview para items
        self.tree_items_edit = ttk.Treeview(frame_items_edit, columns=('sabor', 'cantidad'), show='headings', height=5)
        self.tree_items_edit.heading('sabor', text='Sabor')
        self.tree_items_edit.column('sabor', width=150)
        self.tree_items_edit.heading('cantidad', text='Cantidad')
        self.tree_items_edit.column('cantidad', width=80, anchor=tk.E)
        self.tree_items_edit.pack(fill=tk.BOTH, expand=True)

        ttk.Button(frame_items_edit, text="Quitar Item Seleccionado", command=self.quitar_item_edit).pack(pady=5)

        # Cargar items iniciales
        self.actualizar_tree_items_edit()

    def _setup_buttons(self, parent):
        """Configura el frame de botones."""
        btn_frame = ttk.Frame(parent)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Guardar Cambios", command=self.guardar_cambios).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self.win.destroy).pack(side=tk.LEFT, padx=5)

    def actualizar_tree_items_edit(self):
        """Actualiza el Treeview de items en la ventana de edición."""
        for item in self.tree_items_edit.get_children():
            self.tree_items_edit.delete(item)
        for i, item in enumerate(self.items_edit_actual):
            self.tree_items_edit.insert('', 'end', iid=i, values=(item['sabor'], item['cantidad']))

    def agregar_item_edit(self):
        """Agrega un item en la ventana de edición."""
        sabor = self.edit_combo_sabor_item.get().strip().capitalize()
        cantidad_str = self.edit_entry_cantidad_item.get().strip()

        if not sabor or sabor not in SABORES_VALIDOS:
            messagebox.showwarning("Item Inválido", "Sabor inválido.", parent=self.win)
            return

        cantidad = validar_numero(cantidad_str, tipo='int', permitir_cero=False)
        if cantidad is None:
            messagebox.showwarning("Item Inválido", "Cantidad inválida.", parent=self.win)
            return

        self.items_edit_actual.append({'sabor': sabor, 'cantidad': cantidad})
        self.actualizar_tree_items_edit()
        self.edit_combo_sabor_item.set('')
        self.edit_entry_cantidad_item.delete(0, tk.END)

    def quitar_item_edit(self):
        """Quita el item seleccionado en la ventana de edición."""
        seleccionados = self.tree_items_edit.selection()
        if not seleccionados:
            messagebox.showwarning("Selección Vacía", "Seleccione item a quitar.", parent=self.win)
            return

        indices_a_quitar = sorted([int(iid) for iid in seleccionados], reverse=True)
        for index in indices_a_quitar:
            if 0 <= index < len(self.items_edit_actual):
                del self.items_edit_actual[index]
        self.actualizar_tree_items_edit()

    def guardar_cambios(self):
        """Guarda los cambios realizados en el pedido."""
        # Recoger datos
        dia = self.edit_entry_dia.get().strip()
        nombre = self.edit_entry_nombre.get().strip()
        precio_pedido_str = self.edit_entry_precio_pedido.get().strip()
        precio_envio_str = self.edit_entry_precio_envio.get().strip()
        direccion = self.edit_entry_direccion.get().strip()
        horario = self.edit_entry_horario.get().strip()

        # Validaciones
        if not dia or not nombre:
            messagebox.showerror("Error", "Día y Nombre son obligatorios.", parent=self.win)
            return

        precio_pedido = validar_numero(precio_pedido_str, tipo='float', permitir_cero=False, permitir_vacio=False)
        if precio_pedido is None:
            messagebox.showerror("Error", "Precio del pedido inválido.", parent=self.win)
            return

        precio_envio = validar_numero(precio_envio_str, tipo='float', permitir_cero=True, permitir_vacio=True)
        if precio_envio is None:
            messagebox.showerror("Error", "Precio del envío inválido.", parent=self.win)
            return

        if not self.items_edit_actual:
            messagebox.showerror("Error", "El pedido debe tener al menos un item.", parent=self.win)
            return

        try:
            self.db_manager.actualizar_pedido(
                self.pedido['id'],
                dia, nombre, precio_pedido, precio_envio,
                direccion, horario, self.items_edit_actual
            )
            self.win.destroy()
            self.callback_actualizar()
            messagebox.showinfo("Éxito", "Pedido actualizado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el pedido: {e}", parent=self.win) 