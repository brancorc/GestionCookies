import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
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

        # Configurar Grid del main_frame
        self.main_frame.columnconfigure(0, weight=0)
        self.main_frame.columnconfigure(1, weight=2)
        self.main_frame.columnconfigure(2, weight=1)
        self.main_frame.rowconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=0)

        # Frame para el Formulario de Entrada
        self.form_frame = ttk.LabelFrame(self.main_frame, text="Registrar Nuevo Pedido", padding="10")
        self.form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self._setup_form_frame()
        self._setup_summary_frame()
        self._setup_list_frame()
        self._setup_daily_summary_frame()

        # Bindings
        self.tree_pedidos.bind("<Double-1>", self.toggle_pago_status)

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
        columns = ('dia', 'cliente', 'sabor', 'cantidad', 'precio', 'envio', 'direccion', 'horario', 'pago')
        self.tree_pedidos = ttk.Treeview(list_frame, columns=columns, show='headings', height=25)

        # Configurar columnas
        self._configure_treeview_columns()

        # Scrollbars
        scrollbar_y = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree_pedidos.yview)
        scrollbar_x = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.tree_pedidos.xview)
        self.tree_pedidos.configure(yscroll=scrollbar_y.set, xscroll=scrollbar_x.set)

        # Empaquetar elementos
        self.tree_pedidos.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')

        # Frame para botones de acción
        action_frame = ttk.Frame(list_frame)
        action_frame.grid(row=2, column=0, pady=10, sticky='ew')
        action_frame.columnconfigure(0, weight=1)
        action_frame.columnconfigure(1, weight=1)

        ttk.Button(action_frame, text="Editar Pedido", command=self.editar_pedido).grid(row=0, column=0, padx=5)
        ttk.Button(action_frame, text="Eliminar Pedido", command=self.eliminar_pedido).grid(row=0, column=1, padx=5)

    def _setup_daily_summary_frame(self):
        """Configura el frame para el resumen diario."""
        daily_summary_frame = ttk.LabelFrame(self.main_frame, text="Producción por Día", padding="10")
        daily_summary_frame.grid(row=0, column=2, rowspan=2, padx=10, pady=10, sticky="nsew")

        self.text_resumen_dia = scrolledtext.ScrolledText(daily_summary_frame, wrap=tk.WORD, state='disabled', height=15, width=40)
        self.text_resumen_dia.pack(expand=True, fill=tk.BOTH)

    def _configure_treeview_columns(self):
        """Configura las columnas del Treeview principal."""
        column_configs = {
            'dia': ('Día', 70, tk.CENTER),
            'cliente': ('Cliente', 110, tk.W),
            'sabor': ('Sabor', 90, tk.W),
            'cantidad': ('Cant. Total', 70, tk.E),
            'precio': ('P. Pedido', 70, tk.E),
            'envio': ('P. Envío', 60, tk.E),
            'direccion': ('Dirección', 150, tk.W),
            'horario': ('Horario', 80, tk.W),
            'pago': ('Pagó?', 50, tk.CENTER)
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
        self.actualizar_resumen_por_dia()

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

                pago_status = pedido.get('pago', 0)
                pago_display = "Sí" if pago_status == 1 else "No"

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
                        pedido.get('horario', ''),
                        pago_display
                    )
                )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudieron cargar los pedidos: {e}")

    def actualizar_resumen_produccion(self):
        """Actualiza el resumen de producción."""
        try:
            pedidos = self.db_manager.cargar_pedidos()
            produccion = defaultdict(int)
            cantidad_total_produccion = 0

            for pedido in pedidos:
                for item in pedido.get('items', []):
                    if item.get('sabor') and item.get('cantidad'):
                        cantidad = item['cantidad']
                        produccion[item['sabor']] += cantidad
                        cantidad_total_produccion += cantidad

            resumen_texto = "Resumen General de Producción:\n"
            if not produccion:
                resumen_texto += "(No hay pedidos registrados)"
            else:
                items_resumen = [f"- {cantidad} de {sabor}" for sabor, cantidad in sorted(produccion.items())]
                resumen_texto += "\n".join(items_resumen)
                resumen_texto += f"\n--------------------\nTotal Cookies a Producir: {cantidad_total_produccion}"

            self.label_resumen_produccion.config(text=resumen_texto)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el resumen: {e}")

    def actualizar_resumen_por_dia(self):
        """Actualiza el resumen de producción por día."""
        try:
            pedidos = self.db_manager.cargar_pedidos()
            produccion_por_dia = defaultdict(lambda: defaultdict(int))

            for pedido in pedidos:
                dia = pedido.get('dia', 'Sin Día')
                for item in pedido.get('items', []):
                    if item.get('sabor') and item.get('cantidad'):
                        produccion_por_dia[dia][item['sabor']] += item['cantidad']

            resumen_texto = "Resumen de Producción por Día:\n\n"
            if not produccion_por_dia:
                resumen_texto += "(No hay pedidos registrados)"
            else:
                for dia in sorted(produccion_por_dia.keys()):
                    resumen_texto += f"--- Día: {dia} ---\n"
                    items_dia = produccion_por_dia[dia]
                    total_dia = 0
                    for sabor, cantidad in sorted(items_dia.items()):
                        resumen_texto += f"  - {cantidad} de {sabor}\n"
                        total_dia += cantidad
                    resumen_texto += f"  Total del día: {total_dia}\n\n"

            self.text_resumen_dia.configure(state='normal')
            self.text_resumen_dia.delete('1.0', tk.END)
            self.text_resumen_dia.insert(tk.END, resumen_texto)
            self.text_resumen_dia.configure(state='disabled')
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el resumen por día: {e}")

    def actualizar_total_recaudado(self):
        """Actualiza el total recaudado."""
        try:
            pedidos = self.db_manager.cargar_pedidos()
            total = sum(
                pedido.get('precio_pedido', 0.0) + pedido.get('precio_envio', 0.0)
                for pedido in pedidos
            )
            self.label_total_recaudado.config(text=f"Total Recaudado (General): ${total:.2f}")
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
        """Quita un item del pedido actual."""
        seleccionados = self.tree_items_actual.selection()
        if not seleccionados:
            messagebox.showwarning("Selección Vacía", "Seleccione un item de la lista para quitar.")
            return
        indices_a_quitar = sorted([int(iid) for iid in seleccionados], reverse=True)
        for index in indices_a_quitar:
            if 0 <= index < len(self.items_pedido_actual):
                del self.items_pedido_actual[index]
        self.actualizar_tree_items_actual()

    def actualizar_tree_items_actual(self):
        """Actualiza el Treeview de items actuales."""
        for item in self.tree_items_actual.get_children():
            self.tree_items_actual.delete(item)
        for i, item in enumerate(self.items_pedido_actual):
            self.tree_items_actual.insert('', 'end', iid=i, values=(item['sabor'], item['cantidad']))

    def agregar_pedido(self):
        """Agrega un nuevo pedido a la base de datos."""
        dia = self.entry_dia.get().strip()
        nombre = self.entry_nombre.get().strip()
        precio_pedido_str = self.entry_precio_pedido.get().strip()
        precio_envio_str = self.entry_precio_envio.get().strip()
        direccion = self.entry_direccion.get().strip()
        horario = self.entry_horario.get().strip()

        if not dia:
            messagebox.showerror("Error", "El campo 'Día de Entrega' es obligatorio.")
            return
        if not nombre:
            messagebox.showerror("Error", "El campo 'Nombre del Cliente' es obligatorio.")
            return
        if not self.items_pedido_actual:
            messagebox.showerror("Error", "Debe agregar al menos un item.")
            return

        precio_pedido = validar_numero(precio_pedido_str, tipo='float', permitir_cero=False, permitir_vacio=False)
        if precio_pedido is None:
            messagebox.showerror("Error", "El 'Precio del Pedido' debe ser un número positivo.")
            return
        precio_envio = validar_numero(precio_envio_str, tipo='float', permitir_cero=True, permitir_vacio=True)
        if precio_envio is None:
            messagebox.showerror("Error", "El 'Precio del Envío' debe ser un número.")
            return
        if precio_envio > 0 and not direccion:
            if not messagebox.askyesno("Aviso", "Hay costo de envío pero no dirección. ¿Continuar?"):
                return

        try:
            self.db_manager.agregar_pedido(dia, nombre, precio_pedido, precio_envio, direccion, horario, self.items_pedido_actual)
            messagebox.showinfo("Éxito", "Pedido registrado correctamente.")
            self.limpiar_campos_entrada()
            self.actualizar_todo()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el pedido: {e}")

    def eliminar_pedido(self):
        """Elimina los pedidos seleccionados."""
        seleccionados = self.tree_pedidos.selection()
        if not seleccionados:
            messagebox.showwarning("Selección Vacía", "Seleccione el pedido a eliminar.")
            return

        if messagebox.askyesno("Confirmar Eliminación", "¿Eliminar los pedidos seleccionados?"):
            try:
                ids_a_eliminar = [int(iid) for iid in seleccionados]
                count = 0
                for pedido_id in ids_a_eliminar:
                    if self.db_manager.eliminar_pedido(pedido_id):
                        count += 1
                if count > 0:
                    messagebox.showinfo("Eliminado", f"{count} Pedido(s) eliminado(s).")
                    self.actualizar_todo()
                else:
                    messagebox.showwarning("Sin Cambios", "No se encontraron los pedidos.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar: {e}")

    def editar_pedido(self):
        """Abre la ventana de edición de pedido."""
        seleccionados = self.tree_pedidos.selection()
        if not seleccionados or len(seleccionados) > 1:
            messagebox.showwarning("Selección Inválida", "Seleccione un único pedido para editar.")
            return

        pedido_id = int(seleccionados[0])
        try:
            pedido = self.db_manager.obtener_pedido(pedido_id)
            if not pedido:
                messagebox.showerror("Error", f"No se encontró el pedido ID {pedido_id}.")
                return

            edit_window = EditWindow(self.root, self.db_manager, pedido, self.actualizar_todo)
            edit_window.grab_set()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar el pedido para editar: {e}")

    def toggle_pago_status(self, event):
        """Cambia el estado de pago del pedido seleccionado con doble clic."""
        selected_items = self.tree_pedidos.selection()
        if not selected_items or len(selected_items) > 1:
            return

        pedido_id = int(selected_items[0])
        try:
            self.db_manager.toggle_pago_pedido(pedido_id)
            self.actualizar_lista_pedidos()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo actualizar el estado de pago: {e}") 