#!/usr/bin/env python3
"""Script de migración para crear la tabla tareas_evento"""

import sqlite3
import os
import sys

DATABASE_PATH = os.getenv('DATABASE_PATH', '/app/data/colorin.db')

def migrate():
    """Crear la tabla tareas_evento"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Verificar si la tabla ya existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tareas_evento'")
        if cursor.fetchone():
            print("✓ La tabla tareas_evento ya existe")
            conn.close()
            return
        
        print("Creando tabla tareas_evento...")
        cursor.execute("""
            CREATE TABLE tareas_evento (
                id INTEGER NOT NULL PRIMARY KEY,
                evento_id INTEGER NOT NULL,
                descripcion VARCHAR(300) NOT NULL,
                completada BOOLEAN NOT NULL,
                creada_en DATETIME NOT NULL,
                completada_en DATETIME,
                FOREIGN KEY(evento_id) REFERENCES eventos(id)
            )
        """)
        
        # Crear índices
        cursor.execute("CREATE INDEX ix_tareas_evento_evento_id ON tareas_evento(evento_id)")
        cursor.execute("CREATE INDEX ix_tareas_evento_completada ON tareas_evento(completada)")
        
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

