#!/usr/bin/env python3
"""Script de migración para agregar horarios a la tabla eventos"""

import sqlite3
import os
import sys

DATABASE_PATH = os.getenv('DATABASE_PATH', '/app/data/colorin.db')

def migrate():
    """Migrar la tabla eventos para agregar campos de horario"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Verificar si las columnas ya existen
        cursor.execute("PRAGMA table_info(eventos)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'horario_colorin' in columns and 'horario_cumpleanos' in columns:
            print("✓ Las columnas de horario ya existen")
            conn.close()
            return
        
        print("Migrando tabla eventos...")
        
        # Agregar columna horario_colorin si no existe
        if 'horario_colorin' not in columns:
            print("Agregando columna horario_colorin...")
            cursor.execute("ALTER TABLE eventos ADD COLUMN horario_colorin VARCHAR(20)")
        
        # Agregar columna horario_cumpleanos si no existe
        if 'horario_cumpleanos' not in columns:
            print("Agregando columna horario_cumpleanos...")
            cursor.execute("ALTER TABLE eventos ADD COLUMN horario_cumpleanos VARCHAR(20)")
        
        conn.commit()
        print("✓ Migración completada exitosamente")
        
        conn.close()
        
    except Exception as e:
        print(f"ERROR en la migración: {e}")
        conn.rollback()
        conn.close()
        sys.exit(1)

if __name__ == "__main__":
    migrate()

