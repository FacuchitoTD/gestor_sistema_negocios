@echo off
title Compilador Automatico de Kiosco
echo ============================================================
echo   PREPARANDO COMPILACION DEL KIOSCO PARA WINDOWS
echo ============================================================
echo.

:: 1. Crear entorno virtual si no existe
if not exist venv (
    echo [1/4] Creando entorno virtual de Python (venv)...
    python -m venv venv
) else (
    echo [1/4] El entorno virtual ya existe. Saltando paso...
)
echo.

:: 2. Activar entorno virtual e instalar dependencias
echo [2/4] Activando entorno virtual e instalando dependencias...
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
echo.

:: 3. Compilar usando PyInstaller
echo [3/4] Compilando aplicacion con PyInstaller...
:: --noconsole: Oculta la terminal negra de fondo
:: --onefile: Empaqueta todo en un unico archivo .exe independiente
pyinstaller --noconsole --onefile Main.py
echo.

:: 4. Limpieza de archivos temporales
echo [4/4] Limpiando archivos temporales de compilacion...
rmdir /s /q build
del /q Main.spec
echo.

echo ============================================================
echo   PROCESO FINALIZADO CON EXITO
echo   El ejecutable 'Main.exe' se encuentra en la carpeta 'dist'
echo ============================================================
pause