# 🎨 Colorin - Sistema de Gestión de Eventos

Sistema completo (Backend + Frontend) para gestionar eventos de niños y asignar profesores de manera equitativa.

## ✨ Características

### Backend (FastAPI + Python)
- ✅ Gestión de profesores (crear, editar, listar, eliminar)
- ✅ Gestión de eventos (crear, editar, listar, eliminar)
- ✅ Asignación de profesores a eventos
- ✅ **Asignación automática equitativa** - distribuye eventos de manera justa entre profesores
- ✅ Reportes y estadísticas por profesor
- ✅ Conteo automático de eventos por profesor
- ✅ Base de datos SQLite (gratuita, no requiere servidor externo)
- ✅ API REST completa con documentación interactiva

### Frontend (React + Vite)
- ✅ Dashboard con estadísticas generales
- ✅ Gestión completa de profesores con interfaz visual
- ✅ Gestión completa de eventos con asignación automática
- ✅ Reportes y estadísticas detalladas
- ✅ Diseño responsive para móvil y desktop
- ✅ Interfaz intuitiva y moderna

## 📋 Requisitos

- Python 3.11+
- Node.js 18+ (para el frontend)
- Docker (opcional, pero recomendado)

## 🚀 Instalación y Uso

### Backend

#### Opción 1: Con Docker (Recomendado)

```bash
# Construir y ejecutar
docker-compose up --build

# La API estará disponible en http://localhost:8000
```

#### Opción 2: Sin Docker

```bash
# Instalar dependencias
pip install -r requirements.txt

# Cargar datos de ejemplo (opcional)
python init_data.py

# Ejecutar servidor
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
# Ir al directorio del frontend
cd frontend

# Instalar dependencias
npm install

# Copiar archivo de configuración
cp .env.example .env

# Editar .env si es necesario (la URL del backend por defecto es http://localhost:8000)

# Ejecutar en desarrollo
npm run dev

# La aplicación estará disponible en http://localhost:5173
```

### Acceso

Una vez que ambos servicios estén corriendo:
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Documentación API**: http://localhost:8000/docs

## Documentación de la API

Una vez que el servidor esté corriendo, visita:

- **Documentación interactiva (Swagger)**: http://localhost:8000/docs
- **Documentación alternativa (ReDoc)**: http://localhost:8000/redoc

## Endpoints Principales

### Profesores
- `POST /profesores/` - Crear profesor
- `GET /profesores/` - Listar profesores
- `GET /profesores/{id}` - Obtener profesor
- `PUT /profesores/{id}` - Actualizar profesor
- `DELETE /profesores/{id}` - Eliminar profesor

### Eventos
- `POST /eventos/` - Crear evento
- `GET /eventos/` - Listar eventos (con filtros opcionales)
- `GET /eventos/{id}` - Obtener evento
- `PUT /eventos/{id}` - Actualizar evento
- `DELETE /eventos/{id}` - Eliminar evento

### Asignaciones
- `POST /asignaciones/` - Asignar profesor a evento manualmente
- `POST /eventos/{evento_id}/asignar-automatico?cantidad_profes=X` - Asignación automática equitativa
- `GET /asignaciones/` - Listar asignaciones
- `DELETE /asignaciones/{id}` - Eliminar asignación

### Reportes
- `GET /reportes/estadisticas-profesores` - Estadísticas de eventos por profesor
- `GET /reportes/eventos-por-profe/{profesor_id}` - Eventos de un profesor específico
- `GET /reportes/distribucion-equitativa` - Análisis de distribución actual

## Ejemplo de Uso

### 1. Crear profesores

```bash
curl -X POST "http://localhost:8000/profesores/" \
  -H "Content-Type: application/json" \
  -d '{"nombre": "María González", "activo": true}'
```

### 2. Crear un evento

```bash
curl -X POST "http://localhost:8000/eventos/" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Cumpleaños de Juan",
    "fecha": "2024-03-15",
    "tipo": "cumpleaños",
    "ubicacion": "Parque Central",
    "notas": "Necesita 3 profesores"
  }'
```

### 3. Asignar profesores automáticamente (de forma equitativa)

```bash
curl -X POST "http://localhost:8000/eventos/1/asignar-automatico?cantidad_profes=3"
```

Este endpoint seleccionará automáticamente los 3 profesores que tienen menos eventos asignados, garantizando distribución equitativa.

### 4. Ver estadísticas

```bash
curl "http://localhost:8000/reportes/estadisticas-profesores"
```

## Despliegue para Acceso desde Celular

Para acceder desde tu celular, puedes:

1. **Usar GitHub Pages/Netlify/Vercel** para el frontend (React)
2. **Desplegar el backend** en:
   - Render.com (gratis)
   - Railway.app (gratis)
   - Heroku (gratis)
   - PythonAnywhere (gratis)

O ejecutarlo localmente y acceder desde la misma red Wi-Fi usando la IP de tu computadora.

## Base de Datos

La base de datos SQLite se crea automáticamente en `colorin.db` al iniciar la aplicación por primera vez.

**Nota**: Para producción, considera usar PostgreSQL u otra base de datos más robusta. SQLite es perfecto para desarrollo y uso personal.

