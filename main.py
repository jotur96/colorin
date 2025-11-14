from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
import database
import models
import schemas
import auth
import json

# Crear tablas en la base de datos
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="Colorin - Gestión de Eventos",
    description="Sistema de gestión de eventos y asignación de profesores",
    version="1.0.0"
)

# Configurar CORS para permitir acceso desde cualquier origen (incluye celular)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependencia para obtener la sesión de base de datos
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ========== ENDPOINTS DE AUTENTICACIÓN ==========

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login de usuario"""
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/usuarios/me", response_model=schemas.Usuario)
def read_users_me(current_user: models.Usuario = Depends(auth.get_current_active_admin)):
    """Obtener información del usuario actual"""
    return current_user


@app.put("/usuarios/me/cambiar-password")
def cambiar_password(
    cambio: schemas.CambiarPassword,
    current_user: models.Usuario = Depends(auth.get_current_active_admin),
    db: Session = Depends(get_db)
):
    """Cambiar la contraseña del usuario actual"""
    # Obtener el usuario desde la base de datos para asegurar que está en la sesión
    db_user = db.query(models.Usuario).filter(models.Usuario.id == current_user.id).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    
    # Verificar que la contraseña actual sea correcta
    if not auth.verify_password(cambio.password_actual, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual es incorrecta"
        )
    
    # Validar que la nueva contraseña no esté vacía
    if not cambio.password_nueva or len(cambio.password_nueva.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La nueva contraseña no puede estar vacía"
        )
    
    # Hashear y actualizar la contraseña
    db_user.hashed_password = auth.get_password_hash(cambio.password_nueva)
    db.commit()
    db.refresh(db_user)
    
    return {"message": "Contraseña actualizada correctamente"}


@app.post("/usuarios/", response_model=schemas.Usuario)
def create_user(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    """Crear nuevo usuario (solo para configuración inicial - solo si no hay usuarios)"""
    # Verificar si ya existe un usuario
    existing_user = db.query(models.Usuario).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Ya existe un usuario. Usa el endpoint /login para acceder."
        )
    
    # Verificar si el username ya existe
    db_user = db.query(models.Usuario).filter(models.Usuario.username == usuario.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    
    # Verificar si el email ya existe
    db_email = db.query(models.Usuario).filter(models.Usuario.email == usuario.email).first()
    if db_email:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    hashed_password = auth.get_password_hash(usuario.password)
    db_user = models.Usuario(
        username=usuario.username,
        email=usuario.email,
        hashed_password=hashed_password,
        activo=True,
        es_admin=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@app.get("/")
def root():
    return {
        "message": "API de Colorin - Gestión de Eventos",
        "version": "1.0.0"
    }


# ========== ENDPOINTS DE PROFESORES ==========

@app.post("/profesores/", response_model=schemas.Profesor)
def crear_profesor(
    profesor: schemas.ProfesorCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(auth.get_current_active_admin)
):
    """Crear un nuevo profesor"""
    db_profesor = models.Profesor(nombre=profesor.nombre, activo=profesor.activo)
    db.add(db_profesor)
    db.commit()
    db.refresh(db_profesor)
    return db_profesor


@app.get("/profesores/", response_model=List[schemas.Profesor])
def listar_profesores(
    activo: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(auth.get_current_active_admin)
):
    """Listar todos los profesores, opcionalmente filtrar por activos"""
    query = db.query(models.Profesor)
    if activo is not None:
        query = query.filter(models.Profesor.activo == activo)
    return query.all()


@app.get("/profesores/{profesor_id}", response_model=schemas.Profesor)
def obtener_profesor(
    profesor_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(auth.get_current_active_admin)
):
    """Obtener un profesor por ID"""
    profesor = db.query(models.Profesor).filter(models.Profesor.id == profesor_id).first()
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    return profesor


@app.put("/profesores/{profesor_id}", response_model=schemas.Profesor)
def actualizar_profesor(
    profesor_id: int,
    profesor: schemas.ProfesorUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(auth.get_current_active_admin)
):
    """Actualizar un profesor"""
    db_profesor = db.query(models.Profesor).filter(models.Profesor.id == profesor_id).first()
    if not db_profesor:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    
    if profesor.nombre is not None:
        db_profesor.nombre = profesor.nombre
    if profesor.activo is not None:
        db_profesor.activo = profesor.activo
    
    db.commit()
    db.refresh(db_profesor)
    return db_profesor


@app.delete("/profesores/{profesor_id}")
def eliminar_profesor(
    profesor_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(auth.get_current_active_admin)
):
    """Eliminar un profesor (solo si no tiene eventos asignados)"""
    db_profesor = db.query(models.Profesor).filter(models.Profesor.id == profesor_id).first()
    if not db_profesor:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    
    # Verificar si tiene eventos asignados
    asignaciones = db.query(models.Asignacion).filter(models.Asignacion.profesor_id == profesor_id).count()
    if asignaciones > 0:
        raise HTTPException(
            status_code=400, 
            detail=f"No se puede eliminar el profesor. Tiene {asignaciones} eventos asignados."
        )
    
    db.delete(db_profesor)
    db.commit()
    return {"message": "Profesor eliminado correctamente"}


# ========== ENDPOINTS DE EVENTOS ==========

@app.post("/eventos/", response_model=schemas.Evento)
def crear_evento(
    evento: schemas.EventoCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(auth.get_current_active_admin)
):
    """Crear un nuevo evento"""
    # Convertir lista de actividades a JSON string
    actividad_json = None
    if evento.actividad:
        actividad_json = json.dumps(evento.actividad)
    
    db_evento = models.Evento(
        nombre=evento.nombre,
        fecha=evento.fecha,
        tipo=evento.tipo,
        ubicacion=evento.ubicacion,
        horario_colorin=evento.horario_colorin,
        horario_cumpleanos=evento.horario_cumpleanos,
        actividad=actividad_json,
        notas=evento.notas
    )
    db.add(db_evento)
    db.commit()
    db.refresh(db_evento)
    # Convertir JSON string de vuelta a lista para la respuesta
    if db_evento.actividad:
        try:
            db_evento.actividad = json.loads(db_evento.actividad)
        except:
            db_evento.actividad = []
    else:
        db_evento.actividad = []
    return db_evento


@app.get("/eventos/", response_model=List[schemas.Evento])
def listar_eventos(
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    tipo: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(auth.get_current_active_admin)
):
    """Listar eventos con filtros opcionales"""
    query = db.query(models.Evento)
    
    if fecha_desde:
        query = query.filter(models.Evento.fecha >= fecha_desde)
    if fecha_hasta:
        query = query.filter(models.Evento.fecha <= fecha_hasta)
    if tipo:
        query = query.filter(models.Evento.tipo == tipo)
    
    eventos = query.order_by(models.Evento.fecha).all()
    # Convertir JSON string de actividades a lista para cada evento
    for evento in eventos:
        if evento.actividad:
            try:
                evento.actividad = json.loads(evento.actividad)
            except:
                evento.actividad = []
        else:
            evento.actividad = []
    return eventos


@app.get("/eventos/{evento_id}", response_model=schemas.Evento)
def obtener_evento(evento_id: int, db: Session = Depends(get_db), current_user: models.Usuario = Depends(auth.get_current_active_admin)):
    """Obtener un evento por ID con sus asignaciones"""
    evento = db.query(models.Evento).filter(models.Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    # Convertir JSON string de actividades a lista
    if evento.actividad:
        try:
            evento.actividad = json.loads(evento.actividad)
        except:
            evento.actividad = []
    else:
        evento.actividad = []
    return evento


@app.put("/eventos/{evento_id}", response_model=schemas.Evento)
def actualizar_evento(evento_id: int, evento: schemas.EventoUpdate, db: Session = Depends(get_db), current_user: models.Usuario = Depends(auth.get_current_active_admin)):
    """Actualizar un evento"""
    db_evento = db.query(models.Evento).filter(models.Evento.id == evento_id).first()
    if not db_evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    if evento.nombre is not None:
        db_evento.nombre = evento.nombre
    if evento.fecha is not None:
        db_evento.fecha = evento.fecha
    if evento.tipo is not None:
        db_evento.tipo = evento.tipo
    if evento.ubicacion is not None:
        db_evento.ubicacion = evento.ubicacion
    if evento.horario_colorin is not None:
        db_evento.horario_colorin = evento.horario_colorin
    if evento.horario_cumpleanos is not None:
        db_evento.horario_cumpleanos = evento.horario_cumpleanos
    if evento.actividad is not None:
        # Convertir lista de actividades a JSON string
        if evento.actividad:
            db_evento.actividad = json.dumps(evento.actividad)
        else:
            db_evento.actividad = None
    if evento.notas is not None:
        db_evento.notas = evento.notas
    
    db.commit()
    db.refresh(db_evento)
    # Convertir JSON string de vuelta a lista para la respuesta
    if db_evento.actividad:
        try:
            db_evento.actividad = json.loads(db_evento.actividad)
        except:
            db_evento.actividad = []
    else:
        db_evento.actividad = []
    return db_evento


@app.delete("/eventos/{evento_id}")
def eliminar_evento(evento_id: int, db: Session = Depends(get_db), current_user: models.Usuario = Depends(auth.get_current_active_admin)):
    """Eliminar un evento y sus asignaciones"""
    db_evento = db.query(models.Evento).filter(models.Evento.id == evento_id).first()
    if not db_evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    # Eliminar asignaciones asociadas
    db.query(models.Asignacion).filter(models.Asignacion.evento_id == evento_id).delete()
    
    db.delete(db_evento)
    db.commit()
    return {"message": "Evento eliminado correctamente"}


# ========== ENDPOINTS DE ASIGNACIONES ==========

@app.post("/asignaciones/", response_model=schemas.Asignacion)
def crear_asignacion(asignacion: schemas.AsignacionCreate, db: Session = Depends(get_db), current_user: models.Usuario = Depends(auth.get_current_active_admin)):
    """Asignar un profesor a un evento"""
    # Verificar que el profesor existe
    profesor = db.query(models.Profesor).filter(models.Profesor.id == asignacion.profesor_id).first()
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    
    # Verificar que el evento existe
    evento = db.query(models.Evento).filter(models.Evento.id == asignacion.evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    # Verificar que no esté ya asignado
    existe = db.query(models.Asignacion).filter(
        models.Asignacion.profesor_id == asignacion.profesor_id,
        models.Asignacion.evento_id == asignacion.evento_id
    ).first()
    
    if existe:
        raise HTTPException(status_code=400, detail="El profesor ya está asignado a este evento")
    
    db_asignacion = models.Asignacion(
        profesor_id=asignacion.profesor_id,
        evento_id=asignacion.evento_id,
        rol=asignacion.rol
    )
    db.add(db_asignacion)
    db.commit()
    db.refresh(db_asignacion)
    return db_asignacion


@app.get("/asignaciones/", response_model=List[schemas.Asignacion])
def listar_asignaciones(
    profesor_id: Optional[int] = None,
    evento_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(auth.get_current_active_admin)
):
    """Listar asignaciones con filtros opcionales"""
    query = db.query(models.Asignacion)
    
    if profesor_id:
        query = query.filter(models.Asignacion.profesor_id == profesor_id)
    if evento_id:
        query = query.filter(models.Asignacion.evento_id == evento_id)
    
    return query.all()


@app.delete("/asignaciones/{asignacion_id}")
def eliminar_asignacion(asignacion_id: int, db: Session = Depends(get_db), current_user: models.Usuario = Depends(auth.get_current_active_admin)):
    """Eliminar una asignación"""
    db_asignacion = db.query(models.Asignacion).filter(models.Asignacion.id == asignacion_id).first()
    if not db_asignacion:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    
    db.delete(db_asignacion)
    db.commit()
    return {"message": "Asignación eliminada correctamente"}


@app.post("/asignaciones/multiples")
def crear_asignaciones_multiples(asignaciones: List[schemas.AsignacionCreate], db: Session = Depends(get_db), current_user: models.Usuario = Depends(auth.get_current_active_admin)):
    """Asignar múltiples profesores a eventos"""
    asignaciones_creadas = []
    errores = []
    
    for asignacion_data in asignaciones:
        try:
            # Verificar que el profesor existe
            profesor = db.query(models.Profesor).filter(models.Profesor.id == asignacion_data.profesor_id).first()
            if not profesor:
                errores.append(f"Profesor {asignacion_data.profesor_id} no encontrado")
                continue
            
            # Verificar que el evento existe
            evento = db.query(models.Evento).filter(models.Evento.id == asignacion_data.evento_id).first()
            if not evento:
                errores.append(f"Evento {asignacion_data.evento_id} no encontrado")
                continue
            
            # Verificar que no esté ya asignado
            existe = db.query(models.Asignacion).filter(
                models.Asignacion.profesor_id == asignacion_data.profesor_id,
                models.Asignacion.evento_id == asignacion_data.evento_id
            ).first()
            
            if existe:
                errores.append(f"El profesor {profesor.nombre} ya está asignado a este evento")
                continue
            
            db_asignacion = models.Asignacion(
                profesor_id=asignacion_data.profesor_id,
                evento_id=asignacion_data.evento_id,
                rol=asignacion_data.rol
            )
            db.add(db_asignacion)
            asignaciones_creadas.append({
                "profesor_id": profesor.id,
                "profesor_nombre": profesor.nombre,
                "evento_id": evento.id
            })
        except Exception as e:
            errores.append(f"Error al asignar profesor {asignacion_data.profesor_id}: {str(e)}")
    
    db.commit()
    
    return {
        "asignaciones_creadas": asignaciones_creadas,
        "total_creadas": len(asignaciones_creadas),
        "errores": errores if errores else None
    }


# ========== RECOMENDACIONES Y ASIGNACIÓN MANUAL ==========

@app.get("/eventos/{evento_id}/profesores-recomendados")
def obtener_profesores_recomendados(evento_id: int, db: Session = Depends(get_db), current_user: models.Usuario = Depends(auth.get_current_active_admin)):
    """Obtener lista de profesores recomendados para un evento, ordenados por cantidad de eventos (menos eventos primero)"""
    from sqlalchemy import func
    
    # Verificar que el evento existe
    evento = db.query(models.Evento).filter(models.Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    # Obtener profesores ya asignados a este evento
    asignados = db.query(models.Asignacion.profesor_id).filter(
        models.Asignacion.evento_id == evento_id
    ).all()
    asignados_ids = [a.profesor_id for a in asignados]
    
    # Obtener todos los profesores activos
    todos_profesores = db.query(models.Profesor).filter(models.Profesor.activo == True).all()
    
    # Obtener conteo de eventos futuros por profesor
    conteos = db.query(
        models.Profesor.id,
        func.count(models.Asignacion.id).label('total')
    ).outerjoin(
        models.Asignacion, models.Profesor.id == models.Asignacion.profesor_id
    ).outerjoin(
        models.Evento, models.Asignacion.evento_id == models.Evento.id
    ).filter(
        models.Profesor.activo == True,
        (models.Evento.fecha >= date.today()) | (models.Evento.fecha.is_(None))
    ).group_by(models.Profesor.id).all()
    
    conteos_dict = {prof_id: count for prof_id, count in conteos}
    
    # Preparar la lista de recomendados
    recomendados = []
    for profesor in todos_profesores:
        total_eventos = conteos_dict.get(profesor.id, 0)
        ya_asignado = profesor.id in asignados_ids
        
        recomendados.append({
            "profesor_id": profesor.id,
            "nombre": profesor.nombre,
            "total_eventos_futuros": total_eventos,
            "ya_asignado": ya_asignado,
            "recomendado": not ya_asignado  # Recomendado si no está ya asignado
        })
    
    # Ordenar: primero los no asignados, luego por cantidad de eventos (menos eventos primero)
    recomendados.sort(key=lambda x: (x["ya_asignado"], x["total_eventos_futuros"], x["nombre"]))
    
    return {
        "evento_id": evento_id,
        "evento_nombre": evento.nombre,
        "evento_fecha": evento.fecha,
        "profesores": recomendados,
        "total_profesores": len(recomendados),
        "profesores_disponibles": len([p for p in recomendados if not p["ya_asignado"]])
    }


# ========== ASIGNACIÓN AUTOMÁTICA EQUITATIVA ==========

@app.post("/eventos/{evento_id}/asignar-automatico")
def asignar_automatico(evento_id: int, cantidad_profes: int, db: Session = Depends(get_db), current_user: models.Usuario = Depends(auth.get_current_active_admin)):
    """Asignar profesores a un evento de manera equitativa"""
    # Verificar que el evento existe
    evento = db.query(models.Evento).filter(models.Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    # Obtener profesores activos
    profesores_activos = db.query(models.Profesor).filter(models.Profesor.activo == True).all()
    if not profesores_activos:
        raise HTTPException(status_code=400, detail="No hay profesores activos")
    
    if cantidad_profes > len(profesores_activos):
        raise HTTPException(
            status_code=400,
            detail=f"Solo hay {len(profesores_activos)} profesores activos, pero se solicitan {cantidad_profes}"
        )
    
    # Obtener conteo de eventos por profesor (solo eventos futuros)
    from sqlalchemy import func, case
    conteos = db.query(
        models.Profesor.id,
        func.count(models.Asignacion.id).label('total')
    ).outerjoin(
        models.Asignacion, models.Profesor.id == models.Asignacion.profesor_id
    ).outerjoin(
        models.Evento, models.Asignacion.evento_id == models.Evento.id
    ).filter(
        models.Profesor.activo == True,
        (models.Evento.fecha >= date.today()) | (models.Evento.fecha.is_(None))
    ).group_by(models.Profesor.id).all()
    
    # Crear diccionario con conteos
    conteos_dict = {prof_id: count for prof_id, count in conteos}
    
    # Asegurar que todos los profesores activos tengan conteo (aunque sea 0)
    for prof in profesores_activos:
        if prof.id not in conteos_dict:
            conteos_dict[prof.id] = 0
    
    # Ordenar profesores por cantidad de eventos (menos eventos primero)
    profesores_ordenados = sorted(
        profesores_activos,
        key=lambda p: (conteos_dict.get(p.id, 0), p.id)
    )
    
    # Seleccionar los primeros N profesores
    profesores_seleccionados = profesores_ordenados[:cantidad_profes]
    
    # Crear asignaciones
    asignaciones_creadas = []
    for profesor in profesores_seleccionados:
        # Verificar que no esté ya asignado
        existe = db.query(models.Asignacion).filter(
            models.Asignacion.profesor_id == profesor.id,
            models.Asignacion.evento_id == evento_id
        ).first()
        
        if not existe:
            asignacion = models.Asignacion(
                profesor_id=profesor.id,
                evento_id=evento_id,
                rol="Profesor"
            )
            db.add(asignacion)
            asignaciones_creadas.append({
                "profesor_id": profesor.id,
                "profesor_nombre": profesor.nombre
            })
    
    db.commit()
    
    return {
        "message": f"Se asignaron {len(asignaciones_creadas)} profesores al evento",
        "asignaciones": asignaciones_creadas
    }


# ========== ENDPOINTS DE REPORTES ==========

@app.get("/reportes/estadisticas-profesores")
def estadisticas_profesores(
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(auth.get_current_active_admin)
):
    """Obtener estadísticas de eventos por profesor"""
    from sqlalchemy import func, and_
    
    query = db.query(
        models.Profesor.id,
        models.Profesor.nombre,
        models.Profesor.activo,
        func.count(models.Asignacion.id).label('total_eventos')
    ).outerjoin(
        models.Asignacion, models.Profesor.id == models.Asignacion.profesor_id
    ).outerjoin(
        models.Evento, models.Asignacion.evento_id == models.Evento.id
    )
    
    # Aplicar filtros de fecha si existen
    if fecha_desde or fecha_hasta:
        condiciones_fecha = []
        if fecha_desde:
            condiciones_fecha.append(models.Evento.fecha >= fecha_desde)
        if fecha_hasta:
            condiciones_fecha.append(models.Evento.fecha <= fecha_hasta)
        query = query.filter(and_(*condiciones_fecha))
    
    resultados = query.group_by(
        models.Profesor.id,
        models.Profesor.nombre,
        models.Profesor.activo
    ).order_by(models.Profesor.nombre).all()
    
    estadisticas = []
    for prof_id, nombre, activo, total in resultados:
        estadisticas.append({
            "profesor_id": prof_id,
            "nombre": nombre,
            "activo": activo,
            "total_eventos": total or 0
        })
    
    # Calcular estadísticas generales
    total_eventos = sum(stat['total_eventos'] for stat in estadisticas)
    promedio = total_eventos / len(estadisticas) if estadisticas else 0
    
    return {
        "estadisticas": estadisticas,
        "resumen": {
            "total_profesores": len(estadisticas),
            "total_eventos_asignados": total_eventos,
            "promedio_eventos_por_profesor": round(promedio, 2)
        }
    }


@app.get("/reportes/eventos-por-profe/{profesor_id}")
def eventos_por_profesor(
    profesor_id: int,
    fecha_desde: Optional[date] = None,
    fecha_hasta: Optional[date] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(auth.get_current_active_admin)
):
    """Obtener todos los eventos de un profesor específico"""
    from sqlalchemy import and_
    
    profesor = db.query(models.Profesor).filter(models.Profesor.id == profesor_id).first()
    if not profesor:
        raise HTTPException(status_code=404, detail="Profesor no encontrado")
    
    query = db.query(models.Evento).join(
        models.Asignacion, models.Evento.id == models.Asignacion.evento_id
    ).filter(
        models.Asignacion.profesor_id == profesor_id
    )
    
    if fecha_desde:
        query = query.filter(models.Evento.fecha >= fecha_desde)
    if fecha_hasta:
        query = query.filter(models.Evento.fecha <= fecha_hasta)
    
    eventos = query.order_by(models.Evento.fecha).all()
    
    eventos_data = []
    for evento in eventos:
        asignacion = db.query(models.Asignacion).filter(
            models.Asignacion.evento_id == evento.id,
            models.Asignacion.profesor_id == profesor_id
        ).first()
        
        eventos_data.append({
            "evento_id": evento.id,
            "nombre": evento.nombre,
            "fecha": evento.fecha,
            "tipo": evento.tipo,
            "ubicacion": evento.ubicacion,
            "rol": asignacion.rol if asignacion else None
        })
    
    return {
        "profesor": {
            "id": profesor.id,
            "nombre": profesor.nombre,
            "activo": profesor.activo
        },
        "total_eventos": len(eventos_data),
        "eventos": eventos_data
    }


@app.get("/reportes/distribucion-equitativa")
def distribucion_equitativa(db: Session = Depends(get_db), current_user: models.Usuario = Depends(auth.get_current_active_admin)):
    """Mostrar la distribución actual de eventos entre profesores activos"""
    from sqlalchemy import func
    
    # Obtener solo eventos futuros
    resultados = db.query(
        models.Profesor.id,
        models.Profesor.nombre,
        func.count(models.Asignacion.id).label('total_eventos')
    ).outerjoin(
        models.Asignacion, models.Profesor.id == models.Asignacion.profesor_id
    ).outerjoin(
        models.Evento, models.Asignacion.evento_id == models.Evento.id
    ).filter(
        models.Profesor.activo == True,
        (models.Evento.fecha >= date.today()) | (models.Evento.fecha.is_(None))
    ).group_by(
        models.Profesor.id,
        models.Profesor.nombre
    ).order_by(func.count(models.Asignacion.id).asc()).all()
    
    distribucion = []
    for prof_id, nombre, total in resultados:
        distribucion.append({
            "profesor_id": prof_id,
            "nombre": nombre,
            "total_eventos_futuros": total or 0
        })
    
    if distribucion:
        min_eventos = min(d['total_eventos_futuros'] for d in distribucion)
        max_eventos = max(d['total_eventos_futuros'] for d in distribucion)
        diferencia = max_eventos - min_eventos
        
        return {
            "distribucion": distribucion,
            "analisis": {
                "minimo_eventos": min_eventos,
                "maximo_eventos": max_eventos,
                "diferencia": diferencia,
                "es_equitativo": diferencia <= 1
            }
        }
    
    return {
        "distribucion": [],
        "analisis": {
            "mensaje": "No hay eventos futuros asignados"
        }
    }


# ========== ENDPOINTS DE TAREAS ==========

@app.post("/tareas/", response_model=schemas.Tarea)
def crear_tarea(
    tarea: schemas.TareaCreate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(auth.get_current_active_admin)
):
    """Crear una nueva tarea para el usuario actual"""
    db_tarea = models.Tarea(
        usuario_id=current_user.id,
        titulo=tarea.titulo,
        descripcion=tarea.descripcion,
        fecha_vencimiento=tarea.fecha_vencimiento,
        prioridad=tarea.prioridad,
        completada=False
    )
    db.add(db_tarea)
    db.commit()
    db.refresh(db_tarea)
    return db_tarea


@app.get("/tareas/", response_model=List[schemas.Tarea])
def listar_tareas(
    completada: Optional[bool] = None,
    prioridad: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(auth.get_current_active_admin)
):
    """Listar tareas del usuario actual con filtros opcionales"""
    query = db.query(models.Tarea).filter(models.Tarea.usuario_id == current_user.id)
    
    if completada is not None:
        query = query.filter(models.Tarea.completada == completada)
    if prioridad:
        query = query.filter(models.Tarea.prioridad == prioridad)
    
    # Ordenar por fecha de vencimiento (las más urgentes primero), luego por prioridad
    query = query.order_by(
        models.Tarea.fecha_vencimiento.asc().nullslast(),
        models.Tarea.prioridad.desc(),
        models.Tarea.creada_en.desc()
    )
    
    return query.all()


@app.get("/tareas/{tarea_id}", response_model=schemas.Tarea)
def obtener_tarea(
    tarea_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(auth.get_current_active_admin)
):
    """Obtener una tarea por ID del usuario actual"""
    tarea = db.query(models.Tarea).filter(
        models.Tarea.id == tarea_id,
        models.Tarea.usuario_id == current_user.id
    ).first()
    if not tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return tarea


@app.put("/tareas/{tarea_id}", response_model=schemas.Tarea)
def actualizar_tarea(
    tarea_id: int,
    tarea: schemas.TareaUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(auth.get_current_active_admin)
):
    """Actualizar una tarea del usuario actual"""
    db_tarea = db.query(models.Tarea).filter(
        models.Tarea.id == tarea_id,
        models.Tarea.usuario_id == current_user.id
    ).first()
    if not db_tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    # Actualizar solo los campos proporcionados
    update_data = tarea.model_dump(exclude_unset=True)
    if "completada" in update_data:
        if update_data["completada"] and not db_tarea.completada:
            # Si se marca como completada, guardar la fecha
            db_tarea.completada_en = datetime.utcnow()
        elif not update_data["completada"]:
            # Si se desmarca, limpiar la fecha
            db_tarea.completada_en = None
    
    for field, value in update_data.items():
        if field != "completada":  # Ya lo manejamos arriba
            setattr(db_tarea, field, value)
    
    db.commit()
    db.refresh(db_tarea)
    return db_tarea


@app.delete("/tareas/{tarea_id}")
def eliminar_tarea(
    tarea_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(auth.get_current_active_admin)
):
    """Eliminar una tarea del usuario actual"""
    db_tarea = db.query(models.Tarea).filter(
        models.Tarea.id == tarea_id,
        models.Tarea.usuario_id == current_user.id
    ).first()
    if not db_tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    db.delete(db_tarea)
    db.commit()
    return {"message": "Tarea eliminada correctamente"}


@app.patch("/tareas/{tarea_id}/toggle")
def toggle_tarea(
    tarea_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(auth.get_current_active_admin)
):
    """Alternar el estado de completada de una tarea del usuario actual"""
    db_tarea = db.query(models.Tarea).filter(
        models.Tarea.id == tarea_id,
        models.Tarea.usuario_id == current_user.id
    ).first()
    if not db_tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    db_tarea.completada = not db_tarea.completada
    if db_tarea.completada:
        db_tarea.completada_en = datetime.utcnow()
    else:
        db_tarea.completada_en = None
    
    db.commit()
    db.refresh(db_tarea)
    return db_tarea


# ========== ENDPOINTS DE TAREAS DE EVENTO ==========

@app.post("/eventos/{evento_id}/tareas", response_model=schemas.TareaEvento)
def crear_tarea_evento(
    evento_id: int,
    tarea: schemas.TareaEventoBase,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(auth.get_current_active_admin)
):
    """Crear una nueva tarea para un evento"""
    # Verificar que el evento existe
    evento = db.query(models.Evento).filter(models.Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    db_tarea = models.TareaEvento(
        evento_id=evento_id,
        descripcion=tarea.descripcion,
        completada=False
    )
    db.add(db_tarea)
    db.commit()
    db.refresh(db_tarea)
    return db_tarea


@app.get("/eventos/{evento_id}/tareas", response_model=List[schemas.TareaEvento])
def listar_tareas_evento(
    evento_id: int,
    completada: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(auth.get_current_active_admin)
):
    """Listar tareas de un evento con filtros opcionales"""
    # Verificar que el evento existe
    evento = db.query(models.Evento).filter(models.Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    query = db.query(models.TareaEvento).filter(models.TareaEvento.evento_id == evento_id)
    
    if completada is not None:
        query = query.filter(models.TareaEvento.completada == completada)
    
    # Ordenar por completada (pendientes primero), luego por fecha de creación
    query = query.order_by(
        models.TareaEvento.completada.asc(),
        models.TareaEvento.creada_en.desc()
    )
    
    return query.all()


@app.put("/eventos/{evento_id}/tareas/{tarea_id}", response_model=schemas.TareaEvento)
def actualizar_tarea_evento(
    evento_id: int,
    tarea_id: int,
    tarea: schemas.TareaEventoUpdate,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(auth.get_current_active_admin)
):
    """Actualizar una tarea de un evento"""
    # Verificar que el evento existe
    evento = db.query(models.Evento).filter(models.Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    db_tarea = db.query(models.TareaEvento).filter(
        models.TareaEvento.id == tarea_id,
        models.TareaEvento.evento_id == evento_id
    ).first()
    if not db_tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    # Actualizar solo los campos proporcionados
    update_data = tarea.model_dump(exclude_unset=True)
    if "completada" in update_data:
        if update_data["completada"] and not db_tarea.completada:
            # Si se marca como completada, guardar la fecha
            db_tarea.completada_en = datetime.utcnow()
        elif not update_data["completada"]:
            # Si se desmarca, limpiar la fecha
            db_tarea.completada_en = None
    
    for field, value in update_data.items():
        if field != "completada":  # Ya lo manejamos arriba
            setattr(db_tarea, field, value)
    
    db.commit()
    db.refresh(db_tarea)
    return db_tarea


@app.delete("/eventos/{evento_id}/tareas/{tarea_id}")
def eliminar_tarea_evento(
    evento_id: int,
    tarea_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(auth.get_current_active_admin)
):
    """Eliminar una tarea de un evento"""
    # Verificar que el evento existe
    evento = db.query(models.Evento).filter(models.Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    db_tarea = db.query(models.TareaEvento).filter(
        models.TareaEvento.id == tarea_id,
        models.TareaEvento.evento_id == evento_id
    ).first()
    if not db_tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    db.delete(db_tarea)
    db.commit()
    return {"message": "Tarea eliminada correctamente"}


@app.patch("/eventos/{evento_id}/tareas/{tarea_id}/toggle")
def toggle_tarea_evento(
    evento_id: int,
    tarea_id: int,
    db: Session = Depends(get_db),
    current_user: models.Usuario = Depends(auth.get_current_active_admin)
):
    """Alternar el estado de completada de una tarea de un evento"""
    # Verificar que el evento existe
    evento = db.query(models.Evento).filter(models.Evento.id == evento_id).first()
    if not evento:
        raise HTTPException(status_code=404, detail="Evento no encontrado")
    
    db_tarea = db.query(models.TareaEvento).filter(
        models.TareaEvento.id == tarea_id,
        models.TareaEvento.evento_id == evento_id
    ).first()
    if not db_tarea:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    
    db_tarea.completada = not db_tarea.completada
    if db_tarea.completada:
        db_tarea.completada_en = datetime.utcnow()
    else:
        db_tarea.completada_en = None
    
    db.commit()
    db.refresh(db_tarea)
    return db_tarea

