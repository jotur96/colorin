# Cómo Crear tu Usuario Administrador

Tienes **3 formas** de crear tu primer usuario administrador:

## Opción 1: Usar el Endpoint Directamente (Más Fácil)

**Solo funciona la primera vez** (cuando no hay usuarios en la base de datos).

Ejecuta este comando en tu terminal:

```bash
curl -X POST "http://localhost:8000/usuarios/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "tu-email@ejemplo.com",
    "password": "tu-contraseña-segura"
  }'
```

**Ejemplo:**
```bash
curl -X POST "http://localhost:8000/usuarios/" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "email": "admin@colorin.com", "password": "admin123"}'
```

## Opción 2: Usar el Script dentro de Docker

```bash
docker-compose exec api python create_admin.py
```

## Opción 3: Usar la Documentación Interactiva

1. Ve a http://localhost:8000/docs
2. Busca el endpoint `POST /usuarios/`
3. Haz clic en "Try it out"
4. Completa los campos:
   - `username`: tu nombre de usuario (ej: "admin")
   - `email`: tu email (ej: "admin@colorin.com")
   - `password`: tu contraseña
5. Haz clic en "Execute"

## Nota Importante

- Solo puedes crear el primer usuario sin autenticación
- Si ya existe un usuario, necesitas usar `/login` para acceder
- El primer usuario creado será automáticamente administrador

## Después de Crear el Usuario

1. Inicia el frontend: `cd frontend && npm run dev`
2. Ve a http://localhost:5173
3. Ingresa tu `username` y `password`
4. ¡Listo!

