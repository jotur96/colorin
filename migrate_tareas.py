#!/usr/bin/env python3
"""Script de migración para agregar usuario_id a la tabla tareas"""

import sqlite3
import os
import sys

DATABASE_PATH = os.getenv('DATABASE_PATH', '/app/data/colorin.db')

def migrate():
    """Migrar la tabla tareas para agregar usuario_id"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Verificar si la columna ya existe
        cursor.execute("PRAGMA table_info(tareas)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'usuario_id' in columns:
            print("✓ La columna usuario_id ya existe")
            conn.close()
            return
        
        print("Migrando tabla tareas...")
        
        # Obtener el primer usuario admin
        cursor.execute("SELECT id FROM usuarios WHERE es_admin = 1 LIMIT 1")
        admin_result = cursor.fetchone()
        
        if not admin_result:
            print("ERROR: No se encontró usuario admin en la base de datos")
            conn.close()
            sys.exit(1)
        
        admin_id = admin_result[0]
        print(f"✓ Usuario admin encontrado: ID {admin_id}")
        
        # Crear nueva tabla con usuario_id
        cursor.execute("""
            CREATE TABLE tareas_new (
                id INTEGER NOT NULL PRIMARY KEY,
                usuario_id INTEGER NOT NULL,
                titulo VARCHAR(200) NOT NULL,
                descripcion TEXT,
                completada BOOLEAN NOT NULL,
                fecha_vencimiento DATE,
                prioridad VARCHAR(20),
                creada_en DATETIME NOT NULL,
                completada_en DATETIME,
                FOREIGN KEY(usuario_id) REFERENCES usuarios(id)
            )
        """)
        
        # Copiar datos existentes asignando todas las tareas al admin
        cursor.execute("""
            INSERT INTO tareas_new (id, usuario_id, titulo, descripcion, completada, 
                                   fecha_vencimiento, prioridad, creada_en, completada_en)
            SELECT id, ?, titulo, descripcion, completada, 
                   fecha_vencimiento, prioridad, creada_en, completada_en
            FROM tareas
        """, (admin_id,))
        
        # Eliminar tabla antigua y renombrar la nueva
        cursor.execute("DROP TABLE tareas")
        cursor.execute("ALTER TABLE tareas_new RENAME TO tareas")
        
        # Crear índice en usuario_id
        cursor.execute("CREATE INDEX IF NOT EXISTS ix_tareas_usuario_id ON tareas(usuario_id)")
        
        conn.commit()
        print("✓ Migración completada exitosamente")
        
        # Verificar cuántas tareas se migraron
        cursor.execute("SELECT COUNT(*) FROM tareas")
        count = cursor.fetchone()[0]
        print(f"✓ Total de tareas migradas: {count}")
        
        conn.close()
        
    except Exception as e:
        print(f"ERROR en la migración: {e}")
        conn.rollback()
        conn.close()
        sys.exit(1)

if __name__ == "__main__":
    migrate()

