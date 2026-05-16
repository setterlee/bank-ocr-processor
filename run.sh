#!/bin/bash
# Script helper para ejecutar el procesador con entorno virtual

echo "🏦 Procesador de Movimientos Bancarios"
echo "=================================="

# Verificar si existe el entorno virtual
if [ ! -d "venv" ]; then
    echo "❌ Entorno virtual no encontrado. Ejecuta:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Activar entorno virtual y ejecutar
echo "🔄 Activando entorno virtual..."
source venv/bin/activate

echo "🚀 Ejecutando procesador..."
python3 procesar_csv.py

echo ""
echo "✅ Procesamiento completado!"
echo "📁 Revisa la carpeta 'processed/' para los resultados"