# =============================================================
#  controlador_teclado.py — Centralizador de Atajos de Teclado
# =============================================================
def registrar_atajos_cliente(vista):
    """
    Recibe la instancia de VentanaCliente y le vincula todos
    los atajos de teclado a sus respectivos botones.

    Cada grupo de atajos tiene su propio try/except: si falta
    un botón puntual, se avisa por consola pero el resto de los
    atajos se registra igual (no todo o nada).
    """
    # 1. Atajos dinámicos para las categorías (F1, F2, F3...)
    #    F4 y F12 quedan RESERVADAS para el carrito (vaciar / pagar),
    #    así que las categorías nunca se las pisan.
    try:
        RESERVADAS = {4, 12}
        teclas_disponibles = [n for n in range(1, 10) if n not in RESERVADAS]

        for i, (cat, btn) in enumerate(vista.botones_cat.items()):
            if i >= len(teclas_disponibles):
                print(f"Categoría '{cat}' sin atajo: se acabaron las teclas F disponibles.")
                break
            tecla_f = f"<F{teclas_disponibles[i]}>"
            vista.bind(tecla_f, lambda event, b=btn: b.invoke())
        print("Atajos de categorías cargados.")
    except AttributeError as e:
        print(f"No se pudieron cargar los atajos de categorías: {e}")

    # 2. Atajos del panel lateral (Carrito)
    try:
        vista.bind("<Delete>", lambda event: vista.btn_quitar.invoke())
        vista.bind("<F12>", lambda event: vista.btn_pagar.invoke())
        vista.bind("<F4>", lambda event: vista.btn_vaciar.invoke())
        print("Atajos del carrito (Delete, F12, F4) cargados.")
    except AttributeError as e:
        print(f"Falta definir algún botón del carrito en la vista. Detalle: {e}")

    print(" Registro de atajos de VistaCliente finalizado.")


def registrar_atajos_cobro(ventana_cobro, funcion_confirmar):
    """
    Recibe la ventana flotante de cobro y le vincula sus atajos.
    """
    try:
        ventana_cobro.bind("<Return>", lambda event: funcion_confirmar())
        # Escape cancela y cierra la ventana
        ventana_cobro.bind("<Escape>", lambda event: ventana_cobro.destroy())
    except Exception as e:
        print(f"No se pudieron cargar los atajos de la ventana de cobro: {e}")


def registrar_atajos_admin(vista):
    """
    Recibe la instancia de VentanaAdmin y le vincula sus atajos de teclado
    para controlar el formulario y las acciones rápidamente.
    """
    try:
        vista.bind("<Control-s>", lambda event: vista.btn_guardar.invoke())
        vista.bind("<Control-S>", lambda event: vista.btn_guardar.invoke())

        vista.bind("<Control-Delete>", lambda event: vista.btn_eliminar.invoke() if vista.btn_eliminar.cget("state") == "normal" else None)

        vista.bind("<Escape>", lambda event: vista._limpiar_formulario())

        def forzar_foco_nombre():
            vista.entry_nombre.focus_set()
            return "break"

        vista.bind("<Control-n>", lambda event: forzar_foco_nombre())
        vista.bind("<Control-N>", lambda event: forzar_foco_nombre())
        print("Atajos de administración (Ctrl+S, Ctrl+Supr, Esc, Ctrl+N) cargados.")
    except AttributeError as e:
        print(f"Falta definir algún componente en el Admin antes de registrar atajos: {e}")