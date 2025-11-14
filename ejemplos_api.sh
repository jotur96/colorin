#!/bin/bash
# Ejemplos de uso de la API de Colorin
# Asegúrate de tener el servidor corriendo en http://localhost:8000

BASE_URL="http://localhost:8000"

echo "=== EJEMPLOS DE USO DE LA API COLORIN ==="
echo ""

# Colores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}1. Crear un profesor${NC}"
curl -X POST "${BASE_URL}/profesores/" \
  -H "Content-Type: application/json" \
  -d '{"nombre": "María González", "activo": true}' | python -m json.tool
echo ""

echo -e "${BLUE}2. Listar todos los profesores${NC}"
curl -X GET "${BASE_URL}/profesores/" | python -m json.tool
echo ""

echo -e "${BLUE}3. Crear un evento${NC}"
curl -X POST "${BASE_URL}/eventos/" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Cumpleaños de Juan",
    "fecha": "2024-03-15",
    "tipo": "cumpleaños",
    "ubicacion": "Parque Central",
    "notas": "Niño de 7 años, tema dinosaurios"
  }' | python -m json.tool
echo ""

echo -e "${BLUE}4. Listar todos los eventos${NC}"
curl -X GET "${BASE_URL}/eventos/" | python -m json.tool
echo ""

echo -e "${BLUE}5. Asignar profesores automáticamente a un evento (equitativo)${NC}"
echo "Nota: Reemplaza {evento_id} con el ID del evento creado"
curl -X POST "${BASE_URL}/eventos/1/asignar-automatico?cantidad_profes=3" | python -m json.tool
echo ""

echo -e "${BLUE}6. Ver estadísticas de profesores${NC}"
curl -X GET "${BASE_URL}/reportes/estadisticas-profesores" | python -m json.tool
echo ""

echo -e "${BLUE}7. Ver distribución equitativa actual${NC}"
curl -X GET "${BASE_URL}/reportes/distribucion-equitativa" | python -m json.tool
echo ""

echo -e "${BLUE}8. Ver eventos de un profesor específico${NC}"
echo "Nota: Reemplaza {profesor_id} con el ID del profesor"
curl -X GET "${BASE_URL}/reportes/eventos-por-profe/1" | python -m json.tool
echo ""

echo -e "${GREEN}✅ Ejemplos completos!${NC}"
echo "Visita http://localhost:8000/docs para la documentación interactiva"

