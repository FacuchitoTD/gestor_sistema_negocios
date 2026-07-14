# =============================================================
#  impresora.py - Controlador de Impresion Multiplataforma
# =============================================================
import subprocess
import platform

# Intentamos importar las librerias de Windows solo si estamos en Windows
if platform.system() == "Windows":
    try:
        import win32print
        import win32ui
        import win32con
    except ImportError:
        pass

def _imprimir_en_linux(texto_ticket, nombre_impresora):
    """Envia el texto a imprimir usando CUPS (lpr) en Linux."""
    comando = ["lpr"]
    if nombre_impresora:
        comando.extend(["-P", nombre_impresora])
        
    proceso = subprocess.Popen(comando, stdin=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = proceso.communicate(input=texto_ticket)
    return proceso.returncode == 0

def _imprimir_en_windows(texto_ticket, nombre_impresora):
    """Envia el texto a imprimir usando la API nativa de Windows (GDI)."""
    try:
        # Si no se especifica impresora, obtenemos la predeterminada de Windows
        if not nombre_impresora:
            nombre_impresora = win32print.GetDefaultPrinter()
            
        # Abrimos la conexion con la impresora
        h_impresora = win32print.OpenPrinter(nombre_impresora)
        try:
            # Creamos un trabajo de impresion (Job)
            info_trabajo = ("Ticket de Venta", None, "RAW")
            win32print.StartDocPrinter(h_impresora, 1, info_trabajo)
            win32print.StartPagePrinter(h_impresora)
            
            # Enviamos el texto en formato de bytes (importante codificar a cp850 o utf-8)
            datos_bytes = texto_ticket.encode("utf-8")
            win32print.WritePrinter(h_impresora, datos_bytes)
            
            win32print.EndPagePrinter(h_impresora)
            win32print.EndDocPrinter(h_impresora)
        finally:
            win32print.ClosePrinter(h_impresora)
        return True
    except Exception as e:
        print(f"Error al imprimir en Windows: {e}")
        return False

def mandar_a_imprimir(texto_ticket, nombre_impresora=None):
    """
    Detecta el sistema operativo y envia el ticket a la impresora.
    Funciona de forma transparente tanto en Windows como en Linux.
    """
    sistema = platform.system()
    
    try:
        if sistema == "Linux":
            return _imprimir_en_linux(texto_ticket, nombre_impresora)
        elif sistema == "Windows":
            return _imprimir_en_windows(texto_ticket, nombre_impresora)
        else:
            print(f"Sistema operativo no soportado para impresion directa: {sistema}")
            return False
            
    except Exception as e:
        print(f"Error inesperado en el modulo de impresion: {e}")
        return False