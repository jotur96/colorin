from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Profesor(Base):
    __tablename__ = "profesores"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False, index=True)
    activo = Column(Boolean, default=True, nullable=False)
    
    # Relación con asignaciones
    asignaciones = relationship("Asignacion", back_populates="profesor", cascade="all, delete-orphan")


class Evento(Base):
    __tablename__ = "eventos"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    fecha = Column(Date, nullable=False, index=True)
    tipo = Column(String(50), nullable=False)  # "cumpleaños", "evento_especial", etc.
    ubicacion = Column(String(200))
    horario_colorin = Column(String(20))  # Horario de Colorín (ej: "10:00", "10:00 AM")
    horario_cumpleanos = Column(String(20))  # Horario de Cumpleaños (ej: "14:00", "2:00 PM")
    actividad = Column(Text)  # Actividades del evento como JSON array (ej: ["Slime", "Mini cheffs"])
    notas = Column(Text)
    
    # Relación con asignaciones
    asignaciones = relationship("Asignacion", back_populates="evento", cascade="all, delete-orphan")


class Asignacion(Base):
    __tablename__ = "asignaciones"
    
    id = Column(Integer, primary_key=True, index=True)
    profesor_id = Column(Integer, ForeignKey("profesores.id"), nullable=False)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False)
    rol = Column(String(50), default="Profesor")  # "Profesor", "Asistente", etc.
    
    # Relaciones
    profesor = relationship("Profesor", back_populates="asignaciones")
    evento = relationship("Evento", back_populates="asignaciones")
    
    # Asegurar que no haya asignaciones duplicadas
    __table_args__ = (
        {'sqlite_autoincrement': True},
    )


class Usuario(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(200), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    activo = Column(Boolean, default=True, nullable=False)
    es_admin = Column(Boolean, default=True, nullable=False)
    creado_en = Column(DateTime, default=datetime.utcnow, nullable=False)


class Tarea(Base):
    __tablename__ = "tareas"
    
    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    titulo = Column(String(200), nullable=False)
    descripcion = Column(Text)
    completada = Column(Boolean, default=False, nullable=False, index=True)
    fecha_vencimiento = Column(Date)
    prioridad = Column(String(20), default="media")  # "baja", "media", "alta"
    creada_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    completada_en = Column(DateTime, nullable=True)
    
    # Relación con usuario
    usuario = relationship("Usuario", backref="tareas")


class TareaEvento(Base):
    __tablename__ = "tareas_evento"
    
    id = Column(Integer, primary_key=True, index=True)
    evento_id = Column(Integer, ForeignKey("eventos.id"), nullable=False, index=True)
    descripcion = Column(String(300), nullable=False)
    completada = Column(Boolean, default=False, nullable=False, index=True)
    creada_en = Column(DateTime, default=datetime.utcnow, nullable=False)
    completada_en = Column(DateTime, nullable=True)
    
    # Relación con evento
    evento = relationship("Evento", backref="tareas_evento")

