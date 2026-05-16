# 🏦 Procesador de Movimientos Bancarios con OCR

Script automatizado para extraer movimientos bancarios de imágenes (capturas de pantalla) y exportarlos a Excel. Soporta múltiples monedas con conversión automática.

## ✨ Características

- 🖼️ **OCR automatizado** - Extrae texto de imágenes PNG
- 💱 **Multi-moneda** - Maneja pesos chilenos (CLP) y dólares (USD)
- 🔄 **Conversión automática** - USD → CLP con tasa configurable
- 📊 **Export a Excel** - Genera archivos `.xlsx` listos para usar
- 🧹 **Limpieza inteligente** - Remueve códigos y caracteres no deseados
- 📅 **Ordenamiento cronológico** - CLP primero, USD después para auditoría
- 🔢 **Formato chileno** - Montos enteros, sin decimales
- 🏷️ **Categorización automática** - Asigna categorías basadas en patrones configurables
- 📁 **Organización automática** - Mueve archivos procesados y deja carpetas listas para el siguiente procesamiento

## 📋 Requisitos

- Python 3.8 o superior
- Tesseract OCR instalado

## 🚀 Instalación

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/bank-ocr-processor.git
cd bank-ocr-processor
```

### 2. Instalar Tesseract OCR
```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt install tesseract-ocr

# Windows
# Descargar desde: https://github.com/UB-Mannheim/tesseract/wiki
```

### 3. Crear entorno virtual e instalar dependencias
```bash
python3 -m venv venv

# Activar entorno virtual
source venv/bin/activate           # bash/zsh
# o
source venv/bin/activate.fish      # fish shell
# En Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 4. Configurar tasa de cambio
```bash
cp exchange_rates.properties.template exchange_rates.properties
# Editar exchange_rates.properties con la tasa del día
```

### 5. Configurar categorización (opcional)
```bash
cp categorization_rules.properties.template categorization_rules.properties
# Editar categorization_rules.properties para personalizar las reglas
```

## 🎯 Uso

1. **Colocar imágenes** en la carpeta `to_process/`
2. **Ejecutar el procesador**:
   ```bash
   # Asegurate de tener el entorno virtual activado
   source venv/bin/activate.fish  # o source venv/bin/activate
   python3 procesar_csv.py
   ```
3. **Revisar resultados**:
   - ✅ **Excel** generado en `processed/`
   - 📸 **Imágenes procesadas** movidas a `processed/images/`
   - 📄 **Archivos OCR** movidas a `processed/ocr/`
   - 🎯 **Carpetas `to_process/` y `ocr/`** quedan vacías y listas para el siguiente procesamiento

## 📁 Estructura del Proyecto

```
bank-ocr-processor/
├── to_process/                    # Imágenes PNG a procesar (se vacía después de cada ejecución)
├── ocr/                          # Archivos OCR temporales (se vacía después de cada ejecución)  
├── processed/                    # Archivos procesados organizados
│   ├── movimientos_YYYYMMDD_HHMMSS.xlsx  # Archivos Excel generados
│   ├── images/                   # Imágenes procesadas
│   │   └── *.png                 # Capturas procesadas movidas aquí
│   └── ocr/                      # Archivos OCR procesados
│       └── *.txt                 # Textos extraídos movidos aquí
├── csv_processor.py              # Procesador principal
├── procesar_csv.py               # Script de uso simple
├── exchange_rates.properties     # Configuración de tasas (crear desde template)
├── exchange_rates.properties.template  # Plantilla de configuración
├── categorization_rules.properties    # Reglas de categorización (crear desde template)
├── categorization_rules.properties.template  # Plantilla de reglas
├── requirements.txt              # Dependencias Python
├── CATEGORIZACION.md             # Documentación de categorización
└── README.md                     # Este archivo
```

## 🖼️ Formato de Imágenes Soportado

- **Cada imagen = un día** de movimientos
- **Primera línea**: fecha completa (dd/mm/yyyy) + primer movimiento
- **Siguientes líneas**: solo movimientos del mismo día
- **Monedas soportadas**: 
  - Pesos chilenos: `$1.500` o `-$1.500`
  - Dólares: `USD 15.99` o `-USD 15.99`

## 📊 Formato del Excel Generado

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| `descripcion` | Detalle limpio del movimiento | `JUMBO ONECLICK` |
| `monto` | Valor en CLP (entero) | `15400` |
| `dia` | Día del mes | `23` |
| `forma_de_pago` | Forma de pago (fijo) | `Master (Santander Mariabe)` |
| `categoria` | Categoría automática | `Medicinas` |

### Convenciones de signos:
- **Positivo**: Gastos/Cargos
- **Negativo**: Ingresos/Abonos

## ⚙️ Configuración

### Tasa de Cambio
Editar `exchange_rates.properties`:
```properties
USD_TO_CLP=950
```

### Categorización Automática
Editar `categorization_rules.properties`:
```properties
SB=Medicinas
UBER=Transporte
LIDER=Comida
ENEL=Servicios
```

**Ver [CATEGORIZACION.md](CATEGORIZACION.md) para documentación completa de esta funcionalidad.**

### Montos
- Los montos se convierten a **enteros** (formato chileno)
- Conversión USD → CLP con **redondeo hacia arriba**
- Ejemplo: USD 10.50 × 950 = 9,975 CLP

## 🔄 Proceso de Conversión

1. **OCR**: Extrae texto de cada imagen y guarda archivos `.txt` en `ocr/`
2. **Parsing**: Identifica fechas, descripciones y montos
3. **Limpieza**: Remueve códigos y caracteres no deseados
4. **Conversión**: USD → CLP según tasa configurada
5. **Categorización**: Aplica reglas automáticas de categorización
6. **Ordenamiento**: CLP primero (cronológico), USD después (cronológico)
7. **Export**: Genera Excel con formato estándar en `processed/`
8. **Organización**: Mueve automáticamente:
   - ✅ Imágenes procesadas → `processed/images/`
   - ✅ Archivos OCR → `processed/ocr/`
   - ✅ Deja `to_process/` y `ocr/` vacías para el siguiente procesamiento

## �️ Desarrollo

### Estructura del código
- `ExcelBankProcessor`: Clase principal del procesador
- `extract_text_from_image()`: OCR con Tesseract
- `parse_movements_from_text()`: Extracción de movimientos
- `extract_amount_and_description()`: Parsing de montos y descripciones
- `save_to_excel()`: Generación de archivo Excel

### Contribuir
1. Fork el proyecto
2. Crear branch feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push al branch (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## � Licencia

MIT License - ver [LICENSE](LICENSE) para detalles.

## 🙏 Agradecimientos

- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - Motor de OCR
- [OpenPyXL](https://openpyxl.readthedocs.io/) - Manejo de archivos Excel
- [Pandas](https://pandas.pydata.org/) - Procesamiento de datos