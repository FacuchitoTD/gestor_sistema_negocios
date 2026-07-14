# Gestor Sistema Negocios

¡Bienvenido al **Gestor de Sistema para Negocios**! Este proyecto es un sistema de gestión de ventas y stock de escritorio desarrollado en **Python**, diseñado especialmente para optimizar el flujo de trabajo de un comercio minorista o kiosco. 

El sistema cuenta con una arquitectura dividida en dos vistas principales: una interfaz ágil para el cliente/vendedor orientada a la rapidez en la atención, y un panel de administración para controlar el stock, las categorías y la base de datos de manera segura.

---

## Características Principales

*   **Interfaz de Cliente Ultra-Rápida:** Vista diseñada para cargar y registrar ventas en segundos con soporte asíncrono para evitar congelamientos en pantallas pesadas.
*   **Panel de Administración Integral:** Gestión centralizada de productos, precios y stock.
*   **Gestión por Categorías:** Clasificación visual y filtrado de productos en tiempo real.
*   **Control de Teclado Avanzado:** Atajos y mapeo global para operar el sistema sin depender exclusivamente del mouse.
*   **Soporte de Impresión:** Módulo integrado para la emisión de comprobantes o tickets de venta.
*   **Persistencia de Datos Híbrida:** Manejo de datos locales utilizando archivos JSON y bases de datos relacionales SQL para máxima integridad y portabilidad.
*   **Compatibilidad Multiplataforma:** Preparado para funcionar de manera nativa en sistemas **Linux (como Linux Mint XFCE)** y entornos **Windows**.

---

## Estructura del Proyecto

El repositorio está organizado de la siguiente manera:

*   `Main.py`: Punto de entrada principal que inicializa y coordina el arranque de la aplicación.
*   `VistaCliente.py`: Interfaz de usuario diseñada para la atención al público y facturación rápida.
*   `VistaAdmin.py`: Panel de control del administrador para el inventario y configuraciones del sistema.
*   `ClaseProducto.py`: Definición del modelo de datos y reglas de negocio para los productos.
*   `repositorio.py`: Capa de datos encargada de la persistencia de información y comunicación con la base de datos/archivos locales.
*   `controlador_teclado.py`: Módulo que gestiona los atajos globales de teclado para agilizar las operaciones de venta.
*   `impresora.py`: Controlador para el envío de información y formato de impresión a tiqueteras físicas.
*   `datos.json`: Archivo de configuración rápida y almacenamiento auxiliar de datos.
*   `requirements.txt`: Archivo con la lista de librerías y dependencias necesarias para ejecutar el proyecto.
*   `compilar.sh` / `compilar.bat`: Scripts de automatización para empaquetar el proyecto de manera offline en Linux y Windows respectivamente.
*   `dependencias_offline/`: Carpeta con paquetes `.whl` que facilitan la instalación del software en entornos que no cuentan con acceso a internet.

---

## Instalación y Configuración

### Requisitos Previos
*   **Python 3.8 o superior** instalado en el sistema.
*   Un gestor de paquetes de Python (`pip`).

### 1. Clonar el repositorio
Si querés descargar el proyecto localmente, podés clonar el repositorio usando:
```bash
git clone [https://github.com/FacuchitoTD/gestor_sistema_negocios.git](https://github.com/FacuchitoTD/gestor_sistema_negocios.git)
cd gestor_sistema_negocios
