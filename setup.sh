#!/bin/bash
# Script de configuración inicial para Bank OCR Processor

echo "🏦 Configurando Bank OCR Processor..."
echo ""

# Verificar que Python3 esté instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python3 no está instalado"
    echo "Por favor instala Python3 e intenta de nuevo"
    exit 1
fi

# Verificar que Tesseract esté instalado
if ! command -v tesseract &> /dev/null; then
    echo "⚠️  Advertencia: Tesseract OCR no está instalado"
    echo "Para instalar Tesseract:"
    echo "  macOS: brew install tesseract"
    echo "  Ubuntu/Debian: sudo apt install tesseract-ocr"
    echo ""
fi

# Crear carpetas necesarias
echo "📁 Creando estructura de carpetas..."
mkdir -p to_process
mkdir -p processed
mkdir -p ocr

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Error creando entorno virtual"
        exit 1
    fi
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "❌ Error activando entorno virtual"
    exit 1
fi

# Actualizar pip
echo "🔄 Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias
echo "📥 Instalando dependencias..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Error instalando dependencias"
    exit 1
fi

# Crear archivo de configuración si no existe
if [ ! -f "exchange_rates.properties" ]; then
    echo "💱 Creando archivo de configuración..."
    cp exchange_rates.properties.template exchange_rates.properties
    echo "✏️  Por favor edita 'exchange_rates.properties' con la tasa del día"
fi

echo ""
echo "✅ Configuración completada!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Editar 'exchange_rates.properties' con la tasa USD/CLP del día"
echo "2. Colocar imágenes PNG en la carpeta 'to_process/'"
echo "3. Ejecutar: python3 procesar_csv.py"
echo ""
echo "🔗 Más información en README.md"
echo ""
echo "💡 Para activar el entorno virtual manualmente:"
echo "   source venv/bin/activate"