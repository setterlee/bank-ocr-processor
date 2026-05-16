#!/usr/bin/env fish
# Script helper para ejecutar el procesador con entorno virtual (Fish shell)

echo "🏦 Procesador de Movimientos Bancarios"
echo "=================================="

# Verificar si existe el entorno virtual
if not test -d venv
    echo "❌ Entorno virtual no encontrado. Ejecuta:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate.fish"
    echo "   pip install -r requirements.txt"
    exit 1
end

# Verificar si hay imágenes para procesar
set image_count (count to_process/*.png 2>/dev/null)
if test $image_count -eq 0
    echo "⚠️  No hay imágenes PNG en la carpeta 'to_process/'"
    echo "📁 Coloca las capturas de pantalla en 'to_process/' y vuelve a ejecutar"
    exit 0
end

echo "📸 Encontradas $image_count imágenes para procesar"

# Activar entorno virtual y ejecutar
echo "🔄 Activando entorno virtual..."
source venv/bin/activate.fish

echo "🚀 Ejecutando procesador..."
python3 procesar_csv.py

set exit_code $status

if test $exit_code -eq 0
    echo ""
    echo "✅ Procesamiento completado exitosamente!"
    echo "📁 Revisa la carpeta 'processed/' para los resultados"
else
    echo ""
    echo "❌ Error durante el procesamiento (código: $exit_code)"
    echo "🔍 Revisa los mensajes de error arriba"
end