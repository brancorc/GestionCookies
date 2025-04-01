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

        # Crear ventana Toplevel
        self.win = tk.Toplevel(parent)
        self.win.title(f"Editar Pedido #{pedido['id']}")
        self.win.state("zoomed")

        # Frame principal
        self.frame = ttk.Frame(self.win, padding="10")
        self.frame.pack(expand=True, fill=tk.BOTH)

        self._setup_ui()

    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        # Frame para datos generales
        frame_datos_generales = ttk.LabelFrame(self.frame, text="Datos Generales", padding="10")
        frame_datos_generales.pack(pady=5, fill=tk.X)

        # Campos de entrada
        self.entry_dia = self._create_entry_field(frame_datos_generales, "Día Entrega:", 0)
        self.entry_nombre = self._create_entry_field(frame_datos_generales, "Nombre Cliente:", 1)
        self.entry_precio_pedido = self._create_entry_field(frame_datos_generales, "Precio Pedido ($):", 2)
        self.entry_precio_envio = self._create_entry_field(frame_datos_generales, "Precio Envío ($):", 3)
        self.entry_direccion = self._create_entry_field(frame_datos_generales, "Dirección:", 4)
        self.entry_horario = self._create_entry_field(frame_datos_generales, "Horario Entrega:", 5)

        # Checkbutton para estado de pago
        self.pago_var = tk.IntVar(value=self.pedido.get('pago', 0))
        ttk.Checkbutton(frame_datos_generales, text="Pedido Pagado", variable=self.pago_var).grid(
            row=6, column=0, columnspan=2, padx=5, pady=10, sticky=tk.W)

        # Frame para items
        self._setup_items_frame()

        # Frame para botones
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(pady=10)
        ttk.Button(btn_frame, text="Guardar Cambios", command=self.guardar_cambios).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancelar", command=self.win.destroy).pack(side=tk.LEFT, padx=5)

        # Cargar datos iniciales
        self._cargar_datos_iniciales()

    def _create_entry_field(self, parent, label_text, row):
        """Crea un campo de entrada con su etiqueta."""
        ttk.Label(parent, text=label_text).grid(row=row, column=0, padx=5, pady=5, sticky=tk.W)
        entry = ttk.Entry(parent, width=30)
        entry.grid(row=row, column=1, padx=5, pady=5)
        return entry

    def _setup_items_frame(self):
        """Configura el frame para los items del pedido."""
        frame_items = ttk.LabelFrame(self.frame, text="Items del Pedido", padding="10")
        frame_items.pack(pady=10, fill=tk.BOTH, expand=True)

        # Frame para agregar items
        frame_add_item = ttk.Frame(frame_items)
        frame_add_item.pack(pady=5, fill=tk.X)

        ttk.Label(frame_add_item, text="Sabor:").pack(side=tk.LEFT, padx=5)
        self.combo_sabor = ttk.Combobox(frame_add_item, values=SABORES_VALIDOS, width=15, state='readonly')
        self.combo_sabor.pack(side=tk.LEFT, padx=5)

        ttk.Label(frame_add_item, text="Cantidad:").pack(side=tk.LEFT, padx=5)
        self.entry_cantidad = ttk.Entry(frame_add_item, width=8)
        self.entry_cantidad.pack(side=tk.LEFT, padx=5)

        ttk.Button(frame_add_item, text="Añadir Item", command=self.agregar_item).pack(side=tk.LEFT, padx=10)

        # Treeview para items
        self.tree_items = ttk.Treeview(frame_items, columns=('sabor', 'cantidad'), show='headings', height=5)
        self.tree_items.heading('sabor', text='Sabor')
        self.tree_items.column('sabor', width=150)
        self.tree_items.heading('cantidad', text='Cantidad')
        self.tree_items.column('cantidad', width=80, anchor=tk.E)
        self.tree_items.pack(fill=tk.BOTH, expand=True)

        ttk.Button(frame_items, text="Quitar Item Seleccionado", command=self.quitar_item).pack(pady=5)

        # Actualizar treeview con items existentes
        self.actualizar_tree_items()

    def _cargar_datos_iniciales(self):
        """Carga los datos iniciales en los campos."""
        self.entry_dia.insert(0, self.pedido.get('dia', ''))
        self.entry_nombre.insert(0, self.pedido.get('nombre', ''))
        self.entry_precio_pedido.insert(0, str(self.pedido.get('precio_pedido', '')))
        self.entry_precio_envio.insert(0, str(self.pedido.get('precio_envio', '')))
        self.entry_direccion.insert(0, self.pedido.get('direccion', ''))
        self.entry_horario.insert(0, self.pedido.get('horario', ''))

    def actualizar_tree_items(self):
        """Actualiza el Treeview de items."""
        for item in self.tree_items.get_children():
            self.tree_items.delete(item)
        for i, item in enumerate(self.items_edit_actual):
            self.tree_items.insert('', 'end', iid=i, values=(item['sabor'], item['cantidad']))

    def agregar_item(self):
        """Agrega un nuevo item al pedido."""
        sabor = self.combo_sabor.get().strip().capitalize()
        cantidad_str = self.entry_cantidad.get().strip()

        if not sabor or sabor not in SABORES_VALIDOS:
            messagebox.showwarning("Inválido", "Sabor inválido.", parent=self.win)
            return
        cantidad = validar_numero(cantidad_str, tipo='int', permitir_cero=False)
        if cantidad is None:
            messagebox.showwarning("Inválido", "Cantidad inválida.", parent=self.win)
            return

        self.items_edit_actual.append({'sabor': sabor, 'cantidad': cantidad})
        self.actualizar_tree_items()
        self.combo_sabor.set('')
        self.entry_cantidad.delete(0, tk.END)

    def quitar_item(self):
        """Quita el item seleccionado del pedido."""
        seleccionados = self.tree_items.selection()
        if not seleccionados:
            messagebox.showwarning("Vacío", "Seleccione item a quitar.", parent=self.win)
            return
        indices_a_quitar = sorted([int(iid) for iid in seleccionados], reverse=True)
        for index in indices_a_quitar:
            if 0 <= index < len(self.items_edit_actual):
                del self.items_edit_actual[index]
        self.actualizar_tree_items()

    def guardar_cambios(self):
        """Guarda los cambios realizados en el pedido."""
        dia = self.entry_dia.get().strip()
        nombre = self.entry_nombre.get().strip()
        precio_pedido_str = self.entry_precio_pedido.get().strip()
        precio_envio_str = self.entry_precio_envio.get().strip()
        direccion = self.entry_direccion.get().strip()
        horario = self.entry_horario.get().strip()
        pago_estado = self.pago_var.get()

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
                self.pedido['id'], dia, nombre, precio_pedido, precio_envio,
                direccion, horario, self.items_edit_actual, pago_estado
            )
            self.win.destroy()
            self.callback_actualizar()
            messagebox.showinfo("Éxito", "Pedido actualizado correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el pedido: {e}", parent=self.win) 