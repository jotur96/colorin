"""
Script para crear el usuario administrador inicial
Ejecutar una vez después de crear las tablas
"""
from database import SessionLocal
import models
import auth

db = SessionLocal()

try:
    # Verificar si ya existe un usuario
    existing_user = db.query(models.Usuario).first()
    if existing_user:
        print("❌ Ya existe un usuario. No se puede crear otro.")
        print(f"   Usuario existente: {existing_user.username}")
        exit(1)
    
    print("=" * 50)
    print("Crear Usuario Administrador")
    print("=" * 50)
    
    username = input("Usuario (admin): ").strip() or "admin"
    email = input("Email: ").strip()
    if not email:
        print("❌ El email es requerido")
        exit(1)
    
    password = input("Contraseña: ").strip()
    if not password:
        print("❌ La contraseña es requerida")
        exit(1)
    
    # Verificar si el username ya existe
    if db.query(models.Usuario).filter(models.Usuario.username == username).first():
        print(f"❌ El usuario '{username}' ya existe")
        exit(1)
    
    # Verificar si el email ya existe
    if db.query(models.Usuario).filter(models.Usuario.email == email).first():
        print(f"❌ El email '{email}' ya está registrado")
        exit(1)
    
    # Crear usuario
    hashed_password = auth.get_password_hash(password)
    db_user = models.Usuario(
        username=username,
        email=email,
        hashed_password=hashed_password,
        activo=True,
        es_admin=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    print("\n" + "=" * 50)
    print("✅ Usuario administrador creado exitosamente!")
    print("=" * 50)
    print(f"\nUsuario: {db_user.username}")
    print(f"Email: {db_user.email}")
    print(f"\nAhora puedes iniciar sesión en el frontend con estas credenciales.")
    
except Exception as e:
    db.rollback()
    print(f"❌ Error: {e}")
finally:
    db.close()

