@echo off
REM Script de configuración inicial para Bank OCR Processor (Windows)

echo 🏦 Configurando Bank OCR Processor...
echo.

REM Verificar que Python esté instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Python no está instalado
    echo Por favor instala Python e intenta de nuevo
    pause
    exit /b 1
)

REM Verificar que Tesseract esté instalado
tesseract --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Advertencia: Tesseract OCR no está instalado
    echo Para instalar Tesseract en Windows:
    echo   Descargar desde: https://github.com/UB-Mannheim/tesseract/wiki
    echo.
)

REM Crear carpetas necesarias
echo 📁 Creando estructura de carpetas...
if not exist "to_process" mkdir to_process
if not exist "processed" mkdir processed
if not exist "ocr" mkdir ocr

REM Crear entorno virtual si no existe
if not exist "venv" (
    echo 📦 Creando entorno virtual...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ Error creando entorno virtual
        pause
        exit /b 1
    )
)

REM Activar entorno virtual
echo 🔧 Activando entorno virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Error activando entorno virtual
    pause
    exit /b 1
)

REM Actualizar pip
echo 🔄 Actualizando pip...
python -m pip install --upgrade pip

REM Instalar dependencias
echo 📥 Instalando dependencias...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Error instalando dependencias
    pause
    exit /b 1
)

REM Crear archivo de configuración si no existe
if not exist "exchange_rates.properties" (
    echo 💱 Creando archivo de configuración...
    copy exchange_rates.properties.template exchange_rates.properties
    echo ✏️  Por favor edita 'exchange_rates.properties' con la tasa del día
)

echo.
echo ✅ Configuración completada!
echo.
echo 📋 Próximos pasos:
echo 1. Editar 'exchange_rates.properties' con la tasa USD/CLP del día
echo 2. Colocar imágenes PNG en la carpeta 'to_process\'
echo 3. Ejecutar: python procesar_csv.py
echo.
echo 🔗 Más información en README.md
echo.
echo 💡 Para activar el entorno virtual manualmente:
echo    venv\Scripts\activate.bat
echo.
pause