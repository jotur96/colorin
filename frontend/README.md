# Colorin Frontend

Frontend React para la gestión de eventos de Colorin.

## Características

- ✅ Dashboard con estadísticas generales
- ✅ Gestión completa de profesores (CRUD)
- ✅ Gestión completa de eventos (CRUD)
- ✅ Asignación automática equitativa de profesores a eventos
- ✅ Reportes y estadísticas detalladas
- ✅ Diseño responsive para móvil y desktop
- ✅ Interfaz intuitiva y moderna

## Instalación

```bash
# Instalar dependencias
npm install

# Copiar archivo de configuración
cp .env.example .env

# Editar .env si es necesario (cambiar URL del backend)
# VITE_API_URL=http://localhost:8000
```

## Uso

### Desarrollo

```bash
npm run dev
```

La aplicación estará disponible en `http://localhost:5173`

### Producción

```bash
# Construir para producción
npm run build

# Previsualizar build de producción
npm run preview
```

## Configuración

Edita el archivo `.env` para configurar la URL del backend:

```env
VITE_API_URL=http://localhost:8000
```

Si despliegas el backend en la nube, actualiza esta URL con la URL de tu servidor.

## Despliegue

### GitHub Pages

```bash
# Instalar gh-pages
npm install --save-dev gh-pages

# Agregar al package.json:
# "scripts": {
#   ...
#   "predeploy": "npm run build",
#   "deploy": "gh-pages -d dist"
# }

# Desplegar
npm run deploy
```

### Netlify / Vercel

1. Conecta tu repositorio de GitHub
2. Configura el comando de build: `npm run build`
3. Configura el directorio de salida: `dist`
4. Agrega la variable de entorno `VITE_API_URL` con la URL de tu backend

## Estructura del Proyecto

```
src/
├── api/              # Cliente API y configuración
├── components/       # Componentes reutilizables
├── pages/            # Páginas principales
└── App.jsx           # Componente principal con routing
```
