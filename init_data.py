"""
Script para inicializar datos de ejemplo en la base de datos
"""
from database import SessionLocal, engine
import models
from datetime import date, timedelta

# Crear tablas
models.Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Verificar si ya hay datos
    if db.query(models.Profesor).count() > 0:
        print("La base de datos ya tiene datos. Si deseas reinicializar, elimina colorin.db primero.")
        exit(0)
    
    # Crear profesores de ejemplo
    profesores_ejemplo = [
        "María González",
        "Juan Pérez",
        "Ana Martínez",
        "Carlos Rodríguez",
        "Laura Sánchez",
        "Pedro López",
        "Sofía Hernández",
        "Miguel Díaz",
        "Carmen Ruiz",
        "Roberto Torres",
        "Isabel Moreno",
        "Javier Jiménez",
        "Elena Castro",
        "Andrés Ortega",
        "Patricia Vega",
        "Diego Morales",
        "Marta Navarro",
        "Ricardo Peña",
        "Lucía Ramos",
        "Fernando Guzmán"
    ]
    
    print("Creando profesores...")
    profesores_creados = []
    for nombre in profesores_ejemplo:
        profesor = models.Profesor(nombre=nombre, activo=True)
        db.add(profesor)
        profesores_creados.append(profesor)
    
    db.commit()
    print(f"✅ Creados {len(profesores_creados)} profesores")
    
    # Crear algunos eventos de ejemplo
    hoy = date.today()
    eventos_ejemplo = [
        {
            "nombre": "Cumpleaños de Emma",
            "fecha": hoy + timedelta(days=5),
            "tipo": "cumpleaños",
            "ubicacion": "Parque Central",
            "notas": "Niña de 6 años, necesita actividades de arte"
        },
        {
            "nombre": "Cumpleaños de Lucas",
            "fecha": hoy + timedelta(days=7),
            "tipo": "cumpleaños",
            "ubicacion": "Casa privada",
            "notas": "Niño de 8 años, tema superhéroes"
        },
        {
            "nombre": "Evento Corporativo",
            "fecha": hoy + timedelta(days=10),
            "tipo": "evento_especial",
            "ubicacion": "Hotel Plaza",
            "notas": "Evento para 50 niños, necesitamos 5 profesores"
        },
        {
            "nombre": "Cumpleaños de Sofía",
            "fecha": hoy + timedelta(days=12),
            "tipo": "cumpleaños",
            "ubicacion": "Centro de eventos",
            "notas": "Niña de 5 años, tema princesas"
        }
    ]
    
    print("\nCreando eventos de ejemplo...")
    eventos_creados = []
    for evento_data in eventos_ejemplo:
        evento = models.Evento(**evento_data)
        db.add(evento)
        eventos_creados.append(evento)
    
    db.commit()
    print(f"✅ Creados {len(eventos_creados)} eventos")
    
    # Asignar algunos profesores de ejemplo (mostrando la funcionalidad)
    print("\nCreando asignaciones de ejemplo...")
    if len(eventos_creados) > 0 and len(profesores_creados) >= 2:
        # Asignar 2 profesores al primer evento
        asignacion1 = models.Asignacion(
            profesor_id=profesores_creados[0].id,
            evento_id=eventos_creados[0].id,
            rol="Profesor"
        )
        asignacion2 = models.Asignacion(
            profesor_id=profesores_creados[1].id,
            evento_id=eventos_creados[0].id,
            rol="Profesor"
        )
        db.add(asignacion1)
        db.add(asignacion2)
        
        # Asignar 1 profesor al segundo evento
        asignacion3 = models.Asignacion(
            profesor_id=profesores_creados[2].id,
            evento_id=eventos_creados[1].id,
            rol="Profesor"
        )
        db.add(asignacion3)
        
        db.commit()
        print("✅ Creadas 3 asignaciones de ejemplo")
    
    print("\n" + "="*50)
    print("✅ Datos iniciales creados exitosamente!")
    print("="*50)
    print(f"\nProfesores creados: {len(profesores_creados)}")
    print(f"Eventos creados: {len(eventos_creados)}")
    print("\nPuedes ahora iniciar el servidor con:")
    print("  uvicorn main:app --reload")
    print("\nO con Docker:")
    print("  docker-compose up")
    print("\nLuego visita: http://localhost:8000/docs")
    
except Exception as e:
    db.rollback()
    print(f"❌ Error: {e}")
finally:
    db.close()

