#!/usr/bin/env python3
"""
SCRIPT FINAL - Procesador de Movimientos Bancarios a Excel
Uso: python3 procesar_csv.py
"""

from csv_processor import ExcelBankProcessor

def main():
    """Función principal simplificada."""
    print("🏦 Convertir imágenes de movimientos bancarios a Excel")
    print("=" * 52)
    
    processor = ExcelBankProcessor()
    excel_file = processor.run()
    
    if excel_file:
        print(f"\n✅ ¡Listo! Excel creado: {excel_file.name}")
        print("📁 Busca el archivo en la carpeta 'processed/'")
    else:
        print("\n❌ No se pudo crear el Excel")

if __name__ == "__main__":
    main()