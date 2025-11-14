#!/usr/bin/env python3
"""Script de migración para agregar actividad a la tabla eventos"""

import sqlite3
import os
import sys

DATABASE_PATH = os.getenv('DATABASE_PATH', '/app/data/colorin.db')

def migrate():
    """Migrar la tabla eventos para agregar campo de actividad"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(eventos)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'actividad' in columns:
            print("✓ La columna actividad ya existe")
            conn.close()
            return
        
        print("Migrando tabla eventos...")
        print("Agregando columna actividad...")
        cursor.execute("ALTER TABLE eventos ADD COLUMN actividad VARCHAR(100)")
        
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

