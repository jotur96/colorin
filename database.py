from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from pathlib import Path

# SQLite es gratuito y no requiere servidor externo
db_path = os.getenv("DATABASE_PATH", "./colorin.db")
# Asegurar que la ruta sea absoluta y el directorio exista
db_absolute_path = Path(db_path).resolve()
db_absolute_path.parent.mkdir(parents=True, exist_ok=True)

SQLALCHEMY_DATABASE_URL = f"sqlite:///{db_absolute_path}"

# Para SQLite necesitamos check_same_thread=False
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

