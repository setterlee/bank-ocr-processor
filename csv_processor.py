#!/usr/bin/env python3
"""
Procesador optimizado para CSV con manejo correcto de fechas por imagen.
Cada imagen = un día, primera línea tiene fecha, siguientes solo movimientos.
"""

import re
import math
from pathlib import Path
from datetime import datetime
import pandas as pd
import pytesseract
from PIL import Image


class ExcelBankProcessor:
    """Procesador simple que genera Excel."""
    
    def __init__(self):
        self.workspace = Path(__file__).parent
        self.input_folder = self.workspace / "to_process"
        self.output_folder = self.workspace / "processed"
        self.debug_folder = self.workspace / "ocr"
        
        # Cargar tasa de cambio
        self.usd_to_clp = self.load_exchange_rate()
        
        # Cargar reglas de categorización
        self.categorization_rules = self.load_categorization_rules()
        
        # Crear carpetas si no existen
        self.output_folder.mkdir(exist_ok=True)
        self.debug_folder.mkdir(exist_ok=True)
    
    def load_exchange_rate(self):
        """Carga la tasa de cambio desde el archivo properties."""
        properties_file = self.workspace / "exchange_rates.properties"
        
        if not properties_file.exists():
            print("⚠️  Archivo exchange_rates.properties no encontrado, usando tasa por defecto: 950")
            return 950
        
        try:
            with open(properties_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('USD_TO_CLP='):
                        rate = float(line.split('=')[1])
                        print(f"💱 Tasa de cambio cargada: 1 USD = {rate} CLP")
                        return rate
            
            print("⚠️  Tasa USD_TO_CLP no encontrada, usando tasa por defecto: 950")
            return 950
            
        except Exception as e:
            print(f"⚠️  Error leyendo tasa de cambio: {e}, usando tasa por defecto: 950")
            return 950
    
    def load_categorization_rules(self):
        """Carga las reglas de categorización desde el archivo properties."""
        rules_file = self.workspace / "categorization_rules.properties"
        rules = {}
        
        if not rules_file.exists():
            print("⚠️  Archivo categorization_rules.properties no encontrado, categorización deshabilitada")
            return rules
        
        try:
            with open(rules_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    
                    # Ignorar líneas vacías y comentarios
                    if not line or line.startswith('#'):
                        continue
                    
                    # Buscar formato PATRON=CATEGORIA
                    if '=' in line:
                        pattern, category = line.split('=', 1)
                        pattern = pattern.strip().upper()  # Normalizar a mayúsculas
                        category = category.strip()
                        
                        # Validar que la categoría sea una de las permitidas
                        valid_categories = {
                            'Transporte', 'Comida', 'Medicinas', 'Servicios', 'Otros', 
                            'Ingresos', 'Autos', 'N/A', 'TAG', 'sTechSolutions', 
                            'Extras', 'Restaurantes', 'Venezuela', 'Creditos', 
                            'Arreglos', 'Ahorros', 'Pediatria SpA'
                        }
                        
                        if category in valid_categories:
                            rules[pattern] = category
                        else:
                            print(f"⚠️  Línea {line_num}: Categoría '{category}' no válida, ignorada")
                    else:
                        print(f"⚠️  Línea {line_num}: Formato incorrecto, esperado PATRON=CATEGORIA")
            
            print(f"📋 Cargadas {len(rules)} reglas de categorización")
            return rules
            
        except Exception as e:
            print(f"⚠️  Error leyendo reglas de categorización: {e}")
            return {}
    
    def categorize_movement(self, description):
        """Categoriza un movimiento basado en su descripción."""
        if not self.categorization_rules:
            return ''  # Sin categoría si no hay reglas
        
        # Normalizar descripción a mayúsculas para búsqueda case-insensitive
        description_upper = description.upper()
        
        # Buscar patrones que coincidan y tomar el más largo (más específico)
        matching_rules = []
        for pattern, category in self.categorization_rules.items():
            if pattern in description_upper:
                matching_rules.append((pattern, category, len(pattern)))
        
        if matching_rules:
            # Ordenar por longitud de patrón (descendente) y tomar el más largo
            matching_rules.sort(key=lambda x: x[2], reverse=True)
            return matching_rules[0][1]
        
        # Si no encuentra coincidencia, retornar vacío
        return ''
    
    def extract_text_from_image(self, image_path):
        """Extrae texto de una imagen."""
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, config='--oem 3 --psm 6 -l eng')
            
            # Guardar para debug
            debug_file = self.debug_folder / f"{image_path.stem}.txt"
            debug_file.write_text(text, encoding='utf-8')
            
            return text
        except Exception as e:
            print(f"Error procesando {image_path.name}: {e}")
            return ""
    
    def extract_day_from_first_line(self, lines):
        """Extrae el día y fecha completa de la primera línea que contiene fecha."""
        for line in lines:
            line = line.strip()
            if len(line) < 5:
                continue
            
            # Buscar fecha completa en la primera línea
            date_match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', line)
            if date_match:
                day = date_match.group(1).zfill(2)
                month = date_match.group(2).zfill(2)
                year = date_match.group(3)
                full_date = f"{year}-{month}-{day}"  # Formato para ordenar
                print(f"  Día extraído: {day} (fecha: {full_date})")
                return day, full_date
        
        return "01", "2025-01-01"  # Valor por defecto
    
    def extract_amount_and_description(self, line):
        """Extrae monto y descripción de una línea."""
        # Buscar montos en pesos chilenos ($) o dólares (USD)
        peso_match = re.search(r'([+-])\$?([\d\.,]+)', line)
        usd_match = re.search(r'([+-])?USD\s*([\d\.,]+)', line)
        
        amount = None
        currency = None
        sign = None
        
        if usd_match:
            # Encontró dólares
            sign = usd_match.group(1) or '-'  # Por defecto negativo si no hay signo
            amount_str = usd_match.group(2)
            currency = 'USD'
            
            # Procesar monto en dólares
            # Formato puede ser: 10,00 (10.00 USD) o 1000 o 10.50
            if ',' in amount_str and '.' not in amount_str:
                # Formato europeo: 10,00 (coma como decimal)
                amount_str = amount_str.replace(',', '.')
            else:
                # Formato estadounidense: quitar comas de miles si existen
                amount_str = amount_str.replace(',', '')
            
            try:
                usd_amount = float(amount_str)
                # Convertir a pesos chilenos y redondear hacia arriba
                clp_amount = math.ceil(usd_amount * self.usd_to_clp)
                amount = clp_amount
                print(f"    💵 Conversión: USD {usd_amount} → CLP {clp_amount}")
            except ValueError:
                return None, None, None
                
        elif peso_match:
            # Encontró pesos chilenos
            sign = peso_match.group(1)
            amount_str = peso_match.group(2)
            currency = 'CLP'
            
            # Manejar formato chileno: puntos para miles
            if '.' in amount_str and not ',' in amount_str:
                parts = amount_str.split('.')
                if len(parts) == 2 and len(parts[1]) == 3:
                    # Es formato de miles: 17.880 -> 17880
                    amount_str = amount_str.replace('.', '')
                    amount = int(amount_str)  # Entero, sin decimales
                else:
                    # Es decimal, redondear hacia arriba
                    amount = math.ceil(float(amount_str))
            else:
                amount_str = amount_str.replace(',', '')
                amount = int(float(amount_str))
        else:
            return None, None, None
        
        # Aplicar lógica bancaria:
        # - Negativos (-$ o -USD) = gastos → positivos en CSV
        # - Positivos (+$ o +USD) = ingresos → negativos en CSV
        if sign == '+':
            amount = -amount  # Invertir signo para ingresos
        # Si sign == '-', mantener positivo (ya es gasto)
        
        # Extraer descripción (todo excepto monto)
        description = line
        description = re.sub(r'[+-]?\$?[\d\.,]+', '', description)  # Quitar montos en pesos
        description = re.sub(r'[+-]?USD\s*[\d\.,]+', '', description)  # Quitar montos en dólares
        description = re.sub(r'\d{1,2}/\d{1,2}/\d{4}', '', description)  # Quitar fecha si hay
        description = re.sub(r'£\d*', '', description)  # Quitar códigos £ (con o sin números)
        description = re.sub(r'\b(roy|poy|fay)\b\s*', '', description)  # Quitar prefijos comunes
        description = re.sub(r'^\|\s*', '', description)  # Quitar pipes al inicio
        description = re.sub(r'^[^\w\s]+', '', description)  # Quitar símbolos al inicio
        description = re.sub(r'[^\w\s]+$', '', description)  # Quitar símbolos al final
        description = re.sub(r'\s+', ' ', description).strip()  # Limpiar espacios
        
        # Validar descripción
        if len(description) < 3:
            description = "Movimiento bancario"
        
        return amount, description, currency
    
    def parse_movements_from_text(self, text):
        """Parsea movimientos considerando que cada imagen = un día."""
        movements = []
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if not lines:
            return movements
        
        # Extraer día de la primera línea
        day, full_date = self.extract_day_from_first_line(lines)
        
        # Procesar todas las líneas que tengan monto
        for line in lines:
            if len(line) < 5:
                continue
            
            # Verificar que tenga monto (pesos $ o dólares USD)
            if not (re.search(r'[+-]?\$?[\d\.,]+', line) or re.search(r'[+-]?USD\s*[\d\.,]+', line)):
                continue
            
            amount, description, currency = self.extract_amount_and_description(line)
            
            if amount and description:
                # Categorizar el movimiento
                categoria = self.categorize_movement(description)
                
                movement = {
                    'descripcion': description,
                    'monto': amount,
                    'dia': day,
                    'fecha_completa': full_date,  # Para ordenamiento
                    'moneda_original': currency,  # Para separar USD y CLP
                    'forma_de_pago': 'Master (Santander Mariabe)',
                    'categoria': categoria
                }
                movements.append(movement)
                
                # Debug: mostrar categorización si se aplicó
                if categoria:
                    print(f"    📂 Categorizado como: {categoria}")
        
        return movements
    
    def process_all_images(self):
        """Procesa todas las imágenes."""
        all_movements = []
        
        png_files = list(self.input_folder.glob("*.png"))
        if not png_files:
            print("No se encontraron imágenes PNG")
            return all_movements
        
        print(f"Procesando {len(png_files)} imágenes...")
        
        for image_path in png_files:
            print(f"- {image_path.name}")
            
            # Extraer texto
            text = self.extract_text_from_image(image_path)
            if not text:
                continue
            
            # Extraer movimientos
            movements = self.parse_movements_from_text(text)
            all_movements.extend(movements)
            
            print(f"  → {len(movements)} movimientos encontrados")
        
        return all_movements
    
    def save_to_excel(self, movements):
        """Guarda los movimientos en Excel."""
        if not movements:
            print("No hay movimientos para guardar")
            return None
        
        # Crear DataFrame
        df = pd.DataFrame(movements)
        
        # Separar movimientos por moneda para mejor auditoría
        df_clp = df[df['moneda_original'] == 'CLP'].copy()
        df_usd = df[df['moneda_original'] == 'USD'].copy()
        
        # Ordenar cada grupo por fecha
        df_clp = df_clp.sort_values('fecha_completa') if not df_clp.empty else df_clp
        df_usd = df_usd.sort_values('fecha_completa') if not df_usd.empty else df_usd
        
        # Combinar: primero CLP, luego USD
        df = pd.concat([df_clp, df_usd], ignore_index=True)
        
        # Quitar columnas auxiliares
        df = df.drop(['fecha_completa', 'moneda_original'], axis=1)
        
        # Mostrar resumen por moneda
        if not df_clp.empty:
            print(f"  💰 Movimientos en pesos chilenos (CLP): {len(df_clp)}")
        if not df_usd.empty:
            print(f"  💵 Movimientos en dólares convertidos (USD→CLP): {len(df_usd)}")
        
        # Generar nombre de archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_file = self.output_folder / f"movimientos_{timestamp}.xlsx"
        
        # Guardar Excel (sin índice)
        df.to_excel(excel_file, index=False, engine='openpyxl')
        print(f"Excel guardado: {excel_file.name}")
        
        return excel_file
    
    def run(self):
        """Ejecuta el proceso completo."""
        print("=== Procesador Excel de Movimientos Bancarios ===")
        
        movements = self.process_all_images()
        
        if movements:
            print(f"\nTotal: {len(movements)} movimientos")
            excel_file = self.save_to_excel(movements)
            return excel_file
        else:
            print("No se encontraron movimientos")
            return None


def main():
    """Función principal."""
    processor = ExcelBankProcessor()
    processor.run()


if __name__ == "__main__":
    main()