from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime
import json


# ========== SCHEMAS DE PROFESOR ==========

class ProfesorBase(BaseModel):
    nombre: str
    activo: bool = True


class ProfesorCreate(ProfesorBase):
    pass


class ProfesorUpdate(BaseModel):
    nombre: Optional[str] = None
    activo: Optional[bool] = None


class Profesor(ProfesorBase):
    id: int
    
    class Config:
        from_attributes = True


# ========== SCHEMAS DE EVENTO ==========

class EventoBase(BaseModel):
    nombre: str
    fecha: date
    tipo: str
    ubicacion: Optional[str] = None
    horario_colorin: Optional[str] = None  # Horario de Colorín (ej: "10:00", "10:00 AM")
    horario_cumpleanos: Optional[str] = None  # Horario de Cumpleaños (ej: "14:00", "2:00 PM")
    actividad: Optional[List[str]] = None  # Actividades del evento como lista (ej: ["Slime", "Mini cheffs"])
    notas: Optional[str] = None


class EventoCreate(EventoBase):
    pass


class EventoUpdate(BaseModel):
    nombre: Optional[str] = None
    fecha: Optional[date] = None
    tipo: Optional[str] = None
    ubicacion: Optional[str] = None
    horario_colorin: Optional[str] = None
    horario_cumpleanos: Optional[str] = None
    actividad: Optional[List[str]] = None
    notas: Optional[str] = None


class Evento(EventoBase):
    id: int
    
    class Config:
        from_attributes = True


# ========== SCHEMAS DE ASIGNACION ==========

class AsignacionBase(BaseModel):
    profesor_id: int
    evento_id: int
    rol: str = "Profesor"


class AsignacionCreate(AsignacionBase):
    pass


class Asignacion(AsignacionBase):
    id: int
    
    class Config:
        from_attributes = True


# ========== SCHEMAS DE USUARIO ==========

class UsuarioBase(BaseModel):
    username: str
    email: EmailStr


class UsuarioCreate(UsuarioBase):
    password: str


class UsuarioLogin(BaseModel):
    username: str
    password: str


class Usuario(UsuarioBase):
    id: int
    activo: bool
    es_admin: bool
    creado_en: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class CambiarPassword(BaseModel):
    password_actual: str
    password_nueva: str


# ========== SCHEMAS DE TAREA ==========

class TareaBase(BaseModel):
    titulo: str
    descripcion: Optional[str] = None
    fecha_vencimiento: Optional[date] = None
    prioridad: str = "media"


class TareaCreate(TareaBase):
    pass


class TareaUpdate(BaseModel):
    titulo: Optional[str] = None
    descripcion: Optional[str] = None
    completada: Optional[bool] = None
    fecha_vencimiento: Optional[date] = None
    prioridad: Optional[str] = None


class Tarea(TareaBase):
    id: int
    completada: bool
    creada_en: datetime
    completada_en: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ========== SCHEMAS DE TAREAS DE EVENTO ==========

class TareaEventoBase(BaseModel):
    descripcion: str


class TareaEventoCreate(TareaEventoBase):
    evento_id: int


class TareaEventoUpdate(BaseModel):
    descripcion: Optional[str] = None
    completada: Optional[bool] = None


class TareaEvento(TareaEventoBase):
    id: int
    evento_id: int
    completada: bool
    creada_en: datetime
    completada_en: Optional[datetime] = None
    
    class Config:
        from_attributes = True

