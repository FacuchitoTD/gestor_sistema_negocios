#  vista_cliente.py — Pantalla principal del kiosco
#  Interfaz gráfica con CustomTkinter
#  Estructura: categorías arriba + grilla productos + carrito lateral

import customtkinter as ctk
from tkinter import messagebox
from ClaseProducto import Producto, Carrito, Venta 
from repositorio import cargar_productos, guardar_productos
from controlador_teclado import registrar_atajos_cliente, registrar_atajos_cobro
from impresora import mandar_a_imprimir

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLOR_ACENTO      = "#e94560"   
COLOR_ACENTO2     = "#0f3460"   
COLOR_EXITO       = "#4caf50"   
COLOR_ADVERTENCIA = "#ff9800"   

NOMBRE_IMPRESORA = "G2000-series"  # Cambiar por el nombre exacto que devuelva el comando lpstat

class VentanaCliente(ctk.CTkToplevel):
    def __init__(self, ventana_inicio=None):
        super().__init__(master=ventana_inicio)
        self.ventana_inicio = ventana_inicio  
        
        self.title("🛒 Kiosco — Punto de Venta")
        self.geometry("1150x700")
        self.resizable(False, False)

        self.productos = []
        self.carrito = Carrito()
        self.categoria_activa = "Todas"
        self.protocol("WM_DELETE_WINDOW", self._volver_a_inicio)
        self._construir_interfaz()        
        self.after(100, self._inicializar_servicios_seguros)

    def _inicializar_servicios_seguros(self):
        self.productos = cargar_productos()
        self._construir_categorias()
        registrar_atajos_cliente(self)
        self._filtrar_categoria("Todas")

    def _construir_interfaz(self):
        encabezado = ctk.CTkFrame(self, corner_radius=0, fg_color=COLOR_ACENTO)
        encabezado.pack(fill="x")

        ctk.CTkButton(
            encabezado, text="←  Volver",
            font=ctk.CTkFont("Courier New", 12, "bold"),
            fg_color="transparent",
            hover_color="#c73652",
            border_width=1,
            corner_radius=8,
            width=90, height=32,
            command=self._volver_a_inicio
        ).pack(side="left", padx=14, pady=10)

        ctk.CTkLabel(
            encabezado, text="★  KIOSCO  ★",
            font=ctk.CTkFont("Courier New", 22, "bold"),
            text_color="white"
        ).pack(pady=10)

        contenedor = ctk.CTkFrame(self, fg_color="transparent")
        contenedor.pack(fill="both", expand=True, padx=12, pady=10)

        self.panel_izq = ctk.CTkFrame(contenedor, fg_color="transparent")
        self.panel_izq.pack(side="left", fill="both", expand=True)

        panel_der = ctk.CTkFrame(contenedor, width=320, corner_radius=12)
        panel_der.pack(side="right", fill="y", padx=(12, 0))
        panel_der.pack_propagate(False)

        self._construir_categorias()
        self._construir_grilla_productos()
        self._construir_carrito(panel_der)

    def _volver_a_inicio(self):
        """Destruye esta ventana y regresa a la pantalla principal."""
        self.destroy()
        if self.ventana_inicio is not None:
            self.ventana_inicio.deiconify()

    def _construir_categorias(self):
        """Fila de botones para filtrar por categoría."""
        if hasattr(self, 'frame_categorias'):
            for widget in self.frame_categorias.winfo_children():
                widget.destroy()
        else:
            self.frame_categorias = ctk.CTkFrame(self.panel_izq, fg_color="transparent")
            self.frame_categorias.pack(fill="x", pady=(0, 10))

        categorias = ["Todas"] + sorted(set(p.categoria for p in self.productos))
        self.botones_cat = {}

        for cat in categorias:
            btn = ctk.CTkButton(
                self.frame_categorias,  
                text=cat,
                font=ctk.CTkFont("Courier New", 12, "bold"),
                fg_color=COLOR_ACENTO if cat == "Todas" else COLOR_ACENTO2,
                hover_color="#c73652" if cat == "Todas" else "#1a4a8a",
                corner_radius=8,
                width=110, height=34,
                command=lambda c=cat: self._filtrar_categoria(c)
            )
            btn.pack(side="left", padx=4)
            self.botones_cat[cat] = btn

    def _construir_grilla_productos(self):
        """Área scrollable con tarjetas de productos."""
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.panel_izq,
            fg_color="transparent"
        )
        self.scroll_frame.pack(fill="both", expand=True)

        for col in range(3):
            self.scroll_frame.columnconfigure(col, weight=1)

        self._mostrar_productos(self.productos)

    def _construir_carrito(self, panel):
        """Panel derecho: carrito + total + botón pagar."""
        ctk.CTkLabel(
            panel, text="🛒  MI CARRITO",
            font=ctk.CTkFont("Courier New", 14, "bold"),
            text_color=COLOR_ACENTO
        ).pack(pady=(15, 6))

        self.textbox_carrito = ctk.CTkTextbox(
            panel,
            font=ctk.CTkFont("Courier New", 11),
            state="disabled",
            height=320,
            corner_radius=8
        )
        self.textbox_carrito.pack(fill="x", padx=12, pady=4)

        self.btn_quitar = ctk.CTkButton(
            panel, text="✕  Quitar último (Del)",
            font=ctk.CTkFont("Courier New", 11, "bold"),
            fg_color=COLOR_ACENTO2,
            hover_color="#1a4a8a",
            corner_radius=8, height=32,
            command=self._quitar_ultimo
        )
        self.btn_quitar.pack(fill="x", padx=12, pady=(4, 0))

        ctk.CTkFrame(panel, height=2, fg_color=COLOR_ACENTO).pack(fill="x", padx=12, pady=10)

        self.lbl_total = ctk.CTkLabel(
            panel, text="TOTAL:  $0.00",
            font=ctk.CTkFont("Courier New", 15, "bold"),
            text_color=COLOR_EXITO
        )
        self.lbl_total.pack()

        self.btn_pagar = ctk.CTkButton(
            panel, text="💳  PAGAR (F12)",
            font=ctk.CTkFont("Courier New", 14, "bold"),
            fg_color=COLOR_ACENTO,
            hover_color="#c73652",
            corner_radius=10, height=44,
            command=self._abrir_pago
        )
        self.btn_pagar.pack(fill="x", padx=12, pady=10)

        self.btn_vaciar = ctk.CTkButton(
            panel, text="🗑  Vaciar carrito (F4)",
            font=ctk.CTkFont("Courier New", 11),
            fg_color="transparent",
            hover_color="#2a2a3e",
            border_width=1,
            corner_radius=8, height=30,
            command=self._vaciar_carrito
        )
        self.btn_vaciar.pack(fill="x", padx=12)

    def _mostrar_productos(self, productos):
        """Limpia y vuelve a renderizar las tarjetas."""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        COLUMNAS = 3
        for i, producto in enumerate(productos):
            fila = i // COLUMNAS
            col  = i % COLUMNAS
            self._crear_tarjeta(producto, fila, col)

    def _crear_tarjeta(self, producto: Producto, fila: int, col: int):
        """Crea una tarjeta visual para un producto."""
        tarjeta = ctk.CTkFrame(
            self.scroll_frame,
            corner_radius=12,
            border_width=1,
            border_color=COLOR_ACENTO2
        )
        tarjeta.grid(row=fila, column=col, padx=6, pady=6, sticky="nsew")

        ctk.CTkLabel(
            tarjeta, text=producto.nombre,
            font=ctk.CTkFont("Courier New", 12, "bold"),
            wraplength=160
        ).pack(pady=(12, 2))

        ctk.CTkLabel(
            tarjeta, text=producto.categoria,
            font=ctk.CTkFont("Courier New", 10),
            text_color="gray"
        ).pack()

        ctk.CTkLabel(
            tarjeta, text=f"${producto.precio:.2f}",
            font=ctk.CTkFont("Courier New", 16, "bold"),
            text_color=COLOR_ACENTO
        ).pack(pady=6)

        if producto.stock > 5:
            color_stock = COLOR_EXITO
        elif producto.stock > 0:
            color_stock = COLOR_ADVERTENCIA
        else:
            color_stock = COLOR_ACENTO

        ctk.CTkLabel(
            tarjeta, text=f"Stock: {producto.stock}",
            font=ctk.CTkFont("Courier New", 10),
            text_color=color_stock
        ).pack()

        if producto.hay_stock():
            ctk.CTkButton(
                tarjeta, text="+ Agregar",
                font=ctk.CTkFont("Courier New", 11, "bold"),
                fg_color=COLOR_ACENTO,
                hover_color="#c73652",
                corner_radius=8, height=32,
                command=lambda p=producto: self._agregar_al_carrito(p)
            ).pack(fill="x", padx=12, pady=(8, 12))
        else:
            ctk.CTkLabel(
                tarjeta, text="SIN STOCK",
                font=ctk.CTkFont("Courier New", 11, "bold"),
                text_color=COLOR_ACENTO
            ).pack(pady=(8, 12))

    def _filtrar_categoria(self, categoria: str):
        self.categoria_activa = categoria

        for cat, btn in self.botones_cat.items():
            btn.configure(fg_color=COLOR_ACENTO if cat == categoria else COLOR_ACENTO2)

        filtrados = self.productos if categoria == "Todas" else [
            p for p in self.productos if p.categoria == categoria
        ]
        self._mostrar_productos(filtrados)

    def _agregar_al_carrito(self, producto: Producto):
        self.carrito.agregar(producto)
        self._actualizar_vista_carrito()

    def _quitar_ultimo(self):
        """Quita una unidad del último ítem agregado al carrito."""
        if self.carrito.esta_vacio():
            messagebox.showwarning("Carrito vacío", "No hay productos para quitar.")
            return

        ultimo_item = self.carrito.items[-1]

        if ultimo_item.cantidad > 1:
            ultimo_item.cantidad -= 1
        else:
            self.carrito.quitar(ultimo_item.producto.id)
            
        self._actualizar_vista_carrito()

    def _vaciar_carrito(self):
        if not self.carrito.esta_vacio():
            if messagebox.askyesno("Vaciar carrito", "¿Seguro que querés vaciar el carrito?"):
                self.carrito.vaciar()
                self._actualizar_vista_carrito()

    def _actualizar_vista_carrito(self):
        """Refresca el textbox y el total."""
        self.textbox_carrito.configure(state="normal")
        self.textbox_carrito.delete("1.0", "end")

        if self.carrito.esta_vacio():
            self.textbox_carrito.insert("end", "  El carrito está vacío.")
        else:
            for item in self.carrito.items:
                self.textbox_carrito.insert("end", f"  {item}\n")

        self.textbox_carrito.configure(state="disabled")
        self.lbl_total.configure(text=f"TOTAL:  ${self.carrito.total():.2f}")

    def _abrir_pago(self):
        if self.carrito.esta_vacio():
            messagebox.showwarning("Carrito vacío", "Agregá productos antes de pagar.")
            return

        productos_sin_stock = []
        for item in self.carrito.items:
            if item.cantidad > item.producto.stock:
                productos_sin_stock.append({
                    "nombre": item.producto.nombre,
                    "pedido": item.cantidad,
                    "disponible": item.producto.stock,
                    "exceso": item.cantidad - item.producto.stock
                })

        if productos_sin_stock:
            ticket_error = [
                "==============================",
                "   TICKET DE ERROR DE STOCK ",
                "==============================",
                "No se pudo procesar la venta",
                "porque algunos productos superan",
                "el stock real disponible.",
                "------------------------------"
            ]
            
            for p in productos_sin_stock:
                ticket_error.append(f"Producto: {p['nombre']}")
                ticket_error.append(f" En carrito:  {p['pedido']} un.")
                ticket_error.append(f" Disponible:  {p['disponible']} un.")
                ticket_error.append(f" Exceso:     -{p['exceso']} un.")
                ticket_error.append("------------------------------")
                
            ticket_error.extend([
                "Por favor, reducí la cantidad",
                "de estos artículos en el carrito",
                "para poder continuar.",
                "=============================="
            ])
            
            texto_ticket = "\n".join(ticket_error)
            messagebox.showerror("Error de Stock", texto_ticket, parent=self)
            return  

        ventana = ctk.CTkToplevel(self)
        ventana.title("Cobrar venta")
        ventana.geometry("400x600")
        ventana.resizable(False, False)
        ventana.grab_set()

        ctk.CTkLabel(
            ventana, text="💳  COBRAR VENTA",
            font=ctk.CTkFont("Courier New", 15, "bold"),
            text_color=COLOR_ACENTO
        ).pack(pady=15)

        frame_resumen = ctk.CTkFrame(ventana, corner_radius=10)
        frame_resumen.pack(fill="x", padx=20)

        for item in self.carrito.items:
            ctk.CTkLabel(
                frame_resumen, text=str(item),
                font=ctk.CTkFont("Courier New", 11),
                anchor="w"
            ).pack(fill="x", padx=12, pady=1)

        ctk.CTkFrame(frame_resumen, height=2, fg_color=COLOR_ACENTO).pack(fill="x", padx=12, pady=6)

        ctk.CTkLabel(
            frame_resumen,
            text=f"TOTAL:  ${self.carrito.total():.2f}",
            font=ctk.CTkFont("Courier New", 14, "bold"),
            text_color=COLOR_EXITO
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            ventana, text="Monto recibido ($):",
            font=ctk.CTkFont("Courier New", 12)
        ).pack(pady=(14, 4))

        entry_pago = ctk.CTkEntry(
            ventana,
            font=ctk.CTkFont("Courier New", 14),
            justify="center",
            width=200, height=40
        )
        entry_pago.pack()
        entry_pago.focus()

        def confirmar_pago():
            try:
                pago = float(entry_pago.get().replace(",", "."))
            except ValueError:
                messagebox.showerror("Error", "Ingresá un monto válido.", parent=ventana)
                return

            venta = Venta(self.carrito.items[:], self.carrito.total(), pago)

            if not venta.es_valida():
                falta = venta.total - venta.pago
                messagebox.showerror(
                    "Pago insuficiente",
                    f"Falta: ${falta:.2f}",
                    parent=ventana
                )
                return

            # Se descuenta el stock y se guarda
            for item in self.carrito.items:
                item.producto.reducir_stock(item.cantidad)
            guardar_productos(self.productos)

            # Mostramos primero el mensaje de venta registrada en pantalla
            messagebox.showinfo("Venta registrada", venta.ticket(), parent=ventana)

            texto_del_ticket = venta.ticket()
            impresion_correcta = mandar_a_imprimir(texto_del_ticket, nombre_impresora=NOMBRE_IMPRESORA)
            if not impresion_correcta:
                messagebox.showwarning(
                    "Advertencia de Impresión",
                    "La venta se registró correctamente, pero el ticket físico no se pudo imprimir.\n\n"
                    "Verificá que la impresora esté encendida, conectada y con papel.",
                    parent=ventana
                )

            self.carrito.vaciar()
            self._actualizar_vista_carrito()
            self._mostrar_productos(
                self.productos if self.categoria_activa == "Todas"
                else [p for p in self.productos if p.categoria == self.categoria_activa]
            )
            ventana.destroy()
        ctk.CTkButton(
            ventana, text="Confirmar pago",
            font=ctk.CTkFont("Courier New", 13, "bold"),
            fg_color=COLOR_EXITO,
            hover_color="#388e3c",
            corner_radius=10, height=42,
            command=confirmar_pago
        ).pack(fill="x", padx=30, pady=6)

        ctk.CTkButton(
            ventana, text="Cancelar",
            font=ctk.CTkFont("Courier New", 11),
            fg_color="transparent",
            border_width=1,
            corner_radius=8, height=32,
            command=ventana.destroy
        ).pack(fill="x", padx=30)

        registrar_atajos_cobro(ventana, confirmar_pago)

if __name__ == "__main__":
    # CTkToplevel necesita una raíz Tk ya existente. Si no se la damos,
    # Python crea una oculta y sin tematizar (bug real, confirmado).
    # Acá creamos una raíz explícita, la escondemos, y la usamos de master.
    _raiz_oculta = ctk.CTk()
    _raiz_oculta.withdraw()
    app = VentanaCliente(ventana_inicio=_raiz_oculta)
    app.protocol("WM_DELETE_WINDOW", _raiz_oculta.destroy)
    app.mainloop()