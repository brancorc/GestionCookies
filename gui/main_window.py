import tkinter as tk
from tkinter import ttk, messagebox
from collections import defaultdict
from config.settings import SABORES_VALIDOS, WINDOW_TITLE
from utils.validators import validar_numero
from .edit_window import EditWindow

class MainWindow:
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.items_pedido_actual = []
        self.root = tk.Tk()
        self.root.title(WINDOW_TITLE)
        self.root.state('zoomed')
        self._setup_ui()
        self.actualizar_todo()

    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        # Estilo ttk
        style = ttk.Style()
        style.theme_use('clam')

        # Frame Principal
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(expand=True, fill=tk.BOTH)

        # Frame para el Formulario de Entrada
        self.form_frame = ttk.LabelFrame(self.main_frame, text="Registrar Nuevo Pedido", padding="10")
        self.form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self._setup_form_frame()
        self._setup_summary_frame()
        self._setup_list_frame()

        # Configurar grid weights
        self.main_frame.columnconfigure(1, weight=1)
        self.main_frame.rowconfigure(0, weight=1)

    def _setup_form_frame(self):
        """Configura el frame del formulario de entrada."""
        # Frame para datos del cliente
        frame_datos_cliente = ttk.Frame(self.form_frame)
        frame_datos_cliente.pack(pady=5, fill=tk.X)

        # Campos de entrada
        self.entry_dia = self._create_entry_field(frame_datos_cliente, "Día Entrega:", 0)
        self.entry_nombre = self._create_entry_field(frame_datos_cliente, "Nombre Cliente:", 1)
        self.entry_precio_pedido = self._create_entry_field(frame_datos_cliente, "Precio Pedido ($):", 2)
        self.entry_precio_envio = self._create_entry_field(frame_datos_cliente, "Precio Envío ($):", 3)
        self.entry_direccion = self._create_entry_field(frame_datos_cliente, "Dirección (si aplica):", 4)
        self.entry_horario = self._create_entry_field(frame_datos_cliente, "Horario (si aplica):", 5)

        # Frame para items del pedido
        self._setup_items_frame()

        # Botón para agregar pedido
        ttk.Button(self.form_frame, text="Agregar Pedido Completo", command=self.agregar_pedido).pack(pady=15)

    def _create_entry_field(self, parent, label_text, row):
        """Crea un campo de entrada con su etiqueta."""
        ttk.Label(parent, text=label_text).grid(row=row, column=0, padx=5, pady=2, sticky=tk.W)
        entry = ttk.Entry(parent, width=35)
        entry.grid(row=row, column=1, padx=5, pady=2)
        return entry

    def _setup_items_frame(self):
        """Configura el frame para los items del pedido."""
        frame_items_actual = ttk.LabelFrame(self.form_frame, text="Items del Pedido", padding="10")
        frame_items_actual.pack(pady=10, fill=tk.BOTH, expand=True)

        # Frame para agregar items
        frame_add_item = ttk.Frame(frame_items_actual)
        frame_add_item.pack(pady=5, fill=tk.X)

        ttk.Label(frame_add_item, text="Sabor:").pack(side=tk.LEFT, padx=2)
        self.combo_sabor_item = ttk.Combobox(frame_add_item, values=SABORES_VALIDOS, width=15, state='readonly')
        self.combo_sabor_item.pack(side=tk.LEFT, padx=2)

        ttk.Label(frame_add_item, text="Cant:").pack(side=tk.LEFT, padx=2)
        self.entry_cantidad_item = ttk.Entry(frame_add_item, width=5)
        self.entry_cantidad_item.pack(side=tk.LEFT, padx=2)

        ttk.Button(frame_add_item, text="Añadir Item", width=12, command=self.agregar_item_actual).pack(side=tk.LEFT, padx=5)

        # Treeview para items
        self.tree_items_actual = ttk.Treeview(frame_items_actual, columns=('sabor', 'cantidad'), show='headings', height=4)
        self.tree_items_actual.heading('sabor', text='Sabor')
        self.tree_items_actual.column('sabor', width=180)
        self.tree_items_actual.heading('cantidad', text='Cantidad')
        self.tree_items_actual.column('cantidad', width=70, anchor=tk.E)
        self.tree_items_actual.pack(pady=5, fill=tk.BOTH, expand=True)

        ttk.Button(frame_items_actual, text="Quitar Item Seleccionado", command=self.quitar_item_actual).pack(pady=5)

    def _setup_summary_frame(self):
        """Configura el frame para los resúmenes."""
        summary_frame = ttk.Frame(self.main_frame, padding="10")
        summary_frame.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        self.label_resumen_produccion = ttk.Label(summary_frame, text="Resumen de Producción:\n(Cargando...)", 
                                                justify=tk.LEFT, anchor="nw", relief="groove", padding=5, wraplength=350)
        self.label_resumen_produccion.pack(pady=5, fill=tk.X)

        self.label_total_recaudado = ttk.Label(summary_frame, text="Total Recaudado: $0.00", 
                                             justify=tk.LEFT, anchor="nw", relief="groove", padding=5)
        self.label_total_recaudado.pack(pady=5, fill=tk.X)

    def _setup_list_frame(self):
        """Configura el frame para la lista de pedidos."""
        list_frame = ttk.LabelFrame(self.main_frame, text="Pedidos Registrados", padding="10")
        list_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")

        # Configurar Treeview principal
        columns = ('dia', 'cliente', 'sabor', 'cantidad', 'precio', 'envio', 'direccion', 'horario')
        self.tree_pedidos = ttk.Treeview(list_frame, columns=columns, show='headings', height=20)

        # Configurar columnas
        self._configure_treeview_columns()

        # Scrollbars
        scrollbar_y = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree_pedidos.yview)
        scrollbar_x = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.tree_pedidos.xview)
        self.tree_pedidos.configure(yscroll=scrollbar_y.set, xscroll=scrollbar_x.set)

        # Empaquetar elementos
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.tree_pedidos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Frame para botones de acción
        action_buttons_frame = ttk.Frame(list_frame)
        action_buttons_frame.pack(fill=tk.X, pady=5, side=tk.BOTTOM)

        ttk.Button(action_buttons_frame, text="Editar Seleccionado", command=self.editar_pedido).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_buttons_frame, text="Eliminar Seleccionado(s)", command=self.eliminar_pedido).pack(side=tk.LEFT, padx=5)

    def _configure_treeview_columns(self):
        """Configura las columnas del Treeview principal."""
        column_configs = {
            'dia': ('Día', 80, tk.CENTER),
            'cliente': ('Cliente', 120, tk.W),
            'sabor': ('Sabor', 90, tk.W),
            'cantidad': ('Cant. Total', 70, tk.E),
            'precio': ('P. Pedido', 80, tk.E),
            'envio': ('P. Envío', 70, tk.E),
            'direccion': ('Dirección', 180, tk.W),
            'horario': ('Horario', 90, tk.W)
        }

        for col, (heading, width, anchor) in column_configs.items():
            self.tree_pedidos.heading(col, text=heading)
            self.tree_pedidos.column(col, width=width, anchor=anchor)

    def run(self):
        """Inicia el bucle principal de la aplicación."""
        self.root.mainloop()

    def actualizar_todo(self):
        """Actualiza todos los elementos de la interfaz."""
        self.actualizar_lista_pedidos()
        self.actualizar_resumen_produccion()
        self.actualizar_total_recaudado()

    def actualizar_lista_pedidos(self):
        """Actualiza la lista de pedidos en el Treeview."""
        for item in self.tree_pedidos.get_children():
            self.tree_pedidos.delete(item)

        try:
            pedidos = self.db_manager.cargar_pedidos()
            for pedido in pedidos:
                items = pedido.get('items', [])
                sabor_display = '??'
                cantidad_total = 0
                if items:
                    if len(items) == 1:
                        sabor_display = items[0].get('sabor', '??')
                        cantidad_total = items[0].get('cantidad', 0)
                    else:
                        sabor_display = "Múltiple"
                        cantidad_total = sum(item.get('cantidad', 0) for item in items)

                self.tree_pedidos.insert(
                    '', 'end', iid=pedido['id'],
                    values=(
                        pedido.get('dia', ''),
                        pedido.get('nombre', ''),
                        sabor_display,
                        cantidad_total if cantidad_total > 0 else '??',
                        f"${pedido.get('precio_pedido', 0.0):.2f}",
                        f"${pedido.get('precio_envio', 0.0):.2f}",
                        pedido.get('direccion', ''),
                        pedido.get('horario', '')
                    )
                )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los pedidos: {e}")

    def actualizar_resumen_produccion(self):
        """Actualiza el resumen de producción."""
        try:
            pedidos = self.db_manager.cargar_pedidos()
            produccion = defaultdict(int)

            for pedido in pedidos:
                for item in pedido.get('items', []):
                    if item.get('sabor') and item.get('cantidad'):
                        produccion[item['sabor']] += item['cantidad']

            resumen_texto = "Resumen de Producción:\n"
            if not produccion:
                resumen_texto += "(No hay pedidos registrados)"
            else:
                items_resumen = [f"- {cantidad} de {sabor}" for sabor, cantidad in sorted(produccion.items())]
                resumen_texto += "\n".join(items_resumen)

            self.label_resumen_produccion.config(text=resumen_texto)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el resumen: {e}")

    def actualizar_total_recaudado(self):
        """Actualiza el total recaudado."""
        try:
            pedidos = self.db_manager.cargar_pedidos()
            total = sum(
                pedido.get('precio_pedido', 0.0) + pedido.get('precio_envio', 0.0)
                for pedido in pedidos
            )
            self.label_total_recaudado.config(text=f"Total Recaudado: ${total:.2f}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el total: {e}")

    def limpiar_campos_entrada(self):
        """Limpia todos los campos de entrada."""
        self.entry_dia.delete(0, tk.END)
        self.entry_nombre.delete(0, tk.END)
        self.entry_precio_pedido.delete(0, tk.END)
        self.entry_precio_envio.delete(0, tk.END)
        self.entry_direccion.delete(0, tk.END)
        self.entry_horario.delete(0, tk.END)

        self.combo_sabor_item.set('')
        self.entry_cantidad_item.delete(0, tk.END)

        self.items_pedido_actual = []
        for item in self.tree_items_actual.get_children():
            self.tree_items_actual.delete(item)

        self.entry_dia.focus()

    def agregar_item_actual(self):
        """Agrega un item al pedido actual."""
        sabor = self.combo_sabor_item.get().strip().capitalize()
        cantidad_str = self.entry_cantidad_item.get().strip()

        if not sabor or sabor not in SABORES_VALIDOS:
            messagebox.showwarning("Item Inválido", f"Seleccione un sabor válido. '{sabor}' no lo es.")
            return

        cantidad = validar_numero(cantidad_str, tipo='int', permitir_cero=False)
        if cantidad is None:
            messagebox.showwarning("Item Inválido", "La cantidad debe ser un número entero positivo.")
            return

        nuevo_item = {'sabor': sabor, 'cantidad': cantidad}
        self.items_pedido_actual.append(nuevo_item)
        self.actualizar_tree_items_actual()

        self.combo_sabor_item.set('')
        self.entry_cantidad_item.delete(0, tk.END)
        self.combo_sabor_item.focus()

    def quitar_item_actual(self):
        """Quita el item seleccionado del pedido actual."""
        seleccionados = self.tree_items_actual.selection()
        if not seleccionados:
            messagebox.showwarning("Selección Vacía", "Seleccione un item de la lista para quitar.")
            return

        indices_a_quitar = []
        for item_iid in seleccionados:
            try:
                indices_a_quitar.append(int(item_iid))
            except ValueError:
                continue

        indices_a_quitar.sort(reverse=True)
        for index in indices_a_quitar:
            if 0 <= index < len(self.items_pedido_actual):
                del self.items_pedido_actual[index]

        self.actualizar_tree_items_actual()

    def actualizar_tree_items_actual(self):
        """Actualiza el Treeview de items del pedido actual."""
        for item in self.tree_items_actual.get_children():
            self.tree_items_actual.delete(item)
        for i, item in enumerate(self.items_pedido_actual):
            self.tree_items_actual.insert('', 'end', iid=i, values=(item['sabor'], item['cantidad']))

    def agregar_pedido(self):
        """Agrega un nuevo pedido a la base de datos."""
        # Recoger datos
        dia = self.entry_dia.get().strip()
        nombre = self.entry_nombre.get().strip()
        precio_pedido_str = self.entry_precio_pedido.get().strip()
        precio_envio_str = self.entry_precio_envio.get().strip()
        direccion = self.entry_direccion.get().strip()
        horario = self.entry_horario.get().strip()

        # Validaciones
        if not dia or not nombre:
            messagebox.showerror("Error", "Día y Nombre son obligatorios.")
            return

        if not self.items_pedido_actual:
            messagebox.showerror("Error", "Debe agregar al menos un item al pedido.")
            return

        precio_pedido = validar_numero(precio_pedido_str, tipo='float', permitir_cero=False, permitir_vacio=False)
        if precio_pedido is None:
            messagebox.showerror("Error", "El precio del pedido debe ser un número positivo.")
            return

        precio_envio = validar_numero(precio_envio_str, tipo='float', permitir_cero=True, permitir_vacio=True)
        if precio_envio is None:
            messagebox.showerror("Error", "El precio del envío debe ser un número (puede ser 0).")
            return

        if precio_envio > 0 and not direccion:
            if not messagebox.askyesno("Aviso", "Hay costo de envío pero no dirección. ¿Continuar?"):
                return

        try:
            self.db_manager.agregar_pedido(
                dia, nombre, precio_pedido, precio_envio,
                direccion, horario, self.items_pedido_actual
            )
            messagebox.showinfo("Éxito", "Pedido registrado correctamente.")
            self.limpiar_campos_entrada()
            self.actualizar_todo()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el pedido: {e}")

    def eliminar_pedido(self):
        """Elimina los pedidos seleccionados."""
        seleccionados = self.tree_pedidos.selection()
        if not seleccionados:
            messagebox.showwarning("Selección Vacía", "Por favor, seleccione el pedido que desea eliminar.")
            return

        if messagebox.askyesno("Confirmar Eliminación", "¿Está seguro de que desea eliminar los pedidos seleccionados?"):
            try:
                count = 0
                for pedido_id in seleccionados:
                    if self.db_manager.eliminar_pedido(int(pedido_id)):
                        count += 1

                if count > 0:
                    messagebox.showinfo("Eliminado", f"{count} Pedido(s) eliminado(s) correctamente.")
                    self.actualizar_todo()
                else:
                    messagebox.showwarning("Sin Cambios", "No se encontraron los pedidos seleccionados para eliminar.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar el pedido: {e}")

    def editar_pedido(self):
        """Abre la ventana de edición para el pedido seleccionado."""
        seleccionados = self.tree_pedidos.selection()
        if not seleccionados:
            messagebox.showwarning("Selección Vacía", "Por favor, seleccione el pedido que desea editar.")
            return
        if len(seleccionados) > 1:
            messagebox.showwarning("Selección Múltiple", "Por favor, seleccione solo un pedido para editar.")
            return

        try:
            pedido_id = int(seleccionados[0])
            pedido = self.db_manager.obtener_pedido(pedido_id)
            if not pedido:
                messagebox.showerror("Error", f"No se encontró el pedido con ID {pedido_id}.")
                return

            EditWindow(self.root, self.db_manager, pedido, self.actualizar_todo)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el pedido para editar: {e}") 