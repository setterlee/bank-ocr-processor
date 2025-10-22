# Funcionalidad de Categorización Automática

## Descripción

El sistema ahora incluye categorización automática de movimientos bancarios basada en patrones de texto encontrados en las descripciones.

## Características

- **Categorización automática**: Los movimientos se categorizan automáticamente según patrones predefinidos
- **Configurable**: Las reglas se pueden personalizar editando el archivo de configuración
- **Patrón más específico**: Si múltiples patrones coinciden, se usa el más largo (más específico)
- **Case-insensitive**: Los patrones funcionan independiente de mayúsculas/minúsculas
- **Categorías vacías**: Los movimientos sin coincidencias quedan sin categoría (como antes)

## Categorías Disponibles

Las únicas categorías válidas son:

- `Transporte`
- `Comida` 
- `Medicinas`
- `Servicios`
- `Otros`
- `Ingresos`
- `Autos`
- `N/A`
- `TAG`
- `sTechSolutions`
- `Extras`
- `Restaurantes`
- `Venezuela`
- `Creditos`
- `Arreglos`
- `Ahorros`
- `Pediatria SpA`

## Configuración

### Archivo de Reglas

Las reglas se definen en: `categorization_rules.properties`

**Formato**: `PATRON=CATEGORIA`

**Ejemplo**:
```properties
SB=Medicinas
UBER=Transporte
LIDER=Comida
ENEL=Servicios
```

### Ejemplos de Uso

| Descripción del Movimiento | Patrón que Coincide | Categoría Asignada |
|----------------------------|-------------------|-------------------|
| "SB 775 FARMACIA" | `SB` | Medicinas |
| "UBER VIAJE CENTRO" | `UBER` | Transporte |
| "COMPRA LIDER QUILICURA" | `LIDER` | Comida |
| "SHELL GASOLINA" | `GASOLINA` | Autos |
| "DEPOSITO SUELDO" | `DEPOSITO` | Ingresos |

### Personalización

1. **Editar reglas existentes**: Modificar `categorization_rules.properties`
2. **Agregar nuevos patrones**: 
   ```properties
   NUEVO_PATRON=Categoria
   ```
3. **Template disponible**: `categorization_rules.properties.template` contiene ejemplos

### Lógica de Coincidencia

- Se busca cada patrón como **substring** dentro de la descripción
- **No es case-sensitive**: "SB" coincide con "sb", "Sb", etc.
- **Patrón más específico gana**: Si "GAS" y "GASOLINA" coinciden, se usa "GASOLINA"
- **Primera coincidencia del mismo tamaño**: Si hay empate en longitud, se usa la primera

## Estadísticas

El sistema muestra:
- Total de movimientos procesados
- Cantidad de movimientos categorizados
- Porcentaje de efectividad
- Estadísticas por categoría

## Ejemplo de Salida

```
📊 Estadísticas de categorización:
----------------------------------------
  Autos: 1 movimiento(s)
  Comida: 1 movimiento(s)
  Medicinas: 2 movimiento(s)
  Transporte: 1 movimiento(s)
  (sin categoría): 1 movimiento(s)

✅ Categorizados: 4/5 (80.0%)
```

## Compatibilidad

- **Retrocompatible**: Los movimientos sin categoría quedan con campo vacío (como antes)
- **Sin cambios en formato**: El Excel mantiene la misma estructura
- **Configuración opcional**: Si no existe el archivo de reglas, el sistema funciona normal sin categorización

## Archivos Involucrados

- `categorization_rules.properties` - Reglas de categorización activas
- `categorization_rules.properties.template` - Template con ejemplos
- `csv_processor.py` - Lógica principal (modificado)
- `test_categorization.py` - Script de prueba de categorización
- `test_full_processing.py` - Prueba completa del procesamiento