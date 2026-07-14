#  main.py — Punto de entrada del Kiosco
#  Muestra una pantalla de inicio para elegir modo:
#  Cliente (venta) o Administrador (ABM productos)

import customtkinter as ctk
from VistaCliente import VentanaCliente
from VistaAdmin import VentanaAdmin
from repositorio import inicializar

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLOR_ACENTO  = "#e94560"
COLOR_ACENTO2 = "#0f3460"
COLOR_EXITO   = "#4caf50"

class PantallaInicio(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Kiosco — Inicio")
        self.geometry("480x520")
        self.resizable(False, False)

        self._construir_interfaz()

    def _construir_interfaz(self):
        encabezado = ctk.CTkFrame(self, corner_radius=0, fg_color=COLOR_ACENTO)
        encabezado.pack(fill="x")
        ctk.CTkLabel(
            encabezado, text="★  KIOSCO  ★",
            font=ctk.CTkFont("Courier New", 26, "bold"),
            text_color="white"
        ).pack(pady=18)

        ctk.CTkLabel(
            self, text="Bienvenido\n¿Cómo querés ingresar?",
            font=ctk.CTkFont("Courier New", 15),
            text_color="gray",
            justify="center"
        ).pack(pady=(40, 20))

        ctk.CTkButton(
            self,
            text="  Modo Cliente",
            font=ctk.CTkFont("Courier New", 15, "bold"),
            fg_color=COLOR_ACENTO,
            hover_color="#c73652",
            corner_radius=12,
            width=300, height=60,
            command=self._abrir_cliente
        ).pack(pady=12)

        ctk.CTkLabel(
            self, text="Realizá compras y pagos",
            font=ctk.CTkFont("Courier New", 11),
            text_color="gray"
        ).pack()

        ctk.CTkFrame(self, height=2, fg_color=COLOR_ACENTO2, width=300).pack(pady=20)

        ctk.CTkButton(
            self,
            text="  Modo Administrador",
            font=ctk.CTkFont("Courier New", 15, "bold"),
            fg_color=COLOR_ACENTO2,
            hover_color="#1a4a8a",
            corner_radius=12,
            width=300, height=60,
            command=self._abrir_admin
        ).pack(pady=12)

        ctk.CTkLabel(
            self, text="Gestioná productos y stock",
            font=ctk.CTkFont("Courier New", 11),
            text_color="gray"
        ).pack()

        ctk.CTkLabel(
            self, text="v1.0 — Sistema de Kiosco",
            font=ctk.CTkFont("Courier New", 9),
            text_color="#444466"
        ).pack(side="bottom", pady=12)

    def _abrir_cliente(self):
        """Oculta el inicio y abre la pantalla de cliente pasándole esta ventana."""
        self.withdraw()
        VentanaCliente(ventana_inicio=self)
        # No hace falta app.mainloop() acá: al ser CTkToplevel, comparte
        # el mainloop que ya está corriendo en PantallaInicio.

    def _abrir_admin(self):
        """Oculta el inicio y abre el panel de administración pasándole esta ventana."""
        self.withdraw()
        VentanaAdmin(ventana_inicio=self)

if __name__ == "__main__":
    inicializar()   
    inicio = PantallaInicio()
    inicio.mainloop()