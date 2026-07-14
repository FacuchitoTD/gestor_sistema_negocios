#!/bin/bash

# ============================================================
#  compilar.sh - Compilador Automático de Kiosco para Linux
# ============================================================

echo "============================================================"
echo "  PREPARANDO COMPILACIÓN DEL KIOSCO PARA LINUX"
echo "============================================================"
echo ""

# 1. Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "[1/4] Creando entorno virtual de Python (venv)..."
    python3 -m venv venv
else
    echo "[1/4] El entorno virtual ya existe. Saltando paso..."
fi
echo ""

# 2. Activar entorno virtual e instalar dependencias
echo "[2/4] Activando entorno virtual e instalando dependencias..."
source venv/bin/activate
python3 -m pip install --upgrade pip

# Usamos la bandera para evitar bloqueos del sistema en distros modernas
pip install -r requirements.txt --break-system-packages
echo ""

# 3. Compilar usando PyInstaller
echo "[3/4] Compilando aplicación con PyInstaller..."
# --noconsole: Oculta la terminal detrás de la app de CustomTkinter
# --onefile: Empaqueta todo en un único binario ejecutable
pyinstaller --noconsole --onefile Main.py
echo ""

# 4. Limpieza de archivos temporales
echo "[4/4] Limpiando archivos temporales de compilación..."
rm -rf build/
rm -f Main.spec
echo ""

echo "============================================================"
echo "  PROCESO FINALIZADO CON ÉXITO"
echo "  El ejecutable 'Main' se encuentra en la carpeta 'dist'"
echo "============================================================"