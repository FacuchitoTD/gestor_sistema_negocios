#  vista_admin.py — Panel de Administración del Kiosco
#  Permite: ver, agregar, modificar y eliminar productos
#  Usa CustomTkinter igual que vista_cliente.py

import customtkinter as ctk
from tkinter import messagebox
from ClaseProducto import Producto
from repositorio import cargar_productos, guardar_productos, proximo_id
from controlador_teclado import registrar_atajos_admin

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLOR_ACENTO      = "#e94560"
COLOR_ACENTO2     = "#0f3460"
COLOR_EXITO       = "#4caf50"
COLOR_ADVERTENCIA = "#ff9800"

class VentanaAdmin(ctk.CTkToplevel):
    def __init__(self, ventana_inicio=None):
        super().__init__(master=ventana_inicio)
        self.ventana_inicio = ventana_inicio

        self.title(" Kiosco — Panel de Administración")
        self.geometry("1200x720")
        self.resizable(False, False)

        self.productos = cargar_productos()
        self.producto_seleccionado = None   

        self.protocol("WM_DELETE_WINDOW", self._volver_a_inicio)

        self._construir_interfaz()
        self._actualizar_tabla()
        registrar_atajos_admin(self)

    def _construir_interfaz(self):
        encabezado = ctk.CTkFrame(self, corner_radius=0, fg_color=COLOR_ACENTO2)
        encabezado.pack(fill="x")

        ctk.CTkButton(
            encabezado, text="←  Volver",
            font=ctk.CTkFont("Courier New", 12, "bold"),
            fg_color="transparent",
            hover_color="#1a4a8a",
            border_width=1,
            corner_radius=8,
            width=90, height=32,
            command=self._volver_a_inicio
        ).pack(side="left", padx=14, pady=10)

        ctk.CTkLabel(
            encabezado, text=" PANEL DE ADMINISTRACIÓN",
            font=ctk.CTkFont("Courier New", 20, "bold"),
            text_color="white"
        ).pack(pady=10)

        contenedor = ctk.CTkFrame(self, fg_color="transparent")
        contenedor.pack(fill="both", expand=True, padx=12, pady=10)

        panel_izq = ctk.CTkFrame(contenedor, corner_radius=12)
        panel_izq.pack(side="left", fill="both", expand=True)

        panel_der = ctk.CTkFrame(contenedor, width=320, corner_radius=12)
        panel_der.pack(side="right", fill="y", padx=(12, 0))
        panel_der.pack_propagate(False)

        self._construir_tabla(panel_izq)
        self._construir_formulario(panel_der)

    def _construir_tabla(self, panel):
        ctk.CTkLabel(
            panel, text=" Productos en stock",
            font=ctk.CTkFont("Courier New", 14, "bold"),
            text_color=COLOR_ACENTO
        ).pack(pady=(12, 6))

        header = ctk.CTkFrame(panel, fg_color=COLOR_ACENTO2, corner_radius=6)
        header.pack(fill="x", padx=12, pady=(0, 4))

        for texto, ancho in [("ID", 40), ("Nombre", 200), ("Categoría", 120), ("Precio", 80), ("Stock", 60)]:
            ctk.CTkLabel(
                header, text=texto,
                font=ctk.CTkFont("Courier New", 11, "bold"),
                width=ancho, anchor="center"
            ).pack(side="left", padx=4, pady=6)

        self.scroll_tabla = ctk.CTkScrollableFrame(panel, fg_color="transparent")
        self.scroll_tabla.pack(fill="both", expand=True, padx=12, pady=4)

    def _actualizar_tabla(self):
        """Limpia y vuelve a dibujar todas las filas de la tabla."""
        for widget in self.scroll_tabla.winfo_children():
            widget.destroy()

        for producto in self.productos:
            self._crear_fila(producto)

    def _crear_fila(self, producto: Producto):
        """Crea una fila clickeable para un producto."""
        if producto.stock > 5:
            color_borde = COLOR_EXITO
        elif producto.stock > 0:
            color_borde = COLOR_ADVERTENCIA
        else:
            color_borde = COLOR_ACENTO

        fila = ctk.CTkFrame(
            self.scroll_tabla,
            corner_radius=6,
            border_width=1,
            border_color=color_borde,
            fg_color="transparent"
        )
        fila.pack(fill="x", pady=2)

        datos = [
            (str(producto.id),        40),
            (producto.nombre,         200),
            (producto.categoria,      120),
            (f"${producto.precio:.0f}", 80),
            (str(producto.stock),     60),
        ]

        for texto, ancho in datos:
            ctk.CTkLabel(
                fila, text=texto,
                font=ctk.CTkFont("Courier New", 11),
                width=ancho, anchor="center"
            ).pack(side="left", padx=4, pady=6)

        ctk.CTkButton(
            fila, text="Editar",
            font=ctk.CTkFont("Courier New", 10, "bold"),
            fg_color=COLOR_ACENTO2,
            hover_color="#1a4a8a",
            corner_radius=6,
            width=70, height=26,
            command=lambda p=producto: self._cargar_en_formulario(p)
        ).pack(side="right", padx=8)

    def _construir_formulario(self, panel):
        self.lbl_modo = ctk.CTkLabel(
            panel, text=" NUEVO PRODUCTO",
            font=ctk.CTkFont("Courier New", 13, "bold"),
            text_color=COLOR_ACENTO
        )
        self.lbl_modo.pack(pady=(15, 10))

        campos = [
            ("Nombre",    "entry_nombre"),
            ("Categoría", "entry_categoria"),
            ("Precio",    "entry_precio"),
            ("Stock",     "entry_stock"),
        ]

        for label, attr in campos:
            ctk.CTkLabel(
                panel, text=label + ":",
                font=ctk.CTkFont("Courier New", 11),
                anchor="w"
            ).pack(fill="x", padx=20, pady=(6, 0))

            entry = ctk.CTkEntry(
                panel,
                font=ctk.CTkFont("Courier New", 12),
                height=34, corner_radius=8
            )
            entry.pack(fill="x", padx=20)
            setattr(self, attr, entry)  

        self.lbl_estado = ctk.CTkLabel(
            panel, text="",
            font=ctk.CTkFont("Courier New", 11),
            wraplength=260
        )
        self.lbl_estado.pack(pady=8)

        ctk.CTkFrame(panel, height=2, fg_color=COLOR_ACENTO2).pack(fill="x", padx=20, pady=6)

        self.btn_guardar = ctk.CTkButton(
            panel, text=" Guardar nuevo (Ctrl+S)",
            font=ctk.CTkFont("Courier New", 12, "bold"),
            fg_color=COLOR_EXITO,
            hover_color="#388e3c",
            corner_radius=10, height=40,
            command=self._accion_guardar
        )
        self.btn_guardar.pack(fill="x", padx=20, pady=4)

        self.btn_eliminar = ctk.CTkButton(
            panel, text=" Eliminar producto (Ctrl+Supr)",
            font=ctk.CTkFont("Courier New", 12, "bold"),
            fg_color=COLOR_ACENTO,
            hover_color="#c73652",
            corner_radius=10, height=40,
            state="disabled",
            command=self._accion_eliminar
        )
        self.btn_eliminar.pack(fill="x", padx=20, pady=4)

        ctk.CTkButton(
            panel, text="✕  Limpiar formulario",
            font=ctk.CTkFont("Courier New", 11),
            fg_color="transparent",
            border_width=1,
            hover_color="#2a2a3e",
            corner_radius=8, height=32,
            command=self._limpiar_formulario
        ).pack(fill="x", padx=20, pady=4)

    def _cargar_en_formulario(self, producto: Producto):
        """Carga los datos de un producto en el formulario para editar."""
        self.producto_seleccionado = producto

        self.lbl_modo.configure(text=" EDITAR PRODUCTO")
        self.btn_guardar.configure(text=" Guardar cambios (Ctrl+S)")
        self.btn_eliminar.configure(state="normal")
        self.lbl_estado.configure(text=f"Editando ID {producto.id}", text_color=COLOR_ADVERTENCIA)

        self._limpiar_campos()
        self.entry_nombre.insert(0, producto.nombre)
        self.entry_categoria.insert(0, producto.categoria)
        self.entry_precio.insert(0, str(producto.precio))
        self.entry_stock.insert(0, str(producto.stock))

    def _accion_guardar(self):
        """Guarda un producto nuevo o aplica los cambios al existente."""
        nombre    = self.entry_nombre.get().strip()
        categoria = self.entry_categoria.get().strip()
        precio_str = self.entry_precio.get().strip()
        stock_str  = self.entry_stock.get().strip()

        if not nombre or not categoria or not precio_str or not stock_str:
            self.lbl_estado.configure(text="Completá todos los campos.", text_color=COLOR_ADVERTENCIA)
            return

        try:
            precio = float(precio_str.replace(",", "."))
            stock  = int(stock_str)
            if precio <= 0 or stock < 0:
                raise ValueError
        except ValueError:
            self.lbl_estado.configure(text="⚠ Precio y stock deben ser números válidos.", text_color=COLOR_ACENTO)
            return

        if self.producto_seleccionado:
            p = self.producto_seleccionado
            p.nombre    = nombre
            p.categoria = categoria
            p.precio    = precio
            p.stock     = stock
            guardar_productos(self.productos)
            self.lbl_estado.configure(text=f"'{nombre}' actualizado.", text_color=COLOR_EXITO)
        else:
            nuevo_id = proximo_id(self.productos)
            nuevo = Producto(nuevo_id, nombre, precio, categoria, stock)
            self.productos.append(nuevo)
            guardar_productos(self.productos)
            self.lbl_estado.configure(text=f"'{nombre}' agregado.", text_color=COLOR_EXITO)

        self._limpiar_formulario()
        self._actualizar_tabla()

    def _accion_eliminar(self):
        """Elimina el producto seleccionado con confirmación."""
        if not self.producto_seleccionado:
            return

        nombre = self.producto_seleccionado.nombre

        confirmacion = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Seguro que querés eliminar '{nombre}'?\nEsta acción no se puede deshacer."
        )
        if not confirmacion:
            return

        self.productos = [p for p in self.productos if p.id != self.producto_seleccionado.id]
        guardar_productos(self.productos)

        self.lbl_estado.configure(text=f"'{nombre}' eliminado.", text_color=COLOR_ACENTO)
        self._limpiar_formulario()
        self._actualizar_tabla()

    def _limpiar_formulario(self):
        """Resetea el formulario al modo 'nuevo producto'."""
        self.producto_seleccionado = None
        self.lbl_modo.configure(text=" NUEVO PRODUCTO")
        self.btn_guardar.configure(text=" Guardar nuevo")
        self.btn_eliminar.configure(state="disabled")
        self.lbl_estado.configure(text="")
        self._limpiar_campos()

    def _limpiar_campos(self):
        """Vacía los campos del formulario."""
        for entry in [self.entry_nombre, self.entry_categoria, self.entry_precio, self.entry_stock]:
            entry.delete(0, "end")

    def _volver_a_inicio(self):
        """
        Cierra esta ventana y vuelve a la pantalla de inicio, en vez de
        cerrar toda la aplicación. Si se abrió sin pantalla de inicio
        (corriendo este archivo directamente), simplemente cierra.
        """
        self.destroy()
        if self.ventana_inicio is not None:
            self.ventana_inicio.deiconify()


if __name__ == "__main__":
    # CTkToplevel necesita una raíz Tk ya existente (mismo motivo que en
    # VistaCliente.py). Creamos una raíz oculta explícita para testear solo.
    _raiz_oculta = ctk.CTk()
    _raiz_oculta.withdraw()
    app = VentanaAdmin(ventana_inicio=_raiz_oculta)
    app.protocol("WM_DELETE_WINDOW", _raiz_oculta.destroy)
    app.mainloop()